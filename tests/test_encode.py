"""Tests for encoding functionality.

Based on TypeScript test suite from test/encode.test.ts
"""

import pytest
from tone import encode


# Primitives
def test_safe_strings():
    """Encode safe strings without quotes."""
    assert encode('hello') == 'hello'
    assert encode('Ada_99') == 'Ada_99'


def test_empty_string():
    """Quote empty string."""
    assert encode('') == '""'


def test_boolean_number_looking_strings():
    """Quote strings that look like booleans or numbers."""
    assert encode('true') == '"true"'
    assert encode('false') == '"false"'
    assert encode('null') == '"null"'
    assert encode('42') == '"42"'
    assert encode('-3.14') == '"-3.14"'
    assert encode('1e-6') == '"1e-6"'
    assert encode('05') == '"05"'


def test_escape_control_characters():
    """Escape control characters in strings."""
    assert encode('line1\nline2') == '"line1\\nline2"'
    assert encode('tab\there') == '"tab\\there"'
    assert encode('return\rcarriage') == '"return\\rcarriage"'
    # Note: Python backslash is '\\' in string literal
    assert encode('C:\\Users\\path') == '"C:\\\\Users\\\\path"'


def test_structural_characters():
    """Quote strings with structural characters."""
    assert encode('[3]: x,y') == '"[3]: x,y"'
    assert encode('- item') == '"- item"'
    assert encode('[test]') == '"[test]"'
    assert encode('{key}') == '"{key}"'


def test_unicode_emoji():
    """Handle Unicode and emoji."""
    assert encode('café') == 'café'
    assert encode('你好') == '你好'
    assert encode('🚀') == '🚀'
    assert encode('hello 👋 world') == 'hello 👋 world'


def test_encode_numbers():
    """Encode numbers."""
    assert encode(42) == '42'
    assert encode(3.14) == '3.14'
    assert encode(-7) == '-7'
    assert encode(0) == '0'


def test_special_numeric_values():
    """Handle special numeric values."""
    assert encode(-0.0) == '0'
    # Python's str() for large floats may add .0 or use scientific notation
    assert encode(1e6) in ['1000000', '1000000.0', '1e+06']
    assert encode(1e-6) in ['0.000001', '1e-06', '1e-6']
    assert encode(1e20) in ['100000000000000000000', '1e+20']


def test_preserve_precision():
    """Preserve precision for repeating decimals."""
    value = 1 / 3
    encoded = encode({'value': value})
    # Check it contains the expected precision
    assert '0.3333333333333333' in encoded


def test_encode_booleans():
    """Encode booleans."""
    assert encode(True) == 'true'
    assert encode(False) == 'false'


def test_encode_null():
    """Encode null."""
    assert encode(None) == 'null'


# Objects (simple)
def test_preserve_key_order():
    """Preserve key order in objects."""
    obj = {'id': 123, 'name': 'Ada', 'active': True}
    assert encode(obj) == 'id: 123\nname: Ada\nactive: true'


def test_encode_null_values():
    """Encode null values in objects."""
    obj = {'id': 123, 'value': None}
    assert encode(obj) == 'id: 123\nvalue: null'


def test_encode_empty_objects():
    """Encode empty objects as empty string."""
    assert encode({}) == ''


def test_quote_string_values_special_chars():
    """Quote string values with special characters."""
    assert encode({'note': 'a:b'}) == 'note: "a:b"'
    assert encode({'note': 'a,b'}) == 'note: "a,b"'
    assert encode({'text': 'line1\nline2'}) == 'text: "line1\\nline2"'
    assert encode({'text': 'say "hello"'}) == 'text: "say \\"hello\\""'


def test_quote_leading_trailing_spaces():
    """Quote string values with leading/trailing spaces."""
    assert encode({'text': ' padded '}) == 'text: " padded "'
    assert encode({'text': '  '}) == 'text: "  "'


def test_quote_boolean_number_looking_values():
    """Quote string values that look like booleans/numbers."""
    assert encode({'v': 'true'}) == 'v: "true"'
    assert encode({'v': '42'}) == 'v: "42"'
    assert encode({'v': '-7.5'}) == 'v: "-7.5"'


