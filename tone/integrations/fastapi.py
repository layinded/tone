"""
FastAPI integration for TONE format.

Provides a TONEResponse class for FastAPI applications to return
token-efficient TONE format instead of JSON for LLM-friendly APIs.
"""

from typing import Any

try:
    from fastapi.responses import Response

    class TONEResponse(Response):
        """
        FastAPI response class that returns TONE format.
        
        Usage:
            from fastapi import FastAPI
            from tone.integrations import TONEResponse
            
            app = FastAPI()
            
            @app.get("/users", response_class=TONEResponse)
            async def get_users():
                return [{'id': 1, 'name': 'Alice'}]
        
        Benefits:
            - Token-efficient responses
            - LLM-optimized output
            - Web API integration
        """

        media_type = "text/plain; charset=utf-8"

        def __init__(self, content: Any = None, **kwargs) -> None:
            """Initialize TONE response."""
            from tone import encode

            if content is not None:
                tone_content = encode(content)
                super().__init__(content=tone_content, **kwargs)
            else:
                super().__init__(**kwargs)

        def render(self, content: Any) -> bytes:
            """Render content as TONE format."""
            from tone import encode

            tone_str = encode(content)
            return tone_str.encode("utf-8")

except ImportError:
    # FastAPI not installed, create placeholder that raises error on use
    class TONEResponse:  # type: ignore
        """Placeholder for TONEResponse when FastAPI is not installed."""

        def __init__(self, *args, **kwargs):
            raise ImportError("FastAPI not installed. Install with: pip install fastapi")


__all__ = ["TONEResponse"]

