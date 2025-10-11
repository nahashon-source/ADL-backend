"""
Integration Tests - Complete User Flows
Tests end-to-end user journeys through multiple endpoints
"""
import pytest
from httpx import AsyncClient
from fastapi import status
from datetime import timedelta

from backend.app.core.security import create_access_token


# ==================== USER REGISTRATION & LOGIN FLOW ====================

@pytest.mark.asyncio
@pytest.mark.integration
async def test_complete_user_registration_and_login_flow(async_client: AsyncClient):
    """Test complete user journey: register → login → access protected endpoint"""
    # Step 1: Register new user
    registration_data = {
        "email": "newuser@example.com",
        "username": "newuser",
        "password": "SecurePass123!",
        "full_name": "New User"
    }
    
    register_response = await async_client.post(
        "/api/users/register",
        json=registration_data
    )
    assert register_response.status_code == status.HTTP_201_CREATED
    register_data = register_response.json()
    assert register_data["email"] == registration_data["email"]
    assert register_data["username"] == registration_data["username"]
    assert register_data["full_name"] == registration_data["full_name"]
    assert "id" in register_data
    
    # Step 2: Login with registered credentials
    login_data = {
        "username": registration_data["username"],
        "password": registration_data["password"]
    }
    
    login_response = await async_client.post(
        "/api/users/login",
        json=login_data
    )
    assert login_response.status_code == status.HTTP_200_OK
    login_result = login_response.json()
    assert "access_token" in login_result
    assert "refresh_token" in login_result
    assert login_result["token_type"] == "bearer"
    
    access_token = login_result["access_token"]
    
    # Step 3: Access protected endpoint with token
    headers = {"Authorization": f"Bearer {access_token}"}
    me_response = await async_client.get("/api/users/me", headers=headers)
    
    assert me_response.status_code == status.HTTP_200_OK
    user_data = me_response.json()
    assert user_data["email"] == registration_data["email"]
    assert user_data["username"] == registration_data["username"]
    assert user_data["full_name"] == registration_data["full_name"]
    assert user_data["is_active"] is True


@pytest.mark.asyncio
@pytest.mark.integration
async def test_duplicate_registration_fails(async_client: AsyncClient):
    """Test that registering with duplicate email/username fails with 409 Conflict"""
    # Step 1: Register first user
    user_data = {
        "email": "duplicate@example.com",
        "username": "duplicateuser",
        "password": "SecurePass123!"
    }
    
    first_response = await async_client.post("/api/users/register", json=user_data)
    assert first_response.status_code == status.HTTP_201_CREATED
    
    # Step 2: Try to register with same email - should return 409 Conflict
    second_response = await async_client.post("/api/users/register", json=user_data)
    assert second_response.status_code == status.HTTP_409_CONFLICT


@pytest.mark.asyncio
@pytest.mark.integration
async def test_login_with_wrong_password_fails(async_client: AsyncClient):
    """Test that login with incorrect password fails"""
    # Step 1: Register user
    user_data = {
        "email": "testlogin@example.com",
        "username": "testlogin",
        "password": "CorrectPass123!"
    }
    await async_client.post("/api/users/register", json=user_data)
    
    # Step 2: Try to login with wrong password
    login_data = {
        "username": "testlogin",
        "password": "WrongPassword123!"
    }
    
    login_response = await async_client.post("/api/users/login", json=login_data)
    assert login_response.status_code == status.HTTP_401_UNAUTHORIZED


# ==================== TOKEN REFRESH FLOW ====================

@pytest.mark.asyncio
@pytest.mark.integration
async def test_token_refresh_flow(async_client: AsyncClient):
    """Test token refresh flow: register → login → refresh token → access endpoint"""
    # Step 1: Register and login
    user_data = {
        "email": "refreshtest@example.com",
        "username": "refreshtest",
        "password": "SecurePass123!"
    }
    await async_client.post("/api/users/register", json=user_data)
    
    login_response = await async_client.post(
        "/api/users/login",
        json={"username": user_data["username"], "password": user_data["password"]}
    )
    tokens = login_response.json()
    refresh_token = tokens["refresh_token"]
    
    # Step 2: Use refresh token to get new access token
    refresh_response = await async_client.post(
        "/api/users/refresh",
        json={"refresh_token": refresh_token}
    )
    assert refresh_response.status_code == status.HTTP_200_OK
    new_tokens = refresh_response.json()
    assert "access_token" in new_tokens
    assert new_tokens["token_type"] == "bearer"
    
    # Step 3: Use new access token to access protected endpoint
    headers = {"Authorization": f"Bearer {new_tokens['access_token']}"}
    me_response = await async_client.get("/api/users/me", headers=headers)
    assert me_response.status_code == status.HTTP_200_OK


