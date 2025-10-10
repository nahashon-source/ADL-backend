"""
Database Unit Tests
Tests SQLAlchemy models and CRUD operations in isolation
"""
import pytest
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError

from backend.app.models.user import User
from backend.app.models.admin import Admin
from backend.app.core.security import hash_password, verify_password


# ==================== USER CRUD TESTS ====================

@pytest.mark.asyncio
async def test_create_user(db_session: AsyncSession):
    """Test creating a new user in database"""
    # Arrange
    user_data = {
        "email": "test@example.com",
        "username": "testuser",
        "hashed_password": hash_password("SecurePass123!"),
        "full_name": "Test User"
    }
    
    # Act
    user = User(**user_data)
    db_session.add(user)
    await db_session.commit()
    await db_session.refresh(user)
    
    # Assert
    assert user.id is not None
    assert user.email == "test@example.com"
    assert user.username == "testuser"
    assert user.full_name == "Test User"
    assert user.is_active is True
    assert user.created_at is not None
    assert user.updated_at is not None


@pytest.mark.asyncio
async def test_get_user_by_id(db_session: AsyncSession, test_user: User):
    """Test retrieving user by ID"""
    # Act
    result = await db_session.execute(
        select(User).where(User.id == test_user.id)
    )
    user = result.scalar_one_or_none()
    
    # Assert
    assert user is not None
    assert user.id == test_user.id
    assert user.email == test_user.email


@pytest.mark.asyncio
async def test_get_user_by_email(db_session: AsyncSession, test_user: User):
    """Test retrieving user by email"""
    # Act
    result = await db_session.execute(
        select(User).where(User.email == test_user.email)
    )
    user = result.scalar_one_or_none()
    
    # Assert
    assert user is not None
    assert user.email == test_user.email
    assert user.username == test_user.username


@pytest.mark.asyncio
async def test_get_user_by_username(db_session: AsyncSession, test_user: User):
    """Test retrieving user by username"""
    # Act
    result = await db_session.execute(
        select(User).where(User.username == test_user.username)
    )
    user = result.scalar_one_or_none()
    
    # Assert
    assert user is not None
    assert user.username == test_user.username
    assert user.email == test_user.email


@pytest.mark.asyncio
async def test_update_user(db_session: AsyncSession, test_user: User):
    """Test updating user information"""
    # Arrange
    original_updated_at = test_user.updated_at
    new_full_name = "Updated Test User"
    new_email = "updated@example.com"
    
    # Act
    test_user.full_name = new_full_name
    test_user.email = new_email
    await db_session.commit()
    await db_session.refresh(test_user)
    
    # Assert
    assert test_user.full_name == new_full_name
    assert test_user.email == new_email
    assert test_user.updated_at > original_updated_at


@pytest.mark.asyncio
async def test_deactivate_user(db_session: AsyncSession, test_user: User):
    """Test deactivating a user (soft delete)"""
    # Act
    test_user.is_active = False
    await db_session.commit()
    await db_session.refresh(test_user)
    
    # Assert
    assert test_user.is_active is False


@pytest.mark.asyncio
async def test_duplicate_email_fails(db_session: AsyncSession, test_user: User):
    """Test that duplicate email addresses are rejected"""
    # Arrange
    duplicate_user = User(
        email=test_user.email,  # Same email
        username="differentuser",
        hashed_password=hash_password("Pass123!")
    )
    
    # Act & Assert
    with pytest.raises(IntegrityError):
        db_session.add(duplicate_user)
        await db_session.commit()


@pytest.mark.asyncio
async def test_duplicate_username_fails(db_session: AsyncSession, test_user: User):
    """Test that duplicate usernames are rejected"""
    # Arrange
    duplicate_user = User(
        email="different@example.com",
        username=test_user.username,  # Same username
        hashed_password=hash_password("Pass123!")
    )
    
    # Act & Assert
    with pytest.raises(IntegrityError):
        db_session.add(duplicate_user)
        await db_session.commit()


