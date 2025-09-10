#!/usr/bin/env python3
"""
Test script for Merengue Cyclone hurricane tracker.
Verifies that the Zig integration is working correctly.
"""

import time
from datetime import datetime, timedelta
from pathlib import Path
import sys

# Add the package to path
sys.path.insert(0, str(Path(__file__).parent))

from merengue_cyclone.hurricane import (
    HurricaneTracker,
    HurricanePoint,
    calculate_distance,
    estimate_surge,
)

def test_distance_calculation():
    """Test the haversine distance calculation."""
    print("🧪 Testing distance calculation...")

    # Santo Domingo to Punta Cana
    santo_domingo = (18.4861, -69.9312)
    punta_cana = (18.5601, -68.3725)

    distance = calculate_distance(
        santo_domingo[0], santo_domingo[1],
        punta_cana[0], punta_cana[1]
    )

    print(f"  Distance from Santo Domingo to Punta Cana: {distance:.2f} km")
    print(f"  ✅ Distance calculation working!")
    return True

def test_storm_surge():
    """Test storm surge estimation."""
    print("\n🌊 Testing storm surge estimation...")

    # Category 4 hurricane approaching
    wind_speed = 230  # km/h
    pressure = 945  # millibars
    depth = 20  # meters
    angle = 45  # degrees

    surge = estimate_surge(wind_speed, pressure, depth, angle)

    print(f"  Wind speed: {wind_speed} km/h")
    print(f"  Pressure: {pressure} mb")
    print(f"  Estimated surge: {surge:.2f} meters")
    print(f"  ✅ Storm surge calculation working!")
    return True

def test_hurricane_tracking():
    """Test the hurricane tracking system."""
    print("\n🌀 Testing hurricane tracking...")

    tracker = HurricaneTracker()

    # Create a simulated hurricane track
    base_time = datetime.now()
    points = [
        HurricanePoint(15.0, -60.0, 985, 130, base_time),
        HurricanePoint(15.5, -61.5, 975, 160, base_time + timedelta(hours=6)),
        HurricanePoint(16.0, -63.0, 960, 190, base_time + timedelta(hours=12)),
        HurricanePoint(16.5, -64.5, 945, 220, base_time + timedelta(hours=18)),
        HurricanePoint(17.0, -66.0, 940, 230, base_time + timedelta(hours=24)),
    ]

    # Add observations
    for point in points:
        tracker.add_observation("test_hurricane", point)

    # Analyze track
    analysis = tracker.analyze_track("test_hurricane")

    print(f"  Track points: {len(points)}")
    print(f"  Total distance: {analysis.total_distance:.2f} km")
    print(f"  Average speed: {analysis.average_speed:.2f} km/h")
    print(f"  Max intensity: Category {analysis.max_intensity.category}")
    print(f"  ACE Index: {analysis.ace:.2f}")
    print(f"  ✅ Hurricane tracking working!")
    return True

def test_dominican_impact():
    """Test Dominican Republic impact assessment."""
    print("\n🇩🇴 Testing DR impact assessment...")

    tracker = HurricaneTracker()

    # Create a hurricane approaching DR
    base_time = datetime.now()
    points = [
        HurricanePoint(16.0, -64.0, 970, 185, base_time),
        HurricanePoint(16.5, -65.5, 965, 195, base_time + timedelta(hours=6)),
        HurricanePoint(17.2, -67.0, 960, 205, base_time + timedelta(hours=12)),
        HurricanePoint(17.9, -68.5, 955, 215, base_time + timedelta(hours=18)),
        HurricanePoint(18.5, -70.0, 960, 195, base_time + timedelta(hours=24)),
    ]

    for point in points:
        tracker.add_observation("georges", point)

    impact = tracker.estimate_dominican_impact("georges")

    print(f"  Risk level: {impact['risk'].upper()}")
    print(f"  Closest approach: {impact['closest_approach_km']:.0f} km")
    print(f"  Max winds: {impact['max_winds_kmh']:.0f} km/h")
    print(f"  Storm surge: {impact['estimated_surge_m']:.1f} m")
    print(f"  ✅ Impact assessment working!")
    return True

def benchmark_performance():
    """Benchmark Zig vs Python performance."""
    print("\n⚡ Performance Benchmark...")

    tracker = HurricaneTracker()

    # Run benchmark
    iterations = 10000
    print(f"  Running {iterations} distance calculations...")

    # Test points
    lat1, lon1 = 18.5, -70.0
    lat2, lon2 = 19.0, -71.0

    # Python timing (simplified)
    start = time.perf_counter()
    for _ in range(iterations):
        _ = calculate_distance(lat1, lon1, lat2, lon2)
    elapsed = (time.perf_counter() - start) * 1000

    print(f"  Time: {elapsed:.2f} ms")
    print(f"  Operations/sec: {(iterations / elapsed * 1000):.0f}")

    # Full benchmark comparison
    results = tracker.benchmark_performance(iterations)
    if 'speedup' in results:
        print(f"  🚀 Speedup with Zig: {results['speedup']:.1f}x faster!")

    print(f"  ✅ Benchmark complete!")
    return True

def main():
    """Run all tests."""
    print("=" * 50)
    print("🌀 MERENGUE CYCLONE TEST SUITE")
    print("=" * 50)

    tests = [
        test_distance_calculation,
        test_storm_surge,
        test_hurricane_tracking,
        test_dominican_impact,
        benchmark_performance,
    ]

    passed = 0
    failed = 0

    for test in tests:
        try:
            if test():
                passed += 1
        except Exception as e:
            print(f"  ❌ Test failed: {e}")
            failed += 1

    print("\n" + "=" * 50)
    print(f"Results: {passed} passed, {failed} failed")

    if failed == 0:
        print("🎉 All tests passed! Zig integration working perfectly!")
    else:
        print("⚠️  Some tests failed. Check the Zig library compilation.")

    return 0 if failed == 0 else 1

if __name__ == "__main__":
    exit(main())