@pytest.mark.asyncio
@pytest.mark.integration
async def test_invalid_refresh_token_fails(async_client: AsyncClient):
    """Test that invalid refresh token is rejected"""
    refresh_response = await async_client.post(
        "/api/users/refresh",
        json={"refresh_token": "invalid.token.here"}
    )
    assert refresh_response.status_code == status.HTTP_401_UNAUTHORIZED


# ==================== USER PROFILE UPDATE FLOW ====================

@pytest.mark.asyncio
@pytest.mark.integration
async def test_user_profile_update_flow(async_client: AsyncClient):
    """Test user profile update: register → login → update profile → verify"""
    # Step 1: Register and login
    user_data = {
        "email": "updatetest@example.com",
        "username": "updatetest",
        "password": "SecurePass123!",
        "full_name": "Original Name"
    }
    await async_client.post("/api/users/register", json=user_data)
    
    login_response = await async_client.post(
        "/api/users/login",
        json={"username": user_data["username"], "password": user_data["password"]}
    )
    access_token = login_response.json()["access_token"]
    headers = {"Authorization": f"Bearer {access_token}"}
    
    # Step 2: Get current profile
    profile_response = await async_client.get("/api/users/me", headers=headers)
    assert profile_response.status_code == status.HTTP_200_OK
    
    # Step 3: Update profile
    update_data = {
        "full_name": "Updated Name",
        "email": "updated@example.com"
    }
    update_response = await async_client.put(
        "/api/users/me",
        headers=headers,
        json=update_data
    )
    assert update_response.status_code == status.HTTP_200_OK
    
    # Step 4: Verify changes
    verify_response = await async_client.get("/api/users/me", headers=headers)
    updated_profile = verify_response.json()
    assert updated_profile["full_name"] == update_data["full_name"]
    assert updated_profile["email"] == update_data["email"]


@pytest.mark.asyncio
@pytest.mark.integration
async def test_change_password_flow(async_client: AsyncClient):
    """Test password change: register → change password → login with new pass"""
    # Step 1: Register and login
    user_data = {
        "email": "changepass@example.com",
        "username": "changepass",
        "password": "OldPassword123!"
    }
    await async_client.post("/api/users/register", json=user_data)
    
    login_response = await async_client.post(
        "/api/users/login",
        json={"username": user_data["username"], "password": user_data["password"]}
    )
    access_token = login_response.json()["access_token"]
    headers = {"Authorization": f"Bearer {access_token}"}
    
    # Step 2: Change password
    new_password = "NewPassword123!"
    change_response = await async_client.post(
        "/api/users/change-password",
        headers=headers,
        json={
            "current_password": user_data["password"],
            "new_password": new_password
        }
    )
    assert change_response.status_code == status.HTTP_200_OK
    
    # Step 3: Login with new password
    new_login_response = await async_client.post(
        "/api/users/login",
        json={"username": user_data["username"], "password": new_password}
    )
    assert new_login_response.status_code == status.HTTP_200_OK
    
    # Step 4: Verify old password doesn't work
    old_login_response = await async_client.post(
        "/api/users/login",
        json={"username": user_data["username"], "password": user_data["password"]}
    )
    assert old_login_response.status_code == status.HTTP_401_UNAUTHORIZED


# ==================== ADMIN FLOW TESTS ====================

@pytest.mark.asyncio
@pytest.mark.integration
async def test_admin_registration_and_user_list_flow(async_client: AsyncClient):
    """Test admin flow: register admin → login → list users"""
    # Step 1: Register admin
    admin_data = {
        "email": "admin@example.com",
        "username": "adminuser",
        "password": "AdminPass123!"
    }
    admin_register = await async_client.post("/api/admins/register", json=admin_data)
    assert admin_register.status_code == status.HTTP_201_CREATED
    
    # Step 2: Login as admin
    admin_login = await async_client.post(
        "/api/admins/login",
        json={"username": admin_data["username"], "password": admin_data["password"]}
    )
    assert admin_login.status_code == status.HTTP_200_OK
    admin_token = admin_login.json()["access_token"]
    admin_headers = {"Authorization": f"Bearer {admin_token}"}
    
    # Step 3: Create some users first
    for i in range(3):
        await async_client.post(
            "/api/users/register",
            json={
                "email": f"user{i}@test.com",
                "username": f"user{i}",
                "password": "Pass123!"
            }
        )
    
    # Step 4: List all users (admin-only) - response has "items" field from PaginatedResponse
    users_response = await async_client.get("/api/admins/users", headers=admin_headers)
    assert users_response.status_code == status.HTTP_200_OK
    users_data = users_response.json()
    assert "items" in users_data
    assert len(users_data["items"]) >= 3


