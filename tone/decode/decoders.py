"""Main decoding logic for TOON format.

This module provides the core decoding functionality following SPEC Section 5-12.
"""

from typing import Dict, List

from tone.constants import COLON, DEFAULT_DELIMITER, LIST_ITEM_PREFIX
from tone.decode.parser import (
    is_array_header_after_hyphen,
    is_object_first_field_after_hyphen,
    map_row_values_to_primitives,
    parse_array_header_line,
    parse_delimited_values,
    parse_key_token,
    parse_primitive_token,
)
from tone.decode.validation import (
    assert_expected_count,
    validate_no_blank_lines_in_range,
    validate_no_extra_list_items,
    validate_no_extra_tabular_rows,
)
from tone.shared.string_utils import find_closing_quote
from tone.types import Depth, JsonArray, JsonObject, JsonPrimitive, JsonValue, ResolvedDecodeOptions


def decode_value_from_lines(cursor, options: ResolvedDecodeOptions) -> JsonValue:
    """Decode TOON value from line cursor.
    
    Args:
        cursor: LineCursor for parsing lines
        options: Decoding options
        
    Returns:
        Python value (dict, list, or primitive)
        
    Raises:
        ReferenceError: If no content to decode
    """
    first = cursor.peek()
    if not first:
        raise ReferenceError("No content to decode")
    
    # Check for root array
    if is_array_header_after_hyphen(first["content"]):
        header_info = parse_array_header_line(first["content"], DEFAULT_DELIMITER)
        if header_info:
            cursor.advance()  # Move past the header line
            return decode_array_from_header(
                header_info["header"],
                header_info.get("inlineValues"),
                cursor,
                0,
                options,
            )
    
    # Check for single primitive value
    if cursor.length == 1 and not is_key_value_line(first):
        return parse_primitive_token(first["content"].strip())
    
    # Default to object
    return decode_object(cursor, 0, options)


def is_key_value_line(line: Dict) -> bool:
    """Check if line is a key-value line.
    
    Args:
        line: ParsedLine dict
        
    Returns:
        True if line is a key-value pair
    """
    content = line["content"]
    # Look for unquoted colon or quoted key followed by colon
    if content.startswith('"'):
        # Quoted key - find the closing quote
        closing_quote_index = find_closing_quote(content, 0)
        if closing_quote_index == -1:
            return False
        # Check if there's a colon after the quoted key
        return closing_quote_index + 1 < len(content) and content[closing_quote_index + 1] == COLON
    else:
        # Unquoted key - look for first colon not inside quotes
        return COLON in content


# Object decoding


def decode_object(cursor, base_depth: Depth, options: ResolvedDecodeOptions) -> JsonObject:
    """Decode a JSON object from lines.
    
    Args:
        cursor: LineCursor
        base_depth: Base indentation depth
        options: Decode options
        
    Returns:
        Decoded JSON object
    """
    obj: JsonObject = {}
    
    while not cursor.at_end():
        line = cursor.peek()
        if not line or line["depth"] < base_depth:
            break
        
        if line["depth"] == base_depth:
            key, value = decode_key_value_pair(line, cursor, base_depth, options)
            obj[key] = value
        else:
            break
    
    return obj


def decode_key_value(
    content: str,
    cursor,
    base_depth: Depth,
    options: ResolvedDecodeOptions,
) -> Dict:
    """Decode a key-value pair.
    
    Args:
        content: Line content
        cursor: LineCursor
        base_depth: Base depth
        options: Decode options
        
    Returns:
        Dict with 'key', 'value', 'followDepth'
    """
    # Check for array header first (before parsing key)
    array_header = parse_array_header_line(content, DEFAULT_DELIMITER)
    if array_header and array_header["header"].get("key"):
        value = decode_array_from_header(
            array_header["header"],
            array_header.get("inlineValues"),
            cursor,
            base_depth,
            options,
        )
        # After an array, subsequent fields are at baseDepth + 1 (where array content is)
        return {
            "key": array_header["header"]["key"],
            "value": value,
            "followDepth": base_depth + 1,
        }
    
    # Regular key-value pair
    key, end = parse_key_token(content, 0)
    rest = content[end:].strip()
    
    # No value after colon - expect nested object or empty
    if not rest:
        next_line = cursor.peek()
        if next_line and next_line["depth"] > base_depth:
            nested = decode_object(cursor, base_depth + 1, options)
            return {"key": key, "value": nested, "followDepth": base_depth + 1}
        # Empty object
        return {"key": key, "value": {}, "followDepth": base_depth + 1}
    
    # Inline primitive value
    value = parse_primitive_token(rest)
    return {"key": key, "value": value, "followDepth": base_depth + 1}


