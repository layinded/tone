"""
Pydantic integration for TONE format.

Provides helpers for encoding/decoding Pydantic models to/from TONE.
"""

from typing import Any, List, Type, TypeVar, Union

try:
    from pydantic import BaseModel
    
    T = TypeVar("T", bound=BaseModel)
except ImportError:
    BaseModel = None
    T = TypeVar("T", bound=Any)  # Fallback when Pydantic not available


def encode_model(model: Union[BaseModel, List[BaseModel]], **options) -> str:
    """
    Encode Pydantic model(s) to TONE format.
    
    Args:
        model: Pydantic model instance or list of models
        **options: Encoding options (indent, delimiter, length_marker)
        
    Returns:
        TONE-formatted string
        
    Example:
        >>> from tone.integrations import encode_model
        >>> from pydantic import BaseModel
        >>> 
        >>> class User(BaseModel):
        ...     id: int
        ...     name: str
        ...
        >>> user = User(id=1, name='Alice')
        >>> tone = encode_model(user)
    """
    if BaseModel is None:
        raise ImportError("Pydantic not installed. Install with: pip install pydantic")

    from tone import encode

    # Convert Pydantic model to dict
    if isinstance(model, BaseModel):
        data = model.model_dump() if hasattr(model, "model_dump") else model.dict()
    elif isinstance(model, list):
        data = [m.model_dump() if hasattr(m, "model_dump") else m.dict() for m in model]
    else:
        raise TypeError(f"Expected Pydantic model or list of models, got {type(model)}")

    return encode(data, options)


def decode_model(tone_str: str, model: Type[T], **options) -> Union[T, List[T]]:
    """
    Decode TONE string to Pydantic model(s).
    
    Args:
        tone_str: TONE-formatted string
        model: Pydantic model class
        **options: Decoding options (indent, strict)
        
    Returns:
        Pydantic model instance or list of models
        
    Example:
        >>> tone = 'id: 1\nname: Alice'
        >>> user = decode_model(tone, User)
        >>> assert isinstance(user, User)
        >>> assert user.name == 'Alice'
    """
    if BaseModel is None:
        raise ImportError("Pydantic not installed. Install with: pip install pydantic")

    from tone import decode

    # Decode to Python dict
    data = decode(tone_str, options)

    # Convert to Pydantic model(s)
    if isinstance(data, dict):
        return model(**data)
    elif isinstance(data, list):
        return [model(**item) if isinstance(item, dict) else item for item in data]
    else:
        raise TypeError(f"Cannot convert {type(data)} to Pydantic model")


__all__ = ["encode_model", "decode_model"]

