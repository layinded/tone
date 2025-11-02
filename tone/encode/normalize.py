"""Type normalization for encoding.

This module normalizes Python values to JSON-compatible types according to
SPEC Section 3 (Encoding Normalization).
"""

import math
from datetime import datetime
from typing import Any, List, Union

from tone.exceptions import TONENormalizationError
from tone.types import JsonArray, JsonObject, JsonPrimitive, JsonValue


def normalize_value(value: Any) -> JsonValue:
    """Normalize Python values to JSON-compatible types.
    
    Args:
        value: Any Python value
        
    Returns:
        JSON-serializable value
        
    Following SPEC Section 3:
    - null → null
    - string, boolean → as-is
    - number: -0 → 0, NaN/Infinity → null
    - BigInt → number (if safe) or string
    - Date → ISO string
    - Array → array with normalized elements
    - Set → array
    - Map → object
    - Plain object → object with normalized values
    - Function/symbol/undefined → null
    """
    # null
    if value is None:
        return None
    
    # Primitives
    if isinstance(value, (str, bool)):
        return value
    
    # Numbers: canonicalize -0 to 0, handle NaN and Infinity
    if isinstance(value, (int, float)):
        # Check for -0.0
        if value == 0 and math.copysign(1, value) < 0:
            return 0
        # Check for NaN or Infinity
        if not math.isfinite(value):
            return None
        return value
    
    # BigInt handling (Python int is arbitrary precision)
    # For Python, we don't need special BigInt handling, but we track it for completeness
    if isinstance(value, int):
        # Python int can be very large
        # If within safe range, return as-is
        # Otherwise, could convert to string, but for now keep as int
        return value
    
    # Date → ISO string
    if isinstance(value, datetime):
        return value.isoformat()
    
    # Array → array with normalized elements
    if isinstance(value, list):
        return [normalize_value(item) for item in value]
    
    # Set → array
    if isinstance(value, (set, frozenset)):
        return [normalize_value(item) for item in value]
    
    # Map → object (collections.OrderedDict, dict subclasses)
    # For Python, we'll handle dict specially
    if isinstance(value, dict):
        # Plain dict
        if _is_plain_dict(value):
            result = {}
            for key in value:
                if _is_valid_dict_key(key):
                    result[str(key)] = normalize_value(value[key])
            return result
    
    # Fallback: function, class, or other → null
    return None


def _is_plain_dict(value: Any) -> bool:
    """Check if value is a plain dict (not a dict subclass).
    
    Args:
        value: Value to check
        
    Returns:
        True if it's a plain dict
    """
    return isinstance(value, dict) and type(value) is dict


def _is_valid_dict_key(key: Any) -> bool:
    """Check if key can be used in a dict for JSON serialization.
    
    Args:
        key: Key to check
        
    Returns:
        True if key is valid
    """
    return isinstance(key, (str, int, float, bool))


# Type guards


def is_json_primitive(value: Any) -> bool:
    """Check if value is a JSON primitive.
    
    Args:
        value: Value to check
        
    Returns:
        True if value is a JSON primitive (str, int, float, bool, None)
    """
    return value is None or isinstance(value, (str, int, float, bool))


def is_json_array(value: Any) -> bool:
    """Check if value is a JSON array.
    
    Args:
        value: Value to check
        
    Returns:
        True if value is a list
    """
    return isinstance(value, list)


def is_json_object(value: Any) -> bool:
    """Check if value is a JSON object.
    
    Args:
        value: Value to check
        
    Returns:
        True if value is a dict
    """
    return isinstance(value, dict)


def is_plain_object(value: Any) -> bool:
    """Check if value is a plain object (dict, not list).
    
    Args:
        value: Value to check
        
    Returns:
        True if value is a dict
    """
    return isinstance(value, dict) and not isinstance(value, list)


# Array type detection


def is_array_of_primitives(value: JsonArray) -> bool:
    """Check if array contains only primitives.
    
    Args:
        value: Array to check
        
    Returns:
        True if all items are primitives
    """
    return all(is_json_primitive(item) for item in value)


def is_array_of_arrays(value: JsonArray) -> bool:
    """Check if array contains only arrays.
    
    Args:
        value: Array to check
        
    Returns:
        True if all items are arrays
    """
    return all(is_json_array(item) for item in value)


def is_array_of_objects(value: JsonArray) -> bool:
    """Check if array contains only objects.
    
    Args:
        value: Array to check
        
    Returns:
        True if all items are objects
    """
    return all(is_json_object(item) for item in value)

