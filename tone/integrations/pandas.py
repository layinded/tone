"""
Pandas integration for TONE format.

Provides direct support for pandas DataFrames to/from TONE,
leveraging TONE's efficient tabular array format.
"""

try:
    import pandas as pd
except ImportError:
    pd = None

from typing import Optional


def to_toon(df, options: Optional[dict] = None) -> str:
    """
    Convert pandas DataFrame to TONE format.
    
    Takes advantage of TONE's tabular format for optimal token efficiency.
    
    Args:
        df: pandas DataFrame
        options: Optional encoding options
        
    Returns:
        TONE-formatted string
        
    Example:
        >>> import pandas as pd
        >>> from tone.integrations import to_toon
        >>>
        >>> df = pd.DataFrame({
        ...     'id': [1, 2, 3],
        ...     'name': ['Alice', 'Bob', 'Charlie']
        ... })
        >>> tone_str = to_toon(df)
    """
    if pd is None:
        raise ImportError("Pandas not installed. Install with: pip install pandas")

    from tone import encode

    # Convert DataFrame to dict
    data = df.to_dict("records")

    # Convert options if provided
    if options is None:
        options = {}

    return encode(data, options)


def from_toon(tone_str: str, options: Optional[dict] = None) -> "pd.DataFrame":
    """
    Convert TONE format to pandas DataFrame.
    
    Args:
        tone_str: TONE-formatted string
        options: Optional decoding options
        
    Returns:
        pandas DataFrame
        
    Example:
        >>> tone_str = 'users[2]{id,name}:\n  1,Alice\n  2,Bob'
        >>> df = from_toon(tone_str)
        >>> print(df)
           id   name
        0   1  Alice
        1   2    Bob
    """
    if pd is None:
        raise ImportError("Pandas not installed. Install with: pip install pandas")

    from tone import decode

    # Convert options if provided
    if options is None:
        options = {}

    # Decode to list of dicts
    data = decode(tone_str, options)

    # Handle root array vs object with array
    if isinstance(data, list):
        records = data
    elif isinstance(data, dict):
        # Try to find first array in the dict
        records = None
        for key, value in data.items():
            if isinstance(value, list):
                records = value
                break
        if records is None:
            # Wrap single object in list
            records = [data]
    else:
        raise ValueError(f"Cannot convert {type(data)} to DataFrame")

    # Create DataFrame
    if len(records) > 0:
        df = pd.DataFrame(records)
    else:
        df = pd.DataFrame()

    return df


__all__ = ["to_toon", "from_toon"]

