# Zig for Pythonistas: A Hands‑On Guide

This tutorial helps an advanced Python developer get productive with Zig by building on familiar mental models and using this repo’s Python↔Zig interop as a concrete anchor. You’ll learn the Zig basics, memory model, error handling, build system, and how to expose high‑performance functions back to Python via `ctypes`.

If you’re comfortable with NumPy, typing, and packaging in Python, you already have the right instincts. Zig gives you precise control, C‑level performance, and safety features without a garbage collector.

---

## Why Zig (coming from Python)

- Control without ceremony: no GC, deterministic memory, explicit allocators.
- Safety tools: bounds checks, `defer`/`errdefer`, error unions instead of exceptions.
- Interop: C ABI is a first‑class citizen; easy to export/call from Python.
- Tooling: single self‑hosted compiler, batteries‑included standard library, simple build.

Use Zig when a tight loop is your bottleneck and you need predictable performance. Keep Python for orchestration, I/O, and rich ecosystems.

---

## The Mental Model (Zig vs Python)

- Everything is explicit. If memory is allocated, you must decide who frees it.
- No exceptions. Functions return “error unions” and you propagate with `try`.
- Immutability by default is encouraged (use `const` unless you really need `var`).
- Arrays are fixed‑size; slices are views over memory (`[]T`). Strings are `[]const u8`.
- No hidden conversions. Types don’t auto‑coerce; cast explicitly.

---

## A Tiny Tour of the Language

### Hello, world and functions

```zig
const std = @import("std");

pub fn main() !void {
    try std.io.getStdOut().writer().print("Hello, Zig!\n", .{});
}

pub fn add(a: i64, b: i64) i64 {
    return a + b;
}
```

- `!void` means “this function returns either an error or `void`”.
- `try` propagates errors up the call stack.
- `pub` exports a symbol (visible to other files or, for `export fn`, to C ABI).

### Arrays, slices, and pointers

```zig
var arr: [4]i32 = .{ 1, 2, 3, 4 };   // fixed-size array
var s: []i32 = arr[0..];             // slice: view over arr
s[1] = 20;                           // mutate through slice

var x: i32 = 42;
const px: *i32 = &x;                 // single-item pointer
```

- Arrays copy by value; slices are non‑owning views: `[]T`.
- C‑style “many item” pointer is `[ * ]T` (no length). We use this in C interop.

### Optionals and errors

```zig
fn maybe_index(s: []const u8, needle: u8) ?usize {
    for (s, 0..) |ch, i| if (ch == needle) return i;
    return null; // no match
}

fn might_fail(x: i32) !i32 {
    if (x < 0) return error.Negative;
    return x * 2;
}
```

- `?T` is an optional; handle with `if (opt) |v| { ... } else { ... }`.
- `!T` is an error union; `try` unwraps or returns the error.

### defer and errdefer

```zig
const std = @import("std");

pub fn use_file() !void {
    var file = try std.fs.cwd().createFile("tmp.bin", .{});
    defer file.close();               // always runs on scope exit
    errdefer std.fs.cwd().deleteFile("tmp.bin") catch {};
    try file.writeAll("hello");
    // If any error happens after errdefer, file is deleted.
}
```

### Allocators (no GC)

Zig standard library APIs that allocate take an `allocator`. Common choices:

- `std.heap.page_allocator`: global OS pages (simple, fine for examples).
- `std.heap.ArenaAllocator`: bulk‑allocate and free once.

```zig
const std = @import("std");

pub fn make_numbers(n: usize) ![]i64 {
    var arena = std.heap.ArenaAllocator.init(std.heap.page_allocator);
    defer arena.deinit();
    const alloc = arena.allocator();
    const buf = try alloc.alloc(i64, n);
    for (buf, 0..) |*v, i| v.* = @intCast(i64, i);
    return buf; // valid until arena.deinit()
}
```

---

## Build System Basics

- Standalone: `zig build-exe src/main.zig -O ReleaseFast`
- Using build.zig (recommended): `zig build`, `zig build run`, `zig build test`

This repo’s `src/fire_calc_zig/build.zig` defines:

- a shared library: `libfire_calc.{so|dylib|dll}` for Python `ctypes`
- a tiny demo executable

Key lines:

```zig
const lib = b.addSharedLibrary(.{
    .name = "fire_calc",
    .root_source_file = b.path("src/fire_calc.zig"),
    .target = target,
    .optimize = optimize,
});
```

Use `-Doptimize=ReleaseFast` for benchmarking.

---

## Python ↔ Zig Interop (ctypes)

We expose a C‑ABI function from Zig and call it from Python.

Zig (C ABI export):

```zig
// src/fire_calc_zig/src/fire_calc.zig
export fn calculate_fire_danger_index_out(
    drought_factor: [*]const f64,
    ffmc: [*]const f64,
    wind_speed: [*]const f64,
    temperature_c: [*]const f64,
    humidity_frac: [*]const f64,
    elevation_m: [*]const f64,
    size: usize,
    out: [*]f64,
) void {
    var i: usize = 0;
    while (i < size) : (i += 1) {
        // compute one element (pure scalar loop for portability)
        out[i] = /* ... */;
    }
}
```

- `[ * ]const f64` is a C‑style pointer to many elements (no length).
- `usize` matches C’s `size_t`.

Python (ctypes binding):

