use anyhow::{Context, Result};
use bytemuck::{Pod, Zeroable};
use wgpu::{util::DeviceExt, BufferUsages};

#[repr(C)]
#[derive(Clone, Copy, Pod, Zeroable, Debug)]
pub struct Params {
    pub dims: [u32; 2],  // width, height
    pub cell: f32,       // pixel size (meters)
    pub _pad0: f32,      // padding
    pub azimuth: f32,    // radians
    pub zenith: f32,     // radians (90 - altitude)
    pub _pad1: [f32; 2], // padding to 32 bytes
}

pub struct GpuContext {
    pub device: wgpu::Device,
    pub queue: wgpu::Queue,
    shader: wgpu::ShaderModule,
    pipeline: wgpu::ComputePipeline,
    bind_layout: wgpu::BindGroupLayout,
}

impl GpuContext {
    pub async fn new() -> Result<Self> {
        let instance = wgpu::Instance::default();
        let adapter = instance
            .request_adapter(&wgpu::RequestAdapterOptions {
                power_preference: wgpu::PowerPreference::HighPerformance,
                compatible_surface: None,
                force_fallback_adapter: false,
            })
            .await
            .context("No suitable GPU adapter found")?;

        let (device, queue) = adapter
            .request_device(
                &wgpu::DeviceDescriptor {
                    label: Some("hillshade-device"),
                    required_features: wgpu::Features::empty(),
                    required_limits: wgpu::Limits::default(),
                    ..Default::default()
                },
                None,
            )
            .await
            .context("request_device failed")?;

        let shader = device.create_shader_module(wgpu::ShaderModuleDescriptor {
            label: Some("hillshade-shader"),
            source: wgpu::ShaderSource::Wgsl(include_str!("shader.wgsl").into()),
        });

        let bind_layout = device.create_bind_group_layout(&wgpu::BindGroupLayoutDescriptor {
            label: Some("hillshade-bind-layout"),
            entries: &[
                // heightmap
                wgpu::BindGroupLayoutEntry {
                    binding: 0,
                    visibility: wgpu::ShaderStages::COMPUTE,
                    ty: wgpu::BindingType::Buffer {
                        ty: wgpu::BufferBindingType::Storage { read_only: true },
                        has_dynamic_offset: false,
                        min_binding_size: None,
                    },
                    count: None,
                },
                // out_rgba
                wgpu::BindGroupLayoutEntry {
                    binding: 1,
                    visibility: wgpu::ShaderStages::COMPUTE,
                    ty: wgpu::BindingType::Buffer {
                        ty: wgpu::BufferBindingType::Storage { read_only: false },
                        has_dynamic_offset: false,
                        min_binding_size: None,
                    },
                    count: None,
                },
                // params (uniform)
                wgpu::BindGroupLayoutEntry {
                    binding: 2,
                    visibility: wgpu::ShaderStages::COMPUTE,
                    ty: wgpu::BindingType::Buffer {
                        ty: wgpu::BufferBindingType::Uniform,
                        has_dynamic_offset: false,
                        min_binding_size: None,
                    },
                    count: None,
                },
            ],
        });

        let pipeline_layout = device.create_pipeline_layout(&wgpu::PipelineLayoutDescriptor {
            label: Some("hillshade-pipeline-layout"),
            bind_group_layouts: &[&bind_layout],
            push_constant_ranges: &[],
        });

        let pipeline = device.create_compute_pipeline(&wgpu::ComputePipelineDescriptor {
            label: Some("hillshade-pipeline"),
            layout: Some(&pipeline_layout),
            module: &shader,
            entry_point: "main",
            compilation_options: wgpu::PipelineCompilationOptions::default(),
        });

        Ok(Self {
            device,
            queue,
            shader,
            pipeline,
            bind_layout,
        })
    }

    pub fn run(
        &self,
        heightmap: &[f32],
        width: u32,
        height: u32,
        params: Params,
    ) -> Result<Vec<u8>> {
        let npx = (width as usize) * (height as usize);
        assert_eq!(heightmap.len(), npx);

        let device = &self.device;
        let queue = &self.queue;

        let hm_bytes = bytemuck::cast_slice(heightmap);
        let hm_buf = device.create_buffer_init(&wgpu::util::BufferInitDescriptor {
            label: Some("heightmap"),
            contents: hm_bytes,
            usage: BufferUsages::STORAGE | BufferUsages::COPY_DST,
        });

        let out_buf = device.create_buffer(&wgpu::BufferDescriptor {
            label: Some("out-rgba"),
            size: (npx * 4) as u64, // rgba8
            usage: BufferUsages::STORAGE | BufferUsages::COPY_SRC,
            mapped_at_creation: false,
        });

        let params_buf = device.create_buffer_init(&wgpu::util::BufferInitDescriptor {
            label: Some("params"),
            contents: bytemuck::bytes_of(&params),
            usage: BufferUsages::UNIFORM | BufferUsages::COPY_DST,
        });

        let bind_group = device.create_bind_group(&wgpu::BindGroupDescriptor {
            label: Some("hillshade-bind-group"),
            layout: &self.bind_layout,
            entries: &[
                wgpu::BindGroupEntry {
                    binding: 0,
                    resource: hm_buf.as_entire_binding(),
                },
                wgpu::BindGroupEntry {
                    binding: 1,
                    resource: out_buf.as_entire_binding(),
                },
                wgpu::BindGroupEntry {
                    binding: 2,
                    resource: params_buf.as_entire_binding(),
                },
            ],
        });

        let mut encoder =
            device.create_command_encoder(&wgpu::CommandEncoderDescriptor { label: Some("enc") });
        {
            let mut pass = encoder.begin_compute_pass(&wgpu::ComputePassDescriptor {
                label: Some("pass"),
                timestamp_writes: None,
            });
            pass.set_pipeline(&self.pipeline);
            pass.set_bind_group(0, &bind_group, &[]);
            let wg_x = (width + 15) / 16;
            let wg_y = (height + 15) / 16;
            pass.dispatch_workgroups(wg_x, wg_y, 1);
        }

        let read_buf = device.create_buffer(&wgpu::BufferDescriptor {
            label: Some("readback"),
            size: (npx * 4) as u64,
            usage: BufferUsages::MAP_READ | BufferUsages::COPY_DST,
            mapped_at_creation: false,
        });
        encoder.copy_buffer_to_buffer(&out_buf, 0, &read_buf, 0, (npx * 4) as u64);

        queue.submit(Some(encoder.finish()));

        {
            let (sender, receiver) = std::sync::mpsc::sync_channel(1);
            read_buf
                .slice(..)
                .map_async(wgpu::MapMode::Read, move |res| {
                    sender.send(res).ok();
                });
            device.poll(wgpu::Maintain::Wait);
            receiver
                .recv()
                .context("readback channel closed")?
                .context("map_async failed")?;
        }

        let view = read_buf.slice(..).get_mapped_range();
        let mut out = vec![0u8; npx * 4];
        out.copy_from_slice(&view);
        drop(view);
        read_buf.unmap();

        Ok(out)
    }
}

pub fn radians(deg: f32) -> f32 {
    std::f32::consts::PI * deg / 180.0
}
