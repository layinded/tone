"""
Pretty printing and formatting utilities for TOON.

Provides human-readable formatting and visualization of TOON data.
"""

from typing import Any, Dict, List, Optional

try:
    from rich.console import Console
    from rich.table import Table
except ImportError:
    Console = None
    Table = None


def format_value(value: Any, indent: int = 0, max_depth: int = 10) -> str:
    """
    Format a value as a human-readable string.
    
    Args:
        value: Value to format
        indent: Current indentation level
        max_depth: Maximum nesting depth
 From 0 to max_depth.
    Returns:
        Formatted string representation
        
    Example:
        >>> data = {'name': 'Alice', 'items': [1, 2, 3]}
        >>> print(format_value(data))
        name: Alice
        items: [3]
          1, 2, 3
    """
    if max_depth < 0:
        return "..."
    
    indent_str = "  " * indent
    
    if value is None:
        return f"{indent_str}null"
    
    if isinstance(value, bool):
        return f"{indent_str}{str(value).lower()}"
    
    if isinstance(value, (int, float)):
        return f"{indent_str}{value}"
    
    if isinstance(value, str):
        # Truncate long strings
        if len(value) > 80:
            return f'{indent_str}"{value[:77]}..."'
        return f'{indent_str}"{value}"'
    
    if isinstance(value, list):
        if len(value) == 0:
            return f"{indent_str}[]"
        
        # Format as array
        lines = [f"{indent_str}[{len(value)}]"]
        for item in value:
            lines.append(format_value(item, indent + 1, max_depth - 1))
        return "\n".join(lines)
    
    if isinstance(value, dict):
        if len(value) == 0:
            return f"{indent_str}{{}}"
        
        # Format as object
        lines = []
        for key, val in value.items():
            if isinstance(val, (list, dict)) and len(val) > 0:
                formatted = format_value(val, indent, max_depth - 1)
                # Add key prefix to first line
                parts = formatted.split("\n", 1)
                first_line = parts[0]
                rest = parts[1] if len(parts) > 1 else None
                lines.append(f"{indent_str}{key}: {first_line.lstrip()}")
                if rest:
                    lines.append(rest)
            else:
                formatted = format_value(val, 0, max_depth - 1)
                lines.append(f"{indent_str}{key}: {formatted.lstrip()}")
        return "\n".join(lines)
    
    return f"{indent_str}{repr(value)}"


def format_toon(toon_str: str, syntax_highlight: bool = False) -> str:
    """
    Format a TOON string with syntax highlighting (if rich available).
    
    Args:
        toon_str: TOON string to format
        syntax_highlight: Whether to apply syntax highlighting
        
    Returns:
        Formatted string
    """
    if not syntax_highlight or Console is None:
        return toon_str
    
    console = Console()
    # For now, just return plain - could add syntax highlighting later
    return toon_str


def summarize_structure(value: Any, max_items: int = 10) -> str:
    """
    Create a summary of a data structure.
    
    Args:
        value: Value to summarize
        max_items: Maximum items to show per collection
        
    Returns:
        Summary string
        
    Example:
        >>> data = {'users': [{'id': i} for i in range(100)]}
        >>> print(summarize_structure(data))
        Object with 1 key: 'users'
          users: Array with 100 items
            Items: {'id': 0}, {'id': 1}, ... + 98 more
    """
    summary_parts = []
    
    if isinstance(value, dict):
        keys = list(value.keys())
        summary_parts.append(f"Object with {len(keys)} key{'' if len(keys) == 1 else 's'}: {', '.join(repr(k) for k in keys[:3])}")
        if len(keys) > 3:
            summary_parts[-1] += f" + {len(keys) - 3} more"
        
        # Show value summaries
        for key in keys[:max_items]:
            val_summary = summarize_structure(value[key], max_items=max_items)
            lines = val_summary.split("\n")
            summary_parts.append(f"  {key}: {lines[0]}")
            for line in lines[1:]:
                summary_parts.append(f"    {line}")
    
    elif isinstance(value, list):
        summary_parts.append(f"Array with {len(value)} item{'' if len(value) == 1 else 's'}")
        
        if len(value) > 0:
            first_item_summary = summarize_structure(value[0], max_items=max_items)
            first_line = first_item_summary.split("\n")[0]
            summary_parts.append(f"  First item: {first_line}")
            
            if len(value) > 1:
                last_item_summary = summarize_structure(value[-1], max_items=max_items)
                last_line = last_item_summary.split("\n")[0]
                summary_parts.append(f"  Last item: {last_line}")
            
            if len(value) > 2:
                summary_parts.append(f"  Items: {first_line}, {last_line}, + {len(value) - 2} more")
    
    elif isinstance(value, (str, int, float, bool)):
        return f"{type(value).__name__}: {repr(value)[:50]}"
    
    else:
        return f"{type(value).__name__}"
    
    return "\n".join(summary_parts)


def create_table(data: List[Dict[str, Any]], title: Optional[str] = None) -> Optional["Table"]:
    """
    Create a rich Table from tabular data.
    
    Args:
        data: List of dictionaries
        title: Optional table title
        
    Returns:
        Rich Table object (or None if rich not available)
        
    Example:
        >>> data = [{'name': 'Alice', 'score': 95}, {'name': 'Bob', 'score': 87}]
        >>> table = create_table(data, title="Scores")
        >>> console.print(table)
    """
    if Table is None or len(data) == 0:
        return None
    
    table = Table(title=title)
    
    # Get all keys from first item
    keys = list(data[0].keys())
    
    # Add columns
    for key in keys:
        table.add_column(key)
    
    # Add rows
    for row in data:
        table.add_row(*[str(row.get(key, "")) for key in keys])
    
    return table


__all__ = [
    "format_value",
    "format_toon",
    "summarize_structure",
    "create_table",
]