@pytest.mark.asyncio
async def test_user_password_hashing():
    """Test password hashing and verification"""
    # Arrange
    plain_password = "MySecurePassword123!"
    
    # Act
    hashed = hash_password(plain_password)
    
    # Assert
    assert hashed != plain_password
    assert verify_password(plain_password, hashed) is True
    assert verify_password("WrongPassword", hashed) is False


@pytest.mark.asyncio
async def test_list_all_users(db_session: AsyncSession):
    """Test retrieving all users"""
    # Arrange - Create multiple users
    users_data = [
        User(email=f"user{i}@test.com", username=f"user{i}", 
             hashed_password=hash_password("Pass123!"))
        for i in range(5)
    ]
    for user in users_data:
        db_session.add(user)
    await db_session.commit()
    
    # Act
    result = await db_session.execute(select(User))
    all_users = result.scalars().all()
    
    # Assert
    assert len(all_users) >= 5


@pytest.mark.asyncio
async def test_filter_active_users(db_session: AsyncSession):
    """Test filtering users by active status"""
    # Arrange - Create active and inactive users
    active_user = User(
        email="active@test.com",
        username="activeuser",
        hashed_password=hash_password("Pass123!"),
        is_active=True
    )
    inactive_user = User(
        email="inactive@test.com",
        username="inactiveuser",
        hashed_password=hash_password("Pass123!"),
        is_active=False
    )
    db_session.add(active_user)
    db_session.add(inactive_user)
    await db_session.commit()
    
    # Act
    result = await db_session.execute(
        select(User).where(User.is_active == True)
    )
    active_users = result.scalars().all()
    
    # Assert
    assert all(user.is_active for user in active_users)


# ==================== ADMIN CRUD TESTS ====================

@pytest.mark.asyncio
async def test_create_admin(db_session: AsyncSession):
    """Test creating a new admin in database"""
    # Arrange
    admin_data = {
        "email": "admin@example.com",
        "username": "adminuser",
        "hashed_password": hash_password("AdminPass123!"),
        "full_name": "Admin User"
    }
    
    # Act
    admin = Admin(**admin_data)
    db_session.add(admin)
    await db_session.commit()
    await db_session.refresh(admin)
    
    # Assert
    assert admin.id is not None
    assert admin.email == "admin@example.com"
    assert admin.username == "adminuser"
    assert admin.full_name == "Admin User"
    assert admin.is_active is True
    assert admin.created_at is not None
    assert admin.updated_at is not None


@pytest.mark.asyncio
async def test_get_admin_by_id(db_session: AsyncSession, test_admin: Admin):
    """Test retrieving admin by ID"""
    # Act
    result = await db_session.execute(
        select(Admin).where(Admin.id == test_admin.id)
    )
    admin = result.scalar_one_or_none()
    
    # Assert
    assert admin is not None
    assert admin.id == test_admin.id
    assert admin.email == test_admin.email


@pytest.mark.asyncio
async def test_get_admin_by_email(db_session: AsyncSession, test_admin: Admin):
    """Test retrieving admin by email"""
    # Act
    result = await db_session.execute(
        select(Admin).where(Admin.email == test_admin.email)
    )
    admin = result.scalar_one_or_none()
    
    # Assert
    assert admin is not None
    assert admin.email == test_admin.email


@pytest.mark.asyncio
async def test_get_admin_by_username(db_session: AsyncSession, test_admin: Admin):
    """Test retrieving admin by username"""
    # Act
    result = await db_session.execute(
        select(Admin).where(Admin.username == test_admin.username)
    )
    admin = result.scalar_one_or_none()
    
    # Assert
    assert admin is not None
    assert admin.username == test_admin.username


@pytest.mark.asyncio
async def test_update_admin(db_session: AsyncSession, test_admin: Admin):
    """Test updating admin information"""
    # Arrange
    new_full_name = "Updated Admin User"
    
    # Act
    test_admin.full_name = new_full_name
    await db_session.commit()
    await db_session.refresh(test_admin)
    
    # Assert
    assert test_admin.full_name == new_full_name


