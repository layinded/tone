"""
Token counting utilities for TONE output.

Helps estimate token usage for LLM contexts.
"""

from typing import Any, Dict, Optional


def estimate_tokens(tone_str: str, method: str = "simple") -> int:
    """
    Estimate token count for TONE string.

    Args:
        tone_str: TONE-formatted string
        method: Estimation method ('simple' or 'tiktoken' if available)

    Returns:
        Estimated token count

    Example:
        >>> tone = encode({'users': [{'id': 1, 'name': 'Alice'}]})
        >>> tokens = estimate_tokens(tone)
        >>> print(f"Estimated tokens: {tokens}")
    """
    if method == "simple":
        return _simple_token_estimate(tone_str)
    elif method == "tiktoken":
        return _tiktoken_estimate(tone_str, model="gpt-4")
    else:
        raise ValueError(f"Unknown method: {method}. Use 'simple' or 'tiktoken'")


def _simple_token_estimate(tone_str: str) -> int:
    """
    Simple token estimation using word count and characters.

    This is a rough approximation. For accurate counts, use 'tiktoken' method.
    """
    # Rough estimate: 4 characters per token
    return len(tone_str) // 4


def _tiktoken_estimate(tone_str: str, model: str = "gpt-4") -> int:
    """
    Accurate token count using tiktoken library.

    Requires: pip install tiktoken

    Args:
        tone_str: TONE-formatted string
        model: Model to use for tokenization

    Returns:
        Accurate token count
    """
    try:
        import tiktoken
    except ImportError:
        raise ImportError(
            "tiktoken is required for accurate token counting. Install with: pip install tiktoken"
        )

    try:
        encoding = tiktoken.encoding_for_model(model)
    except KeyError:
        # Fallback to cl100k_base (GPT-4)
        encoding = tiktoken.get_encoding("cl100k_base")

    return len(encoding.encode(tone_str))


def compare_formats(data: Any, delimiter: str = ",") -> Dict[str, int]:
    """
    Compare token usage across different formats (JSON and TONE).

    Args:
        data: Data to encode and measure
        delimiter: Delimiter to use

    Returns:
        Dictionary with token counts for different formats

    Example:
        >>> data = {'users': [{'id': 1, 'name': 'Alice'}]}
        >>> results = compare_formats(data)
        >>> print(results)
        {'json': 45, 'toon_comma': 25, 'toon_tab': 24, 'toon_pipe': 25}
    """
    import json
    from tone import encode

    results = {}

    # JSON baseline
    json_str = json.dumps(data)
    results["json"] = estimate_tokens(json_str)

    # TOON with different delimiters
    for delim, delim_str in [(",", "comma"), ("\t", "tab"), ("|", "pipe")]:
        toon_str = encode(data, {"delimiter": delim})
        tokens = estimate_tokens(toon_str)
        results[f"toon_{delim_str}"] = tokens

    return results


def optimize_for_tokens(data: Any, target_method: str = "simple") -> Dict[str, Any]:
    """
    Find optimal TONE encoding configuration for token usage.

    Args:
        data: Data to optimize
        target_method: Token estimation method

    Returns:
        Dictionary with optimal configuration and token count

    Example:
        >>> data = {'users': [{'id': 1, 'name': 'Alice'}]}
        >>> optimal = optimize_for_tokens(data)
        >>> print(f"Best: {optimal['best']}, Tokens: {optimal['tokens']}")
    """
    from tone import encode

    best_config = None
    best_tokens = float("inf")

    for delimiter in [",", "\t", "|"]:
        for length_marker in [None, "#"]:
            toon_str = encode(data, {"delimiter": delimiter, "length_marker": length_marker})
            tokens = estimate_tokens(toon_str, target_method)

            if tokens < best_tokens:
                best_tokens = tokens
                best_config = {"delimiter": delimiter, "length_marker": length_marker}

    return {
        "best": best_config,
        "tokens": best_tokens,
        "optimized": encode(data, best_config) if best_config else None,
    }


__all__ = ["estimate_tokens", "compare_formats", "optimize_for_tokens"]

