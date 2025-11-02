"""Core encode/decode functions.

This module provides the main API for encoding Python values to TOON format
and decoding TOON strings back to Python values.
"""

from typing import Any, Optional

from tone.constants import DEFAULT_DELIMITER
from tone.decode.decoders import decode_value_from_lines  # TODO: Implement
from tone.decode.scanner import LineCursor, to_parsed_lines  # TODO: Implement
from tone.encode.encoders import encode_value  # TODO: Implement
from tone.encode.normalize import normalize_value  # TODO: Implement
from tone.types import DecodeOptions, EncodeOptions, JsonValue, ResolvedDecodeOptions, ResolvedEncodeOptions


def encode(value: Any, options: Optional[EncodeOptions] = None) -> str:
    """Encode a Python value to TOON format.
    
    Args:
        value: Any JSON-serializable value (object, array, primitive, or nested)
        options: Optional encoding options (indent, delimiter, length_marker)
        
    Returns:
        TOON-formatted string with no trailing newline or spaces.
        
    Example:
        >>> encode({'users': [{'id': 1, 'name': 'Alice'}]})
        'users[1]{id,name}:\\n  1,Alice'
    """
    normalized_value = normalize_value(value)
    resolved_options = _resolve_encode_options(options)
    return encode_value(normalized_value, resolved_options)


def decode(input_str: str, options: Optional[DecodeOptions] = None) -> JsonValue:
    """Decode a TOON-formatted string to Python values.
    
    Args:
        input_str: A TOON-formatted string to parse
        options: Optional decoding options (indent, strict)
        
    Returns:
        Python value (dict, list, or primitive) representing the parsed TOON data.
        
    Example:
        >>> decode('users[1]{id,name}:\\n  1,Alice')
        {'users': [{'id': 1, 'name': 'Alice'}]}
    """
    resolved_options = _resolve_decode_options(options)
    scan_result = to_parsed_lines(input_str, resolved_options["indent"], resolved_options["strict"])
    
    if len(scan_result["lines"]) == 0:
        raise ValueError("Cannot decode empty input: input must be a non-empty string")
    
    cursor = LineCursor(scan_result["lines"], scan_result["blank_lines"])
    return decode_value_from_lines(cursor, resolved_options)


def _resolve_encode_options(options: Optional[EncodeOptions] = None) -> ResolvedEncodeOptions:
    """Resolve encode options with defaults.
    
    Args:
        options: Optional user-provided options
        
    Returns:
        Resolved options with all fields set
    """
    return ResolvedEncodeOptions(
        indent=2 if options is None or options.get("indent") is None else options["indent"],
        delimiter=DEFAULT_DELIMITER if options is None or options.get("delimiter") is None else options["delimiter"],
        length_marker=None if options is None or options.get("length_marker") is None else options["length_marker"],
    )


def _resolve_decode_options(options: Optional[DecodeOptions] = None) -> ResolvedDecodeOptions:
    """Resolve decode options with defaults.
    
    Args:
        options: Optional user-provided options
        
    Returns:
        Resolved options with all fields set
    """
    return ResolvedDecodeOptions(
        indent=2 if options is None or options.get("indent") is None else options["indent"],
        strict=True if options is None or options.get("strict") is None else options["strict"],
    )

