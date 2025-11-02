"""
Async support for TOON encoding and decoding.

Provides async/await interfaces for non-blocking operations,
useful for web applications and concurrent processing.
"""

import asyncio
from typing import Any, AsyncIterator, Iterator, Optional

from tone._core import decode, encode
from tone.types import DecodeOptions, EncodeOptions, JsonValue


async def aencode(value: Any, options: Optional[EncodeOptions] = None) -> str:
    """
    Async encode Python value to TOON format.
    
    This is a non-blocking version of encode() that runs in a thread pool
    to avoid blocking the event loop.
    
    Args:
        value: Python value to encode
        options: Optional encoding options
        
    Returns:
        TOON-formatted string
        
    Example:
        >>> import asyncio
        >>> data = {'users': [{'id': 1, 'name': 'Alice'}]}
        >>> result = await aencode(data)
        >>> print(result)
    """
    loop = asyncio.get_event_loop()
    return await loop.run_in_executor(None, encode, value, options)


async def adecode(input_str: str, options: Optional[DecodeOptions] = None) -> JsonValue:
    """
    Async decode TOON string to Python value.
    
    This is a non-blocking version of decode() that runs in a thread pool
    to avoid blocking the event loop.
    
    Args:
        input_str: TOON-formatted string
        options: Optional decoding options
        
    Returns:
        Python data structure
        
    Example:
        >>> import asyncio
        >>> toon = 'users[1]{id,name}:\n  1,Alice'
        >>> result = await adecode(toon)
        >>> print(result)
    """
    loop = asyncio.get_event_loop()
    return await loop.run_in_executor(None, decode, input_str, options)


async def aencode_batch(values: Iterator[Any], options: Optional[EncodeOptions] = None) -> AsyncIterator[str]:
    """
    Async encode batch of values.
    
    Yields encoded strings as they become available, allowing streaming
    of results without blocking.
    
    Args:
        values: Iterator of Python values
        options: Optional encoding options
        
    Yields:
        TOON-formatted strings
        
    Example:
        >>> async def process():
        ...     data = [{'id': i} for i in range(10)]
        ...     async for encoded in aencode_batch(data):
        ...         print(encoded)
    """
    loop = asyncio.get_event_loop()
    
    for value in values:
        # Run each encoding in executor
        encoded = await loop.run_in_executor(None, encode, value, options)
        yield encoded


async def adecode_batch(toon_strings: Iterator[str], options: Optional[DecodeOptions] = None) -> AsyncIterator[JsonValue]:
    """
    Async decode batch of TOON strings.
    
    Yields decoded values as they become available, allowing streaming
    of results without blocking.
    
    Args:
        toon_strings: Iterator of TOON strings
        options: Optional decoding options
        
    Yields:
        Python data structures
        
    Example:
        >>> async def process():
        ...     toons = ['id: 1', 'id: 2', 'id: 3']
        ...     async for decoded in adecode_batch(toons):
        ...         print(decoded)
    """
    loop = asyncio.get_event_loop()
    
    for toon_str in toon_strings:
        # Run each decoding in executor
        decoded = await loop.run_in_executor(None, decode, toon_str, options)
        yield decoded


async def aencode_parallel(values: list[Any], options: Optional[EncodeOptions] = None, max_workers: int = 5) -> list[str]:
    """
    Async encode multiple values in parallel.
    
    This encodes all values concurrently using multiple workers for better
    performance on large batches.
    
    Args:
        values: List of Python values
        options: Optional encoding options
        max_workers: Maximum concurrent encodings
        
    Returns:
        List of TOON strings (in same order as input)
        
    Example:
        >>> async def process():
        ...     data = [{'id': i} for i in range(100)]
        ...     results = await aencode_parallel(data, max_workers=10)
        ...     print(f"Encoded {len(results)} items")
    """
    if not values:
        return []
    
    loop = asyncio.get_event_loop()
    
    # Create semaphore to limit concurrency
    semaphore = asyncio.Semaphore(max_workers)
    
    async def encode_one(value: Any) -> str:
        async with semaphore:
            return await loop.run_in_executor(None, encode, value, options)
    
    # Run all encodings concurrently
    return await asyncio.gather(*[encode_one(value) for value in values])


async def adecode_parallel(toon_strings: list[str], options: Optional[DecodeOptions] = None, max_workers: int = 5) -> list[JsonValue]:
    """
    Async decode multiple TOON strings in parallel.
    
    This decodes all strings concurrently using multiple workers for better
    performance on large batches.
    
    Args:
        toon_strings: List of TOON strings
        options: Optional decoding options
        max_workers: Maximum concurrent decodings
        
    Returns:
        List of Python values (in same order as input)
        
    Example:
        >>> async def process():
        ...     toons = ['id: 1', 'id: 2', 'id: 3'] * 100
        ...     results = await adecode_parallel(toons, max_workers=10)
        ...     print(f"Decoded {len(results)} items")
    """
    if not toon_strings:
        return []
    
    loop = asyncio.get_event_loop()
    
    # Create semaphore to limit concurrency
    semaphore = asyncio.Semaphore(max_workers)
    
    async def decode_one(toon_str: str) -> JsonValue:
        async with semaphore:
            return await loop.run_in_executor(None, decode, toon_str, options)
    
    # Run all decodings concurrently
    return await asyncio.gather(*[decode_one(toon_str) for toon_str in toon_strings])


__all__ = [
    "aencode",
    "adecode",
    "aencode_batch",
    "adecode_batch",
    "aencode_parallel",
    "adecode_parallel",
]

