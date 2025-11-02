"""TONE - Token-Optimized Notation Engine for LLMs.

A compact, human-readable data format designed for AI and LLM contexts.
Encodes JSON-compatible structures using far fewer tokens — typically 40-60% less —
making it ideal for AI assistants, RAG systems, and conversational data pipelines.
"""

from tone.__version__ import __version__
from tone._core import decode, encode
from tone.constants import DEFAULT_DELIMITER, DELIMITERS
from tone.async_support import (
    adecode,
    adecode_batch,
    adecode_parallel,
    aencode,
    aencode_batch,
    aencode_parallel,
)
from tone.context import TONEDecoder, TONEEncoder
from tone.debug import debug_decode, debug_encode, inspect_parse_tree
from tone.format import (
    create_table,
    format_toon,
    format_value,
    summarize_structure,
)
from tone.types import (
    DecodeOptions,
    Delimiter,
    DelimiterKey,
    EncodeOptions,
    JsonArray,
    JsonObject,
    JsonPrimitive,
    JsonValue,
    ResolvedDecodeOptions,
    ResolvedEncodeOptions,
)

__all__ = [
    "__version__",
    "adecode",
    "adecode_batch",
    "adecode_parallel",
    "aencode",
    "aencode_batch",
    "aencode_parallel",
    "create_table",
    "debug_decode",
    "debug_encode",
    "decode",
    "DecodeOptions",
    "DEFAULT_DELIMITER",
    "Delimiter",
    "DelimiterKey",
    "DELIMITERS",
    "encode",
    "EncodeOptions",
    "format_toon",
    "format_value",
    "inspect_parse_tree",
    "JsonArray",
    "JsonObject",
    "JsonPrimitive",
    "JsonValue",
    "ResolvedDecodeOptions",
    "ResolvedEncodeOptions",
    "summarize_structure",
    "TONEDecoder",
    "TONEEncoder",
]

# Optional advanced features
try:
    from tone.stream import decode_stream, encode_stream

    __all__.extend(["encode_stream", "decode_stream"])
except ImportError:
    pass

try:
    from tone.tokens import compare_formats, estimate_tokens, optimize_for_tokens

    __all__.extend(["estimate_tokens", "compare_formats", "optimize_for_tokens"])
except ImportError:
    pass

# Optional ecosystem integrations
try:
    from tone.integrations import (
        TONEResponse,
        decode_model,
        encode_model,
        from_toon,
        to_toon,
    )

    __all__.extend(["TONEResponse", "encode_model", "decode_model", "to_toon", "from_toon"])
except ImportError:
    pass

try:
    from tone.integrations import (
        from_csv,
        from_json,
        from_yaml,
        to_csv,
        to_json,
        to_yaml,
    )

    __all__.extend(["to_json", "from_json", "to_yaml", "from_yaml", "to_csv", "from_csv"])
except ImportError:
    pass

# Import exceptions for easy access
try:
    from tone.exceptions import (
        TONEDecodeError,
        TONEEncodeError,
        TONEError,
        TONENormalizationError,
        TONESyntaxError,
        TONETypeError,
        TONEValidationError,
        TONEValueError,
    )

    __all__.extend([
        "TONEError",
        "TONEEncodeError",
        "TONEDecodeError",
        "TONESyntaxError",
        "TONEValidationError",
        "TONENormalizationError",
        "TONETypeError",
        "TONEValueError",
    ])
except ImportError:
    pass
