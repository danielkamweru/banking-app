#!/usr/bin/env python3
import requests
import json
import time

BASE_URL = "http://localhost:8000"

def test_signup():
    data = {
        "first_name": "Test",
        "last_name": "User", 
        "email": "test@example.com",
        "pin": "1234"
    }
    response = requests.post(f"{BASE_URL}/api/auth/signup", json=data)
    print(f"Signup: {response.status_code} - {response.text}")
    return response.status_code == 200

def test_login():
    data = {
        "email": "test@example.com",
        "pin": "1234"
    }
    response = requests.post(f"{BASE_URL}/api/auth/login", json=data)
    print(f"Login: {response.status_code} - {response.text}")
    if response.status_code == 200:
        return response.json()["access_token"]
    return None

def test_profile(token):
    headers = {"Authorization": f"Bearer {token}"}
    response = requests.get(f"{BASE_URL}/api/users/me", headers=headers)
    print(f"Profile: {response.status_code} - {response.text}")
    return response.status_code == 200

def test_deposit(token):
    headers = {"Authorization": f"Bearer {token}"}
    data = {"amount": 100.0}
    response = requests.post(f"{BASE_URL}/api/transactions/deposit", json=data, headers=headers)
    print(f"Deposit: {response.status_code} - {response.text}")
    return response.status_code == 200

def test_transactions(token):
    headers = {"Authorization": f"Bearer {token}"}
    response = requests.get(f"{BASE_URL}/api/transactions", headers=headers)
    print(f"Transactions: {response.status_code} - {response.text}")
    return response.status_code == 200

if __name__ == "__main__":
    print("Testing Banking App API...")
    
    # Test signup
    if test_signup():
        print("✅ Signup works")
    else:
        print("❌ Signup failed")
        exit(1)
    
    # Test login
    token = test_login()
    if token:
        print("✅ Login works")
    else:
        print("❌ Login failed")
        exit(1)
    
    # Test profile
    if test_profile(token):
        print("✅ Profile works")
    else:
        print("❌ Profile failed")
    
    # Test deposit
    if test_deposit(token):
        print("✅ Deposit works")
    else:
        print("❌ Deposit failed")
    
    # Test transactions
    if test_transactions(token):
        print("✅ Transactions works")
    else:
        print("❌ Transactions failed")
    
    print("\n🎉 All tests completed!")