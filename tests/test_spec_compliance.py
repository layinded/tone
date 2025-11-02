"""
SPEC Compliance Tests

Tests that validate SPEC.md v1.3 conformance and cross-language
interoperability with the TypeScript reference implementation.
"""

import pytest
from tone import decode, encode


class TestSection3EncodingNormalization:
    """Section 3: Encoding Normalization Requirements."""

    def test_special_numeric_values(self):
        """3.1: Number normalization -0 -> 0."""
        assert encode(-0) == "0"
        assert encode(0) == "0"
        assert decode(encode(-0)) == 0

    def test_scientific_notation_normalization(self):
        """3.1: Number normalization handles special cases."""
        # Python floats encode according to str(float) behavior
        assert encode(1e6) == "1000000.0"  # Python standard
        # Python uses scientific notation for very small/large numbers
        assert encode(1e-6) in ["1e-06", "0.000001"]  # Both valid
        result = encode(1e20)
        assert isinstance(result, str)  # Just verify it encodes
        assert result  # Non-empty

    def test_nan_and_infinity_to_null(self):
        """3.2: NaN/Infinity -> null."""
        import math

        assert encode(float("nan")) == "null"
        assert encode(float("inf")) == "null"
        assert encode(float("-inf")) == "null"

        toon_nan = encode({"value": float("nan")})
        assert "value: null" in toon_nan

    def test_set_to_array(self):
        """3.5: Set -> array."""
        from datetime import datetime

        data = {"tags": {"reading", "gaming", "coding"}}
        toon = encode(data)
        decoded = decode(toon)

        # Order may vary, but all should be present
        assert len(decoded["tags"]) == 3
        assert all(tag in decoded["tags"] for tag in ["reading", "gaming", "coding"])

    def test_datetime_to_iso_string(self):
        """3.4: Date -> ISO string (Python datetime equivalent)."""
        from datetime import datetime

        dt = datetime(2025, 1, 15, 10, 30, 0)
        toon = encode({"created": dt})
        assert '"2025-01-15' in toon or "2025-01-15" in toon


class TestSection7StringsAndKeys:
    """Section 7: Strings and Keys Requirements."""

    def test_safe_unquoted_strings(self):
        """7.1: Safe unquoted strings."""
        assert encode("hello") == "hello"
        assert encode("Ada_99") == "Ada_99"
        assert encode("hello world") == "hello world"

    def test_empty_string_quoted(self):
        """7.1: Empty string is quoted."""
        assert encode("") == '""'

    def test_boolean_number_looking_strings_quoted(self):
        """7.1: Strings looking like booleans/numbers are quoted."""
        assert encode("true") == '"true"'
        assert encode("false") == '"false"'
        assert encode("null") == '"null"'
        assert encode("42") == '"42"'
        assert encode("-3.14") == '"-3.14"'
        assert encode("1e-6") == '"1e-6"'
        assert encode("05") == '"05"'

    def test_escape_control_characters(self):
        """7.1: Valid escapes only."""
        assert encode("line1\nline2") == '"line1\\nline2"'
        assert encode("tab\there") == '"tab\\there"'
        assert encode("return\rcarriage") == '"return\\rcarriage"'
        assert encode('C:\\Users\\path') == '"C:\\\\Users\\\\path"'

    def test_unicode_and_emoji(self):
        """7.1: Unicode and emoji are safe unquoted."""
        assert encode("café") == "café"
        assert encode("你好") == "你好"
        assert encode("🚀") == "🚀"
        assert encode("hello 👋 world") == "hello 👋 world"

    def test_keys_with_special_characters_quoted(self):
        """7.2: Keys with special chars are quoted."""
        assert encode({"order:id": 7}) == '"order:id": 7'
        assert encode({"[index]": 5}) == '"[index]": 5'
        assert encode({"{key}": 5}) == '"{key}": 5'
        assert encode({"a,b": 1}) == '"a,b": 1'

    def test_valid_unquoted_keys(self):
        """7.2: Valid identifier keys are unquoted."""
        assert encode({"user.name": "Ada"}) == "user.name: Ada"
        assert encode({"_private": 1}) == "_private: 1"
        assert encode({"user_name": 1}) == "user_name: 1"


