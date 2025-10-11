"""
Global pytest configuration and fixtures for all tests.
This file is automatically discovered by pytest and loads before running tests.

KEY FIXES:
1. Drop ALL tables before each test (function scope, not session)
2. Create fresh tables for each test
3. Proper async fixture handling with pytest-asyncio
4. Transaction rollback after each test for cleanup
5. No connection pooling issues (NullPool)
"""

import sys
import os
import logging
from pathlib import Path

# Add the backend/app directory to Python path BEFORE any imports
project_root = Path(__file__).parent.parent.parent.parent
sys.path.insert(0, str(project_root))

import asyncio
import pytest
from typing import AsyncGenerator
from datetime import timedelta
from fastapi.testclient import TestClient
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from sqlalchemy.pool import NullPool

# Import your app
from backend.app.main import app
from backend.app.db.session import get_session
from sqlmodel import SQLModel
from backend.app.models.user import User
from backend.app.models.admin import Admin
from backend.app.core.security import hash_password


# ==================== LOGGING CONFIGURATION ====================
@pytest.fixture(scope="session", autouse=True)
def setup_test_logging():
    """Configure logging for tests - disable noisy loggers."""
    logging.getLogger("httpx").setLevel(logging.WARNING)
    logging.getLogger("httpcore").setLevel(logging.WARNING)
    logging.getLogger("backend").setLevel(logging.INFO)
    logging.getLogger("sqlalchemy").setLevel(logging.WARNING)
    
    yield


