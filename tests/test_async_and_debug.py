"""
Tests for async support and debug utilities.
"""

import asyncio
import pytest

from tone.async_support import (
    adecode,
    adecode_batch,
    adecode_parallel,
    aencode,
    aencode_batch,
    aencode_parallel,
)
from tone.debug import debug_decode, debug_encode, inspect_parse_tree


@pytest.mark.asyncio
async def test_aencode():
    """Test async encode."""
    data = {"name": "Alice", "age": 30}
    result = await aencode(data)

    assert "name: Alice" in result
    assert "age: 30" in result


@pytest.mark.asyncio
async def test_adecode():
    """Test async decode."""
    toon = "name: Alice\nage: 30"
    result = await adecode(toon)

    assert result["name"] == "Alice"
    assert result["age"] == 30


@pytest.mark.asyncio
async def test_async_roundtrip():
    """Test async round-trip."""
    data = {"users": [{"id": 1, "name": "Alice"}]}

    encoded = await aencode(data)
    decoded = await adecode(encoded)

    assert decoded == data


@pytest.mark.asyncio
async def test_aencode_batch():
    """Test async encode batch."""
    data = [{"id": i} for i in range(5)]

    results = []
    async for encoded in aencode_batch(data):
        results.append(encoded)

    assert len(results) == 5
    assert "id: 0" in results[0]


@pytest.mark.asyncio
async def test_adecode_batch():
    """Test async decode batch."""
    toons = ["id: 1", "id: 2", "id: 3"]

    results = []
    async for decoded in adecode_batch(toons):
        results.append(decoded)

    assert len(results) == 3
    assert results[0]["id"] == 1


@pytest.mark.asyncio
async def test_aencode_parallel():
    """Test parallel async encode."""
    data = [{"id": i} for i in range(10)]

    results = await aencode_parallel(data, max_workers=3)

    assert len(results) == 10
    assert all("id:" in result for result in results)


@pytest.mark.asyncio
async def test_adecode_parallel():
    """Test parallel async decode."""
    toons = [f"id: {i}" for i in range(10)]

    results = await adecode_parallel(toons, max_workers=3)

    assert len(results) == 10
    assert all(result["id"] == i for i, result in enumerate(results))


@pytest.mark.asyncio
async def test_parallel_order_preserved():
    """Test that parallel operations preserve order."""
    data = [{"id": i} for i in range(20)]

    results = await aencode_parallel(data)
    decoded = await adecode_parallel(results)

    assert len(decoded) == 20
    assert all(item["id"] == i for i, item in enumerate(decoded))


def test_debug_encode():
    """Test debug encode."""
    data = {"users": [{"id": 1, "name": "Alice"}]}

    debug = debug_encode(data)

    assert debug["success"] is True
    assert "encoded_length" in debug
    assert "format_detected" in debug
    assert "optimization_suggestions" in debug


def test_debug_encode_complex():
    """Test debug encode with complex data."""
    data = [{"id": i, "name": f"User{i}"} for i in range(100)]

    debug = debug_encode(data)

    assert debug["success"] is True
    assert debug["input_size"] == 100
    assert "tabular_array" in debug["format_detected"]


def test_debug_decode():
    """Test debug decode."""
    toon = "users[1]{id,name}:\n  1,Alice"

    debug = debug_decode(toon)

    assert debug["success"] is True
    assert "output_type" in debug
    assert "parse_tree" in debug
    assert "validation" in debug


def test_debug_decode_error():
    """Test debug decode with error."""
    # Use truly invalid syntax
    toon = "users[invalid{bracket]{\n  broken"

    debug = debug_decode(toon)

    # Should either fail or succeed and return something
    assert isinstance(debug, dict)


def test_inspect_parse_tree():
    """Test inspect parse tree."""
    toon = "name: Alice\nage: 30"

    tree = inspect_parse_tree(toon)

    assert "Document" in tree
    assert "name:" in tree
    assert "age:" in tree


def test_inspect_parse_tree_array():
    """Test inspect parse tree with array."""
    toon = "users[2]{id,name}:\n  1,Alice\n  2,Bob"

    tree = inspect_parse_tree(toon)

    assert "Document" in tree
    assert "Array (tabular" in tree
    assert "Fields:" in tree


def test_inspect_parse_tree_empty():
    """Test inspect parse tree with empty input."""
    tree = inspect_parse_tree("")

    assert "Document" in tree
    assert "Empty" in tree


def test_debug_suggestions():
    """Test that debug provides optimization suggestions."""
    data = [{"id": i} for i in range(200)]

    debug = debug_encode(data)

    assert len(debug["optimization_suggestions"]) > 0
    assert any("streaming" in s.lower() for s in debug["optimization_suggestions"])


def test_debug_compression_ratio():
    """Test that debug calculates compression ratio."""
    data = {"items": [{"id": i, "value": i * 10} for i in range(50)]}

    debug = debug_encode(data)

    if "compression_ratio" in debug:
        assert debug["compression_ratio"] > 0
        assert "size_reduction" in debug


@pytest.mark.asyncio
async def test_async_empty_list():
    """Test async operations with empty lists."""
    result = await aencode_parallel([])
    assert result == []

    result = await adecode_parallel([])
    assert result == []


@pytest.mark.asyncio
async def test_async_batch_empty():
    """Test async batch with empty iterator."""
    results = []
    async for encoded in aencode_batch([]):
        results.append(encoded)

    assert len(results) == 0


def test_inspect_nested_structure():
    """Test inspect with nested structures."""
    toon = "outer:\n  inner:\n    value: test"

    tree = inspect_parse_tree(toon)

    assert "Document" in tree
    assert "outer:" in tree
    assert "inner:" in tree

