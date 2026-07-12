import numpy as np
import time

# Test without video first
def test_rust_module():
    try:
        import video_filters
        print("✅ Rust module imported successfully!")

        # Create fake image data (100x100 RGB)
        width, height = 100, 100
        data = np.random.randint(0, 256, width * height * 3, dtype=np.uint8).tolist()

        # Test Rust function
        start = time.perf_counter()
        result = video_filters.process_frame(data, width, height, 10)
        elapsed = (time.perf_counter() - start) * 1000

        print(f"✅ Processed in {elapsed:.2f}ms")
        print("ASCII output preview:")
        print(result[:200])  # First few lines

    except ImportError as e:
        print(f"❌ Failed to import: {e}")
        print("Run: maturin develop")

if __name__ == "__main__":
    test_rust_module()
