"""Line scanner and cursor for parsing TOON input.

This module provides line parsing and cursor functionality following
SPEC Section 12 (Indentation and Whitespace).
"""

from typing import List

from tone.constants import SPACE, TAB
from tone.types import Depth


class LineCursor:
    """Cursor for navigating parsed lines."""
    
    def __init__(self, lines: List, blank_lines: List = None) -> None:
        """Initialize cursor with lines and blank line info.
        
        Args:
            lines: List of parsed lines
            blank_lines: List of blank line info (optional)
        """
        self.lines = lines
        self.index = 0
        self.blank_lines = blank_lines or []
    
    def peek(self):
        """Peek at current line without advancing."""
        return self.lines[self.index] if self.index < len(self.lines) else None
    
    def next(self):
        """Get next line and advance cursor."""
        if self.index < len(self.lines):
            result = self.lines[self.index]
            self.index += 1
            return result
        return None
    
    def advance(self) -> None:
        """Advance cursor to next line."""
        if self.index < len(self.lines):
            self.index += 1
    
    def at_end(self) -> bool:
        """Check if at end of lines."""
        return self.index >= len(self.lines)
    
    @property
    def length(self) -> int:
        """Get total number of lines."""
        return len(self.lines)
    
    def get_blank_lines(self) -> List:
        """Get blank line information."""
        return self.blank_lines
    
    def current(self):
        """Get current line (last advanced line)."""
        return self.lines[self.index - 1] if self.index > 0 else None
    
    def peek_at_depth(self, target_depth: Depth):
        """Peek at line at specific depth.
        
        Args:
            target_depth: Target depth to peek at
            
        Returns:
            Line if at target depth, None otherwise
        """
        line = self.peek()
        if not line or line["depth"] < target_depth:
            return None
        if line["depth"] == target_depth:
            return line
        return None
    
    def has_more_at_depth(self, target_depth: Depth) -> bool:
        """Check if there are more lines at specific depth.
        
        Args:
            target_depth: Target depth
            
        Returns:
            True if more lines at depth
        """
        return self.peek_at_depth(target_depth) is not None


def to_parsed_lines(source: str, indent_size: int, strict: bool):
    """Parse TOON source into lines with metadata.
    
    Args:
        source: TOON-formatted string
        indent_size: Spaces per indentation level
        strict: Enable strict validation
        
    Returns:
        ScanResult with parsed lines
        
    Raises:
        SyntaxError: If indentation errors in strict mode
    """
    if not source.strip():
        return {"lines": [], "blank_lines": []}
    
    lines = source.split("\n")
    parsed: List = []
    blank_lines: List = []
    
    for i, raw in enumerate(lines):
        line_number = i + 1
        indent = 0
        while indent < len(raw) and raw[indent] == SPACE:
            indent += 1
        
        content = raw[indent:]
        
        # Track blank lines
        if not content.strip():
            depth = _compute_depth_from_indent(indent, indent_size)
            blank_lines.append({"line_number": line_number, "indent": indent, "depth": depth})
            continue
        
        depth = _compute_depth_from_indent(indent, indent_size)
        
        # Strict mode validation
        if strict:
            # Find the full leading whitespace region (spaces and tabs)
            ws_end = 0
            while ws_end < len(raw) and (raw[ws_end] == SPACE or raw[ws_end] == TAB):
                ws_end += 1
            
            # Check for tabs in leading whitespace (before actual content)
            if TAB in raw[:ws_end]:
                raise SyntaxError(
                    f"Line {line_number}: Tabs are not allowed in indentation in strict mode"
                )
            
            # Check for exact multiples of indentSize
            if indent > 0 and indent % indent_size != 0:
                raise SyntaxError(
                    f"Line {line_number}: Indentation must be exact multiple of {indent_size}, "
                    f"but found {indent} spaces"
                )
        
        parsed.append({
            "raw": raw,
            "indent": indent,
            "content": content,
            "depth": depth,
            "line_number": line_number,
        })
    
    return {"lines": parsed, "blank_lines": blank_lines}


def _compute_depth_from_indent(indent_spaces: int, indent_size: int) -> Depth:
    """Compute depth from indentation spaces.
    
    Args:
        indent_spaces: Number of leading spaces
        indent_size: Spaces per indentation level
        
    Returns:
        Computed depth
    """
    import math
    return math.floor(indent_spaces / indent_size)

