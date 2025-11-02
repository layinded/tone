"""Tests for decoding functionality.

Based on TypeScript test suite from test/decode.test.ts
"""

import pytest
from tone import decode


# Primitives
def test_decode_safe_strings():
    """Decode safe unquoted strings."""
    assert decode('hello') == 'hello'
    assert decode('Ada_99') == 'Ada_99'


def test_decode_quoted_strings():
    """Decode quoted strings and unescape control characters."""
    assert decode('""') == ''
    assert decode('"line1\\nline2"') == 'line1\nline2'
    assert decode('"tab\\there"') == 'tab\there'
    assert decode('"return\\rcarriage"') == 'return\rcarriage'
    assert decode('"C:\\\\Users\\\\path"') == 'C:\\Users\\path'
    assert decode('"say \\"hello\\""') == 'say "hello"'


def test_decode_unicode_emoji():
    """Decode unicode and emoji."""
    assert decode('café') == 'café'
    assert decode('你好') == '你好'
    assert decode('🚀') == '🚀'
    assert decode('hello 👋 world') == 'hello 👋 world'


def test_decode_numbers_booleans_null():
    """Decode numbers, booleans and null."""
    assert decode('42') == 42
    assert decode('3.14') == 3.14
    assert decode('-7') == -7
    assert decode('true') is True
    assert decode('false') is False
    assert decode('null') is None


def test_unquoted_invalid_numeric_formats():
    """Treat unquoted invalid numeric formats as strings."""
    assert decode('05') == '05'
    assert decode('007') == '007'
    assert decode('0123') == '0123'
    assert decode('a: 05') == {'a': '05'}
    assert decode('nums[3]: 05,007,0123') == {'nums': ['05', '007', '0123']}


def test_ambiguity_quoting():
    """Respect ambiguity quoting (quoted primitives remain strings)."""
    assert decode('"true"') == 'true'
    assert decode('"false"') == 'false'
    assert decode('"null"') == 'null'
    assert decode('"42"') == '42'
    assert decode('"-3.14"') == '-3.14'
    assert decode('"1e-6"') == '1e-6'
    assert decode('"05"') == '05'


# Objects (simple)
def test_parse_objects_primitives():
    """Parse objects with primitive values."""
    toon = 'id: 123\nname: Ada\nactive: true'
    assert decode(toon) == {'id': 123, 'name': 'Ada', 'active': True}


def test_parse_null_values():
    """Parse null values in objects."""
    toon = 'id: 123\nvalue: null'
    assert decode(toon) == {'id': 123, 'value': None}


def test_parse_empty_nested_object():
    """Parse empty nested object header."""
    assert decode('user:') == {'user': {}}


def test_parse_quoted_values():
    """Parse quoted object values with special characters and escapes."""
    assert decode('note: "a:b"') == {'note': 'a:b'}
    assert decode('note: "a,b"') == {'note': 'a,b'}
    assert decode('text: "line1\\nline2"') == {'text': 'line1\nline2'}
    assert decode('text: "say \\"hello\\""') == {'text': 'say "hello"'}
    assert decode('text: " padded "') == {'text': ' padded '}
    assert decode('text: "  "') == {'text': '  '}
    assert decode('v: "true"') == {'v': 'true'}
    assert decode('v: "42"') == {'v': '42'}
    assert decode('v: "-7.5"') == {'v': '-7.5'}


# Objects (keys)
def test_parse_quoted_keys():
    """Parse quoted keys with special characters and escapes."""
    assert decode('"order:id": 7') == {'order:id': 7}
    assert decode('"[index]": 5') == {'[index]': 5}
    assert decode('"{key}": 5') == {'{key}': 5}
    assert decode('"a,b": 1') == {'a,b': 1}
    assert decode('"full name": Ada') == {'full name': 'Ada'}
    assert decode('"-lead": 1') == {'-lead': 1}
    assert decode('" a ": 1') == {' a ': 1}
    assert decode('"123": x') == {'123': 'x'}
    assert decode('"": 1') == {'': 1}


def test_parse_dotted_keys():
    """Parse dotted keys as identifiers."""
    assert decode('user.name: Ada') == {'user.name': 'Ada'}
    assert decode('_private: 1') == {'_private': 1}
    assert decode('user_name: 1') == {'user_name': 1}


def test_unescape_keys():
    """Unescape control characters and quotes in keys."""
    assert decode('"line\\nbreak": 1') == {'line\nbreak': 1}
    assert decode('"tab\\there": 2') == {'tab\there': 2}
    assert decode('"he said \\"hi\\"": 1') == {'he said "hi"': 1}


# Nested objects
def test_parse_deeply_nested():
    """Parse deeply nested objects with indentation."""
    toon = 'a:\n  b:\n    c: deep'
    assert decode(toon) == {'a': {'b': {'c': 'deep'}}}


# Arrays of primitives
def test_parse_string_arrays():
    """Parse string arrays inline."""
    toon = 'tags[3]: reading,gaming,coding'
    assert decode(toon) == {'tags': ['reading', 'gaming', 'coding']}


def test_parse_number_arrays():
    """Parse number arrays inline."""
    toon = 'nums[3]: 1,2,3'
    assert decode(toon) == {'nums': [1, 2, 3]}


def test_parse_mixed_primitive_arrays():
    """Parse mixed primitive arrays inline."""
    toon = 'data[4]: x,y,true,10'
    assert decode(toon) == {'data': ['x', 'y', True, 10]}


def test_parse_empty_arrays():
    """Parse empty arrays."""
    assert decode('items[0]:') == {'items': []}


