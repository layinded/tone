"""Line writer utility for building TOON output."""

from typing import List


class LineWriter:
    """Utility for writing indented TOON lines."""
    
    def __init__(self, indent_size: int) -> None:
        """Initialize writer with indentation size.
        
        Args:
            indent_size: Number of spaces per indentation level
        """
        self.lines: List[str] = []
        self.indentation_string = " " * indent_size
    
    def push(self, depth: int, content: str) -> None:
        """Add a line with indentation.
        
        Args:
            depth: Indentation depth (0 = no indent)
            content: Line content
        """
        indent = self.indentation_string * depth
        self.lines.append(indent + content)
    
    def push_list_item(self, depth: int, content: str) -> None:
        """Add a list item with hyphen prefix.
        
        Args:
            depth: Indentation depth
            content: Line content (without "- ")
        """
        from tone.constants import LIST_ITEM_PREFIX
        
        self.push(depth, LIST_ITEM_PREFIX + content)
    
    def to_string(self) -> str:
        """Convert to TOON string.
        
        Returns:
            TOON-formatted string
        """
        return "\n".join(self.lines)
    
    def __str__(self) -> str:
        """Convert to TOON string (magic method)."""
        return self.to_string()

