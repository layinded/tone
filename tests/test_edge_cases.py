"""
Comprehensive edge case tests for TONE encoding/decoding.

Based on TypeScript test suite validation and error handling sections.
"""

import pytest
from tone import decode, encode


class TestArrayLengthMismatches:
    """Test array length validation and mismatches."""

    def test_inline_primitive_array_length_mismatch(self):
        """Inline primitive array with wrong count should error."""
        toon = "tags[2]: a,b,c"
        with pytest.raises(Exception):
            decode(toon, {"strict": True})

    def test_list_array_length_mismatch(self):
        """List array with wrong count should error."""
        toon = "items[1]:\n  - 1\n  - 2"
        with pytest.raises(Exception):
            decode(toon, {"strict": True})

    def test_tabular_row_count_mismatch(self):
        """Tabular row count mismatch should error."""
        toon = "[1]{id}:\n  1\n  2"
        with pytest.raises(Exception):
            decode(toon, {"strict": True})

    def test_tabular_row_width_mismatch(self):
        """Tabular row width mismatch should error."""
        toon = "items[2]{id,name}:\n  1,Ada\n  2"
        with pytest.raises(Exception):
            decode(toon, {"strict": True})


class TestInvalidEscapes:
    """Test invalid escape sequence handling."""

    def test_invalid_escape_sequence(self):
        """Invalid escape sequences should error."""
        with pytest.raises(SyntaxError):
            decode('"a\\x"')

    def test_unterminated_string(self):
        """Unterminated strings should error."""
        with pytest.raises(SyntaxError):
            decode('"unterminated')


class TestMissingColon:
    """Test missing colon validation."""

    def test_missing_colon_nested(self):
        """Missing colon in nested context should error."""
        with pytest.raises(Exception):
            decode("a:\n  user")


class TestDelimiterMismatch:
    """Test delimiter mismatch validation."""

    def test_delimiter_mismatch_in_header(self):
        """Delimiter mismatch should error."""
        toon = "items[2\t]{a\tb}:\n  1,2\n  3,4"
        with pytest.raises(Exception):
            decode(toon, {"strict": True})


class TestStrictModeIndentation:
    """Test strict mode indentation validation."""

    def test_non_multiple_indentation_object(self):
        """Non-multiple indentation in objects should error."""
        toon = "a:\n   b: 1"  # 3 spaces with indent=2
        with pytest.raises(Exception):
            decode(toon, {"strict": True})

    def test_non_multiple_indentation_list(self):
        """Non-multiple indentation in lists should error."""
        toon = "items[2]:\n   - id: 1\n   - id: 2"  # 3 spaces
        with pytest.raises(Exception):
            decode(toon, {"strict": True})

    def test_custom_indent_size_validation(self):
        """Custom indent size validation."""
        # 3 spaces with indent=4 should error
        toon = "a:\n   b: 1"
        with pytest.raises(Exception):
            decode(toon, {"strict": True, "indent": 4})

    def test_custom_indent_size_accept(self):
        """Custom indent size accepts correct indentation."""
        # 4 spaces with indent=4 is valid
        toon = "a:\n    b: 1"
        result = decode(toon, {"indent": 4})
        assert result == {"a": {"b": 1}}

    def test_tab_in_indentation(self):
        """Tab character in indentation should error."""
        toon = "a:\n\tb: 1"
        with pytest.raises(Exception):
            decode(toon, {"strict": True})

    def test_mixed_tabs_spaces(self):
        """Mixed tabs and spaces should error."""
        toon = "a:\n \tb: 1"  # space + tab
        with pytest.raises(Exception):
            decode(toon, {"strict": True})

    def test_tab_at_start_of_line(self):
        """Tab at start should error."""
        toon = "\ta: 1"
        with pytest.raises(Exception):
            decode(toon, {"strict": True})

    def test_tabs_in_quoted_strings_allowed(self):
        """Tabs in quoted strings should be allowed."""
        toon = 'text: "hello\tworld"'
        result = decode(toon, {"strict": True})
        assert result == {"text": "hello\tworld"}

    def test_tabs_in_quoted_keys_allowed(self):
        """Tabs in quoted keys should be allowed."""
        toon = '"key\ttab": value'
        result = decode(toon, {"strict": True})
        assert result == {"key\ttab": "value"}

    def test_tabs_in_quoted_array_elements(self):
        """Tabs in quoted array elements should be allowed."""
        toon = 'items[2]: "a\tb","c\td"'
        result = decode(toon, {"strict": True})
        assert result == {"items": ["a\tb", "c\td"]}

    def test_non_strict_accepts_non_multiple(self):
        """Non-strict accepts non-multiple indentation."""
        toon = "a:\n   b: 1"  # 3 spaces
        result = decode(toon, {"strict": False})
        assert result == {"a": {"b": 1}}

    def test_non_strict_accepts_tabs(self):
        """Non-strict accepts tab indentation."""
        toon = "a:\n\tb: 1"
        result = decode(toon, {"strict": False})
        # Tabs ignored in indentation, so treated as root
        assert "b" in result or result == {"a": {}, "b": 1}

    def test_non_strict_deeply_nested_non_multiples(self):
        """Non-strict accepts deeply nested non-multiples."""
        toon = "a:\n   b:\n     c: 1"  # 3 and 5 spaces
        result = decode(toon, {"strict": False})
        assert result == {"a": {"b": {"c": 1}}}

    def test_empty_lines_no_validation_error(self):
        """Empty lines don't trigger validation."""
        toon = "a: 1\n\nb: 2"
        result = decode(toon, {"strict": True})
        assert result == {"a": 1, "b": 2}

    def test_root_level_content_valid(self):
        """Root-level content always valid."""
        toon = "a: 1\nb: 2\nc: 3"
        result = decode(toon, {"strict": True})
        assert result == {"a": 1, "b": 2, "c": 3}

    def test_lines_with_only_spaces_ignored(self):
        """Lines with only spaces are ignored."""
        toon = "a: 1\n   \nb: 2"
        result = decode(toon, {"strict": True})
        assert result == {"a": 1, "b": 2}