# Objects (keys)
def test_quote_keys_special_chars():
    """Quote keys with special characters."""
    assert encode({'order:id': 7}) == '"order:id": 7'
    assert encode({'[index]': 5}) == '"[index]": 5'
    assert encode({'{key}': 5}) == '"{key}": 5'
    assert encode({'a,b': 1}) == '"a,b": 1'


def test_quote_keys_spaces_hyphens():
    """Quote keys with spaces or leading hyphens."""
    assert encode({'full name': 'Ada'}) == '"full name": Ada'
    assert encode({'-lead': 1}) == '"-lead": 1'
    assert encode({' a ': 1}) == '" a ": 1'


def test_quote_numeric_keys():
    """Quote numeric keys."""
    assert encode({'123': 'x'}) == '"123": x'


def test_quote_empty_string_key():
    """Quote empty string key."""
    assert encode({'': 1}) == '"": 1'


def test_escape_control_characters_in_keys():
    """Escape control characters in keys."""
    assert encode({'line\nbreak': 1}) == '"line\\nbreak": 1'
    assert encode({'tab\there': 2}) == '"tab\\there": 2'


def test_escape_quotes_in_keys():
    """Escape quotes in keys."""
    assert encode({'he said "hi"': 1}) == '"he said \\"hi\\"": 1'


# Nested objects
def test_deeply_nested_objects():
    """Encode deeply nested objects."""
    obj = {'a': {'b': {'c': 'deep'}}}
    assert encode(obj) == 'a:\n  b:\n    c: deep'


def test_empty_nested_object():
    """Encode empty nested object."""
    assert encode({'user': {}}) == 'user:'


# Arrays of primitives
def test_string_arrays_inline():
    """Encode string arrays inline."""
    obj = {'tags': ['reading', 'gaming']}
    assert encode(obj) == 'tags[2]: reading,gaming'


def test_number_arrays_inline():
    """Encode number arrays inline."""
    obj = {'nums': [1, 2, 3]}
    assert encode(obj) == 'nums[3]: 1,2,3'


def test_mixed_primitive_arrays_inline():
    """Encode mixed primitive arrays inline."""
    obj = {'data': ['x', 'y', True, 10]}
    assert encode(obj) == 'data[4]: x,y,true,10'


def test_empty_arrays():
    """Encode empty arrays."""
    obj = {'items': []}
    assert encode(obj) == 'items[0]:'


def test_empty_string_in_arrays():
    """Handle empty string in arrays."""
    obj = {'items': ['']}
    assert encode(obj) == 'items[1]: ""'
    obj2 = {'items': ['a', '', 'b']}
    assert encode(obj2) == 'items[3]: a,"",b'


def test_whitespace_only_strings():
    """Handle whitespace-only strings in arrays."""
    obj = {'items': [' ', '  ']}
    assert encode(obj) == 'items[2]: " ","  "'


def test_quote_array_strings_special_chars():
    """Quote array strings with special characters."""
    obj = {'items': ['a', 'b,c', 'd:e']}
    assert encode(obj) == 'items[3]: a,"b,c","d:e"'


def test_quote_array_strings_looking_like_primitives():
    """Quote strings that look like booleans/numbers in arrays."""
    obj = {'items': ['x', 'true', '42', '-3.14']}
    assert encode(obj) == 'items[4]: x,"true","42","-3.14"'


def test_quote_array_strings_structural():
    """Quote strings with structural meanings in arrays."""
    obj = {'items': ['[5]', '- item', '{key}']}
    assert encode(obj) == 'items[3]: "[5]","- item","{key}"'


# Arrays of objects (tabular)
def test_tabular_format():
    """Encode arrays of similar objects in tabular format."""
    obj = {
        'items': [
            {'sku': 'A1', 'qty': 2, 'price': 9.99},
            {'sku': 'B2', 'qty': 1, 'price': 14.5},
        ]
    }
    assert encode(obj) == 'items[2]{sku,qty,price}:\n  A1,2,9.99\n  B2,1,14.5'


def test_null_values_tabular():
    """Handle null values in tabular format."""
    obj = {'items': [{'id': 1, 'value': None}, {'id': 2, 'value': 'test'}]}
    assert encode(obj) == 'items[2]{id,value}:\n  1,null\n  2,test'


