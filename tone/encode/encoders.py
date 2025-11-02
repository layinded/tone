"""Main encoding logic for TOON format.

This module provides the core encoding functionality following SPEC Section 5-12.
"""

from typing import List, Optional

from tone.constants import LIST_ITEM_MARKER
from tone.encode.normalize import (
    is_array_of_arrays,
    is_array_of_objects,
    is_array_of_primitives,
    is_json_array,
    is_json_object,
    is_json_primitive,
)
from tone.encode.primitives import (
    encode_and_join_primitives,
    encode_key,
    encode_primitive,
    format_header,
)
from tone.encode.writer import LineWriter
from tone.types import Depth, JsonArray, JsonObject, JsonPrimitive, JsonValue, ResolvedEncodeOptions


def encode_value(value: JsonValue, options: ResolvedEncodeOptions) -> str:
    """Encode a Python value to TOON format.
    
    Args:
        value: JSON-serializable value
        options: Encoding options
        
    Returns:
        TOON-formatted string
    """
    if is_json_primitive(value):
        return encode_primitive(value, options["delimiter"])
    
    writer = LineWriter(options["indent"])
    
    if is_json_array(value):
        encode_array(None, value, writer, 0, options)
    elif is_json_object(value):
        encode_object(value, writer, 0, options)
    
    return writer.to_string()


# Object encoding


def encode_object(value: JsonObject, writer: LineWriter, depth: Depth, options: ResolvedEncodeOptions) -> None:
    """Encode a JSON object to TOON format.
    
    Args:
        value: Object to encode
        writer: Line writer
        depth: Current indentation depth
        options: Encoding options
    """
    for key, val in value.items():
        encode_key_value_pair(key, val, writer, depth, options)


def encode_key_value_pair(key: str, value: JsonValue, writer: LineWriter, depth: Depth, options: ResolvedEncodeOptions) -> None:
    """Encode a key-value pair.
    
    Args:
        key: Object key
        value: Value to encode
        writer: Line writer
        depth: Current indentation depth
        options: Encoding options
    """
    encoded_key = encode_key(key)
    
    if is_json_primitive(value):
        writer.push(depth, f"{encoded_key}: {encode_primitive(value, options['delimiter'])}")
    elif is_json_array(value):
        encode_array(key, value, writer, depth, options)
    elif is_json_object(value):
        nested_keys = list(value.keys())
        if len(nested_keys) == 0:
            # Empty object
            writer.push(depth, f"{encoded_key}:")
        else:
            writer.push(depth, f"{encoded_key}:")
            encode_object(value, writer, depth + 1, options)


# Array encoding


def encode_array(
    key: Optional[str],
    value: JsonArray,
    writer: LineWriter,
    depth: Depth,
    options: ResolvedEncodeOptions,
) -> None:
    """Encode a JSON array to TOON format.
    
    Args:
        key: Optional key for this array
        value: Array to encode
        writer: Line writer
        depth: Current indentation depth
        options: Encoding options
    """
    if len(value) == 0:
        header = format_header(
            0,
            key=key,
            delimiter=options["delimiter"],
            length_marker=options["length_marker"],
        )
        writer.push(depth, header)
        return
    
    # Primitive array
    if is_array_of_primitives(value):
        formatted = encode_inline_array_line(value, options["delimiter"], key, options["length_marker"])
        writer.push(depth, formatted)
        return
    
    # Array of arrays (all primitives)
    if is_array_of_arrays(value):
        all_primitive_arrays = all(is_array_of_primitives(arr) for arr in value)
        if all_primitive_arrays:
            encode_array_of_arrays_as_list_items(key, value, writer, depth, options)
            return
    
    # Array of objects
    if is_array_of_objects(value):
        header = extract_tabular_header(value)
        if header:
            encode_array_of_objects_as_tabular(key, value, header, writer, depth, options)
        else:
            encode_mixed_array_as_list_items(key, value, writer, depth, options)
        return
    
    # Mixed array: fallback to expanded format
    encode_mixed_array_as_list_items(key, value, writer, depth, options)


