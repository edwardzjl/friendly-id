#!/usr/bin/env python3
"""
Performance benchmark for FriendlyID.

This script benchmarks the two key aspects of FriendlyID:
1. Serialization Performance (CPU) - base62 encoding overhead
2. Bandwidth Efficiency (I/O) - network/storage savings

Usage:
    python benchmark.py
    python benchmark.py --count 10000  # Custom count
    python benchmark.py --verbose      # Show individual results
"""

import argparse
import json
import statistics
import sys
import time
import uuid
from typing import Callable

from friendly_id import FriendlyID


def time_function(func: Callable, iterations: int = 3) -> dict[str, float]:
    """Time a function multiple times and return statistics."""
    times = []
    for _ in range(iterations):
        start = time.perf_counter()
        func()
        end = time.perf_counter()
        times.append(end - start)

    return {
        "mean": statistics.mean(times),
        "median": statistics.median(times),
        "min": min(times),
        "max": max(times),
        "std": statistics.stdev(times) if len(times) > 1 else 0.0,
    }


class BenchmarkRunner:
    """Main benchmark runner class."""

    def __init__(self, count: int = 1000, iterations: int = 3, verbose: bool = False):
        self.count = count
        self.iterations = iterations
        self.verbose = verbose

        # Pre-generate test data
        print(f"Generating {count} test UUIDs...")
        self.standard_uuids = [uuid.uuid4() for _ in range(count)]
        self.friendly_ids = [FriendlyID.from_uuid(u) for u in self.standard_uuids]

    def benchmark_serialization_performance(self):
        """Benchmark CPU cost of serialization - the core base62 conversion."""
        print("\n⚡ Serialization Performance (CPU)")
        print("=" * 50)

        # Core serialization: the base62 conversion bottleneck
        def uuid_to_string():
            return [str(u) for u in self.standard_uuids]

        def friendly_to_string():
            return [str(f) for f in self.friendly_ids]

        # JSON scenario (common real-world case)
        def uuid_json():
            data = [str(u) for u in self.standard_uuids]
            return json.dumps(data)

        def friendly_json():
            data = [str(f) for f in self.friendly_ids]
            return json.dumps(data)

        results = {
            "UUID -> string": time_function(uuid_to_string, self.iterations),
            "FriendlyID -> base62": time_function(friendly_to_string, self.iterations),
            "UUID -> JSON": time_function(uuid_json, self.iterations),
            "FriendlyID -> JSON": time_function(friendly_json, self.iterations),
        }

        # Calculate performance overhead
        uuid_string_time = results["UUID -> string"]["mean"]
        friendly_string_time = results["FriendlyID -> base62"]["mean"]
        overhead_factor = (
            friendly_string_time / uuid_string_time if uuid_string_time > 0 else 0
        )

        self._print_results(results)

        print("\n💡 Performance Analysis:")
        print(
            f"   Base62 encoding is {overhead_factor:.1f}x slower than UUID string conversion"
        )
        print(
            f"   Overhead: {(friendly_string_time - uuid_string_time) * 1000:.2f}ms per {self.count:,} IDs"
        )
        print(
            f"   Per ID: {((friendly_string_time - uuid_string_time) / self.count) * 1000000:.2f} microseconds"
        )

        return results

    def benchmark_bandwidth_efficiency(self):
        """Benchmark I/O efficiency - network/storage bandwidth savings."""
        print("\n📡 Bandwidth Efficiency (I/O)")
        print("=" * 50)

        # The core difference: UUID string vs base62 string
        uuid_strings = [str(u) for u in self.standard_uuids]
        friendly_strings = [str(f) for f in self.friendly_ids]

        # Calculate total characters and bytes
        uuid_chars = sum(len(s) for s in uuid_strings)
        friendly_chars = sum(len(s) for s in friendly_strings)
        uuid_bytes = sum(len(s.encode("utf-8")) for s in uuid_strings)
        friendly_bytes = sum(len(s.encode("utf-8")) for s in friendly_strings)

        # Calculate savings
        char_savings = (uuid_chars - friendly_chars) / uuid_chars * 100
        byte_savings = (uuid_bytes - friendly_bytes) / uuid_bytes * 100
        kb_saved = (uuid_chars - friendly_chars) / 1024

        print(f"String Length Comparison ({self.count:,} IDs):")
        print(
            f"  Standard UUIDs:    {uuid_chars:,} chars ({uuid_chars / len(uuid_strings):.0f} per ID)"
        )
        print(
            f"  FriendlyIDs:     {friendly_chars:,} chars ({friendly_chars / len(friendly_strings):.0f} per ID)"
        )
        print(f"  Character savings: {char_savings:.1f}%")

        print("\nUTF-8 Byte Size:")
        print(f"  Standard UUIDs:    {uuid_bytes:,} bytes")
        print(f"  FriendlyIDs:     {friendly_bytes:,} bytes")
        print(f"  Bandwidth savings: {byte_savings:.1f}%")

        print("\n💡 I/O Impact Analysis:")
        print(f"   Network: {kb_saved:.1f} KB less data per {self.count:,} IDs")
        print(f"   Storage: {byte_savings:.1f}% reduction in database/log size")
        print(f"   URLs: {char_savings:.1f}% shorter (better for SEO and UX)")

        return {
            "uuid_chars": uuid_chars,
            "friendly_chars": friendly_chars,
            "uuid_bytes": uuid_bytes,
            "friendly_bytes": friendly_bytes,
            "char_savings_percent": char_savings,
            "byte_savings_percent": byte_savings,
            "kb_saved": kb_saved,
        }

    def _print_results(self, results: dict[str, dict[str, float]]):
        """Print benchmark results in a formatted table."""
        if not results:
            return

        print(f"{'Operation':<35} {'Mean (ms)':<12} {'Min (ms)':<12} {'Max (ms)':<12}")
        print("-" * 75)

        for operation, times in results.items():
            mean_ms = times["mean"] * 1000
            min_ms = times["min"] * 1000
            max_ms = times["max"] * 1000

            print(f"{operation:<35} {mean_ms:<12.3f} {min_ms:<12.3f} {max_ms:<12.3f}")

            if self.verbose and times["std"] > 0:
                std_ms = times["std"] * 1000
                print(f"{'  (std dev)':<35} {std_ms:<12.3f}")

    def run_all_benchmarks(self):
        """Run all available benchmarks."""
        print("🚀 FriendlyID Performance Benchmark")
        print(f"Testing with {self.count:,} items, {self.iterations} iterations each")
        print("=" * 70)

        all_results = {}

        # Core benchmarks: CPU vs I/O
        all_results["performance"] = self.benchmark_serialization_performance()
        all_results["bandwidth"] = self.benchmark_bandwidth_efficiency()

        return all_results


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(description="FriendlyID performance benchmark")
    parser.add_argument(
        "--count",
        type=int,
        default=1000,
        help="Number of UUIDs to test (default: 1000)",
    )
    parser.add_argument(
        "--iterations",
        type=int,
        default=3,
        help="Number of timing iterations (default: 3)",
    )
    parser.add_argument("--verbose", action="store_true", help="Show detailed results")

    args = parser.parse_args()

    # Show environment info
    print(f"Python version: {sys.version}")

    runner = BenchmarkRunner(
        count=args.count, iterations=args.iterations, verbose=args.verbose
    )

    runner.run_all_benchmarks()

    # Summary
    print("\n📊 Summary")
    print("=" * 50)
    print("FriendlyID Trade-offs:")
    print("• CPU: ~6x slower base62 encoding (microseconds per ID)")
    print("• I/O: ~39% bandwidth savings (significant for APIs/storage)")
    print("• Format: URL-safe, no special characters")
    print("• Verdict: Great for most applications where I/O > CPU cost")


if __name__ == "__main__":
    main()
