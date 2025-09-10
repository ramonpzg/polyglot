#!/usr/bin/env python3
"""
Build script for compiling Zig hurricane tracking module.
"""

import subprocess
import sys
from pathlib import Path


def build_zig():
    """Compile the Zig source code to a shared library."""
    src_dir = Path(__file__).parent / "merengue_cyclone" / "src"
    src_file = src_dir / "hurricane.zig"
    output_file = src_dir / "hurricane.so"

    if not src_file.exists():
        print(f"Error: Source file {src_file} not found")
        return False

    # Ensure source directory exists
    src_dir.mkdir(parents=True, exist_ok=True)

    # Zig build command for shared library
    cmd = [
        "zig", "build-lib",
        str(src_file),
        "-dynamic",
        "-O", "ReleaseFast",
        "-femit-bin=" + str(output_file),
        "-fPIC",
        "-lc",
    ]

    print(f"Building Zig library...")
    print(f"  Source: {src_file}")
    print(f"  Output: {output_file}")
    print(f"  Command: {' '.join(cmd)}")

    try:
        result = subprocess.run(cmd, capture_output=True, text=True)
        if result.returncode != 0:
            print(f"Error building Zig library:")
            print(result.stderr)
            return False
        else:
            print(f"✅ Successfully built {output_file}")
            return True
    except FileNotFoundError:
        print("Error: Zig compiler not found. Please install Zig.")
        print("  Visit: https://ziglang.org/download/")
        return False
    except Exception as e:
        print(f"Error building Zig library: {e}")
        return False


def build_fallback():
    """Create a marker file indicating to use pure Python fallback."""
    src_dir = Path(__file__).parent / "merengue_cyclone" / "src"
    marker_file = src_dir / ".use_python_fallback"

    src_dir.mkdir(parents=True, exist_ok=True)
    marker_file.touch()

    print("⚠️  Using pure Python fallback (Zig not available)")
    print("  Performance will be reduced but functionality preserved")


if __name__ == "__main__":
    # Try to build with Zig
    if not build_zig():
        # Fall back to pure Python if Zig build fails
        build_fallback()
        print("\nNote: Install Zig for maximum performance:")
        print("  pip install ziglang")
        print("  or visit https://ziglang.org/download/")
    else:
        print("\n🚀 Zig acceleration enabled!")
        print("  Run benchmarks with: merengue-cyclone benchmark --compare")
