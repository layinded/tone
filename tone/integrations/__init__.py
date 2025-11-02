"""
Integration modules for TONE.

Provides integrations with popular Python frameworks and libraries:
- FastAPI: Web API response formatting
- Pydantic: Type-safe model serialization
- Pandas: DataFrame support
- Format converters: JSON, YAML, CSV
"""

__all__ = []

# Optional FastAPI integration
try:
    from tone.integrations.fastapi import TONEResponse
    __all__.append("TONEResponse")
except ImportError:
    pass

# Optional Pandas integration
try:
    from tone.integrations.pandas import from_toon, to_toon
    __all__.extend(["to_toon", "from_toon"])
except ImportError:
    pass

# Optional Pydantic integration
try:
    from tone.integrations.pydantic import decode_model, encode_model
    __all__.extend(["encode_model", "decode_model"])
except ImportError:
    pass

# Optional converters
try:
    from tone.integrations.converters import (
        from_csv,
        from_json,
        from_yaml,
        to_csv,
        to_json,
        to_yaml,
    )
    __all__.extend(["to_json", "from_json", "to_yaml", "from_yaml", "to_csv", "from_csv"])
except ImportError:
    pass
