"""Constants for TOON format tokens, delimiters, and structural elements."""

# List markers
LIST_ITEM_MARKER = "-"
LIST_ITEM_PREFIX = "- "

# Structural characters
COMMA = ","
COLON = ":"
SPACE = " "
PIPE = "|"
HASH = "#"

# Brackets and braces
OPEN_BRACKET = "["
CLOSE_BRACKET = "]"
OPEN_BRACE = "{"
CLOSE_BRACE = "}"

# Literals
NULL_LITERAL = "null"
TRUE_LITERAL = "true"
FALSE_LITERAL = "false"

# Escape characters
BACKSLASH = "\\"
DOUBLE_QUOTE = '"'
NEWLINE = "\n"
CARRIAGE_RETURN = "\r"
TAB = "\t"

# Delimiters
DELIMITERS = {
    "comma": COMMA,
    "tab": TAB,
    "pipe": PIPE,
}

# Type aliases for type hints
Delimiter = str  # Will be made more specific with Literal
DelimiterKey = str  # Will be made more specific with Literal

DEFAULT_DELIMITER: Delimiter = DELIMITERS["comma"]