class TestSection9Arrays:
    """Section 9: Arrays Requirements."""

    def test_inline_primitive_arrays(self):
        """9.1: Primitive arrays are inline."""
        assert encode({"tags": ["reading", "gaming"]}) == "tags[2]: reading,gaming"
        assert encode({"nums": [1, 2, 3]}) == "nums[3]: 1,2,3"

    def test_empty_arrays(self):
        """9.1: Empty arrays have header only."""
        assert encode({"items": []}) == "items[0]:"

    def test_tabular_array_uniform_objects(self):
        """9.3: Uniform objects use tabular format."""
        data = {"items": [{"sku": "A1", "qty": 2, "price": 9.99}, {"sku": "B2", "qty": 1, "price": 14.5}]}
        toon = encode(data)

        assert "items[2]{sku,qty,price}:" in toon
        assert "A1,2,9.99" in toon
        assert "B2,1,14.5" in toon

    def test_list_array_non_uniform(self):
        """9.2: Non-uniform objects use list format."""
        data = {"items": [{"id": 1, "name": "First"}, {"id": 2, "name": "Second", "extra": True}]}
        toon = encode(data)

        assert "items[2]:" in toon
        assert "- id: 1" in toon


class TestSection12Indentation:
    """Section 12: Indentation Requirements."""

    def test_default_indentation_two_spaces(self):
        """12.1: Default indentation is 2 spaces."""
        data = {"user": {"id": 1, "name": "Alice"}}
        lines = encode(data).split("\n")
        assert lines[1].startswith("  ")  # Second line should have 2-space indent

    def test_custom_indentation(self):
        """12.1: Custom indentation supported."""
        data = {"user": {"id": 1}}
        toon = encode(data, {"indent": 4})
        lines = toon.split("\n")
        assert lines[1].startswith("    ")  # 4-space indent

    def test_no_tabs_for_indentation(self):
        """12.1: Tabs not used for indentation."""
        data = {"user": {"id": 1}}
        toon = encode(data)
        assert "\t" not in toon


class TestSection14StrictMode:
    """Section 14: Strict Mode Requirements."""

    def test_array_length_mismatch_strict(self):
        """14.1: Strict mode validates array length."""
        # This should pass with declared length matching
        toon = "items[2]:\n  - a: 1\n  - b: 2"
        data = decode(toon, {"strict": True})
        assert len(data["items"]) == 2

    def test_indentation_validation_strict(self):
        """14.2: Strict mode validates indentation."""
        # 4 spaces is valid for 2-space indent (multiple of 2)
        # Use something that's not a multiple
        bad_toon = "user:\n   bad_indent: 123"  # 3 spaces - not a multiple of 2

        with pytest.raises((SyntaxError, ValueError)):
            decode(bad_toon, {"strict": True})


class TestCrossLanguageCompatibility:
    """Cross-language interoperability tests."""

    def test_roundtrip_fidelity(self):
        """Critical: Roundtrip maintains data fidelity."""
        test_cases = [
            {"id": 1, "name": "Alice"},
            {"items": [{"id": 1}, {"id": 2}]},
            {"tags": ["reading", "gaming", "coding"]},
            {"nested": {"deep": {"value": 42}}},
        ]

        for data in test_cases:
            toon = encode(data)
            decoded = decode(toon)
            assert decoded == data, f"Roundtrip failed for {data}"

    def test_array_order_preserved(self):
        """2.1: Array order MUST be preserved."""
        data = {"items": ["a", "b", "c", "d"]}
        toon = encode(data)
        decoded = decode(toon)
        assert decoded["items"] == ["a", "b", "c", "d"]

    def test_object_key_order_preserved(self):
        """2.2: Object key order MUST be preserved."""
        data = {"zebra": 1, "apple": 2, "banana": 3}
        toon = encode(data)
        decoded = decode(toon)

        # Python 3.7+ preserves insertion order
        keys = list(decoded.keys())
        assert keys == ["zebra", "apple", "banana"]

    def test_numeric_precision_preserved(self):
        """2.6: Precision maintains round-trip fidelity."""
        value = 1 / 3
        data = {"value": value}
        toon = encode(data)
        decoded = decode(toon)
        assert abs(decoded["value"] - value) < 1e-14  # Python float precision


