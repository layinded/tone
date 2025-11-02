"""
Format converters for multi-format interoperability.

Convert between TONE and other common serialization formats:
JSON, YAML, CSV, XML, etc.
"""

import json
from typing import Any, Dict, Optional

try:
    import yaml
except ImportError:
    yaml = None

try:
    import csv
    import io
except ImportError:
    csv = None
    io = None


def to_json(tone_str: str, options: Optional[Dict[str, Any]] = None) -> str:
    """
    Convert TONE to JSON format.
    
    Args:
        tone_str: TONE-formatted string
        options: Optional JSON encoding options (indent, etc.)
        
    Returns:
        JSON-formatted string
        
    Example:
        >>> from tone.integrations import to_json
        >>> tone = 'id: 1\nname: Alice'
        >>> json_str = to_json(tone)
        >>> print(json_str)
        {"id": 1, "name": "Alice"}
    """
    from tone import decode

    data = decode(tone_str)

    # JSON encoding options
    if options is None:
        options = {"indent": 2}

    return json.dumps(data, **options)


def from_json(json_str: str) -> str:
    """
    Convert JSON to TONE format.
    
    Args:
        json_str: JSON-formatted string
        
    Returns:
        TONE-formatted string
        
    Example:
        >>> from tone.integrations import from_json
        >>> json_str = '{"id": 1, "name": "Alice"}'
        >>> tone = from_json(json_str)
        >>> print(tone)
        id: 1
        name: Alice
    """
    from tone import encode

    data = json.loads(json_str)
    return encode(data)


def to_yaml(tone_str: str, options: Optional[Dict[str, Any]] = None) -> str:
    """
    Convert TONE to YAML format.
    
    Args:
        tone_str: TONE-formatted string
        options: Optional YAML encoding options
        
    Returns:
        YAML-formatted string
    """
    if yaml is None:
        raise ImportError("PyYAML not installed. Install with: pip install pyyaml")

    from tone import decode

    data = decode(tone_str)

    # YAML encoding options
    if options is None:
        options = {"default_flow_style": False, "sort_keys": False}

    return yaml.dump(data, **options)


def from_yaml(yaml_str: str) -> str:
    """
    Convert YAML to TONE format.
    
    Args:
        yaml_str: YAML-formatted string
        
    Returns:
        TONE-formatted string
    """
    if yaml is None:
        raise ImportError("PyYAML not installed. Install with: pip install pyyaml")

    from tone import encode

    data = yaml.safe_load(yaml_str)
    return encode(data)


def to_csv(tone_str: str, options: Optional[Dict[str, Any]] = None) -> str:
    """
    Convert TONE tabular data to CSV format.
    
    Args:
        tone_str: TONE-formatted string
        options: Optional CSV encoding options
        
    Returns:
        CSV-formatted string
        
    Note: Works best with tabular TONE arrays
    """
    if csv is None or io is None:
        raise ImportError("csv module not available (should be built-in)")

    from tone import decode

    data = decode(tone_str)

    # Extract tabular data
    if isinstance(data, list):
        records = data
    elif isinstance(data, dict):
        # Find first array in dict
        records = None
        for key, value in data.items():
            if isinstance(value, list):
                records = value
                break
        if records is None:
            # Convert dict to list
            records = [data]
    else:
        records = []

    if not records:
        return ""

    # CSV options
    if options is None:
        options = {}

    # Write CSV
    output = io.StringIO()
    if records and isinstance(records[0], dict):
        fieldnames = list(records[0].keys())
        writer = csv.DictWriter(output, fieldnames=fieldnames, **options)
        writer.writeheader()
        writer.writerows(records)
    else:
        # Primitive arrays
        writer = csv.writer(output, **options)
        writer.writerows(records)

    return output.getvalue()


def from_csv(csv_str: str) -> str:
    """
    Convert CSV to TONE format.
    
    Args:
        csv_str: CSV-formatted string
        
    Returns:
        TONE-formatted string (as tabular array)
    """
    if csv is None or io is None:
        raise ImportError("csv module not available (should be built-in)")

    from tone import encode

    # Read CSV
    input_io = io.StringIO(csv_str)
    reader = csv.DictReader(input_io)
    records = list(reader)

    # Convert to TONE
    return encode(records)


__all__ = ["to_json", "from_json", "to_yaml", "from_yaml", "to_csv", "from_csv"]

