const std = @import("std");

pub fn build(b: *std.Build) void {
    const target = b.standardTargetOptions(.{});
    const optimize = b.standardOptimizeOption(.{});

    // Shared library for Python ctypes
    const lib = b.addSharedLibrary(.{
        .name = "fire_calc",
        .root_source_file = b.path("src/fire_calc.zig"),
        .target = target,
        .optimize = optimize,
    });
    b.installArtifact(lib);

    // Simple standalone Zig executable (optional demo)
    const exe = b.addExecutable(.{
        .name = "fire_calc_demo",
        .root_source_file = b.path("src/fire_calc.zig"),
        .target = target,
        .optimize = optimize,
    });
    b.installArtifact(exe);

    const run_demo = b.addRunArtifact(exe);
    run_demo.step.dependOn(b.getInstallStep());

    const demo_step = b.step("run-demo", "Run the fire_calc demo executable");
    demo_step.dependOn(&run_demo.step);
}
