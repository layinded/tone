"""Command-line interface for TONE."""

import json
import sys
from pathlib import Path
from typing import Dict, Optional

try:
    import click
    from rich.console import Console
except ImportError:
    click = None
    Console = None

from tone import DEFAULT_DELIMITER, DELIMITERS, decode, encode
from tone.types import DecodeOptions, Delimiter, EncodeOptions


def main() -> None:
    """Main CLI entry point."""
    if click is None:
        print("Error: CLI dependencies not installed. Run: pip install 'tone[cli]'", file=sys.stderr)
        sys.exit(1)
    
    cli()


@click.command()
@click.argument("input_file", type=click.Path(exists=True, path_type=Path), required=True)
@click.option(
    "-o",
    "--output",
    "output_file",
    type=click.Path(path_type=Path),
    help="Output file path (default: stdout)",
)
@click.option(
    "-e",
    "--encode",
    "encode_flag",
    is_flag=True,
    default=False,
    help="Encode JSON to TONE (auto-detected by default)",
)
@click.option(
    "-d",
    "--decode",
    "decode_flag",
    is_flag=True,
    default=False,
    help="Decode TONE to JSON (auto-detected by default)",
)
@click.option(
    "--delimiter",
    type=click.Choice(["comma", "tab", "pipe", ",", "\t", "|"]),
    default=",",
    help="Delimiter for arrays: comma, tab, or pipe",
)
@click.option(
    "--indent",
    type=int,
    default=2,
    help="Indentation size",
)
@click.option(
    "--length-marker",
    is_flag=True,
    default=False,
    help="Use length marker (#) for arrays",
)
@click.option(
    "--strict/--no-strict",
    default=True,
    help="Enable strict mode for decoding",
)
@click.version_option(version="1.0.0")
def cli(
    input_file: Path,
    output_file: Optional[Path],
    encode_flag: bool,
    decode_flag: bool,
    delimiter: str,
    indent: int,
    length_marker: bool,
    strict: bool,
) -> None:
    """TONE CLI — Convert between JSON and TONE formats."""
    console = Console()
    
    # Parse delimiter
    delimiter_map: Dict[str, Delimiter] = {
        "comma": DELIMITERS["comma"],
        "tab": DELIMITERS["tab"],
        "pipe": DELIMITERS["pipe"],
        ",": DELIMITERS["comma"],
        "\t": DELIMITERS["tab"],
        "|": DELIMITERS["pipe"],
    }
    parsed_delimiter = delimiter_map[delimiter]
    
    # Validate indent
    if indent < 0:
        console.print("[red]Error:[/] Indent must be non-negative", err=True)
        sys.exit(1)
    
    # Detect mode
    mode = detect_mode(input_file, encode_flag, decode_flag)
    
    try:
        if mode == "encode":
            encode_to_toon(
                console,
                input_file=input_file,
                output_file=output_file,
                delimiter=parsed_delimiter,
                indent=indent,
                length_marker="#" if length_marker else None,
            )
        else:
            decode_to_json(
                console,
                input_file=input_file,
                output_file=output_file,
                indent=indent,
                strict=strict,
            )
    except Exception as e:
        console.print(f"[red]Error:[/] {e}", err=True)
        sys.exit(1)


def detect_mode(input_file: Path, encode_flag: bool, decode_flag: bool) -> str:
    """Detect conversion mode.
    
    Args:
        input_file: Input file path
        encode_flag: Encode flag provided
        decode_flag: Decode flag provided
        
    Returns:
        'encode' or 'decode'
    """
    # Explicit flags take precedence
    if encode_flag:
        return "encode"
    if decode_flag:
        return "decode"
    
    # Auto-detect based on file extension
    if input_file.suffix == ".json":
        return "encode"
    if input_file.suffix in (".tone", ".toon"):  # Support both extensions for backwards compatibility
        return "decode"
    
    # Default to encode
    return "encode"


def encode_to_toon(
    console: "Console",
    input_file: Path,
    output_file: Optional[Path],
    delimiter: Delimiter,
    indent: int,
    length_marker: Optional[str],
) -> None:
    """Encode JSON to TONE format.
    
    Args:
        console: Rich console for output
        input_file: Input JSON file
        output_file: Output TONE file (optional)
        delimiter: Delimiter to use
        indent: Indentation size
        length_marker: Length marker to use
    """
    # Read JSON input
    json_content = input_file.read_text(encoding="utf-8")
    
    try:
        data = json.loads(json_content)
    except json.JSONDecodeError as e:
        raise ValueError(f"Failed to parse JSON: {e}")
    
    # Encode options
    encode_options: EncodeOptions = {
        "delimiter": delimiter,
        "indent": indent,
        "length_marker": length_marker,
    }
    
    # Encode to TONE
    tone_output = encode(data, encode_options)
    
    # Write output
    if output_file:
        output_file.write_text(tone_output, encoding="utf-8")
        console.print(
            f"[green]✓[/] Encoded [cyan]{input_file}[/] → [cyan]{output_file}[/]"
        )
    else:
        print(tone_output)


def decode_to_json(
    console: "Console",
    input_file: Path,
    output_file: Optional[Path],
    indent: int,
    strict: bool,
) -> None:
    """Decode TONE to JSON format.
    
    Args:
        console: Rich console for output
        input_file: Input TONE file
        output_file: Output JSON file (optional)
        indent: Indentation size for JSON output
        strict: Enable strict mode
    """
    # Read TONE input
    tone_content = input_file.read_text(encoding="utf-8")
    
    try:
        decode_options: DecodeOptions = {
            "indent": indent,
            "strict": strict,
        }
        data = decode(tone_content, decode_options)
    except Exception as e:
        raise ValueError(f"Failed to decode TONE: {e}")
    
    # Convert to JSON
    json_output = json.dumps(data, indent=indent)
    
    # Write output
    if output_file:
        output_file.write_text(json_output, encoding="utf-8")
        console.print(
            f"[green]✓[/] Decoded [cyan]{input_file}[/] → [cyan]{output_file}[/]"
        )
    else:
        print(json_output)


if __name__ == "__main__":
    main()