# Array of arrays (expanded format)


def encode_array_of_arrays_as_list_items(
    prefix: Optional[str],
    values: JsonArray,
    writer: LineWriter,
    depth: Depth,
    options: ResolvedEncodeOptions,
) -> None:
    """Encode array of arrays as list items.
    
    Args:
        prefix: Optional key prefix
        values: Array of arrays to encode
        writer: Line writer
        depth: Current indentation depth
        options: Encoding options
    """
    header = format_header(
        len(values),
        key=prefix,
        delimiter=options["delimiter"],
        length_marker=options["length_marker"],
    )
    writer.push(depth, header)
    
    for arr in values:
        if is_array_of_primitives(arr):
            inline = encode_inline_array_line(arr, options["delimiter"], None, options["length_marker"])
            writer.push_list_item(depth + 1, inline)


def encode_inline_array_line(
    values: List[JsonPrimitive],
    delimiter: str,
    prefix: Optional[str] = None,
    length_marker: Optional[str] = None,
) -> str:
    """Encode inline array line.
    
    Args:
        values: Primitive values
        delimiter: Delimiter to use
        prefix: Optional key prefix
        length_marker: Optional length marker
        
    Returns:
        Formatted inline array line
    """
    header = format_header(len(values), key=prefix, delimiter=delimiter, length_marker=length_marker)
    joined_value = encode_and_join_primitives(values, delimiter)
    # Only add space if there are values
    if len(values) == 0:
        return header
    return f"{header} {joined_value}"


# Array of objects (tabular format)


def encode_array_of_objects_as_tabular(
    prefix: Optional[str],
    rows: JsonArray,
    header: List[str],
    writer: LineWriter,
    depth: Depth,
    options: ResolvedEncodeOptions,
) -> None:
    """Encode array of objects in tabular format.
    
    Args:
        prefix: Optional key prefix
        rows: Array of objects to encode
        header: Field header names
        writer: Line writer
        depth: Current indentation depth
        options: Encoding options
    """
    formatted_header = format_header(
        len(rows),
        key=prefix,
        fields=header,
        delimiter=options["delimiter"],
        length_marker=options["length_marker"],
    )
    writer.push(depth, formatted_header)
    
    write_tabular_rows(rows, header, writer, depth + 1, options)


def extract_tabular_header(rows: JsonArray) -> Optional[List[str]]:
    """Extract tabular header from array of objects.
    
    Args:
        rows: Array of objects
        
    Returns:
        Header field names if tabular format applies, None otherwise
    """
    if len(rows) == 0:
        return None
    
    first_row = rows[0]
    if not isinstance(first_row, dict):
        return None
    
    first_keys = list(first_row.keys())
    if len(first_keys) == 0:
        return None
    
    if is_tabular_array(rows, first_keys):
        return first_keys
    
    return None


def is_tabular_array(rows: JsonArray, header: List[str]) -> bool:
    """Check if array of objects is tabular (same fields, primitive values).
    
    Args:
        rows: Array of objects to check
        header: Header field names
        
    Returns:
        True if all rows have same keys and all values are primitives
    """
    for row in rows:
        if not isinstance(row, dict):
            return False
        
        keys = list(row.keys())
        
        # All objects must have the same keys (but order can differ)
        if len(keys) != len(header):
            return False
        
        # Check that all header keys exist in the row and all values are primitives
        for key in header:
            if key not in row:
                return False
            if not is_json_primitive(row[key]):
                return False
    
    return True


def write_tabular_rows(
    rows: JsonArray,
    header: List[str],
    writer: LineWriter,
    depth: Depth,
    options: ResolvedEncodeOptions,
) -> None:
    """Write tabular rows.
    
    Args:
        rows: Array of objects
        header: Field header names
        writer: Line writer
        depth: Current indentation depth
        options: Encoding options
    """
    for row in rows:
        if not isinstance(row, dict):
            continue
        values = [row[key] for key in header]
        joined_value = encode_and_join_primitives(values, options["delimiter"])
        writer.push(depth, joined_value)


