"""
Debug utilities for TOON introspection and visualization.

Provides tools for debugging TOON encoding/decoding, inspecting parse trees,
and visualizing data structures.
"""

from typing import Any, Dict, List, Optional

try:
    import json
except ImportError:
    json = None


def inspect_parse_tree(toon_str: str, indent: str = "  ") -> str:
    """
    Inspect the parse tree of a TOON string.
    
    Shows the hierarchical structure as it would be parsed, useful
    for debugging syntax and understanding how TOON structures data.
    
    Args:
        toon_str: TOON string to inspect
        indent: Indentation string for tree display
        
    Returns:
        Human-readable parse tree
        
    Example:
        >>> toon = 'users[2]{id,name}:\n  1,Alice\n  2,Bob'
        >>> print(inspect_parse_tree(toon))
        Document
        ├─ Array (tabular)
        │  ├─ Header: users, length=2, fields=[id,name]
        │  └─ Rows:
        │     ├─ {id: 1, name: Alice}
        │     └─ {id: 2, name: Bob}
    """
    lines = ["Document"]
    
    if not toon_str.strip():
        lines.append(f"{indent}├─ Empty")
        return "\n".join(lines)
    
    # Simple parse tree visualization
    from tone import decode
    
    try:
        data = decode(toon_str)
        _add_parse_node(lines, data, indent, is_root=True)
    except Exception as e:
        lines.append(f"{indent}└─ Error: {e}")
    
    return "\n".join(lines)


def _add_parse_node(lines: List[str], data: Any, indent: str, is_root: bool = False) -> None:
    """Helper to add a node to the parse tree."""
    prefix = indent if is_root else ""
    
    if isinstance(data, dict):
        if len(data) == 0:
            lines.append(f"{prefix}└─ Object (empty)")
            return
        
        items = list(data.items())
        for i, (key, value) in enumerate(items):
            is_last = i == len(items) - 1
            node_prefix = "└─" if is_last else "├─"
            
            if isinstance(value, dict) and not value:
                lines.append(f"{prefix}{node_prefix} {key}: Object (empty)")
            elif isinstance(value, list) and not value:
                lines.append(f"{prefix}{node_prefix} {key}: Array (empty)")
            elif isinstance(value, (dict, list)):
                lines.append(f"{prefix}{node_prefix} {key}:")
                _add_parse_node(lines, value, indent + "│  " + "  ", is_root=False)
            else:
                lines.append(f"{prefix}{node_prefix} {key}: {_format_primitive(value)}")
    
    elif isinstance(data, list):
        if len(data) == 0:
            lines.append(f"{prefix}└─ Array (empty)")
            return
        
        # Check if it's a tabular array
        if len(data) > 0 and isinstance(data[0], dict):
            lines.append(f"{prefix}├─ Array (tabular, {len(data)} items)")
            lines.append(f"{indent}│  ├─ Fields: {list(data[0].keys())}")
            lines.append(f"{indent}│  └─ Rows:")
            for i, item in enumerate(data[:5]):
                is_last = i == len(data) - 1 or i == 4
                node_prefix = "└─" if is_last else "├─"
                if isinstance(item, dict):
                    lines.append(f"{indent}│     {node_prefix} {item}")
                else:
                    lines.append(f"{indent}│     {node_prefix} {_format_primitive(item)}")
            
            if len(data) > 5:
                lines.append(f"{indent}│     └─ ... and {len(data) - 5} more")
        else:
            lines.append(f"{prefix}├─ Array (primitive, {len(data)} items)")
            for i, item in enumerate(data[:5]):
                is_last = i == len(data) - 1 or i == 4
                node_prefix = "└─" if is_last else "├─"
                lines.append(f"{indent}│  {node_prefix} {_format_primitive(item)}")
            
            if len(data) > 5:
                lines.append(f"{indent}│  └─ ... and {len(data) - 5} more")
    else:
        lines.append(f"{prefix}└─ {_format_primitive(data)}")


def _format_primitive(value: Any) -> str:
    """Format a primitive value for display."""
    if value is None:
        return "null"
    if isinstance(value, bool):
        return str(value).lower()
    if isinstance(value, str):
        return f'"{value[:50]}..."' if len(value) > 50 else f'"{value}"'
    if isinstance(value, (int, float)):
        return str(value)
    return repr(value)[:50]


