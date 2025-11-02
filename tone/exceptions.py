"""
Enhanced exceptions for TONE with rich context and suggestions.

Provides detailed error messages with actionable guidance for developers.
"""

from typing import Any, Dict, List, Optional, Tuple


class TONEError(Exception):
    """Base exception for TONE-related errors."""

    def __init__(
        self,
        message: str,
        context: Optional[Dict[str, Any]] = None,
        suggestions: Optional[List[str]] = None,
    ) -> None:
        """Initialize TONE error with rich context.

        Args:
            message: Primary error message
            context: Additional context (line number, position, etc.)
            suggestions: Optional suggestions for fixing the error
        """
        super().__init__(message)
        self.message = message
        self.context = context or {}
        self.suggestions = suggestions or []

    def __str__(self) -> str:
        """Format error with context and suggestions."""
        parts = [self.message]

        if self.context:
            context_parts = [f"  {k}: {v}" for k, v in self.context.items()]
            parts.append("\nContext:")
            parts.extend(context_parts)

        if self.suggestions:
            parts.append("\nSuggestions:")
            for i, suggestion in enumerate(self.suggestions, 1):
                parts.append(f"  {i}. {suggestion}")

        return "\n".join(parts)


class TONEEncodeError(TONEError):
    """Error during encoding."""

    def __init__(
        self,
        message: str,
        value: Any = None,
        context: Optional[Dict[str, Any]] = None,
        suggestions: Optional[List[str]] = None,
    ) -> None:
        """Initialize encoding error."""
        if value is not None:
            if context is None:
                context = {}
            context["value_type"] = type(value).__name__
            if hasattr(value, "__len__"):
                try:
                    context["value_size"] = len(value)
                except (TypeError, ValueError):
                    pass

        super().__init__(message, context, suggestions)


class TONEDecodeError(TONEError):
    """Error during decoding."""

    def __init__(
        self,
        message: str,
        line_number: Optional[int] = None,
        position: Optional[int] = None,
        content: Optional[str] = None,
        context: Optional[Dict[str, Any]] = None,
        suggestions: Optional[List[str]] = None,
    ) -> None:
        """Initialize decoding error."""
        if context is None:
            context = {}

        if line_number is not None:
            context["line_number"] = line_number

        if position is not None:
            context["position"] = position

        if content is not None:
            context["content"] = content[:100]  # Limit length

        super().__init__(message, context, suggestions)


class TONESyntaxError(TONEDecodeError):
    """Syntax error in TONE format."""

    def __init__(
        self,
        message: str,
        line_number: Optional[int] = None,
        position: Optional[int] = None,
        content: Optional[str] = None,
        context: Optional[Dict[str, Any]] = None,
        suggestions: Optional[List[str]] = None,
    ) -> None:
        """Initialize syntax error.

        Common suggestions added automatically based on error type.
        """
        # Auto-add common suggestions
        if suggestions is None:
            suggestions = []

        if "indentation" in message.lower() or "Indentation" in message:
            suggestions.extend([
                "Check your indentation (use spaces, not tabs)",
                "Ensure consistent indentation throughout",
                "Use '--no-strict' to be more permissive",
            ])
        elif "delimiter" in message.lower() or "Delimiter" in message:
            suggestions.extend([
                "Check that delimiters match the header",
                "Ensure no unquoted delimiters in string values",
                "Use quotes around values containing delimiters",
            ])
        elif "length" in message.lower() or "Length" in message:
            suggestions.extend([
                "Verify the actual count of items",
                "Check for extra or missing items",
                "Use exact count as specified in header",
            ])
        elif "quote" in message.lower() or "Quote" in message:
            suggestions.extend([
                "Check for unmatched quotes",
                "Escape quotes with backslash if needed",
                "Ensure proper quote placement",
            ])

        super().__init__(message, line_number, position, content, context, suggestions)


class TONEValidationError(TONEError):
    """Validation error (strict mode, etc.)."""

    def __init__(
        self,
        message: str,
        context: Optional[Dict[str, Any]] = None,
        suggestions: Optional[List[str]] = None,
    ) -> None:
        """Initialize validation error."""
        # Auto-add suggestion to disable strict mode
        if suggestions is None:
            suggestions = []

        if "strict" in message.lower() or "Strict" in message:
            suggestions.append("Use 'strict=False' to disable strict validation")

        super().__init__(message, context, suggestions)


class TONENormalizationError(TONEEncodeError):
    """Error during value normalization."""

    def __init__(
        self,
        value: Any,
        context: Optional[Dict[str, Any]] = None,
    ) -> None:
        """Initialize normalization error."""
        value_type = type(value).__name__
        message = f"Cannot normalize value of type: {value_type}"

        suggestions = [
            "Convert to JSON-compatible types (dict, list, str, int, float, bool, None)",
            "Implement custom serialization for your type",
            "Use to_dict() method if available",
        ]

        super().__init__(message, value=value, context=context, suggestions=suggestions)


class TONETypeError(TONEError):
    """Type-related error."""

    def __init__(
        self,
        message: str,
        expected_type: str,
        actual_type: str,
        context: Optional[Dict[str, Any]] = None,
        suggestions: Optional[List[str]] = None,
    ) -> None:
        """Initialize type error."""
        full_message = f"{message} (expected: {expected_type}, got: {actual_type})"

        if suggestions is None:
            suggestions = []

        suggestions.append(f"Ensure value is of type: {expected_type}")

        if context is None:
            context = {}

        context["expected_type"] = expected_type
        context["actual_type"] = actual_type

        super().__init__(full_message, context, suggestions)


class TONEValueError(TONEError):
    """Value-related error."""

    def __init__(
        self,
        message: str,
        invalid_value: Any = None,
        context: Optional[Dict[str, Any]] = None,
        suggestions: Optional[List[str]] = None,
    ) -> None:
        """Initialize value error."""
        if invalid_value is not None and context is None:
            context = {"invalid_value": str(invalid_value)[:100]}

        super().__init__(message, context, suggestions)


__all__ = [
    "TONEError",
    "TONEEncodeError",
    "TONEDecodeError",
    "TONESyntaxError",
    "TONEValidationError",
    "TONENormalizationError",
    "TONETypeError",
    "TONEValueError",
]