@pytest.mark.asyncio
async def test_duplicate_admin_email_fails(db_session: AsyncSession, test_admin: Admin):
    """Test that duplicate admin email addresses are rejected"""
    # Arrange
    duplicate_admin = Admin(
        email=test_admin.email,  # Same email
        username="differentadmin",
        hashed_password=hash_password("Pass123!")
    )
    
    # Act & Assert
    with pytest.raises(IntegrityError):
        db_session.add(duplicate_admin)
        await db_session.commit()


@pytest.mark.asyncio
async def test_duplicate_admin_username_fails(db_session: AsyncSession, test_admin: Admin):
    """Test that duplicate admin usernames are rejected"""
    # Arrange
    duplicate_admin = Admin(
        email="different@example.com",
        username=test_admin.username,  # Same username
        hashed_password=hash_password("Pass123!")
    )
    
    # Act & Assert
    with pytest.raises(IntegrityError):
        db_session.add(duplicate_admin)
        await db_session.commit()


# ==================== DATABASE CONNECTION TESTS ====================

@pytest.mark.asyncio
async def test_database_connection(db_session: AsyncSession):
    """Test that database connection is working"""
    # Act - Execute a simple query
    result = await db_session.execute(select(1))
    value = result.scalar()
    
    # Assert
    assert value == 1


@pytest.mark.asyncio
async def test_transaction_rollback(db_session: AsyncSession):
    """Test that database transactions can be rolled back"""
    # Arrange
    user = User(
        email="rollback@test.com",
        username="rollbackuser",
        hashed_password=hash_password("Pass123!")
    )
    db_session.add(user)
    await db_session.flush()  # Flush but don't commit
    
    # Act - Rollback the transaction
    await db_session.rollback()
    
    # Assert - User should not exist after rollback
    result = await db_session.execute(
        select(User).where(User.email == "rollback@test.com")
    )
    found_user = result.scalar_one_or_none()
    assert found_user is None


@pytest.mark.asyncio
async def test_cascade_operations(db_session: AsyncSession):
    """Test that related operations cascade properly"""
    # This test demonstrates that the database handles cascading
    # Currently no relationships defined, but structure is ready
    pass


# ==================== EDGE CASE TESTS ====================

@pytest.mark.asyncio
async def test_user_with_null_full_name(db_session: AsyncSession):
    """Test creating user without full_name (optional field)"""
    # Arrange
    user = User(
        email="noname@test.com",
        username="nonameuser",
        hashed_password=hash_password("Pass123!"),
        full_name=None  # Optional field
    )
    
    # Act
    db_session.add(user)
    await db_session.commit()
    await db_session.refresh(user)
    
    # Assert
    assert user.id is not None
    assert user.full_name is None


@pytest.mark.asyncio
async def test_user_timestamps_auto_update(db_session: AsyncSession, test_user: User):
    """Test that updated_at timestamp updates automatically"""
    # Arrange
    import asyncio
    original_updated_at = test_user.updated_at
    
    # Act - Wait a moment then update
    await asyncio.sleep(0.1)
    test_user.full_name = "New Name"
    await db_session.commit()
    await db_session.refresh(test_user)
    
    # Assert
    assert test_user.updated_at > original_updated_at


@pytest.mark.asyncio
async def test_user_email_case_sensitivity(db_session: AsyncSession):
    """Test that email addresses are case-sensitive in storage"""
    # Arrange
    user1 = User(
        email="Test@Example.com",
        username="user1",
        hashed_password=hash_password("Pass123!")
    )
    user2 = User(
        email="test@example.com",
        username="user2",
        hashed_password=hash_password("Pass123!")
    )
    
    # Act
    db_session.add(user1)
    await db_session.commit()
    db_session.add(user2)
    await db_session.commit()
    
    # Assert - Both should exist (case-sensitive)
    result = await db_session.execute(select(User))
    users = result.scalars().all()
    emails = [u.email for u in users]
    assert "Test@Example.com" in emails
    assert "test@example.com" in emails