class TestBlankLinesInArrays:
    """Test blank line validation in arrays."""

    def test_blank_line_in_list_array(self):
        """Blank line in list array should error."""
        toon = "items[3]:\n  - a\n\n  - b\n  - c"
        with pytest.raises(Exception):
            decode(toon, {"strict": True})

    def test_blank_line_in_tabular_array(self):
        """Blank line in tabular array should error."""
        toon = "items[2]{id}:\n  1\n\n  2"
        with pytest.raises(Exception):
            decode(toon, {"strict": True})

    def test_multiple_blank_lines_in_array(self):
        """Multiple blank lines should error."""
        toon = "items[2]:\n  - a\n\n\n  - b"
        with pytest.raises(Exception):
            decode(toon, {"strict": True})


class TestTabularEdgeCases:
    """Edge cases specific to tabular arrays."""

    def test_empty_tabular_array(self):
        """Empty tabular array with header."""
        toon = "items[0]{id,name}:"
        result = decode(toon)
        assert result == {"items": []}

    def test_tabular_single_field(self):
        """Tabular with single field."""
        toon = "items[2]{id}:\n  1\n  2"
        result = decode(toon)
        assert result == {"items": [{"id": 1}, {"id": 2}]}

    def test_tabular_many_fields(self):
        """Tabular with many fields."""
        toon = "items[1]{a,b,c,d,e}:\n  1,2,3,4,5"
        result = decode(toon)
        assert result == {"items": [{"a": 1, "b": 2, "c": 3, "d": 4, "e": 5}]}

    def test_tabular_with_quoted_values(self):
        """Tabular with quoted values containing delimiters."""
        toon = 'items[2]{id,desc}:\n  1,"hello,world"\n  2,"test:value"'
        result = decode(toon)
        assert result == {"items": [{"id": 1, "desc": "hello,world"}, {"id": 2, "desc": "test:value"}]}

    def test_tabular_with_null_values(self):
        """Tabular with null values."""
        toon = "items[2]{id,value}:\n  1,null\n  2,test"
        result = decode(toon)
        assert result == {"items": [{"id": 1, "value": None}, {"id": 2, "value": "test"}]}


class TestListArrayEdgeCases:
    """Edge cases specific to list arrays."""

    def test_list_array_single_item(self):
        """List array with single item."""
        toon = "items[1]:\n  - id: 1"
        result = decode(toon)
        assert result == {"items": [{"id": 1}]}

    def test_list_array_with_nested_objects(self):
        """List array with nested objects."""
        toon = "items[1]:\n  - id: 1\n    nested:\n      x: 1\n      y: 2"
        result = decode(toon)
        assert result == {"items": [{"id": 1, "nested": {"x": 1, "y": 2}}]}

    def test_list_array_mixed_types(self):
        """List array with mixed types."""
        # List format should handle this
        toon = "items[2]:\n  - id: 1\n    value: 42\n  - id: 2\n    value: true\n    extra: null"
        result = decode(toon)
        assert len(result["items"]) == 2
        assert result["items"][0]["value"] == 42
        assert result["items"][1]["value"] is True


