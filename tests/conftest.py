"""Pytest configuration and shared fixtures."""

import pytest


@pytest.fixture
def sample_data():
    """Sample data for testing."""
    return {
        "users": [
            {"id": 1, "name": "Alice", "role": "admin"},
            {"id": 2, "name": "Bob", "role": "user"},
        ]
    }