@pytest.mark.asyncio
@pytest.mark.integration
async def test_regular_user_cannot_access_admin_endpoints(async_client: AsyncClient):
    """Test that regular users cannot access admin-only endpoints"""
    # Step 1: Register regular user
    user_data = {
        "email": "regularuser@example.com",
        "username": "regularuser",
        "password": "UserPass123!"
    }
    await async_client.post("/api/users/register", json=user_data)
    
    # Step 2: Login as regular user
    login_response = await async_client.post(
        "/api/users/login",
        json={"username": user_data["username"], "password": user_data["password"]}
    )
    user_token = login_response.json()["access_token"]
    user_headers = {"Authorization": f"Bearer {user_token}"}
    
    # Step 3: Try to access admin endpoint (should fail)
    admin_response = await async_client.get("/api/admins/users", headers=user_headers)
    assert admin_response.status_code == status.HTTP_403_FORBIDDEN


@pytest.mark.asyncio
@pytest.mark.integration
async def test_admin_login_with_email(async_client: AsyncClient):
    """Test that admin can login with email instead of username"""
    # Step 1: Register admin
    admin_data = {
        "email": "emailadmin@example.com",
        "username": "emailadmin",
        "password": "AdminPass123!"
    }
    await async_client.post("/api/admins/register", json=admin_data)
    
    # Step 2: Login with email (not username)
    login_response = await async_client.post(
        "/api/admins/login",
        json={"email": admin_data["email"], "password": admin_data["password"]}
    )
    assert login_response.status_code == status.HTTP_200_OK
    assert "access_token" in login_response.json()


# ==================== AUTHORIZATION TESTS ====================

@pytest.mark.asyncio
@pytest.mark.integration
async def test_access_protected_endpoint_without_token(async_client: AsyncClient):
    """Test that accessing protected endpoint without token fails"""
    response = await async_client.get("/api/users/me")
    assert response.status_code == status.HTTP_401_UNAUTHORIZED


@pytest.mark.asyncio
@pytest.mark.integration
async def test_access_protected_endpoint_with_invalid_token(async_client: AsyncClient):
    """Test that accessing protected endpoint with invalid token fails"""
    headers = {"Authorization": "Bearer invalid.token.here"}
    response = await async_client.get("/api/users/me", headers=headers)
    assert response.status_code == status.HTTP_401_UNAUTHORIZED


@pytest.mark.asyncio
@pytest.mark.integration
async def test_access_protected_endpoint_with_expired_token(async_client: AsyncClient):
    """Test that expired tokens are rejected"""
    expired_token = create_access_token(
        data={"id": 1, "role": "user"},
        expires_delta=timedelta(seconds=-1)
    )
    
    headers = {"Authorization": f"Bearer {expired_token}"}
    response = await async_client.get("/api/users/me", headers=headers)
    assert response.status_code == status.HTTP_401_UNAUTHORIZED


# ==================== PAGINATION TESTS ====================

@pytest.mark.asyncio
@pytest.mark.integration
async def test_user_list_pagination(async_client: AsyncClient):
    """Test pagination in admin user list endpoint"""
    # Step 1: Register admin
    admin_data = {
        "email": "paginadmin@example.com",
        "username": "paginadmin",
        "password": "AdminPass123!"
    }
    await async_client.post("/api/admins/register", json=admin_data)
    
    admin_login = await async_client.post(
        "/api/admins/login",
        json={"username": admin_data["username"], "password": admin_data["password"]}
    )
    admin_token = admin_login.json()["access_token"]
    admin_headers = {"Authorization": f"Bearer {admin_token}"}
    
    # Step 2: Create multiple users
    for i in range(15):
        await async_client.post(
            "/api/users/register",
            json={
                "email": f"paginuser{i}@test.com",
                "username": f"paginuser{i}",
                "password": "Pass123!"
            }
        )
    
    # Step 3: Test pagination - page 1 (uses "items" from PaginatedResponse)
    page1_response = await async_client.get(
        "/api/admins/users?page=1&page_size=5",
        headers=admin_headers
    )
    assert page1_response.status_code == status.HTTP_200_OK
    page1_data = page1_response.json()
    assert len(page1_data["items"]) <= 5
    assert page1_data["page"] == 1
    assert page1_data["total"] >= 15
    
    # Step 4: Test pagination - page 2
    page2_response = await async_client.get(
        "/api/admins/users?page=2&page_size=5",
        headers=admin_headers
    )
    assert page2_response.status_code == status.HTTP_200_OK
    page2_data = page2_response.json()
    assert page2_data["page"] == 2


