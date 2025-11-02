"""
Utility modules for TOON.

Provides advanced features and utilities:
- async_support: Async/await operations
- context: Context managers for file operations
- debug: Debugging and inspection tools
- exceptions: Rich error handling
- format: Pretty printing and formatting
- stream: Streaming support for large data
- tokens: Token estimation and optimization
"""

from tone.utils.async_support import (
    adecode,
    adecode_batch,
    adecode_parallel,
    aencode,
    aencode_batch,
    aencode_parallel,
)
from tone.utils.context import TONEDecoder, TONEEncoder
from tone.utils.debug import debug_decode, debug_encode, inspect_parse_tree
from tone.utils.exceptions import (
    TONEDecodeError,
    TONEEncodeError,
    TONEError,
    TONENormalizationError,
    TONESyntaxError,
    TONETypeError,
    TONEValidationError,
    TONEValueError,
)
from tone.utils.format import create_table, format_toon, format_value, summarize_structure
from tone.utils.stream import decode_stream, encode_stream

__all__ = [
    # Async support
    "aencode",
    "adecode",
    "aencode_batch",
    "adecode_batch",
    "aencode_parallel",
    "adecode_parallel",
    # Context managers
    "TONEEncoder",
    "TONEDecoder",
    # Debug tools
    "debug_encode",
    "debug_decode",
    "inspect_parse_tree",
    # Exceptions
    "TONEError",
    "TONEEncodeError",
    "TONEDecodeError",
    "TONESyntaxError",
    "TONEValidationError",
    "TONENormalizationError",
    "TONETypeError",
    "TONEValueError",
    # Formatting
    "format_value",
    "format_toon",
    "summarize_structure",
    "create_table",
    # Streaming
    "encode_stream",
    "decode_stream",
]

# Optional token utilities
try:
    from tone.utils.tokens import compare_formats, estimate_tokens, optimize_for_tokens

    __all__.extend(["estimate_tokens", "compare_formats", "optimize_for_tokens"])
except ImportError:
    pass

