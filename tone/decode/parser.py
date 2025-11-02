"""Parser utilities for TOON format.

This module provides parsing functions for headers, keys, tokens, and delimited values
following SPEC Section 4, 6, and 7.
"""

from typing import Dict, List, Optional, Tuple

from tone.constants import (
    BACKSLASH,
    CLOSE_BRACE,
    CLOSE_BRACKET,
    COLON,
    DEFAULT_DELIMITER,
    DELIMITERS,
    DOUBLE_QUOTE,
    FALSE_LITERAL,
    HASH,
    NULL_LITERAL,
    OPEN_BRACE,
    OPEN_BRACKET,
    PIPE,
    TAB,
    TRUE_LITERAL,
)
from tone.shared.literal_utils import is_boolean_or_null_literal, is_numeric_literal
from tone.shared.string_utils import find_closing_quote, find_unquoted_char, unescape_string
from tone.types import Delimiter, JsonPrimitive


def parse_array_header_line(content: str, default_delimiter: Delimiter) -> Optional[Dict]:
    """Parse array header from line content.
    
    Args:
        content: Line content
        default_delimiter: Default delimiter to use
        
    Returns:
        Dict with 'header' and optional 'inlineValues', or None if not a header
    """
    # Don't match if the line starts with a quote (it's a quoted key, not an array)
    if content.lstrip().startswith(DOUBLE_QUOTE):
        return None
    
    # Find the bracket segment first
    bracket_start = content.find(OPEN_BRACKET)
    if bracket_start == -1:
        return None
    
    bracket_end = content.find(CLOSE_BRACKET, bracket_start)
    if bracket_end == -1:
        return None
    
    # Find the colon that comes after all brackets and braces
    colon_index = bracket_end + 1
    brace_end = colon_index
    
    # Check for fields segment (braces come after bracket)
    brace_start = content.find(OPEN_BRACE, bracket_end)
    if brace_start != -1 and brace_start < content.find(COLON, bracket_end):
        found_brace_end = content.find(CLOSE_BRACE, brace_start)
        if found_brace_end != -1:
            brace_end = found_brace_end + 1
    
    # Now find colon after brackets and braces
    colon_index = content.find(COLON, max(bracket_end, brace_end))
    if colon_index == -1:
        return None
    
    key = content[:bracket_start] if bracket_start > 0 else None
    after_colon = content[colon_index + 1:].strip()
    
    bracket_content = content[bracket_start + 1:bracket_end]
    
    # Try to parse bracket segment
    try:
        parsed_bracket = parse_bracket_segment(bracket_content, default_delimiter)
    except Exception:
        return None
    
    length = parsed_bracket["length"]
    delimiter = parsed_bracket["delimiter"]
    has_length_marker = parsed_bracket["has_length_marker"]
    
    # Check for fields segment
    fields = None
    if brace_start != -1 and brace_start < colon_index:
        found_brace_end = content.find(CLOSE_BRACE, brace_start)
        if found_brace_end != -1 and found_brace_end < colon_index:
            fields_content = content[brace_start + 1:found_brace_end]
            fields = [
                parse_string_literal(field.strip())
                for field in parse_delimited_values(fields_content, delimiter)
            ]
    
    return {
        "header": {
            "key": key,
            "length": length,
            "delimiter": delimiter,
            "fields": fields,
            "has_length_marker": has_length_marker,
        },
        "inlineValues": after_colon if after_colon else None,
    }


def parse_bracket_segment(seg: str, default_delimiter: Delimiter) -> Dict:
    """Parse bracket segment (e.g., "3", "#3", "3|", "#3\t").
    
    Args:
        seg: Bracket content
        default_delimiter: Default delimiter
        
    Returns:
        Dict with length, delimiter, has_length_marker
        
    Raises:
        TypeError: If invalid array length
    """
    has_length_marker = False
    content = seg
    
    # Check for length marker
    if content.startswith(HASH):
        has_length_marker = True
        content = content[1:]
    
    # Check for delimiter suffix
    delimiter = default_delimiter
    if content.endswith(TAB):
        delimiter = DELIMITERS["tab"]
        content = content[:-1]
    elif content.endswith(PIPE):
        delimiter = DELIMITERS["pipe"]
        content = content[:-1]
    
    try:
        length = int(content)
    except ValueError:
        raise TypeError(f"Invalid array length: {seg}")
    
    return {"length": length, "delimiter": delimiter, "has_length_marker": has_length_marker}


def parse_delimited_values(input_str: str, delimiter: Delimiter) -> List[str]:
    """Parse delimited values respecting quotes.
    
    Args:
        input_str: Content with delimited values
        delimiter: Active delimiter
        
    Returns:
        List of parsed value strings
    """
    values: List[str] = []
    current = ""
    in_quotes = False
    i = 0
    
    while i < len(input_str):
        char = input_str[i]
        
        if char == BACKSLASH and i + 1 < len(input_str) and in_quotes:
            # Escape sequence in quoted string
            current += char + input_str[i + 1]
            i += 2
            continue
        
        if char == DOUBLE_QUOTE:
            in_quotes = not in_quotes
            current += char
            i += 1
            continue
        
        if char == delimiter and not in_quotes:
            values.append(current.strip())
            current = ""
            i += 1
            continue
        
        current += char
        i += 1
    
    # Add last value
    if current or len(values) > 0:
        values.append(current.strip())
    
    return values