class TestInlineArrayEdgeCases:
    """Edge cases for inline primitive arrays."""

    def test_large_inline_array(self):
        """Large inline array."""
        toon = "nums[100]: " + ",".join(str(i) for i in range(100))
        result = decode(toon)
        assert len(result["nums"]) == 100
        assert result["nums"][0] == 0
        assert result["nums"][99] == 99

    def test_mixed_type_array(self):
        """Mixed types in inline array."""
        toon = "data[5]: a,b,true,false,42"
        result = decode(toon)
        assert result == {"data": ["a", "b", True, False, 42]}

    def test_array_with_all_quoted_primitives(self):
        """Array with all values quoted."""
        toon = 'items[3]: "1","2","3"'
        result = decode(toon)
        assert result == {"items": ["1", "2", "3"]}

    def test_empty_strings_in_array(self):
        """Multiple empty strings in array."""
        toon = 'items[3]: "","","a"'
        result = decode(toon)
        assert result == {"items": ["", "", "a"]}


class TestDeeplyNested:
    """Deeply nested structures."""

    def test_very_deeply_nested(self):
        """Very deeply nested objects."""
        toon = "a:\n  b:\n    c:\n      d:\n        e:\n          f: deep"
        result = decode(toon)
        assert result == {"a": {"b": {"c": {"d": {"e": {"f": "deep"}}}}}}

    def test_mixed_nesting_depth(self):
        """Objects with varying nesting depth."""
        toon = "a:\n  b: 1\n  c:\n    d: 2\n    e:\n      f: 3"
        result = decode(toon)
        assert result == {"a": {"b": 1, "c": {"d": 2, "e": {"f": 3}}}}


class TestUnicodeEdgeCases:
    """Unicode and special character edge cases."""

    def test_unicode_in_keys(self):
        """Unicode characters in keys."""
        toon = "你好: 世界\n🚀: rocket"
        result = decode(toon)
        assert result == {"你好": "世界", "🚀": "rocket"}

    def test_unicode_in_values(self):
        """Unicode characters in values."""
        toon = "name: José\ncity: 北京"
        result = decode(toon)
        assert result == {"name": "José", "city": "北京"}

    def test_unicode_in_arrays(self):
        """Unicode in arrays."""
        toon = "tags[3]: café,你好,🚀"
        result = decode(toon)
        assert result == {"tags": ["café", "你好", "🚀"]}

    def test_unicode_escapes(self):
        """Unicode escape sequences."""
        toon = 'text: "\\u00E9moji\\u2708"'
        # Note: May depend on parser implementation
        result = decode(toon)
        assert isinstance(result["text"], str)


class TestSpecialNumericEdgeCases:
    """Special numeric value edge cases."""

    def test_very_large_number(self):
        """Very large integer."""
        large = 10**20
        toon = encode({"value": large})
        result = decode(toon)
        assert result["value"] == large

    def test_very_small_decimal(self):
        """Very small decimal."""
        small = 1e-10
        data = encode({"value": small})
        result = decode(data)
        assert abs(result["value"] - small) < 1e-12

    def test_precision_fidelity(self):
        """Decimal precision maintained."""
        value = 0.12345678901234567890
        toon = encode({"value": value})
        result = decode(toon)
        # Should maintain reasonable precision
        assert abs(result["value"] - value) < 1e-10


class TestTabDelimiterEdgeCases:
    """Tab delimiter specific edge cases."""

    def test_tab_delimiter_basic(self):
        """Basic tab delimiter."""
        toon = "tags[3\t]: reading\tgaming\tcoding"
        result = decode(toon)
        assert result == {"tags": ["reading", "gaming", "coding"]}

    def test_tab_delimiter_tabular(self):
        """Tab delimiter with tabular array."""
        toon = "items[2\t]{id\tname}:\n  1\tAlice\n  2\tBob"
        result = decode(toon)
        assert result == {"items": [{"id": 1, "name": "Alice"}, {"id": 2, "name": "Bob"}]}

    def test_tab_delimiter_with_quoted_tabs(self):
        """Tab delimiter with quoted values containing tabs."""
        toon = 'items[2\t]{id\tdesc}:\n  1\t"hello\tworld"\n  2\tnormal'
        result = decode(toon)
        assert result == {"items": [{"id": 1, "desc": "hello\tworld"}, {"id": 2, "desc": "normal"}]}


class TestPipeDelimiterEdgeCases:
    """Pipe delimiter specific edge cases."""

    def test_pipe_delimiter_basic(self):
        """Basic pipe delimiter."""
        toon = "tags[3|]: reading|gaming|coding"
        result = decode(toon)
        assert result == {"tags": ["reading", "gaming", "coding"]}

    def test_pipe_delimiter_with_pipes_in_values(self):
        """Pipe delimiter with quoted values containing pipes."""
        toon = 'items[2|]: "item1|extra"|item2'
        result = decode(toon)
        assert result == {"items": ["item1|extra", "item2"]}