# Array of objects (expanded format)


def encode_mixed_array_as_list_items(
    prefix: Optional[str],
    items: JsonArray,
    writer: LineWriter,
    depth: Depth,
    options: ResolvedEncodeOptions,
) -> None:
    """Encode mixed array as list items.
    
    Args:
        prefix: Optional key prefix
        items: Array of mixed values
        writer: Line writer
        depth: Current indentation depth
        options: Encoding options
    """
    header = format_header(
        len(items),
        key=prefix,
        delimiter=options["delimiter"],
        length_marker=options["length_marker"],
    )
    writer.push(depth, header)
    
    for item in items:
        encode_list_item_value(item, writer, depth + 1, options)


def encode_object_as_list_item(obj: JsonObject, writer: LineWriter, depth: Depth, options: ResolvedEncodeOptions) -> None:
    """Encode an object as a list item.
    
    Args:
        obj: Object to encode
        writer: Line writer
        depth: Current indentation depth
        options: Encoding options
    """
    keys = list(obj.keys())
    if len(keys) == 0:
        writer.push(depth, LIST_ITEM_MARKER)
        return
    
    # First key-value on the same line as "- "
    first_key = keys[0]
    encoded_key = encode_key(first_key)
    first_value = obj[first_key]
    
    if is_json_primitive(first_value):
        writer.push_list_item(depth, f"{encoded_key}: {encode_primitive(first_value, options['delimiter'])}")
    elif is_json_array(first_value):
        if is_array_of_primitives(first_value):
            # Inline format for primitive arrays
            formatted = encode_inline_array_line(first_value, options["delimiter"], first_key, options["length_marker"])
            writer.push_list_item(depth, formatted)
        elif is_array_of_objects(first_value):
            # Check if array of objects can use tabular format
            header = extract_tabular_header(first_value)
            if header:
                # Tabular format for uniform arrays of objects
                formatted_header = format_header(
                    len(first_value),
                    key=first_key,
                    fields=header,
                    delimiter=options["delimiter"],
                    length_marker=options["length_marker"],
                )
                writer.push_list_item(depth, formatted_header)
                write_tabular_rows(first_value, header, writer, depth + 1, options)
            else:
                # Fall back to list format for non-uniform arrays of objects
                writer.push_list_item(depth, f"{encoded_key}[{len(first_value)}]:")
                for item in first_value:
                    encode_object_as_list_item(item, writer, depth + 1, options)
        else:
            # Complex arrays on separate lines (array of arrays, etc.)
            writer.push_list_item(depth, f"{encoded_key}[{len(first_value)}]:")
            
            # Encode array contents at depth + 1
            for item in first_value:
                encode_list_item_value(item, writer, depth + 1, options)
    elif is_json_object(first_value):
        nested_keys = list(first_value.keys())
        if len(nested_keys) == 0:
            writer.push_list_item(depth, f"{encoded_key}:")
        else:
            writer.push_list_item(depth, f"{encoded_key}:")
            encode_object(first_value, writer, depth + 2, options)
    
    # Remaining keys on indented lines
    for i in range(1, len(keys)):
        key = keys[i]
        encode_key_value_pair(key, obj[key], writer, depth + 1, options)


# List item encoding helpers


def encode_list_item_value(
    value: JsonValue,
    writer: LineWriter,
    depth: Depth,
    options: ResolvedEncodeOptions,
) -> None:
    """Encode a value as a list item.
    
    Args:
        value: Value to encode
        writer: Line writer
        depth: Current indentation depth
        options: Encoding options
    """
    if is_json_primitive(value):
        writer.push_list_item(depth, encode_primitive(value, options["delimiter"]))
    elif is_json_array(value) and is_array_of_primitives(value):
        inline = encode_inline_array_line(value, options["delimiter"], None, options["length_marker"])
        writer.push_list_item(depth, inline)
    elif is_json_object(value):
        encode_object_as_list_item(value, writer, depth, options)

