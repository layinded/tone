"""
Performance benchmark - measures encoding/decoding speed.

This benchmark measures the time taken to encode and decode various
data structures to evaluate runtime performance.
"""

import json
import time
from typing import Any, Dict, List

from tone import decode, encode


def time_encoding(data: Dict[str, Any], iterations: int = 1000) -> float:
    """Time encoding operation."""
    start = time.perf_counter()
    for _ in range(iterations):
        encode(data)
    end = time.perf_counter()
    return (end - start) / iterations


def time_decoding(toon_str: str, iterations: int = 1000) -> float:
    """Time decoding operation."""
    start = time.perf_counter()
    for _ in range(iterations):
        decode(toon_str)
    end = time.perf_counter()
    return (end - start) / iterations


def time_roundtrip(data: Dict[str, Any], iterations: int = 1000) -> float:
    """Time roundtrip encode->decode operation."""
    start = time.perf_counter()
    for _ in range(iterations):
        toon_str = encode(data)
        decode(toon_str)
    end = time.perf_counter()
    return (end - start) / iterations


def generate_small_data() -> Dict[str, Any]:
    """Generate small test dataset."""
    return {
        "users": [
            {"id": 1, "name": "Alice", "role": "admin"},
            {"id": 2, "name": "Bob", "role": "user"},
        ]
    }


def generate_medium_data() -> Dict[str, Any]:
    """Generate medium test dataset."""
    return {
        "repositories": [
            {
                "id": i,
                "name": f"repo-{i}",
                "stars": i * 1000,
                "forks": i * 100,
                "active": i % 2 == 0,
            }
            for i in range(100)
        ]
    }


def generate_large_data() -> Dict[str, Any]:
    """Generate large test dataset."""
    return {
        "analytics": [
            {
                "date": f"2025-01-{i:02d}",
                "views": 1000 + i * 10,
                "clicks": i * 5,
                "conversions": i % 10,
                "revenue": i * 100.5,
            }
            for i in range(1, 1001)
        ]
    }


def format_time(microseconds: float) -> str:
    """Format time in appropriate units."""
    if microseconds < 1:
        return f"{microseconds * 1000:.3f} ns"
    if microseconds < 1000:
        return f"{microseconds:.3f} µs"
    return f"{microseconds / 1000:.3f} ms"


def run_performance_benchmark():
    """Run performance benchmark."""
    print("╔══════════════════════════════════════════════════════════════════╗")
    print("║                                                                  ║")
    print("║         TOON Python - Performance Benchmark                       ║")
    print("║                                                                  ║")
    print("╚══════════════════════════════════════════════════════════════════╝\n")

    datasets = [
        ("Small (2 records)", generate_small_data, 10000),
        ("Medium (100 records)", generate_medium_data, 1000),
        ("Large (1000 records)", generate_large_data, 100),
    ]

    for name, data_fn, iterations in datasets:
        data = data_fn()
        toon_str = encode(data)

        encode_time_us = time_encoding(data, iterations) * 1e6
        decode_time_us = time_decoding(toon_str, iterations) * 1e6
        roundtrip_time_us = time_roundtrip(data, iterations) * 1e6

        print(f"📊 {name} ({iterations} iterations)")
        print(f"   Encode:    {format_time(encode_time_us)}")
        print(f"   Decode:    {format_time(decode_time_us)}")
        print(f"   Roundtrip: {format_time(roundtrip_time_us)}")
        print()

    print("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
    print("Note: Times are per operation averages across iterations")
    print("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n")


if __name__ == "__main__":
    run_performance_benchmark()

