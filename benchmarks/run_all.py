"""
Run all benchmarks and generate a comprehensive report.
"""

import sys
from typing import List

from benchmarks.memory import run_memory_benchmark
from benchmarks.performance import run_performance_benchmark
from benchmarks.token_efficiency import run_benchmark as run_token_efficiency_benchmark


def main():
    """Run all benchmarks."""
    benchmarks = [
        ("Token Efficiency", run_token_efficiency_benchmark),
        ("Performance", run_performance_benchmark),
        ("Memory Usage", run_memory_benchmark),
    ]

    if len(sys.argv) > 1 and sys.argv[1] == "--list":
        print("Available benchmarks:")
        for name, _ in benchmarks:
            print(f"  - {name}")
        return

    print("Running all benchmarks...\n")

    for name, benchmark_fn in benchmarks:
        try:
            print(f"\n{'='*70}")
            benchmark_fn()
        except Exception as e:
            print(f"\n❌ Error running {name}: {e}")
            import traceback
            traceback.print_exc()

    print("\n✅ All benchmarks complete!")


if __name__ == "__main__":
    main()

