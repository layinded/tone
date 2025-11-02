"""
Streaming support for TOON encoding and decoding.

Provides memory-efficient processing for large datasets.
"""

from typing import Any, Iterator, List, Optional

from tone.constants import LIST_ITEM_PREFIX, NEWLINE
from tone.encode.encoders import encode_value
from tone.encode.normalize import is_array_of_objects, is_json_array, is_json_object, is_json_primitive, normalize_value
from tone.encode.primitives import format_header
from tone.encode.writer import LineWriter
from tone.types import JsonArray, JsonObject, JsonValue, ResolvedEncodeOptions


def encode_stream(
    items: Iterator[Any],
    options: Optional[dict] = None,
    chunk_size: int = 1000,
) -> Iterator[str]:
    """
    Encode a stream of items to TOON format incrementally.

    Yields TOON-formatted strings in chunks for memory-efficient processing.

    Args:
        items: Iterator of items to encode
        items: Iterator of items to encode
        options: Optional encoding options
        chunk_size: Number of items per chunk

    Yields:
        TOON-formatted string chunks

    Example:
        >>> items = [{'id': i, 'name': f'item_{i}'} for i in range(10000)]
        >>> for chunk in encode_stream(iter(items), chunk_size=100):
        ...     file.write(chunk)
    """
    from tone._core import _resolve_encode_options

    resolved_options = _resolve_encode_options(options)

    # Buffer items to determine format
    buffer: List[Any] = []
    header_written = False

    for item in items:
        buffer.append(item)

        # When buffer is full, yield chunk
        if len(buffer) >= chunk_size:
            if not header_written:
                # Determine if tabular format can be used
                normalized_items = [normalize_value(item) for item in buffer]
                chunk = _encode_items_chunk(normalized_items, resolved_options, header_written)
                header_written = True
            else:
                chunk = _encode_items_body(buffer, resolved_options, header_written)

            yield chunk
            buffer = []

    # Yield remaining items
    if buffer:
        if not header_written:
            normalized_items = [normalize_value(item) for item in buffer]
            chunk = _encode_items_chunk(normalized_items, resolved_options, header_written)
        else:
            chunk = _encode_items_body(buffer, resolved_options, header_written)
        yield chunk


def _encode_items_chunk(items: List[JsonValue], options: ResolvedEncodeOptions, header_written: bool) -> str:
    """Encode a chunk of items with header."""
    if not items:
        return ""

    normalized = items

    # Check if we can use tabular format (all items are objects with same keys)
    if is_tabular_items(normalized):
        return _encode_tabular_chunk(normalized, options)
    else:
        return _encode_list_chunk(normalized, options, not header_written)


def _encode_items_body(items: List[Any], options: ResolvedEncodeOptions, header_written: bool) -> str:
    """Encode chunk body (after header)."""
    normalized = [normalize_value(item) for item in items]

    if is_tabular_items(normalized):
        return _encode_tabular_body(normalized, options)
    else:
        return _encode_list_body(normalized, options)


def is_tabular_items(items: List[JsonValue]) -> bool:
    """Check if items can be encoded as tabular."""
    if not items or not all(is_json_object(item) for item in items):
        return False

    # Check all items have same keys
    first_keys = list(items[0].keys()) if items else []
    return all(list(item.keys()) == first_keys for item in items) and all(
        is_json_primitive(item[key]) for item in items for key in first_keys
    )


def _encode_tabular_chunk(items: List[JsonObject], options: ResolvedEncodeOptions) -> str:
    """Encode items as tabular format with header."""
    if not items:
        return format_header(0, delimiter=options["delimiter"], length_marker=options["length_marker"])

    header_fields = list(items[0].keys())
    header_line = format_header(
        len(items),
        fields=header_fields,
        delimiter=options["delimiter"],
        length_marker=options["length_marker"],
    )
    header_line += ":"

    rows = _encode_tabular_body(items, options)
    return header_line + NEWLINE + rows


def _encode_tabular_body(items: List[JsonObject], options: ResolvedEncodeOptions) -> str:
    """Encode tabular rows."""
    from tone.encode.primitives import encode_and_join_primitives

    if not items:
        return ""

    header_fields = list(items[0].keys())
    lines = []
    indent = " " * options["indent"]

    for item in items:
        values = [item[field] for field in header_fields]
        row = encode_and_join_primitives(values, options["delimiter"])
        lines.append(indent + row)

    return NEWLINE.join(lines)


def _encode_list_chunk(items: List[JsonValue], options: ResolvedEncodeOptions, include_header: bool = True) -> str:
    """Encode items as list format with optional header."""
    if not items:
        header = format_header(0, delimiter=options["delimiter"], length_marker=options["length_marker"])
        return header + ":"

    header_line = format_header(len(items), delimiter=options["delimiter"], length_marker=options["length_marker"])
    header_line += ":"

    body = _encode_list_body(items, options)
    if include_header:
        return header_line + NEWLINE + body
    return body


def _encode_list_body(items: List[JsonValue], options: ResolvedEncodeOptions) -> str:
    """Encode list items."""
    writer = LineWriter(options["indent"])
    indent = " " * options["indent"]
    indent_level = 1

    for item in items:
        if is_json_primitive(item):
            from tone.encode.primitives import encode_primitive

            encoded = encode_primitive(item, options["delimiter"])
            writer.push_list_item(indent_level, encoded)
        elif is_json_object(item):
            # Encode as object list item
            _encode_object_list_item(writer, item, indent_level, options)
        elif is_json_array(item):
            # Encode as array list item
            _encode_array_list_item(writer, item, indent_level, options)

    return writer.to_string()


def _encode_object_list_item(writer: LineWriter, obj: JsonObject, depth: int, options: ResolvedEncodeOptions) -> None:
    """Encode object as list item."""
    from tone.encode.encoders import encode_object_as_list_item

    encode_object_as_list_item(obj, writer, depth, options)


def _encode_array_list_item(writer: LineWriter, arr: JsonArray, depth: int, options: ResolvedEncodeOptions) -> None:
    """Encode array as list item."""
    from tone.encode.primitives import encode_and_join_primitives

    if is_json_primitive(arr[0]) if arr else False:
        # Primitive array, inline
        inline = encode_and_join_primitives(arr, options["delimiter"])
        header = format_header(len(arr), delimiter=options["delimiter"], length_marker=options["length_marker"])
        writer.push_list_item(depth, f"{header}: {inline}")
    else:
        # Complex array, use list format
        header = format_header(len(arr), delimiter=options["delimiter"], length_marker=options["length_marker"])
        writer.push_list_item(depth, f"{header}:")


def decode_stream(
    file_handle,
    options: Optional[dict] = None,
) -> Iterator[JsonValue]:
    """
    Decode TOON data from a file incrementally.

    Reads and parses TOON data line by line for memory-efficient processing.

    Args:
        file_handle: File-like object to read from
        options: Optional decoding options

    Yields:
        Decoded TOON values

    Example:
        >>> with open('data.toon') as f:
        ...     for item in decode_stream(f):
        ...         process(item)
    """
    from tone import decode

    # For now, read entire content and split by top-level objects
    # TODO: Implement true streaming parser
    content = file_handle.read()
    data = decode(content, options)

    # If decoded data is a list, yield items
    if isinstance(data, list):
        for item in data:
            yield item
    else:
        yield data


__all__ = ["encode_stream", "decode_stream"]