def test_quote_delimiters_tabular():
    """Quote strings containing delimiters in tabular rows."""
    obj = {'items': [{'sku': 'A,1', 'desc': 'cool', 'qty': 2}, {'sku': 'B2', 'desc': 'wip: test', 'qty': 1}]}
    assert encode(obj) == 'items[2]{sku,desc,qty}:\n  "A,1",cool,2\n  B2,"wip: test",1'


def test_list_format_different_fields():
    """Use list format for objects with different fields."""
    obj = {'items': [{'id': 1, 'name': 'First'}, {'id': 2, 'name': 'Second', 'extra': True}]}
    assert encode(obj) == 'items[2]:\n  - id: 1\n    name: First\n  - id: 2\n    name: Second\n    extra: true'


def test_list_format_nested_values():
    """Use list format for objects with nested values."""
    obj = {'items': [{'id': 1, 'nested': {'x': 1}}]}
    assert encode(obj) == 'items[1]:\n  - id: 1\n    nested:\n      x: 1'


# Arrays of arrays
def test_nested_arrays_primitives():
    """Encode nested arrays of primitives."""
    obj = {'pairs': [['a', 'b'], ['c', 'd']]}
    assert encode(obj) == 'pairs[2]:\n  - [2]: a,b\n  - [2]: c,d'


def test_empty_inner_arrays():
    """Handle empty inner arrays."""
    obj = {'pairs': [[], []]}
    assert encode(obj) == 'pairs[2]:\n  - [0]:\n  - [0]:'


# Root arrays
def test_root_arrays_primitives():
    """Encode arrays of primitives at root level."""
    arr = ['x', 'y', 'true', True, 10]
    assert encode(arr) == '[5]: x,y,"true",true,10'


def test_root_arrays_tabular():
    """Encode arrays of similar objects in tabular format."""
    arr = [{'id': 1}, {'id': 2}]
    assert encode(arr) == '[2]{id}:\n  1\n  2'


def test_empty_root_arrays():
    """Encode empty arrays at root level."""
    assert encode([]) == '[0]:'


# Options
def test_delimiter_options():
    """Test delimiter options."""
    obj = {'tags': ['reading', 'gaming', 'coding']}
    assert encode(obj, {'delimiter': ','}) == 'tags[3]: reading,gaming,coding'
    assert encode(obj, {'delimiter': '|'}) == 'tags[3|]: reading|gaming|coding'
    assert encode(obj, {'delimiter': '\t'}) == 'tags[3\t]: reading\tgaming\tcoding'


def test_length_marker():
    """Add length marker to arrays."""
    obj = {'tags': ['reading', 'gaming', 'coding']}
    assert encode(obj, {'length_marker': '#'}) == 'tags[#3]: reading,gaming,coding'


def test_tabular_length_marker():
    """Add length marker to tabular arrays."""
    obj = {'items': [{'sku': 'A1', 'qty': 2, 'price': 9.99}, {'sku': 'B2', 'qty': 1, 'price': 14.5}]}
    assert encode(obj, {'length_marker': '#'}) == 'items[#2]{sku,qty,price}:\n  A1,2,9.99\n  B2,1,14.5'


def test_length_marker_with_delimiter():
    """Works with delimiter option."""
    obj = {'tags': ['reading', 'gaming', 'coding']}
    assert encode(obj, {'length_marker': '#', 'delimiter': '|'}) == 'tags[#3|]: reading|gaming|coding'


def test_default_no_length_marker():
    """Default is no length marker."""
    obj = {'tags': ['reading', 'gaming', 'coding']}
    assert encode(obj) == 'tags[3]: reading,gaming,coding'


# Formatting invariants
def test_no_trailing_spaces():
    """Produce no trailing spaces at end of lines."""
    obj = {'user': {'id': 123, 'name': 'Ada'}, 'items': ['a', 'b']}
    result = encode(obj)
    lines = result.split('\n')
    for line in lines:
        assert not line.endswith(' ')


def test_no_trailing_newline():
    """Produce no trailing newline at end of output."""
    obj = {'id': 123}
    result = encode(obj)
    assert not result.endswith('\n')
