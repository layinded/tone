"""Primitive encoding (strings, numbers, booleans, null).

This module provides encoding functions for primitive values following
SPEC Section 7 (Strings and Keys).
"""

from typing import List, Optional

from tone.constants import COMMA, DEFAULT_DELIMITER, DOUBLE_QUOTE, NULL_LITERAL
from tone.shared.string_utils import escape_string
from tone.shared.validation import is_safe_unquoted, is_valid_unquoted_key
from tone.types import JsonPrimitive


def encode_primitive(value: JsonPrimitive, delimiter: str = COMMA) -> str:
    """Encode a primitive value to TOON string.
    
    Args:
        value: Primitive value (str, int, float, bool, None)
        delimiter: Active delimiter for array context
        
    Returns:
        Encoded primitive string
    """
    if value is None:
        return NULL_LITERAL
    
    if isinstance(value, bool):
        return str(value).lower()  # true/false
    
    if isinstance(value, (int, float)):
        return str(value)
    
    return encode_string_literal(value, delimiter)


def encode_string_literal(value: str, delimiter: str = COMMA) -> str:
    """Encode a string literal with proper quoting.
    
    Args:
        value: String to encode
        delimiter: Active delimiter (for delimiter-aware quoting)
        
    Returns:
        Encoded string (quoted if necessary)
    """
    if is_safe_unquoted(value, delimiter):
        return value
    
    return DOUBLE_QUOTE + escape_string(value) + DOUBLE_QUOTE


def encode_key(key: str) -> str:
    """Encode an object key with proper quoting.
    
    Args:
        key: Key string
        
    Returns:
        Encoded key (quoted if necessary)
    """
    if is_valid_unquoted_key(key):
        return key
    
    return DOUBLE_QUOTE + escape_string(key) + DOUBLE_QUOTE


def encode_and_join_primitives(values: List[JsonPrimitive], delimiter: str = COMMA) -> str:
    """Encode and join multiple primitive values.
    
    Args:
        values: List of primitive values
        delimiter: Delimiter to join with
        
    Returns:
        Joined encoded string
    """
    return delimiter.join(encode_primitive(v, delimiter) for v in values)


def format_header(
    length: int,
    key: Optional[str] = None,
    fields: Optional[List[str]] = None,
    delimiter: str = COMMA,
    length_marker: Optional[str] = None,
) -> str:
    """Format an array header.
    
    Args:
        length: Array length
        key: Optional key name
        fields: Optional field names for tabular arrays
        delimiter: Delimiter to use
        length_marker: Optional '#' marker
        
    Returns:
        Formatted header string
        
    Examples:
        >>> format_header(3)
        '[3]:'
        >>> format_header(2, key='items', fields=['id', 'name'])
        'items[2]{id,name}:'
        >>> format_header(2, key='tags', delimiter='|', length_marker='#')
        'tags[#2|]:'
    """
    parts = []
    
    if key:
        parts.append(encode_key(key))
    
    # Build bracket part
    bracket_parts = []
    if length_marker:
        bracket_parts.append("#")
    bracket_parts.append(str(length))
    if delimiter != DEFAULT_DELIMITER:
        bracket_parts.append(delimiter)
    
    parts.append("[" + "".join(bracket_parts) + "]")
    
    if fields:
        quoted_fields = [encode_key(f) for f in fields]
        parts.append("{" + delimiter.join(quoted_fields) + "}")
    
    parts.append(":")
    
    return "".join(parts)

