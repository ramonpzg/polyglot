import cv2
import numpy as np
import time
import sys
import os

try:
    import video_filters
    RUST_AVAILABLE = True
except ImportError:
    RUST_AVAILABLE = False
    print("⚠️  Rust module not built yet. Run: maturin develop")

class VideoProcessor:
    def __init__(self, source=None, scale=10):
        self.scale = scale
        self.use_rust = RUST_AVAILABLE
        self.cap = None

        # Auto-detect source
        if source is None:
            source = self.find_video_source()

        # Try to open video source
        if isinstance(source, str) and os.path.isfile(source):
            print(f"📹 Using video file: {source}")
            self.cap = cv2.VideoCapture(source)
        elif isinstance(source, int):
            print(f"📷 Trying camera index: {source}")
            self.cap = cv2.VideoCapture(source)
            if not self.cap.isOpened():
                # Try with different backend
                self.cap = cv2.VideoCapture(source, cv2.CAP_V4L2)

        if not self.cap or not self.cap.isOpened():
            print("❌ Could not open video source")
            print("Falling back to generated test pattern...")
            self.use_test_pattern = True
        else:
            self.use_test_pattern = False
            # Set camera properties
            self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
            self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)

    def find_video_source(self):
        """Auto-detect available video source"""
        # Try cameras 0-5
        for i in range(6):
            cap = cv2.VideoCapture(i)
            if cap.isOpened():
                ret, _ = cap.read()
                cap.release()
                if ret:
                    print(f"✅ Found working camera at index {i}")
                    return i

        print("⚠️  No camera found")
        return None

    def generate_test_frame(self, frame_num):
        """Generate a test pattern when no camera is available"""
        height, width = 480, 640
        frame = np.zeros((height, width, 3), dtype=np.uint8)

        # Create gradient pattern
        for y in range(height):
            for x in range(width):
                val = (x + frame_num * 5) % 256
                frame[y, x] = [val, (y * 255) // height, 128]

        # Add text
        cv2.putText(frame, "TEST PATTERN", (width//2 - 100, height//2),
                   cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2)

        return frame

    def process_frame_python(self, frame):
        """Pure Python ASCII conversion"""
        if frame is None:
            return "No frame available"

        height, width = frame.shape[:2]
        ascii_chars = ' .:-=+*#%@'

        # Calculate dimensions
        chars_per_row = width // self.scale
        rows = height // self.scale

        result = []
        for y in range(rows):
            row = ''
            for x in range(chars_per_row):
                # Get average brightness of the block
                y_start = y * self.scale
                x_start = x * self.scale
                y_end = min(y_start + self.scale, height)
                x_end = min(x_start + self.scale, width)

                block = frame[y_start:y_end, x_start:x_end]

                if block.size > 0:
                    # Calculate average brightness
                    brightness = np.mean(block)
                    # Map to ASCII character
                    idx = int(brightness * len(ascii_chars) / 256)
                    idx = min(idx, len(ascii_chars) - 1)
                    row += ascii_chars[idx]
                else:
                    row += ' '
            result.append(row)

        return '\n'.join(result)

    def process_frame_rust(self, frame):
        """Rust-powered processing"""
        if frame is None or not RUST_AVAILABLE:
            return self.process_frame_python(frame)

        height, width = frame.shape[:2]

        # Convert BGR to RGB and flatten
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        flat_data = rgb_frame.flatten().tolist()

        # Call Rust function
        return video_filters.process_frame_parallel(flat_data, width, height, self.scale)

    def run_comparison(self):
        """Run the main demo"""
        print("\n" + "="*60)
        print("🎬 Video ASCII Art Processor")
        print("="*60)
        print("Controls:")
        print("  'q' - Quit")
        print("  'r' - Toggle Rust/Python")
        print("  's' - Change scale (detail level)")
        print("="*60 + "\n")

        use_rust = self.use_rust
        frame_num = 0

        while True:
            # Get frame
            if self.use_test_pattern:
                frame = self.generate_test_frame(frame_num)
                frame_num += 1
            else:
                ret, frame = self.cap.read()
                if not ret:
                    print("Failed to grab frame")
                    continue

            # Process frame
            start = time.perf_counter()

            if use_rust and RUST_AVAILABLE:
                ascii_art = self.process_frame_rust(frame)
                method = "RUST 🦀"
            else:
                ascii_art = self.process_frame_python(frame)
                method = "PYTHON 🐍"

            elapsed = (time.perf_counter() - start) * 1000
            fps = 1000 / elapsed if elapsed > 0 else 0

            # Clear terminal and display ASCII art
            print("\033[H\033[J", end='')  # Clear terminal
            print(f"Method: {method} | Frame time: {elapsed:.1f}ms | FPS: {fps:.1f}")
            print(f"Scale: {self.scale} (smaller = more detail)")
            print("-" * 80)
            print(ascii_art)

            # Show original video in window
            display_frame = frame.copy()
            color = (0, 255, 0) if use_rust else (0, 0, 255)
            cv2.putText(display_frame, f"{method}: {elapsed:.1f}ms",
                       (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, color, 2)
            cv2.imshow('Original Video', display_frame)

            # Handle keyboard input
            key = cv2.waitKey(1) & 0xFF
            if key == ord('q'):
                break
            elif key == ord('r'):
                use_rust = not use_rust
                if not RUST_AVAILABLE:
                    print("\n⚠️  Rust module not available. Run: maturin develop")
                    use_rust = False
            elif key == ord('s'):
                # Cycle through scales
                scales = [5, 8, 10, 15, 20]
                current_idx = scales.index(self.scale) if self.scale in scales else 0
                self.scale = scales[(current_idx + 1) % len(scales)]

        # Cleanup
        if self.cap:
            self.cap.release()
        cv2.destroyAllWindows()

def main():
    import argparse
    parser = argparse.ArgumentParser(description='Video ASCII Art Processor')
    parser.add_argument('--camera', type=int, default=None,
                       help='Camera index (0, 1, 2, ...)')
    parser.add_argument('--scale', type=int, default=8,
                       help='Scale factor (lower = more detail)')
    args = parser.parse_args()

    processor = VideoProcessor(source=args.camera, scale=args.scale)
    processor.run_comparison()

if __name__ == "__main__":
    main()
