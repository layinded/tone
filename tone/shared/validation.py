"""Shared validation utilities for encoding and decoding."""

import re

from tone.constants import COLON, COMMA, LIST_ITEM_MARKER


def is_valid_unquoted_key(key: str) -> bool:
    """Check if a key can be used without quotes.
    
    Args:
        key: Key string to check
        
    Returns:
        True if key is valid unquoted key
        
    Valid unquoted keys must start with a letter or underscore,
    followed by letters, digits, underscores, or dots.
    """
    return bool(re.match(r"^[A-Z_][\w.]*$", key, re.IGNORECASE))


def is_safe_unquoted(value: str, delimiter: str = COMMA) -> bool:
    """Determine if a string value can be safely encoded without quotes.
    
    Args:
        value: String to check
        delimiter: Active delimiter (default: comma)
        
    Returns:
        True if safe to emit without quotes
        
    A string needs quoting if it:
    - Is empty
    - Has leading or trailing whitespace
    - Could be confused with a literal (boolean, null, number)
    - Contains structural characters (colons, brackets, braces)
    - Contains quotes or backslashes (need escaping)
    - Contains control characters (newlines, tabs, etc.)
    - Contains the active delimiter
    - Starts with a list marker (hyphen)
    """
    if not value:
        return False
    
    if value != value.strip():
        return False
    
    # Check if it looks like any literal value (boolean, null, or numeric)
    from tone.shared.literal_utils import is_boolean_or_null_literal, is_numeric_like
    
    if is_boolean_or_null_literal(value) or is_numeric_like(value):
        return False
    
    # Check for colon (always structural)
    if COLON in value:
        return False
    
    # Check for quotes and backslash (always need escaping)
    if '"' in value or "\\" in value:
        return False
    
    # Check for brackets and braces (always structural)
    if re.search(r"[\[\]{}]", value):
        return False
    
    # Check for control characters (newline, carriage return, tab - always need quoting/escaping)
    if re.search(r"[\n\r\t]", value):
        return False
    
    # Check for the active delimiter
    if delimiter in value:
        return False
    
    # Check for hyphen at start (list marker)
    if value.startswith(LIST_ITEM_MARKER):
        return False
    
    return True