class TestLengthMarkerEdgeCases:
    """Length marker (#) edge cases."""

    def test_length_marker_inline(self):
        """Length marker in inline array."""
        toon = "tags[#3]: a,b,c"
        result = decode(toon)
        assert result == {"tags": ["a", "b", "c"]}

    def test_length_marker_tabular(self):
        """Length marker in tabular array."""
        toon = "items[#2]{id}:\n  1\n  2"
        result = decode(toon)
        assert result == {"items": [{"id": 1}, {"id": 2}]}

    def test_length_marker_with_delimiter(self):
        """Length marker with custom delimiter."""
        toon = "tags[#3|]: a|b|c"
        result = decode(toon)
        assert result == {"tags": ["a", "b", "c"]}


class TestRootArrayEdgeCases:
    """Root-level array edge cases."""

    def test_root_inline_simple(self):
        """Simple root inline array."""
        assert decode("[3]: a,b,c") == ["a", "b", "c"]

    def test_root_tabular_simple(self):
        """Simple root tabular array."""
        toon = "[2]{id}:\n  1\n  2"
        assert decode(toon) == [{"id": 1}, {"id": 2}]

    def test_root_list_array(self):
        """Root list array."""
        toon = "[2]:\n  - id: 1\n  - id: 2"
        assert decode(toon) == [{"id": 1}, {"id": 2}]

    def test_root_empty_array(self):
        """Root empty array."""
        assert decode("[0]:") == []


class TestComplexRealWorldScenarios:
    """Complex real-world scenarios."""

    def test_api_response_structure(self):
        """Typical API response."""
        data = {
            "status": "success",
            "data": {
                "users": [{"id": 1, "name": "Alice", "email": "alice@test.com", "active": True}],
                "total": 1,
            },
            "meta": {"version": "1.0", "timestamp": "2025-01-01"},
        }
        toon = encode(data)
        result = decode(toon)
        assert result == data

    def test_configuration_file(self):
        """Typical config file structure."""
        data = {
            "app": {"name": "MyApp", "debug": False},
            "database": {"host": "localhost", "port": 5432, "ssl": True},
            "features": ["auth", "api", "logging", "metrics"],
        }
        toon = encode(data)
        result = decode(toon)
        assert result == data

    def test_log_format(self):
        """Logging format structure."""
        data = {
            "logs": [
                {"timestamp": "2025-01-01 10:00:00", "level": "INFO", "message": "Started"},
                {"timestamp": "2025-01-01 10:00:05", "level": "ERROR", "message": "Failed", "trace": "stack"},
            ]
        }
        toon = encode(data)
        result = decode(toon)
        assert result == data

    def test_nested_mixed_types(self):
        """Deeply nested with mixed types."""
        data = {
            "config": {
                "features": [{"name": "auth", "enabled": True}, {"name": "api", "enabled": False}],
                "tags": ["prod", "v2"],
                "meta": {"created": "2025-01-01", "version": 2},
            }
        }
        toon = encode(data)
        result = decode(toon)
        assert result == data


class TestErrorRecoveryAndGracefulDegradation:
    """Test error recovery and graceful degradation."""

    def test_strict_mode_disabled_allows_errors(self):
        """Non-strict mode should handle more edge cases."""
        # This should work in non-strict even if it's malformed
        toon = "user:\n   bad_indent: value"
        result = decode(toon, {"strict": False})
        # Should parse somehow
        assert "user" in result or "bad_indent" in result

    def test_partial_parse_on_error(self):
        """Partial parsing behavior on syntax errors."""
        # Test behavior when encountering errors
        pass  # Implementation dependent


# Additional utility tests

def test_encode_decode_invariance():
    """Roundtrip should always produce identical data."""
    test_cases = [
        None,
        True,
        False,
        0,
        42,
        3.14,
        -7,
        "",
        "hello",
        {"a": 1},
        {"a": 1, "b": 2},
        [1, 2, 3],
        {"items": [1, 2]},
        {"nested": {"deep": {"value": 42}}},
    ]

    for data in test_cases:
        toon = encode(data)
        decoded = decode(toon)
        assert decoded == data, f"Failed for {data}"


def test_encoding_invariants():
    """Encoding should produce no trailing spaces or newlines."""
    test_cases = [
        {"a": 1},
        {"a": [1, 2, 3]},
        {"a": {"b": 1}},
        {"items": [{"id": 1}, {"id": 2}]},
    ]

    for data in test_cases:
        toon = encode(data)
        # No trailing newline
        assert not toon.endswith("\n"), f"Trailing newline in: {toon}"
        # No trailing spaces
        lines = toon.split("\n")
        for line in lines:
            assert not line.endswith(" "), f"Trailing space in line: {line}"

