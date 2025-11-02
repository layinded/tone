"""
Tests for enhancement features: exceptions, context managers, formatting.
"""

import tempfile
from pathlib import Path

import pytest

from tone import TONEDecoder, TONEEncoder
from tone.exceptions import (
    TONEDecodeError,
    TONEEncodeError,
    TONEError,
    TONESyntaxError,
    TONEValidationError,
)
from tone.format import create_table, format_value, summarize_structure


def test_toon_exception_base():
    """Test base TOON exception."""
    error = TONEError("Test error", context={"line": 1}, suggestions=["Fix it"])

    assert "Test error" in str(error)
    assert "Context:" in str(error)
    assert "line: 1" in str(error)
    assert "Suggestions:" in str(error)
    assert "Fix it" in str(error)


def test_toon_syntax_error():
    """Test syntax error with suggestions."""
    error = TONESyntaxError(
        "Indentation error",
        line_number=5,
        position=10,
        content="    hello",
    )

    assert "line_number: 5" in str(error)
    assert "Suggestions:" in str(error)
    assert "Check your indentation" in str(error)


def test_toon_validation_error():
    """Test validation error with suggestion."""
    error = TONEValidationError("Strict mode violation")

    assert "Suggestions:" in str(error)
    assert "strict=False" in str(error)


def test_toon_encoder_context_manager():
    """Test TONEEncoder context manager."""
    with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.toon') as tmp:
        tmp_path = Path(tmp.name)

    try:
        with TONEEncoder(tmp_path) as enc:
            enc.encode({"name": "Alice", "age": 30})

        # Read back
        content = tmp_path.read_text()
        assert "name: Alice" in content
        assert "age: 30" in content

    finally:
        tmp_path.unlink()


def test_toon_encoder_with_options():
    """Test TONEEncoder with options."""
    with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.toon') as tmp:
        tmp_path = Path(tmp.name)

    try:
        with TONEEncoder(tmp_path, options={"indent": 4}) as enc:
            enc.encode({"nested": {"data": "value"}})

        # Read back
        content = tmp_path.read_text()
        assert "nested:" in content

    finally:
        tmp_path.unlink()


def test_toon_decoder_context_manager():
    """Test TONEDecoder context manager."""
    with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.toon') as tmp:
        tmp_path = Path(tmp.name)

    try:
        # Write test data
        tmp_path.write_text("name: Alice\nage: 30")

        # Read back
        with TONEDecoder(tmp_path) as dec:
            data = dec.decode()

        assert data["name"] == "Alice"
        assert data["age"] == 30

    finally:
        tmp_path.unlink()


def test_toon_decoder_with_options():
    """Test TONEDecoder with options."""
    with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.toon') as tmp:
        tmp_path = Path(tmp.name)

    try:
        # Write test data
        tmp_path.write_text("name: Alice\nage: 30")

        # Read back with strict
        with TONEDecoder(tmp_path, options={"strict": True}) as dec:
            data = dec.decode()

        assert data["name"] == "Alice"

    finally:
        tmp_path.unlink()


def test_context_manager_outside_with():
    """Test error when using context manager incorrectly."""
    enc = TONEEncoder("/tmp/test.toon")

    with pytest.raises(RuntimeError, match="context manager"):
        enc.encode({"test": "data"})

    dec = TONEDecoder("/tmp/test.toon")

    with pytest.raises(RuntimeError, match="context manager"):
        dec.decode()


def test_format_value_primitive():
    """Test format_value with primitives."""
    assert "null" in format_value(None)
    assert "true" in format_value(True).lower()
    assert "42" in format_value(42)
    assert '"hello"' in format_value("hello")


def test_format_value_list():
    """Test format_value with lists."""
    result = format_value([1, 2, 3])
    assert "[3]" in result
    assert "1" in result
    assert "2" in result
    assert "3" in result


def test_format_value_dict():
    """Test format_value with dicts."""
    result = format_value({"name": "Alice", "age": 30})
    assert "name:" in result
    assert "Alice" in result
    assert "age:" in result
    assert "30" in result


def test_format_value_nested():
    """Test format_value with nested structures."""
    data = {
        "users": [
            {"id": 1, "name": "Alice"},
            {"id": 2, "name": "Bob"}
        ]
    }

    result = format_value(data, max_depth=5)
    assert "users:" in result
    assert "[2]" in result


def test_summarize_structure_dict():
    """Test summarize_structure with dict."""
    result = summarize_structure({"name": "Alice", "age": 30})
    assert "Object" in result
    assert "2 key" in result


def test_summarize_structure_list():
    """Test summarize_structure with list."""
    result = summarize_structure([1, 2, 3, 4, 5])
    assert "Array" in result
    assert "5 item" in result


def test_summarize_structure_complex():
    """Test summarize_structure with complex data."""
    data = {
        "users": [{"id": i} for i in range(100)]
    }

    result = summarize_structure(data, max_items=5)
    assert "Object" in result
    assert "users" in result
    assert "Array" in result


def test_create_table():
    """Test create_table with rich."""
    try:
        from rich.console import Console

        data = [
            {"name": "Alice", "score": 95},
            {"name": "Bob", "score": 87}
        ]

        table = create_table(data, title="Scores")
        assert table is not None
        assert table.title == "Scores"

        # Print to verify (not asserting, just ensuring it works)
        console = Console()
        # console.print(table)  # Would print if enabled

    except ImportError:
        pytest.skip("rich not available")


def test_format_value_max_depth():
    """Test format_value respects max_depth."""
    # Deeply nested data
    data = {"level": [{"a": [{"b": [{"c": 1}]}]}]}

    # Limited depth
    result = format_value(data, max_depth=2)
    assert "level" in result  # Should at least show first level