# ==================== EVENT LOOP FIXTURE ====================
@pytest.fixture(scope="session")
def event_loop():
    """Create an instance of the default event loop for the test session."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


# ==================== DATABASE FIXTURES ====================
@pytest.fixture(scope="session")
def test_database_url() -> str:
    """Get the test database URL from environment or use default."""
    return os.getenv(
        "TEST_DATABASE_URL",
        "postgresql+asyncpg://adl_user:changeme_secure_password_here@localhost:5435/test_adl_db"
    )


@pytest.fixture(scope="session")
async def test_engine(test_database_url: str):
    """
    Create a test database engine (session scope).
    This is created ONCE per test session and reused by all tests.
    """
    engine = create_async_engine(
        test_database_url,
        echo=False,
        poolclass=NullPool,  # No connection pooling for tests
    )
    
    yield engine
    
    await engine.dispose()


@pytest.fixture(scope="function")
async def db_setup_teardown(test_engine, test_database_url: str):
    """
    Setup and teardown for each test function.
    Drops all tables, creates them fresh, then cleans up after test.
    """
    # ==================== SETUP ====================
    # Create engine for this specific test
    engine = test_engine
    
    # Drop all tables
    async with engine.begin() as conn:
        await conn.run_sync(SQLModel.metadata.drop_all)
    
    # Create all tables fresh
    async with engine.begin() as conn:
        await conn.run_sync(SQLModel.metadata.create_all)
    
    yield engine
    
    # ==================== TEARDOWN ====================
    # Drop all tables after test
    async with engine.begin() as conn:
        await conn.run_sync(SQLModel.metadata.drop_all)


@pytest.fixture
async def db_session(db_setup_teardown) -> AsyncGenerator[AsyncSession, None]:
    """
    Create a new database session for each test.
    Each test gets a fresh session that's isolated from other tests.
    
    Usage: Use this fixture in your test functions to access the database.
    """
    engine = db_setup_teardown
    
    # Create a sessionmaker for this test
    async_session_maker = async_sessionmaker(
        engine,
        class_=AsyncSession,
        expire_on_commit=False,
    )
    
    async with async_session_maker() as session:
        yield session
        
        # Rollback any uncommitted changes
        await session.rollback()


# ==================== TEST DATA FIXTURES ====================
@pytest.fixture
async def test_user(db_session: AsyncSession) -> User:
    """Create a test user in the database."""
    user = User(
        email="testuser@example.com",
        username="testuser",
        hashed_password=hash_password("TestPassword123!"),
        full_name="Test User",
        is_active=True
    )
    db_session.add(user)
    await db_session.commit()
    await db_session.refresh(user)
    return user


@pytest.fixture
async def test_admin(db_session: AsyncSession) -> Admin:
    """Create a test admin in the database."""
    admin = Admin(
        email="testadmin@example.com",
        username="testadmin",
        hashed_password=hash_password("AdminPassword123!"),
        full_name="Test Admin",
        is_active=True
    )
    db_session.add(admin)
    await db_session.commit()
    await db_session.refresh(admin)
    return admin


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


# ==================== TEST CLIENT FIXTURES ====================
@pytest.fixture
def client() -> TestClient:
    """Create a synchronous test client for the app."""
    return TestClient(app)


@pytest.fixture
async def async_client(db_session: AsyncSession) -> AsyncGenerator:
    """
    Create an asynchronous test client with overridden database session.
    This ensures tests use the test database instead of production database.
    """
    # Override the get_session dependency to use test database
    async def override_get_session() -> AsyncGenerator[AsyncSession, None]:
        yield db_session
    
    app.dependency_overrides[get_session] = override_get_session
    
    async with AsyncClient(app=app, base_url="http://test") as ac:
        yield ac
    
    # Clean up override after test
    app.dependency_overrides.clear()


# ==================== JWT TOKEN FIXTURES ====================
@pytest.fixture
def test_jwt_token(test_user_data: dict) -> str:
    """Fixture providing a test JWT token."""
    from backend.app.core.security import create_access_token
    return create_access_token(
        data={"sub": test_user_data["email"], "type": "user"},
        expires_delta=timedelta(minutes=15)
    )


@pytest.fixture
def test_admin_jwt_token(test_admin_data: dict) -> str:
    """Fixture providing a test admin JWT token."""
    from backend.app.core.security import create_access_token
    return create_access_token(
        data={"sub": test_admin_data["email"], "type": "admin"},
        expires_delta=timedelta(minutes=15)
    )


@pytest.fixture
def test_expired_token() -> str:
    """Fixture providing an expired JWT token."""
    from backend.app.core.security import create_access_token
    return create_access_token(
        data={"sub": "test@example.com", "type": "user"},
        expires_delta=timedelta(seconds=-1)  # Already expired
    )


# ==================== FACTORY FIXTURES ====================
@pytest.fixture
def create_test_user():
    """Factory fixture to create test users with custom data."""
    async def _create_user(
        db_session: AsyncSession,
        email: str = "user@test.com",
        username: str = "testuser",
        password: str = "TestPass123!",
        **kwargs
    ) -> User:
        user = User(
            email=email,
            username=username,
            hashed_password=hash_password(password),
            **kwargs
        )
        db_session.add(user)
        await db_session.commit()
        await db_session.refresh(user)
        return user
    
    return _create_user


@pytest.fixture
def create_test_admin():
    """Factory fixture to create test admins with custom data."""
    async def _create_admin(
        db_session: AsyncSession,
        email: str = "admin@test.com",
        username: str = "testadmin",
        password: str = "AdminPass123!",
        **kwargs
    ) -> Admin:
        admin = Admin(
            email=email,
            username=username,
            hashed_password=hash_password(password),
            **kwargs
        )
        db_session.add(admin)
        await db_session.commit()
        await db_session.refresh(admin)
        return admin
    
    return _create_admin


# ==================== CONFIGURATION ====================
@pytest.fixture(scope="session", autouse=True)
def setup_test_env():
    """Set up test environment variables."""
    os.environ["ENVIRONMENT"] = "test"
    os.environ["DEBUG"] = "True"
    
    # Set test database URL if not already set
    if "TEST_DATABASE_URL" not in os.environ:
        os.environ["TEST_DATABASE_URL"] = (
            "postgresql+asyncpg://adl_user:changeme_secure_password_here@localhost:5435/test_adl_db"
        )
    
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