PixelFlow — Real-time Image Processing (Rust + Python + WASM)

Overview
- Minimal Rust library targeting native, Python (PyO3), and WebAssembly.
- Focus: Australian satellite imagery — bushfire detection, vegetation health, and coastal analysis.
- Core engine in one Rust codebase with portable bindings.

Key Features
- NDVI and false-color rendering across multispectral bands.
- Bushfire risk assessment for Australian regions.
- Parallel CPU processing with optional Rayon (disabled for WASM).

Build Targets
- Native Rust: `cargo run --bin pixelflow-cli` (synthetic demo)
- Python: `maturin develop --features python`
- WASM: `wasm-pack build --target web --features wasm` (Rayon disabled by default)

Project Layout
- `src/` core engine plus bindings
- `examples/` Python and Rust usage demos
- `web/` minimal browser demo
- `data/` placeholders for imagery (you provide the assets)

Notes
- The CLI and examples generate synthetic data to keep the project lightweight.
- Replace the data loaders with your actual GeoTIFF readers in real deployments.