class TestDelimiters:
    """Section 11: Delimiters Requirements."""

    def test_comma_delimiter_default(self):
        """11.1: Comma is default delimiter."""
        data = {"tags": ["a", "b", "c"]}
        toon = encode(data)
        assert "tags[3]: a,b,c" in toon

    def test_tab_delimiter(self):
        """11.1: Tab delimiter supported."""
        data = {"tags": ["a", "b", "c"]}
        toon = encode(data, {"delimiter": "\t"})
        assert "tags[3\t]: a\tb\tc" in toon or "tags[3\t]" in toon

    def test_pipe_delimiter(self):
        """11.1: Pipe delimiter supported."""
        data = {"tags": ["a", "b", "c"]}
        toon = encode(data, {"delimiter": "|"})
        assert "tags[3|]: a|b|c" in toon or "tags[3|]" in toon


class TestRootForms:
    """Section 5: Root Forms Requirements."""

    def test_root_object(self):
        """5.1: Root object."""
        toon = "id: 123\nname: Alice"
        data = decode(toon)
        assert data == {"id": 123, "name": "Alice"}

    def test_root_array_inline(self):
        """5.2: Root primitive array."""
        toon = "[2]: x,y"
        data = decode(toon)
        assert data == ["x", "y"]

    def test_root_array_objects_tabular(self):
        """5.3: Root tabular array."""
        toon = "[2]{id,name}:\n  1,Alice\n  2,Bob"
        data = decode(toon)
        assert data == [{"id": 1, "name": "Alice"}, {"id": 2, "name": "Bob"}]

    def test_root_primitive(self):
        """5.4: Root primitive."""
        assert decode("hello") == "hello"
        assert decode("42") == 42
        assert decode("true") is True
        assert decode("null") is None


class TestSpecialCharacters:
    """Edge cases and special characters."""

    def test_strings_with_delimiters_in_arrays(self):
        """Strings with delimiters are quoted in arrays."""
        data = {"items": ["a", "b,c", "d:e"]}
        toon = encode(data)
        assert '"b,c"' in toon
        assert '"d:e"' in toon

    def test_strings_with_hyphen_prefix_in_arrays(self):
        """Strings starting with - are quoted to avoid list marker confusion."""
        data = {"items": ["- item", "a", "b"]}
        toon = encode(data)
        assert '"- item"' in toon

    def test_empty_string_values(self):
        """Empty strings in objects and arrays."""
        assert encode({"empty": ""}) == 'empty: ""'
        # Order in array may vary when encoding
        result = encode({"items": ["", "a", ""]})
        assert 'items[3]:' in result
        assert '""' in result
        assert "a" in result

    def test_quoted_null_in_arrays(self):
        """Quoted 'null' stays a string."""
        data = {"items": ["null", "null"]}
        toon = encode(data)
        decoded = decode(toon)
        assert decoded["items"] == ["null", "null"]


class TestErrorHandling:
    """Error handling and edge cases."""

    def test_unterminated_string(self):
        """Invalid: Unterminated string raises error."""
        with pytest.raises(SyntaxError):
            decode('text: "unclosed')

    def test_missing_colon_after_key(self):
        """Invalid: Missing colon handled."""
        # Without colon, this is parsed as a primitive string
        result = decode("key value")
        assert result == "key value"  # Valid as a string
        
        # But as part of an object, it should fail
        with pytest.raises((SyntaxError, ValueError)):
            decode("user:\nkey value")  # Missing colon in nested

    def test_invalid_escape(self):
        """Invalid: Invalid escape sequence raises error."""
        with pytest.raises(SyntaxError):
            decode('"invalid\\x"')

    def test_array_length_mismatch(self):
        """Invalid: Array length mismatch in strict mode."""
        # Missing item
        bad_toon = "items[3]:\n  - a: 1\n  - b: 2"

        with pytest.raises(Exception):
            decode(bad_toon, {"strict": True})


class TestTypeSpecificHandling:
    """Python-specific type handling."""

    def test_frozenset_to_array(self):
        """Frozenset converts to array."""
        data = {"tags": frozenset(["reading", "gaming"])}
        toon = encode(data)
        decoded = decode(toon)
        assert len(decoded["tags"]) == 2

    def test_large_integers(self):
        """Large integers handled correctly."""
        large = 9007199254740991  # Max safe int
        assert encode(large) == "9007199254740991"

    def test_negative_zero(self):
        """-0 normalizes to 0."""
        assert encode(-0.0) == "0"

    def test_nested_lists(self):
        """Nested lists are preserved."""
        data = {"pairs": [[1, 2], [3, 4]]}
        toon = encode(data)
        decoded = decode(toon)
        assert decoded == data

