#!/usr/bin/env python3
"""
Error Handler Testing Script
Tests all custom error handlers to ensure they return proper responses
"""

import requests
import json
from typing import Dict, Any
import random

BASE_URL = "https://localhost"  # Using HTTPS
# Disable SSL warnings for self-signed certificate
import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


def print_test_result(test_name: str, response: requests.Response, expected_status: int):
    """Print formatted test results"""
    print(f"\n{'='*70}")
    print(f"TEST: {test_name}")
    print(f"{'='*70}")
    print(f"Status Code: {response.status_code} (Expected: {expected_status})")
    print(f"Success: {'✅' if response.status_code == expected_status else '❌'}")
    
    try:
        data = response.json()
        print(f"\nResponse Body:")
        print(json.dumps(data, indent=2))
        
        # Check for standardized error format
        if 'error' in data and 'message' in data and 'timestamp' in data:
            print(f"\n✅ Standardized error format present")
        else:
            print(f"\n⚠️  Missing standardized error format")
            
    except Exception as e:
        print(f"Response Text: {response.text[:200]}")
        print(f"⚠️  Could not parse JSON: {e}")
    
    print(f"{'='*70}\n")


def test_404_not_found():
    """Test 404 Not Found handler"""
    response = requests.get(f"{BASE_URL}/api/nonexistent-endpoint", verify=False)
    print_test_result("404 Not Found Handler", response, 404)


def test_validation_error():
    """Test 422 Validation Error handler"""
    # Try to register with invalid data (missing required username field)
    invalid_data = {
        "email": "not-an-email",  # Invalid email
        "password": "123",  # Too short
    }
    response = requests.post(f"{BASE_URL}/api/users/register", json=invalid_data, verify=False)
    print_test_result("422 Validation Error Handler", response, 422)


def test_authentication_error():
    """Test 401 Authentication Error handler"""
    # Try to login with correct format but wrong credentials
    invalid_creds = {
        "username": "nonexistent_user_12345",
        "password": "wrongpassword"
    }
    response = requests.post(f"{BASE_URL}/api/users/login", json=invalid_creds, verify=False)
    print_test_result("401 Authentication Error Handler", response, 401)


def test_protected_endpoint_without_token():
    """Test accessing protected endpoint without token"""
    response = requests.get(f"{BASE_URL}/api/users/me", verify=False)
    print_test_result("401 Missing Token Handler", response, 401)


def test_protected_endpoint_with_invalid_token():
    """Test accessing protected endpoint with invalid token"""
    headers = {"Authorization": "Bearer invalid_token_here"}
    response = requests.get(f"{BASE_URL}/api/users/me", headers=headers, verify=False)
    print_test_result("401 Invalid Token Handler", response, 401)


def test_health_endpoint():
    """Test health endpoint (should work)"""
    response = requests.get(f"{BASE_URL}/health", verify=False)
    print_test_result("Health Endpoint (Should succeed)", response, 200)


def test_duplicate_user():
    """Test duplicate user creation (409 Conflict)"""
    # Create a unique user with correct field names
    username = f"testuser{random.randint(10000, 99999)}"
    email = f"test{random.randint(10000, 99999)}@example.com"
    
    user_data = {
        "username": username,
        "email": email,
        "password": "SecurePass123!@#"
    }
    
    # First registration should succeed
    response1 = requests.post(f"{BASE_URL}/api/users/register", json=user_data, verify=False)
    print(f"\n📝 First registration: Status {response1.status_code}")
    if response1.status_code == 201:
        print(f"   ✅ User created successfully")
    else:
        print(f"   Response: {response1.json()}")
    
    # Second registration with same username should fail with 409
    response2 = requests.post(f"{BASE_URL}/api/users/register", json=user_data, verify=False)
    print_test_result("409 Duplicate User Handler (duplicate username)", response2, 409)


def run_all_tests():
    """Run all error handler tests"""
    print("\n" + "="*70)
    print("🧪 STARTING ERROR HANDLER TESTS")
    print("="*70)
    
    try:
        test_health_endpoint()
        test_404_not_found()
        test_validation_error()
        test_authentication_error()
        test_protected_endpoint_without_token()
        test_protected_endpoint_with_invalid_token()
        test_duplicate_user()
        
        print("\n" + "="*70)
        print("✅ ALL TESTS COMPLETED!")
        print("="*70)
        print("\n💡 Summary of test expectations:")
        print("  ✅ 200: Health endpoint")
        print("  ✅ 404: Not found endpoint")
        print("  ✅ 422: Invalid request data")
        print("  ✅ 401: Invalid credentials (wrong username/password)")
        print("  ✅ 401: Missing authentication token")
        print("  ✅ 401: Invalid/expired token")
        print("  ✅ 409: Duplicate user (username already exists)")
        print("\n📋 All should return standardized format:")
        print("  - error (type)")
        print("  - message")
        print("  - status_code")
        print("  - timestamp")
        print("  - path")
        
    except requests.exceptions.ConnectionError as e:
        print(f"\n❌ Connection Error: Could not connect to {BASE_URL}")
        print("Make sure the backend is running with: docker compose ps")
        print(f"Error: {e}")
    except Exception as e:
        print(f"\n❌ Unexpected Error: {e}")


if __name__ == "__main__":
    run_all_tests()