def test_parse_quoted_strings_in_arrays():
    """Parse quoted strings in arrays including empty and whitespace-only."""
    assert decode('items[1]: ""') == {'items': ['']}
    assert decode('items[3]: a,"",b') == {'items': ['a', '', 'b']}
    assert decode('items[2]: " ","  "') == {'items': [' ', '  ']}


def test_parse_strings_delimiters_structural():
    """Parse strings with delimiters and structural tokens in arrays."""
    assert decode('items[3]: a,"b,c","d:e"') == {'items': ['a', 'b,c', 'd:e']}
    assert decode('items[4]: x,"true","42","-3.14"') == {'items': ['x', 'true', '42', '-3.14']}
    assert decode('items[3]: "[5]","- item","{key}"') == {'items': ['[5]', '- item', '{key}']}


# Arrays of objects (tabular and list items)
def test_parse_tabular_arrays():
    """Parse tabular arrays of uniform objects."""
    toon = 'items[2]{sku,qty,price}:\n  A1,2,9.99\n  B2,1,14.5'
    assert decode(toon) == {
        'items': [
            {'sku': 'A1', 'qty': 2, 'price': 9.99},
            {'sku': 'B2', 'qty': 1, 'price': 14.5},
        ]
    }


def test_parse_nulls_quoted_tabular():
    """Parse nulls and quoted values in tabular rows."""
    toon = 'items[2]{id,value}:\n  1,null\n  2,"test"'
    assert decode(toon) == {
        'items': [
            {'id': 1, 'value': None},
            {'id': 2, 'value': 'test'},
        ]
    }


def test_parse_quoted_header_keys():
    """Parse quoted header keys in tabular arrays."""
    toon = 'items[2]{"order:id","full name"}:\n  1,Ada\n  2,Bob'
    assert decode(toon) == {
        'items': [
            {'order:id': 1, 'full name': 'Ada'},
            {'order:id': 2, 'full name': 'Bob'},
        ]
    }


def test_parse_list_arrays():
    """Parse list arrays for non-uniform objects."""
    toon = (
        'items[2]:\n'
        + '  - id: 1\n'
        + '    name: First\n'
        + '  - id: 2\n'
        + '    name: Second\n'
        + '    extra: true'
    )
    assert decode(toon) == {
        'items': [
            {'id': 1, 'name': 'First'},
            {'id': 2, 'name': 'Second', 'extra': True},
        ]
    }


def test_parse_nested_values_list_items():
    """Parse objects with nested values inside list items."""
    toon = 'items[1]:\n  - id: 1\n    nested:\n      x: 1'
    assert decode(toon) == {
        'items': [{'id': 1, 'nested': {'x': 1}}]
    }


# Arrays of arrays
def test_parse_nested_arrays_primitives():
    """Parse nested arrays of primitives."""
    toon = 'pairs[2]:\n  - [2]: a,b\n  - [2]: c,d'
    assert decode(toon) == {'pairs': [['a', 'b'], ['c', 'd']]}


def test_parse_empty_inner_arrays():
    """Parse empty inner arrays."""
    assert decode('pairs[2]:\n  - [0]:\n  - [0]:') == {'pairs': [[], []]}


# Root arrays
def test_parse_root_arrays_primitives():
    """Parse arrays of primitives at root level."""
    assert decode('[5]: x,y,"true",true,10') == ['x', 'y', 'true', True, 10]


def test_parse_root_arrays_tabular():
    """Parse arrays of similar objects in tabular format."""
    assert decode('[2]{id}:\n  1\n  2') == [{'id': 1}, {'id': 2}]


def test_parse_empty_root_arrays():
    """Parse empty arrays at root level."""
    assert decode('[0]:') == []


def test_parse_root_arrays_list_format():
    """Parse arrays of different objects in list format."""
    toon = '[2]:\n  - id: 1\n  - id: 2\n    name: Ada'
    assert decode(toon) == [{'id': 1}, {'id': 2, 'name': 'Ada'}]


# Complex structures
def test_parse_complex_nested():
    """Parse complex nested structures."""
    toon = (
        'user:\n'
        + '  id: 123\n'
        + '  name: Ada\n'
        + '  tags[2]: reading,gaming\n'
        + '  active: true\n'
        + '  prefs[0]:'
    )
    assert decode(toon) == {
        'user': {
            'id': 123,
            'name': 'Ada',
            'tags': ['reading', 'gaming'],
            'active': True,
            'prefs': [],
        }
    }


# Delimiter options
def test_decode_with_tab_delimiter():
    """Decode with tab delimiter."""
    toon = 'items[2\t]{sku\tqty\tprice}:\n  A1\t2\t9.99\n  B2\t1\t14.5'
    assert decode(toon) == {
        'items': [
            {'sku': 'A1', 'qty': 2, 'price': 9.99},
            {'sku': 'B2', 'qty': 1, 'price': 14.5},
        ]
    }


def test_decode_with_pipe_delimiter():
    """Decode with pipe delimiter."""
    toon = 'tags[3|]: reading|gaming|coding'
    assert decode(toon) == {'tags': ['reading', 'gaming', 'coding']}


# Strict mode
def test_strict_mode_valid():
    """Strict mode with valid input."""
    toon = 'id: 123'
    assert decode(toon, {'strict': True}) == {'id': 123}


def test_strict_mode_invalid_indentation():
    """Strict mode with invalid indentation."""
    toon = 'id: 123\n bad: 456'
    with pytest.raises(SyntaxError):
        decode(toon, {'strict': True})


def test_no_strict_mode_allows_indentation():
    """Non-strict mode allows relaxed indentation."""
    toon = 'id: 123\n bad: 456'
    # Should not raise in non-strict mode
    result = decode(toon, {'strict': False})
    assert 'id' in result
