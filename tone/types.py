"""Type definitions for TOON package."""

from typing import Dict, List, Literal, Optional, TypedDict, Union

# JSON types
JsonPrimitive = Union[str, int, float, bool, None]
JsonObject = Dict[str, "JsonValue"]
JsonArray = List["JsonValue"]
JsonValue = Union[JsonPrimitive, JsonObject, JsonArray]

# Delimiter types
Delimiter = Literal[",", "\t", "|"]
DelimiterKey = Literal["comma", "tab", "pipe"]

# Depth type (number of indentation levels)
Depth = int


# Encoder options (user-provided, optional fields)
class EncodeOptions(TypedDict, total=False):
    """Encoding options provided by user."""
    
    indent: int  # Number of spaces per indentation level (default: 2)
    delimiter: Delimiter  # Delimiter for arrays (default: ',')
    length_marker: Optional[Literal["#"]]  # Optional # prefix for array lengths


# Resolved encoder options (all fields required)
class ResolvedEncodeOptions(TypedDict):
    """Resolved encoding options with all fields set to defaults if needed."""
    
    indent: int  # Number of spaces per indentation level
    delimiter: Delimiter  # Delimiter for arrays
    length_marker: Optional[Literal["#"]]  # Optional # prefix for array lengths


# Decoder options (user-provided, optional fields)
class DecodeOptions(TypedDict, total=False):
    """Decoding options provided by user."""
    
    indent: int  # Number of spaces per indentation level (default: 2)
    strict: bool  # Enable strict validation (default: True)


# Resolved decoder options (all fields required)
class ResolvedDecodeOptions(TypedDict):
    """Resolved decoding options with all fields set to defaults if needed."""
    
    indent: int  # Number of spaces per indentation level
    strict: bool  # Enable strict validation


# Array header information
class ArrayHeaderInfo(TypedDict):
    """Information parsed from an array header."""
    
    length: int
    delimiter: Delimiter
    has_length_marker: bool
    key: Optional[str]
    fields: Optional[List[str]]


# Parsed line information
class ParsedLine(TypedDict):
    """Information about a parsed line."""
    
    raw: str  # Original line content
    depth: Depth  # Indentation depth
    indent: int  # Number of leading spaces
    content: str  # Content after indentation
    line_number: int  # Line number in source (1-indexed)


# Blank line information
class BlankLineInfo(TypedDict):
    """Information about a blank line."""
    
    line_number: int  # Line number in source (1-indexed)
    indent: int  # Number of leading spaces
    depth: Depth  # Indentation depth


# Scan result
class ScanResult(TypedDict):
    """Result of scanning TOON input."""
    
    lines: List[ParsedLine]
    blank_lines: List[BlankLineInfo]

