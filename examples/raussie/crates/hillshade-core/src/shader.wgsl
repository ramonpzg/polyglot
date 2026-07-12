struct Params {
  dims: vec2<u32>,
  cell: f32,
  _pad0: f32,
  azimuth: f32,
  zenith: f32,
  _pad1: vec2<f32>,
};

@group(0) @binding(0) var<storage, read> heightmap: array<f32>;
@group(0) @binding(1) var<storage, read_write> out_rgba: array<u32>;
@group(0) @binding(2) var<uniform> params: Params;

fn clamp_idx(x: i32, y: i32, w: i32, h: i32) -> i32 {
  let xi = max(0, min(x, w - 1));
  let yi = max(0, min(y, h - 1));
  return yi * w + xi;
}

@compute @workgroup_size(16, 16)
fn main(@builtin(global_invocation_id) gid: vec3<u32>) {
  let w: i32 = i32(params.dims.x);
  let h: i32 = i32(params.dims.y);

  let x: i32 = i32(gid.x);
  let y: i32 = i32(gid.y);
  if (x >= w || y >= h) { return; }

  let zc = heightmap[clamp_idx(x, y, w, h)];
  let zx1 = heightmap[clamp_idx(x + 1, y, w, h)];
  let zx0 = heightmap[clamp_idx(x - 1, y, w, h)];
  let zy1 = heightmap[clamp_idx(x, y + 1, w, h)];
  let zy0 = heightmap[clamp_idx(x, y - 1, w, h)];

  let dzdx = (zx1 - zx0) / (2.0 * params.cell);
  let dzdy = (zy1 - zy0) / (2.0 * params.cell);

  let slope = atan(sqrt(dzdx*dzdx + dzdy*dzdy));
  let aspect = atan2(dzdy, -dzdx);

  let cos_i =
    cos(params.zenith) * cos(slope) +
    sin(params.zenith) * sin(slope) * cos(params.azimuth - aspect);

  let i = clamp((cos_i + 1.0) * 0.5, 0.0, 1.0);
  let v: u32 = u32(round(i * 255.0));
  let rgba: u32 = (0xFFu << 24) | (v << 16) | (v << 8) | v;
  out_rgba[u32(y) * u32(w) + u32(x)] = rgba;
}
