"""
Token efficiency benchmark - measures output size reduction.

This benchmark compares TOON output size against JSON, XML, and YAML
to demonstrate token savings for LLM applications.
"""

import json
import time
from typing import Any, Dict, List

from tone import encode


def generate_github_repos(count: int = 3) -> List[Dict[str, Any]]:
    """Generate GitHub repository data."""
    return [
        {
            "id": 28457823,
            "name": "freeCodeCamp",
            "repo": "freeCodeCamp/freeCodeCamp",
            "description": "freeCodeCamp.org's open-source codebase and curriculum. Learn math, programming...",
            "createdAt": "2014-12-24T17:49:19Z",
            "updatedAt": "2025-10-28T11:58:08Z",
            "pushedAt": "2025-10-28T10:17:16Z",
            "stars": 430886,
            "watchers": 8583,
            "forks": 42146,
            "defaultBranch": "main",
        },
        {
            "id": 132750724,
            "name": "build-your-own-x",
            "repo": "codecrafters-io/build-your-own-x",
            "description": "Master programming by recreating your favorite technologies from scratch.",
            "createdAt": "2018-05-09T12:03:18Z",
            "updatedAt": "2025-10-28T12:37:11Z",
            "pushedAt": "2025-10-10T18:45:01Z",
            "stars": 430877,
            "watchers": 6332,
            "forks": 40453,
            "defaultBranch": "master",
        },
        {
            "id": 21737465,
            "name": "awesome",
            "repo": "sindresorhus/awesome",
            "description": "😎 Awesome lists about all kinds of interesting topics",
            "createdAt": "2014-07-11T13:42:37Z",
            "updatedAt": "2025-10-28T12:40:21Z",
            "pushedAt": "2025-10-27T17:57:31Z",
            "stars": 410052,
            "watchers": 8017,
            "forks": 32029,
            "defaultBranch": "main",
        },
    ][:count]


def generate_analytics_data(days: int = 5) -> List[Dict[str, Any]]:
    """Generate analytics time-series data."""
    return [
        {"date": "2025-01-01", "views": 6890, "clicks": 401, "conversions": 23, "revenue": 6015.59, "bounceRate": 0.63},
        {"date": "2025-01-02", "views": 6940, "clicks": 323, "conversions": 37, "revenue": 9086.44, "bounceRate": 0.36},
        {"date": "2025-01-03", "views": 4390, "clicks": 346, "conversions": 26, "revenue": 6360.75, "bounceRate": 0.48},
        {"date": "2025-01-04", "views": 3429, "clicks": 231, "conversions": 13, "revenue": 2360.96, "bounceRate": 0.65},
        {"date": "2025-01-05", "views": 5804, "clicks": 186, "conversions": 22, "revenue": 2535.96, "bounceRate": 0.37},
    ][:days]


def generate_ecommerce_order() -> Dict[str, Any]:
    """Generate e-commerce order data."""
    return {
        "orderId": "ORD-001",
        "customer": {"name": "Alice", "email": "alice@example.com"},
        "items": [
            {"sku": "WIDGET-001", "quantity": 2, "price": 29.99},
            {"sku": "GADGET-002", "quantity": 1, "price": 89.50},
        ],
        "total": 149.48,
        "status": "pending",
        "createdAt": "2025-01-15T10:30:00Z",
    }


def measure_size(data: str) -> int:
    """Measure string size in bytes."""
    return len(data.encode("utf-8"))


def format_json(data: Dict[str, Any]) -> str:
    """Format as JSON."""
    return json.dumps(data, indent=2)


def format_json_compact(data: Dict[str, Any]) -> str:
    """Format as compact JSON."""
    return json.dumps(data, separators=(",", ":"))


def format_toon(data: Dict[str, Any]) -> str:
    """Format as TOON."""
    return encode(data)


def format_toon_tab(data: Dict[str, Any]) -> str:
    """Format as TOON with tab delimiter."""
    return encode(data, {"delimiter": "\t"})


def calculate_savings(toon_size: int, json_size: int) -> float:
    """Calculate percentage savings."""
    return ((json_size - toon_size) / json_size) * 100


def run_benchmark():
    """Run token efficiency benchmark."""
    print("╔══════════════════════════════════════════════════════════════════╗")
    print("║                                                                  ║")
    print("║         TOON Python - Token Efficiency Benchmark                ║")
    print("║                                                                  ║")
    print("╚══════════════════════════════════════════════════════════════════╝\n")

    datasets = [
        ("GitHub Repositories", lambda: {"repositories": generate_github_repos(3)}),
        ("Daily Analytics", lambda: {"metrics": generate_analytics_data(5)}),
        ("E-Commerce Order", generate_ecommerce_order),
    ]

    results = []

    for name, data_fn in datasets:
        data = data_fn()

        json_formatted = format_json(data)
        json_size = measure_size(json_formatted)

        json_compact = format_json_compact(data)
        json_compact_size = measure_size(json_compact)

        toon_formatted = format_toon(data)
        toon_size = measure_size(toon_formatted)

        toon_tab = format_toon_tab(data)
        toon_tab_size = measure_size(toon_tab)

        savings_vs_json = calculate_savings(toon_size, json_size)
        savings_vs_compact = calculate_savings(toon_size, json_compact_size)

        result = {
            "name": name,
            "json": json_size,
            "json_compact": json_compact_size,
            "toon": toon_size,
            "toon_tab": toon_tab_size,
            "savings_vs_json": savings_vs_json,
            "savings_vs_compact": savings_vs_compact,
        }
        results.append(result)

        print(f"📊 {name}")
        print(f"   JSON:        {json_size:>6} bytes")
        print(f"   JSON compact:{json_compact_size:>6} bytes")
        print(f"   TOON:        {toon_size:>6} bytes ({savings_vs_json:.1f}% savings vs JSON)")
        print(f"   TOON (tab):  {toon_tab_size:>6} bytes")
        print()

    # Summary
    total_json = sum(r["json"] for r in results)
    total_compact = sum(r["json_compact"] for r in results)
    total_toon = sum(r["toon"] for r in results)
    total_savings = calculate_savings(total_toon, total_json)

    print("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
    print("📈 Summary")
    print(f"   Total JSON:     {total_json:>6} bytes")
    print(f"   Total compact:  {total_compact:>6} bytes")
    print(f"   Total TOON:     {total_toon:>6} bytes")
    print(f"   Overall savings: {total_savings:.1f}%")
    print("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n")

    return results


if __name__ == "__main__":
    run_benchmark()

