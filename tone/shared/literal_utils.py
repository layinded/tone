"""Literal utility functions for type checking."""

import re

from tone.constants import FALSE_LITERAL, NULL_LITERAL, TRUE_LITERAL


def is_boolean_or_null_literal(token: str) -> bool:
    """Check if a token is a boolean or null literal (true, false, null).
    
    Args:
        token: Token string to check
        
    Returns:
        True if token is true, false, or null
    """
    return token == TRUE_LITERAL or token == FALSE_LITERAL or token == NULL_LITERAL


def is_numeric_like(value: str) -> bool:
    """Check if string looks like a number.
    
    Args:
        value: String to check
        
    Returns:
        True if string matches numeric pattern
        
    Matches: 42, -3.14, 1e-6, 05 (leading zeros are numeric-like)
    """
    # Match numeric patterns: -3.14, 42, 1e-6, etc.
    pattern = r"^-?\d+(?:\.\d+)?(?:[eE][+-]?\d+)?$"
    if re.match(pattern, value):
        return True
    # Check for leading zeros: 05, 0001, etc.
    pattern_leading_zero = r"^0\d+$"
    return bool(re.match(pattern_leading_zero, value))


def is_numeric_literal(token: str) -> bool:
    """Check if a token represents a valid numeric literal.
    
    Args:
        token: Token string to check
        
    Returns:
        True if token is a valid number without forbidden leading zeros
        
    Rejects numbers with leading zeros (except "0" itself or decimals like "0.5").
    """
    if not token:
        return False
    
    # Must not have leading zeros (except for "0" itself or decimals like "0.5")
    if len(token) > 1 and token[0] == "0" and token[1] != ".":
        return False
    
    # Check if it's a valid number
    try:
        num = float(token)
        return not (float("inf") == num or float("-inf") == num) and not (num != num)  # Check for inf/NaN
    except ValueError:
        return False