def map_row_values_to_primitives(values: List[str]) -> List[JsonPrimitive]:
    """Map row value strings to primitive values.
    
    Args:
        values: List of string values
        
    Returns:
        List of parsed primitive values
    """
    return [parse_primitive_token(v) for v in values]


def parse_primitive_token(token: str) -> JsonPrimitive:
    """Parse a primitive token to Python value.
    
    Args:
        token: Token string
        
    Returns:
        Python primitive value
    """
    trimmed = token.strip()
    
    # Empty token
    if not trimmed:
        return ""
    
    # Quoted string (if starts with quote, it MUST be properly quoted)
    if trimmed.startswith(DOUBLE_QUOTE):
        return parse_string_literal(trimmed)
    
    # Boolean or null literals
    if is_boolean_or_null_literal(trimmed):
        if trimmed == TRUE_LITERAL:
            return True
        if trimmed == FALSE_LITERAL:
            return False
        if trimmed == NULL_LITERAL:
            return None
    
    # Numeric literal
    if is_numeric_literal(trimmed):
        try:
            # Try int first, then float
            if "." not in trimmed and "e" not in trimmed.lower():
                return int(trimmed)
            return float(trimmed)
        except ValueError:
            pass
    
    # Unquoted string
    return trimmed


def parse_string_literal(token: str) -> str:
    """Parse a string literal token.
    
    Args:
        token: Token string
        
    Returns:
        Unescaped string value
        
    Raises:
        SyntaxError: If improperly quoted
    """
    trimmed = token.strip()
    
    if trimmed.startswith(DOUBLE_QUOTE):
        # Find the closing quote, accounting for escaped quotes
        closing_quote_index = find_closing_quote(trimmed, 0)
        
        if closing_quote_index == -1:
            # No closing quote was found
            raise SyntaxError("Unterminated string: missing closing quote")
        
        if closing_quote_index != len(trimmed) - 1:
            raise SyntaxError("Unexpected characters after closing quote")
        
        content = trimmed[1:closing_quote_index]
        return unescape_string(content)
    
    return trimmed


def parse_unquoted_key(content: str, start: int) -> Tuple[str, int]:
    """Parse unquoted key.
    
    Args:
        content: Line content
        start: Starting position
        
    Returns:
        Tuple of (key, end_position)
        
    Raises:
        SyntaxError: If missing colon
    """
    end = start
    while end < len(content) and content[end] != COLON:
        end += 1
    
    # Validate that a colon was found
    if end >= len(content) or content[end] != COLON:
        raise SyntaxError("Missing colon after key")
    
    key = content[start:end].strip()
    
    # Skip the colon
    end += 1
    
    return key, end


def parse_quoted_key(content: str, start: int) -> Tuple[str, int]:
    """Parse quoted key.
    
    Args:
        content: Line content
        start: Starting position
        
    Returns:
        Tuple of (key, end_position)
        
    Raises:
        SyntaxError: If invalid quoted key
    """
    # Find the closing quote, accounting for escaped quotes
    closing_quote_index = find_closing_quote(content, start)
    
    if closing_quote_index == -1:
        raise SyntaxError("Unterminated quoted key")
    
    # Extract and unescape the key content
    key_content = content[start + 1:closing_quote_index]
    key = unescape_string(key_content)
    end = closing_quote_index + 1
    
    # Validate and skip colon after quoted key
    if end >= len(content) or content[end] != COLON:
        raise SyntaxError("Missing colon after key")
    end += 1
    
    return key, end


def parse_key_token(content: str, start: int) -> Tuple[str, int]:
    """Parse key token (quoted or unquoted).
    
    Args:
        content: Line content
        start: Starting position
        
    Returns:
        Tuple of (key, end_position)
    """
    if content[start] == DOUBLE_QUOTE:
        return parse_quoted_key(content, start)
    else:
        return parse_unquoted_key(content, start)


def is_array_header_after_hyphen(content: str) -> bool:
    """Check if content after hyphen is an array header.
    
    Args:
        content: Content to check
        
    Returns:
        True if looks like array header
    """
    trimmed = content.strip()
    return trimmed.startswith(OPEN_BRACKET) and find_unquoted_char(content, COLON) != -1


def is_object_first_field_after_hyphen(content: str) -> bool:
    """Check if content after hyphen is an object first field.
    
    Args:
        content: Content to check
        
    Returns:
        True if has colon (object field)
    """
    return find_unquoted_char(content, COLON) != -1