def decode_key_value_pair(
    line: Dict,
    cursor,
    base_depth: Depth,
    options: ResolvedDecodeOptions,
) -> tuple:
    """Decode a key-value pair from a line.
    
    Args:
        line: ParsedLine dict
        cursor: LineCursor
        base_depth: Base depth
        options: Decode options
        
    Returns:
        Tuple of (key, value)
    """
    cursor.advance()
    result = decode_key_value(line["content"], cursor, base_depth, options)
    return result["key"], result["value"]


# Array decoding


def decode_array_from_header(
    header: Dict,
    inline_values,
    cursor,
    base_depth: Depth,
    options: ResolvedDecodeOptions,
) -> JsonArray:
    """Decode an array from its header.
    
    Args:
        header: ArrayHeaderInfo
        inline_values: Optional inline values string
        cursor: LineCursor
        base_depth: Base depth
        options: Decode options
        
    Returns:
        Decoded JSON array
    """
    # Inline primitive array
    if inline_values:
        # For inline arrays, cursor should already be advanced or will be by caller
        return decode_inline_primitive_array(header, inline_values, options)
    
    # For multi-line arrays (tabular or list), the cursor should already be positioned
    # at the array header line, but we haven't advanced past it yet
    
    # Tabular array
    if header.get("fields") and len(header["fields"]) > 0:
        return decode_tabular_array(header, cursor, base_depth, options)
    
    # List array
    return decode_list_array(header, cursor, base_depth, options)


def decode_inline_primitive_array(
    header: Dict,
    inline_values: str,
    options: ResolvedDecodeOptions,
) -> List[JsonPrimitive]:
    """Decode inline primitive array.
    
    Args:
        header: ArrayHeaderInfo
        inline_values: Inline values string
        options: Decode options
        
    Returns:
        List of primitive values
    """
    if not inline_values.strip():
        assert_expected_count(0, header["length"], "inline array items", options)
        return []
    
    values = parse_delimited_values(inline_values, header["delimiter"])
    primitives = map_row_values_to_primitives(values)
    
    assert_expected_count(len(primitives), header["length"], "inline array items", options)
    
    return primitives


def decode_list_array(
    header: Dict,
    cursor,
    base_depth: Depth,
    options: ResolvedDecodeOptions,
) -> JsonArray:
    """Decode list array.
    
    Args:
        header: ArrayHeaderInfo
        cursor: LineCursor
        base_depth: Base depth
        options: Decode options
        
    Returns:
        Decoded JSON array
    """
    items: JsonArray = []
    item_depth = base_depth + 1
    
    # Track line range for blank line validation
    start_line = None
    end_line = None
    
    while not cursor.at_end() and len(items) < header["length"]:
        line = cursor.peek()
        if not line or line["depth"] < item_depth:
            break
        
        if line["depth"] == item_depth and line["content"].startswith(LIST_ITEM_PREFIX):
            # Track first and last item line numbers
            if start_line is None:
                start_line = line["line_number"]
            end_line = line["line_number"]
            
            item = decode_list_item(cursor, item_depth, header["delimiter"], options)
            items.append(item)
            
            # Update endLine to the current cursor position (after item was decoded)
            current_line = cursor.current()
            if current_line:
                end_line = current_line["line_number"]
        else:
            break
    
    assert_expected_count(len(items), header["length"], "list array items", options)
    
    # In strict mode, check for blank lines inside the array
    if options["strict"] and start_line is not None and end_line is not None:
        validate_no_blank_lines_in_range(
            start_line,  # From first item line
            end_line,  # To last item line
            cursor.get_blank_lines(),
            options["strict"],
            "list array",
        )
    
    # In strict mode, check for extra items
    if options["strict"]:
        validate_no_extra_list_items(cursor, item_depth, header["length"])
    
    return items


