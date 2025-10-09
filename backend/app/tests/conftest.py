"""
Global pytest configuration and fixtures for all tests.
This file is automatically discovered by pytest and loads before running tests.
"""

import sys
import os
import logging
from pathlib import Path

# Add the backend/app directory to Python path BEFORE any imports
project_root = Path(__file__).parent.parent.parent.parent  # Goes up to ~/Desktop/ADL-backend
sys.path.insert(0, str(project_root))

import asyncio
import pytest
from typing import AsyncGenerator
from datetime import timedelta
from fastapi.testclient import TestClient
from httpx import AsyncClient

# Import your app
from backend.app.main import app


# ==================== LOGGING CONFIGURATION ====================
@pytest.fixture(scope="session", autouse=True)
def setup_test_logging():
    """Configure logging for tests - disable noisy loggers."""
    # Disable httpx logging to avoid format errors
    logging.getLogger("httpx").setLevel(logging.WARNING)
    logging.getLogger("httpcore").setLevel(logging.WARNING)
    
    # Keep our app logging at INFO level
    logging.getLogger("backend").setLevel(logging.INFO)
    
    yield


# ==================== EVENT LOOP FIXTURE ====================
@pytest.fixture(scope="session")
def event_loop():
    """Create an instance of the default event loop for the test session."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


# ==================== TEST CLIENT FIXTURES ====================
@pytest.fixture
def client() -> TestClient:
    """Create a synchronous test client for the app."""
    return TestClient(app)


@pytest.fixture
async def async_client() -> AsyncGenerator:
    """Create an asynchronous test client for the app."""
    async with AsyncClient(app=app, base_url="http://test") as ac:
        yield ac


# ==================== TEST DATA FIXTURES ====================
@pytest.fixture
def test_user_data() -> dict:
    """Fixture providing test user data."""
    return {
        "username": "testuser",
        "email": "testuser@example.com",
        "password": "TestPassword123!",
        "full_name": "Test User"
    }


@pytest.fixture
def test_admin_data() -> dict:
    """Fixture providing test admin data."""
    return {
        "username": "testadmin",
        "email": "testadmin@example.com",
        "password": "AdminPassword123!",
        "full_name": "Test Admin"
    }


@pytest.fixture
def test_invalid_user() -> dict:
    """Fixture providing invalid user data."""
    return {
        "username": "a",  # Too short
        "email": "invalid-email",  # Invalid email
        "password": "123"  # Too weak
    }


# ==================== JWT TOKEN FIXTURES ====================
@pytest.fixture
def test_jwt_token(test_user_data: dict) -> str:
    """Fixture providing a test JWT token."""
    from backend.app.core.security import create_access_token
    return create_access_token(
        data={"sub": test_user_data["email"]},
        expires_delta=timedelta(minutes=15)
    )


@pytest.fixture
def test_admin_jwt_token(test_admin_data: dict) -> str:
    """Fixture providing a test admin JWT token."""
    from backend.app.core.security import create_access_token
    return create_access_token(
        data={"sub": test_admin_data["email"]},
        expires_delta=timedelta(minutes=15)
    )


# ==================== CONFIGURATION ====================
@pytest.fixture(scope="session", autouse=True)
def setup_test_env():
    """Set up test environment variables."""
    os.environ["ENVIRONMENT"] = "test"
    os.environ["DEBUG"] = "True"
    yield


# ==================== MARKERS ====================
def pytest_configure(config):
    """Register custom markers."""
    config.addinivalue_line(
        "markers", "unit: mark test as a unit test"
    )
    config.addinivalue_line(
        "markers", "integration: mark test as an integration test"
    )
    config.addinivalue_line(
        "markers", "async: mark test as async"
    )
    config.addinivalue_line(
        "markers", "slow: mark test as slow running"
    )