@pytest.mark.asyncio
@pytest.mark.integration
async def test_user_list_filtering_by_active_status(async_client: AsyncClient):
    """Test filtering users by active status"""
    # Step 1: Register admin
    admin_data = {
        "email": "filteradmin@example.com",
        "username": "filteradmin",
        "password": "AdminPass123!"
    }
    await async_client.post("/api/admins/register", json=admin_data)
    
    admin_login = await async_client.post(
        "/api/admins/login",
        json={"username": admin_data["username"], "password": admin_data["password"]}
    )
    admin_token = admin_login.json()["access_token"]
    admin_headers = {"Authorization": f"Bearer {admin_token}"}
    
    # Step 2: Filter active users (uses "items" from PaginatedResponse)
    active_response = await async_client.get(
        "/api/admins/users?is_active=true",
        headers=admin_headers
    )
    assert active_response.status_code == status.HTTP_200_OK
    active_users = active_response.json()["items"]
    assert all(user["is_active"] for user in active_users)


# ==================== ERROR HANDLING TESTS ====================

@pytest.mark.asyncio
@pytest.mark.integration
async def test_malformed_json_request(async_client: AsyncClient):
    """Test that malformed JSON requests are handled gracefully"""
    response = await async_client.post(
        "/api/users/register",
        content=b"{invalid json}",
        headers={"Content-Type": "application/json"}
    )
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY


@pytest.mark.asyncio
@pytest.mark.integration
async def test_missing_required_fields(async_client: AsyncClient):
    """Test that missing required fields are caught"""
    incomplete_data = {
        "email": "incomplete@example.com"
        # Missing username and password
    }
    
    response = await async_client.post("/api/users/register", json=incomplete_data)
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY


@pytest.mark.asyncio
@pytest.mark.integration
async def test_invalid_email_format(async_client: AsyncClient):
    """Test that invalid email format is rejected"""
    invalid_data = {
        "email": "not-an-email",
        "username": "testuser",
        "password": "SecurePass123!"
    }
    
    response = await async_client.post("/api/users/register", json=invalid_data)
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY


# ==================== DATA CONSISTENCY TESTS ====================

@pytest.mark.asyncio
@pytest.mark.integration
async def test_user_data_consistency_across_endpoints(async_client: AsyncClient):
    """Test that user data is consistent across different endpoints"""
    # Step 1: Register user
    user_data = {
        "email": "consistency@test.com",
        "username": "consistency",
        "password": "Pass123!",
        "full_name": "Consistency Test"
    }
    register_response = await async_client.post("/api/users/register", json=user_data)
    registered_user = register_response.json()
    
    # Step 2: Login and get user profile
    login_response = await async_client.post(
        "/api/users/login",
        json={"username": user_data["username"], "password": user_data["password"]}
    )
    access_token = login_response.json()["access_token"]
    headers = {"Authorization": f"Bearer {access_token}"}
    
    profile_response = await async_client.get("/api/users/me", headers=headers)
    profile_user = profile_response.json()
    
    # Step 3: Verify data consistency
    assert registered_user["email"] == profile_user["email"]
    assert registered_user["username"] == profile_user["username"]
    assert registered_user["full_name"] == profile_user["full_name"]
    assert registered_user["id"] == profile_user["id"]


@pytest.mark.asyncio
@pytest.mark.integration
async def test_health_check_endpoint(async_client: AsyncClient):
    """Test that health check endpoint works correctly"""
    response = await async_client.get("/health")
    
    assert response.status_code == status.HTTP_200_OK
    health_data = response.json()
    
    # Verify expected fields
    assert "status" in health_data
    assert "version" in health_data
    assert "environment" in health_data
    assert "database" in health_data
    
    # Database should be connected
    assert health_data["database"]["connected"] is True