```python
# src/fire_calc/zig_binding.py
_lib.calculate_fire_danger_index_out.argtypes = [
    ct.POINTER(ct.c_double),  # drought_factor
    ct.POINTER(ct.c_double),  # ffmc
    ct.POINTER(ct.c_double),  # wind_speed
    ct.POINTER(ct.c_double),  # temperature_c
    ct.POINTER(ct.c_double),  # humidity_frac
    ct.POINTER(ct.c_double),  # elevation_m
    ct.c_size_t,              # size
    ct.POINTER(ct.c_double),  # out
]

out = np.empty_like(d)
_lib.calculate_fire_danger_index_out(
    d.ctypes.data_as(ct.POINTER(ct.c_double)),
    f.ctypes.data_as(ct.POINTER(ct.c_double)),
    # ...
    ct.c_size_t(n),
    out.ctypes.data_as(ct.POINTER(ct.c_double)),
)
```

Tips:

- Ensure NumPy arrays are `float64` and C‑contiguous (`np.ascontiguousarray`).
- Don’t allocate memory in Zig for Python to free; pass an output buffer from Python.
- Name the library appropriately per OS (`.so`, `.dylib`, `.dll`). The loader in this repo auto‑detects.

---

## The FDI Example (what’s in this repo)

We implement a deterministic version of a Fire Danger Index:

```
FDI = 2 * exp((D - FFMC)/50) * (1 + W/10) * Temperature_Factor
Temperature_Factor = (T/30) * (1 - 0.5*RH) * (1 + 0.1*(elev/2000))
```

- Python version lives in `src/fire_calc/python_impl.py` (NumPy vectorized).
- Zig version lives in `src/fire_calc_zig/src/fire_calc.zig` (tight loop).
- `src/fire_calc/zig_binding.py` bridges Python to the Zig shared library.

Build and run:

```bash
cd src/fire_calc_zig
ZIG_GLOBAL_CACHE_DIR=$PWD/.zig-cache zig build -Doptimize=ReleaseFast
cd -
FIRE_CALC_LIB_PATH=$PWD/src/fire_calc_zig/zig-out/lib/libfire_calc.so \
  uv run python -m fire_calc.benchmark --sizes 10000 200000 --use-zig
```

You should see Python and Zig agree exactly, with Zig typically faster.

---

## Performance: What to Know Early

- Keep hot loops simple; let the optimizer work. Avoid virtual calls or dynamic dispatch in inner loops.
- Bounds checks exist; Zig can elide them when provably safe in ReleaseFast.
- Prefer slices (`[]T`) over pointers for known‑length iteration within Zig.
- Consider batching work and minimizing passes over memory.
- SIMD: Zig has portable vector types (`@Vector(N, T)`), but start with scalar; only add vectors once you’ve measured.
- Threads: Use `std.Thread.spawn` and split work by chunks when the task is embarrassingly parallel.

Example vector (advanced; optional):

```zig
fn add_vec(a: f64, b: f64) f64 {
    const V = @Vector(4, f64);
    const va: V = .{ a, a, a, a };
    const vb: V = .{ b, b, b, b };
    const out: V = va + vb;
    return out[0];
}
```

---

## Testing and Debugging

- Inline tests:

```zig
const std = @import("std");

test "scalar fdi sanity" {
    const got = 1.0; // replace with real call
    try std.testing.expect(got >= 0);
}
```

- Run: `zig test src/fire_calc_zig/src/fire_calc.zig`
- Printf‑style debugging: `std.debug.print("{d}\n", .{value});`
- Assertions: `std.debug.assert(cond);`
- Use `-Doptimize=Debug` for dev; `ReleaseFast` for benchmarks.

---

## Common Gotchas (Python perspective)

- Arrays vs slices: `[N]T` copies by value; `[]T` is a view. Returning `[N]T` returns a copy.
- Strings aren’t special: `[]const u8` (no implicit null terminator). Convert explicitly for C APIs.
- Const everywhere: Use `const` by default; switch to `var` only when needed.
- No implicit conversions: `f32` won’t become `f64` unless you cast (`@floatCast`). Same for ints.
- Ownership: Decide which side owns memory. For Python interop, allocate in Python.

---

## Exercises (small wins)

1) AX+Y in Zig, driven by Python

- Zig:

```zig
export fn axpy_out(a: f64, x: [*]const f64, y: [*]const f64, n: usize, out: [*]f64) void {
    var i: usize = 0;
    while (i < n) : (i += 1) out[i] = a * x[i] + y[i];
}
```

- Python (ctypes): ensure `argtypes` and `restype=None`, pass contiguous arrays.

2) Multi‑threaded chunking

- Split `[0..n)` into `t` chunks and spawn `t` threads writing to disjoint `out` ranges. Join threads.

3) Add a Zig unit test

- Create a tiny `test` block for `axpy_out` (rework as a pure function returning a slice).

Measure speedups vs NumPy and learn where the crossover point lies.

---

## Mapping Table (quick mental reference)

- Python list/NumPy array → Zig slice `[]T`
- Python `float` → Zig `f64` (or `f32`)
- Python `int` → Zig sized ints (`i64`, `u64`, etc.)
- Python `None` → Zig `null` (`?T` optionals)
- Python `try/except` → Zig `!T` + `try`/`catch`
- Python context manager → Zig `defer`/`errdefer`

---

## Where to Go Next

- Explore `std` docs in your Zig install (`/usr/lib/zig/std/`).
- Read this repo’s `build.zig` and `fire_calc.zig` closely; duplicate the pattern for your own kernels.
- Add a second Zig routine (e.g., vector normalization) and wire it into Python.
- Try `zig build test` and write some Zig unit tests.

With these tools, you can responsibly move hot paths to Zig and keep Python for everything else. That’s the sweet spot for productive, polyglot performance work.