def decode_tabular_array(
    header: Dict,
    cursor,
    base_depth: Depth,
    options: ResolvedDecodeOptions,
) -> List[JsonObject]:
    """Decode tabular array.
    
    Args:
        header: ArrayHeaderInfo
        cursor: LineCursor
        base_depth: Base depth
        options: Decode options
        
    Returns:
        List of JSON objects
    """
    objects: List[JsonObject] = []
    row_depth = base_depth + 1
    
    # Track line range for blank line validation
    start_line = None
    end_line = None
    
    while not cursor.at_end() and len(objects) < header["length"]:
        line = cursor.peek()
        if not line or line["depth"] < row_depth:
            break
        
        if line["depth"] == row_depth:
            # Track first and last row line numbers
            if start_line is None:
                start_line = line["line_number"]
            end_line = line["line_number"]
            
            cursor.advance()
            values = parse_delimited_values(line["content"], header["delimiter"])
            assert_expected_count(
                len(values), len(header["fields"]), "tabular row values", options
            )
            
            primitives = map_row_values_to_primitives(values)
            obj: JsonObject = {}
            
            for i in range(len(header["fields"])):
                obj[header["fields"][i]] = primitives[i]
            
            objects.append(obj)
        else:
            break
    
    assert_expected_count(len(objects), header["length"], "tabular rows", options)
    
    # In strict mode, check for blank lines inside the array
    if options["strict"] and start_line is not None and end_line is not None:
        validate_no_blank_lines_in_range(
            start_line,  # From first row line
            end_line,  # To last row line
            cursor.get_blank_lines(),
            options["strict"],
            "tabular array",
        )
    
    # In strict mode, check for extra rows
    if options["strict"]:
        validate_no_extra_tabular_rows(cursor, row_depth, header)
    
    return objects


# List item decoding


def decode_list_item(
    cursor,
    base_depth: Depth,
    active_delimiter,
    options: ResolvedDecodeOptions,
) -> JsonValue:
    """Decode a list item.
    
    Args:
        cursor: LineCursor
        base_depth: Base depth
        active_delimiter: Active delimiter
        options: Decode options
        
    Returns:
        Decoded JSON value
        
    Raises:
        ReferenceError: If expected list item not found
    """
    line = cursor.next()
    if not line:
        raise ReferenceError("Expected list item")
    
    after_hyphen = line["content"][len(LIST_ITEM_PREFIX):]
    
    # Check for array header after hyphen
    if is_array_header_after_hyphen(after_hyphen):
        array_header = parse_array_header_line(after_hyphen, DEFAULT_DELIMITER)
        if array_header:
            return decode_array_from_header(
                array_header["header"],
                array_header.get("inlineValues"),
                cursor,
                base_depth,
                options,
            )
    
    # Check for object first field after hyphen
    if is_object_first_field_after_hyphen(after_hyphen):
        return decode_object_from_list_item(line, cursor, base_depth, options)
    
    # Primitive value
    return parse_primitive_token(after_hyphen)


def decode_object_from_list_item(
    first_line: Dict,
    cursor,
    base_depth: Depth,
    options: ResolvedDecodeOptions,
) -> JsonObject:
    """Decode object from list item.
    
    Args:
        first_line: First line dict
        cursor: LineCursor
        base_depth: Base depth
        options: Decode options
        
    Returns:
        Decoded JSON object
    """
    after_hyphen = first_line["content"][len(LIST_ITEM_PREFIX):]
    result = decode_key_value(after_hyphen, cursor, base_depth, options)
    
    obj: JsonObject = {result["key"]: result["value"]}
    
    # Read subsequent fields
    while not cursor.at_end():
        line = cursor.peek()
        if not line or line["depth"] < result["followDepth"]:
            break
        
        if (
            line["depth"] == result["followDepth"]
            and not line["content"].startswith(LIST_ITEM_PREFIX)
        ):
            key, value = decode_key_value_pair(line, cursor, result["followDepth"], options)
            obj[key] = value
        else:
            break
    
    return obj
