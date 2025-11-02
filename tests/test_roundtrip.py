"""Roundtrip tests for encode/decode."""

from tone import decode, encode


def test_simple_object():
    """Roundtrip simple object."""
    data = {'id': 1, 'name': 'Alice'}
    toon_str = encode(data)
    decoded = decode(toon_str)
    assert data == decoded


def test_nested_object():
    """Roundtrip nested object."""
    data = {'user': {'profile': {'id': 1, 'active': True}}}
    toon_str = encode(data)
    decoded = decode(toon_str)
    assert data == decoded


def test_tabular_array():
    """Roundtrip tabular array."""
    data = {'users': [{'id': 1, 'name': 'Alice'}, {'id': 2, 'name': 'Bob'}]}
    toon_str = encode(data)
    decoded = decode(toon_str)
    assert data == decoded


def test_list_array():
    """Roundtrip list array."""
    data = {'items': [{'id': 1}, {'id': 2, 'extra': True}]}
    toon_str = encode(data)
    decoded = decode(toon_str)
    assert data == decoded


def test_inline_array():
    """Roundtrip inline array."""
    data = {'tags': ['admin', 'ops', 'dev']}
    toon_str = encode(data)
    decoded = decode(toon_str)
    assert data == decoded


def test_array_of_arrays():
    """Roundtrip array of arrays."""
    data = {'pairs': [[1, 2], [3, 4]]}
    toon_str = encode(data)
    decoded = decode(toon_str)
    assert data == decoded


def test_complex_nested():
    """Roundtrip complex nested structure."""
    data = {
        'team': {
            'members': [
                {'name': 'Alice', 'role': 'admin'},
                {'name': 'Bob', 'role': 'dev'},
            ],
            'status': 'active',
        }
    }
    toon_str = encode(data)
    decoded = decode(toon_str)
    assert data == decoded


def test_with_delimiter():
    """Roundtrip with different delimiter."""
    data = {'users': [{'id': 1, 'name': 'Alice'}, {'id': 2, 'name': 'Bob'}]}
    toon_str = encode(data, {'delimiter': '|'})
    decoded = decode(toon_str)
    assert data == decoded


def test_with_tab_delimiter():
    """Roundtrip with tab delimiter."""
    data = {'users': [{'id': 1, 'name': 'Alice'}, {'id': 2, 'name': 'Bob'}]}
    toon_str = encode(data, {'delimiter': '\t'})
    decoded = decode(toon_str)
    assert data == decoded


def test_with_length_marker():
    """Roundtrip with length marker."""
    data = {'tags': ['admin', 'ops', 'dev']}
    toon_str = encode(data, {'length_marker': '#'})
    decoded = decode(toon_str)
    assert data == decoded


def test_empty_arrays():
    """Roundtrip empty arrays."""
    data = {'items': []}
    toon_str = encode(data)
    decoded = decode(toon_str)
    assert data == decoded


def test_empty_objects():
    """Roundtrip empty objects."""
    data = {'user': {}}
    toon_str = encode(data)
    decoded = decode(toon_str)
    assert data == decoded


def test_primitives():
    """Roundtrip primitive values."""
    assert decode(encode(None)) is None
    assert decode(encode(True)) is True
    assert decode(encode(False)) is False
    assert decode(encode(42)) == 42
    assert decode(encode(3.14)) == 3.14
    assert decode(encode('hello')) == 'hello'


def test_quoted_strings():
    """Roundtrip quoted strings."""
    data = {'text': 'hello,world', 'note': 'a:b'}
    toon_str = encode(data)
    decoded = decode(toon_str)
    assert data == decoded


def test_special_characters():
    """Roundtrip strings with special characters."""
    data = {'text': 'line1\nline2', 'path': 'C:\\Users\\path'}
    toon_str = encode(data)
    decoded = decode(toon_str)
    assert data == decoded


def test_root_arrays():
    """Roundtrip root arrays."""
    data = [{'id': 1}, {'id': 2}]
    toon_str = encode(data)
    decoded = decode(toon_str)
    assert data == decoded


def test_mixed_structures():
    """Roundtrip mixed data structures."""
    data = {
        'name': 'Test',
        'tags': ['a', 'b', 'c'],
        'users': [
            {'id': 1, 'active': True},
            {'id': 2, 'active': False},
        ],
        'config': {
            'debug': True,
            'ports': [8080, 8081],
        },
    }
    toon_str = encode(data)
    decoded = decode(toon_str)
    assert data == decoded