def debug_encode(value: Any, options: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    """
    Debug encoding process with detailed information.
    
    Returns metadata about the encoding process, including format detection,
    sizing information, and optimization notes.
    
    Args:
        value: Python value to encode
        options: Optional encoding options
        
    Returns:
        Dict with debug information
        
    Example:
        >>> data = {'users': [{'id': 1, 'name': 'Alice'}]}
        >>> debug = debug_encode(data)
        >>> print(debug['format_detected'])
        'tabular_array'
    """
    from tone import encode
    
    result: Dict[str, Any] = {
        "input_type": type(value).__name__,
        "input_size": _estimate_size(value),
    }
    
    try:
        toon_str = encode(value, options)
        result["encoded_length"] = len(toon_str)
        result["encoded_lines"] = toon_str.count("\n") + 1
        result["success"] = True
        result["format_detected"] = _detect_format(toon_str)
        
        # Try to encode as JSON for comparison
        if json:
            try:
                json_str = json.dumps(value, indent=2)
                result["json_length"] = len(json_str)
                result["compression_ratio"] = len(json_str) / len(toon_str) if len(toon_str) > 0 else 1.0
                result["size_reduction"] = 1 - (len(toon_str) / len(json_str)) if len(json_str) > 0 else 0
            except (TypeError, ValueError):
                result["json_comparable"] = False
        
        result["optimization_suggestions"] = _suggest_optimizations(value, toon_str)
        
    except Exception as e:
        result["success"] = False
        result["error"] = str(e)
    
    return result


def debug_decode(toon_str: str, options: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    """
    Debug decoding process with detailed information.
    
    Returns metadata about the decoding process, including parse tree,
    validation results, and error details if any.
    
    Args:
        toon_str: TOON string to decode
        options: Optional decoding options
        
    Returns:
        Dict with debug information
        
    Example:
        >>> toon = 'users[1]{id,name}:\n  1,Alice'
        >>> debug = debug_decode(toon)
        >>> print(debug['parse_tree'])
    """
    from tone import decode
    
    result: Dict[str, Any] = {
        "input_length": len(toon_str),
        "input_lines": toon_str.count("\n") + 1,
    }
    
    try:
        data = decode(toon_str, options)
        result["success"] = True
        result["output_type"] = type(data).__name__
        result["output_size"] = _estimate_size(data)
        result["parse_tree"] = inspect_parse_tree(toon_str)
        
        # Validation checks
        result["validation"] = {
            "valid_structure": True,
            "expected_vs_actual": _validate_lengths(toon_str, data),
        }
        
    except Exception as e:
        result["success"] = False
        result["error"] = str(e)
        result["error_type"] = type(e).__name__
    
    return result


def _estimate_size(data: Any) -> Any:
    """Estimate the size of data."""
    if isinstance(data, (dict, list)):
        return len(data)
    return "N/A"


def _detect_format(toon_str: str) -> str:
    """Detect the TOON format used."""
    if not toon_str.strip():
        return "empty"
    
    first_line = toon_str.strip().split("\n")[0]
    
    if "{" in first_line and "}" in first_line:
        return "tabular_array"
    elif "[[" in toon_str or first_line.startswith("-"):
        return "list_array"
    elif "[" in first_line and ":" in first_line:
        return "primitive_array"
    elif ":" in first_line and "\n" in toon_str:
        return "object"
    else:
        return "simple"


def _suggest_optimizations(value: Any, toon_str: str) -> List[str]:
    """Suggest optimizations for the encoded output."""
    suggestions = []
    
    # Check if it's a large array
    if isinstance(value, list) and len(value) > 100:
        suggestions.append("Consider using streaming for large arrays")
    
    # Check if it could use tab delimiters
    if "," in toon_str and "\t" not in toon_str:
        suggestions.append("Tab delimiter might reduce size for wide data")
    
    # Check for repeated keys
    if isinstance(value, list) and all(isinstance(item, dict) for item in value):
        if len(value) > 1:
            suggestions.append("Tabular format is optimal for uniform objects")
    
    return suggestions


def _validate_lengths(toon_str: str, data: Any) -> Dict[str, Any]:
    """Validate expected vs actual lengths."""
    # Simple validation - check array headers
    result = {}
    
    if "[" in toon_str:
        # Try to extract declared length
        first_line = toon_str.strip().split("\n")[0]
        if "[" in first_line and "]" in first_line:
            try:
                start = first_line.find("[")
                end = first_line.find("]", start)
                declared = int(first_line[start + 1:end])
                
                if isinstance(data, list):
                    actual = len(data)
                    result["array_length"] = {"declared": declared, "actual": actual, "match": declared == actual}
            except (ValueError, AttributeError):
                pass
    
    return result


__all__ = [
    "debug_decode",
    "debug_encode",
    "inspect_parse_tree",
]

