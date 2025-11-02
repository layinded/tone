"""
Context managers for TONE file operations.

Provides Pythonic file handling for encoding/decoding TONE files.
"""

from pathlib import Path
from typing import Any, BinaryIO, Optional, TextIO, Union

from tone._core import decode, encode
from tone.types import DecodeOptions, EncodeOptions, JsonValue


class TONEEncoder:
    """
    Context manager for encoding Python data to TONE files.
    
    Usage:
        with TONEEncoder('output.toon') as enc:
            enc.encode(my_data)
        
        # With options
        with TONEEncoder('output.toon', indent=4, delimiter='\t') as enc:
            enc.encode(my_data)
    """

    def __init__(
        self,
        file_path: Union[str, Path],
        options: Optional[EncodeOptions] = None,
    ) -> None:
        """Initialize TONE encoder.

        Args:
            file_path: Path to output TONE file
            options: Encoding options (indent, delimiter, length_marker)
        """
        self.file_path = Path(file_path)
        self.options = options
        self.file: Optional[TextIO] = None

    def __enter__(self) -> "TONEEncoder":
        """Enter context manager."""
        self.file = self.file_path.open("w", encoding="utf-8")
        return self

    def __exit__(self, exc_type: Any, exc_val: Any, exc_tb: Any) -> None:
        """Exit context manager."""
        if self.file:
            self.file.close()

    def encode(self, value: Any) -> None:
        """
        Encode and write value to file.
        
        Args:
            value: Python value to encode
        """
        if not self.file:
            raise RuntimeError("Encoder must be used as context manager")

        toon_str = encode(value, self.options)
        self.file.write(toon_str)

    def write(self, toon_str: str) -> None:
        """
        Write raw TONE string to file.
        
        Args:
            toon_str: Raw TONE string
        """
        if not self.file:
            raise RuntimeError("Encoder must be used as context manager")

        self.file.write(toon_str)


class TONEDecoder:
    """
    Context manager for decoding TONE files to Python data.
    
    Usage:
        with TONEDecoder('input.toon') as dec:
            data = dec.decode()
        
        # With options
        with TONEDecoder('input.toon', strict=True) as dec:
            data = dec.decode()
    """

    def __init__(
        self,
        file_path: Union[str, Path],
        options: Optional[DecodeOptions] = None,
    ) -> None:
        """Initialize TONE decoder.

        Args:
            file_path: Path to input TONE file
            options: Decoding options (indent, strict)
        """
        self.file_path = Path(file_path)
        self.options = options
        self.file: Optional[TextIO] = None

    def __enter__(self) -> "TONEDecoder":
        """Enter context manager."""
        self.file = self.file_path.open("r", encoding="utf-8")
        return self

    def __exit__(self, exc_type: Any, exc_val: Any, exc_tb: Any) -> None:
        """Exit context manager."""
        if self.file:
            self.file.close()

    def decode(self) -> JsonValue:
        """
        Read and decode file content.
        
        Returns:
            Python data structure
        """
        if not self.file:
            raise RuntimeError("Decoder must be used as context manager")

        toon_str = self.file.read()
        return decode(toon_str, self.options)

    def read(self) -> str:
        """
        Read raw TONE string from file.
        
        Returns:
            Raw TONE string
        """
        if not self.file:
            raise RuntimeError("Decoder must be used as context manager")

        return self.file.read()


__all__ = ["TONEEncoder", "TONEDecoder"]

