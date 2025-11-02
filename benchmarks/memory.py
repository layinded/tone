"""
Memory usage benchmark - measures memory consumption during encoding/decoding.

This benchmark uses memory profiling to measure peak memory usage
for different dataset sizes.
"""

import gc
import sys
from typing import Any, Dict

from tone import decode, encode


def format_bytes(bytes_count: int) -> str:
    """Format bytes in human-readable format."""
    for unit in ["B", "KB", "MB", "GB"]:
        if bytes_count < 1024.0:
            return f"{bytes_count:.2f} {unit}"
        bytes_count /= 1024.0
    return f"{bytes_count:.2f} TB"


def measure_memory(data: Dict[str, Any]) -> Dict[str, float]:
    """Measure memory usage for encoding and decoding."""
    gc.collect()
    baseline = sys.getsizeof(data)

    # Encode
    gc.collect()
    toon_str = encode(data)
    toon_size = len(toon_str.encode("utf-8"))

    # Decode
    gc.collect()
    decoded = decode(toon_str)
    decoded_size = sys.getsizeof(decoded)

    return {
        "input_size": baseline,
        "toon_output": toon_size,
        "decoded_size": decoded_size,
        "compression": (1 - toon_size / baseline) * 100 if baseline > 0 else 0,
    }


def generate_data(size: int) -> Dict[str, Any]:
    """Generate test data of specified size."""
    return {
        "records": [
            {
                "id": i,
                "name": f"Item-{i}",
                "value": i * 1.5,
                "active": i % 2 == 0,
            }
            for i in range(size)
        ]
    }


def run_memory_benchmark():
    """Run memory usage benchmark."""
    print("╔══════════════════════════════════════════════════════════════════╗")
    print("║                                                                  ║")
    print("║         TOON Python - Memory Usage Benchmark                      ║")
    print("║                                                                  ║")
    print("╚══════════════════════════════════════════════════════════════════╝\n")

    sizes = [10, 100, 1000, 10000]

    for size in sizes:
        data = generate_data(size)
        metrics = measure_memory(data)

        print(f"📊 Dataset: {size} records")
        print(f"   Input size:      {format_bytes(metrics['input_size'])}")
        print(f"   TOON output:     {format_bytes(metrics['toon_output'])}")
        print(f"   Decoded size:    {format_bytes(metrics['decoded_size'])}")
        if metrics["compression"] > 0:
            print(f"   Compression:     {metrics['compression']:.1f}%")
        print()

    print("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
    print("Note: Memory measurements approximate, using sys.getsizeof()")
    print("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n")


if __name__ == "__main__":
    run_memory_benchmark()

