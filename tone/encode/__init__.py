"""Encoding module for converting Python values to TOON format."""

from typing import List

# Import all implemented functions
from tone.encode.encoders import encode_value  # NOQA: F401
from tone.encode.normalize import (  # NOQA: F401
    is_array_of_arrays,
    is_array_of_objects,
    is_array_of_primitives,
    is_json_array,
    is_json_object,
    is_json_primitive,
    is_plain_object,
    normalize_value,
)
from tone.encode.primitives import (  # NOQA: F401
    encode_and_join_primitives,
    encode_key,
    encode_primitive,
    format_header,
)
from tone.encode.writer import LineWriter  # NOQA: F401

__all__: List[str] = [
    "LineWriter",
    "encode_and_join_primitives",
    "encode_key",
    "encode_primitive",
    "encode_value",
    "format_header",
    "is_array_of_arrays",
    "is_array_of_objects",
    "is_array_of_primitives",
    "is_json_array",
    "is_json_object",
    "is_json_primitive",
    "is_plain_object",
    "normalize_value",
]

