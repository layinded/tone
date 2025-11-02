"""String utility functions for encoding and decoding."""

from tone.constants import (
    BACKSLASH,
    CARRIAGE_RETURN,
    DOUBLE_QUOTE,
    NEWLINE,
    TAB,
)


def escape_string(value: str) -> str:
    """Escape special characters in a string for encoding.
    
    Args:
        value: String to escape
        
    Returns:
        Escaped string
        
    Handles: backslashes, quotes, newlines, carriage returns, and tabs
    """
    return (
        value.replace(BACKSLASH, BACKSLASH + BACKSLASH)
        .replace(DOUBLE_QUOTE, BACKSLASH + DOUBLE_QUOTE)
        .replace(NEWLINE, BACKSLASH + "n")
        .replace(CARRIAGE_RETURN, BACKSLASH + "r")
        .replace(TAB, BACKSLASH + "t")
    )


def unescape_string(value: str) -> str:
    """Unescape a string by processing escape sequences.
    
    Args:
        value: String to unescape
        
    Returns:
        Unescaped string
        
    Raises:
        SyntaxError: If invalid escape sequence found
        
    Handles: \\n, \\t, \\r, \\\\, and \\"
    """
    result = []
    i = 0
    
    while i < len(value):
        if value[i] == BACKSLASH:
            if i + 1 >= len(value):
                raise SyntaxError("Invalid escape sequence: backslash at end of string")
            
            next_char = value[i + 1]
            if next_char == "n":
                result.append(NEWLINE)
                i += 2
                continue
            if next_char == "t":
                result.append(TAB)
                i += 2
                continue
            if next_char == "r":
                result.append(CARRIAGE_RETURN)
                i += 2
                continue
            if next_char == BACKSLASH:
                result.append(BACKSLASH)
                i += 2
                continue
            if next_char == DOUBLE_QUOTE:
                result.append(DOUBLE_QUOTE)
                i += 2
                continue
            
            raise SyntaxError(f"Invalid escape sequence: \\{next_char}")
        
        result.append(value[i])
        i += 1
    
    return "".join(result)


def find_closing_quote(content: str, start: int) -> int:
    """Find the position of the closing quote for a quoted string.
    
    Args:
        content: String content
        start: Starting position after opening quote
        
    Returns:
        Position of closing quote, or -1 if not found
    """
    i = start + 1
    while i < len(content):
        if content[i] == BACKSLASH and i + 1 < len(content):
            # Skip escaped character
            i += 2
            continue
        if content[i] == DOUBLE_QUOTE:
            return i
        i += 1
    return -1  # Not found


def find_unquoted_char(content: str, char: str, start: int = 0) -> int:
    """Find the index of a specific character outside of quoted sections.
    
    Args:
        content: String to search in
        char: Character to look for
        start: Starting index (defaults to 0)
        
    Returns:
        Index of the character, or -1 if not found outside quotes
    """
    in_quotes = False
    i = start
    
    while i < len(content):
        if content[i] == BACKSLASH and i + 1 < len(content) and in_quotes:
            # Skip escaped character
            i += 2
            continue
        
        if content[i] == DOUBLE_QUOTE:
            in_quotes = not in_quotes
            i += 1
            continue
        
        if content[i] == char and not in_quotes:
            return i
        
        i += 1
    
    return -1

