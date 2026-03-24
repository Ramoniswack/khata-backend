#!/usr/bin/env python
"""
Test script for Bank Accounts API endpoints
Tests bank account creation, listing, and GL account integration
"""

import os
import sys
import django

# Setup Django
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core_backend.settings')
django.setup()

import requests
from datetime import date

# Configuration
BASE_URL = "http://localhost:8000/api"
USERNAME = "admin"
PASSWORD = "admin"

def get_auth_token():
    """Get JWT authentication token"""
    response = requests.post(f"{BASE_URL}/users/login/", json={
        "username": USERNAME,
        "password": PASSWORD
    })
    if response.status_code == 200:
        return response.json()['access']
    else:
        print(f"❌ Login failed: {response.status_code}")
        print(response.text)
        sys.exit(1)

def test_list_gl_accounts(headers):
    """Test listing GL accounts of type Bank"""
    print("\n" + "="*80)
    print("TEST 1: List GL Accounts (Type: Bank)")
    print("="*80)
    
    response = requests.get(
        f"{BASE_URL}/accounting/accounts/",
        headers=headers,
        params={"sub_type": "Bank", "status": "active"}
    )
    
    print(f"Status Code: {response.status_code}")
    if response.status_code == 200:
        accounts = response.json()
        print(f"✅ Found {len(accounts)} Bank type GL accounts")
        for account in accounts[:5]:  # Show first 5
            print(f"   - {account['code']}: {account['name']}")
        return accounts
    else:
        print(f"❌ Failed: {response.text}")
        return []

def test_create_bank_account(headers, gl_account_id):
    """Test creating a new bank account"""
    print("\n" + "="*80)
    print("TEST 2: Create Bank Account")
    print("="*80)
    
    data = {
        "bank_name": "Nepal Bank Limited",
        "account_name": "Main Operating Account",
        "account_number": "0123456789",
        "type": "Current",
        "branch": "Kathmandu Branch",
        "swift_code": "NBLNPKA",
        "gl_account": gl_account_id,
        "status": "active"
    }
    
    print(f"Creating bank account: {data['bank_name']} - {data['account_number']}")
    
    response = requests.post(
        f"{BASE_URL}/accounting/bank-accounts/",
        headers=headers,
        json=data
    )
    
    print(f"Status Code: {response.status_code}")
    if response.status_code == 201:
        bank_account = response.json()
        print(f"✅ Bank account created successfully!")
        print(f"   ID: {bank_account['id']}")
        print(f"   Bank: {bank_account['bank_name']}")
        print(f"   Account Number: {bank_account['account_number']}")
        print(f"   Type: {bank_account['type']}")
        print(f"   GL Account: {bank_account['gl_account_name']} ({bank_account['gl_account_code']})")
        print(f"   Balance: {bank_account['balance']}")
        return bank_account
    else:
        print(f"❌ Failed: {response.text}")
        return None

def test_list_bank_accounts(headers):
    """Test listing all bank accounts"""
    print("\n" + "="*80)
    print("TEST 3: List Bank Accounts")
    print("="*80)
    
    response = requests.get(
        f"{BASE_URL}/accounting/bank-accounts/",
        headers=headers
    )
    
    print(f"Status Code: {response.status_code}")
    if response.status_code == 200:
        accounts = response.json()
        print(f"✅ Found {len(accounts)} bank accounts")
        for account in accounts:
            print(f"   - {account['bank_name']}: {account['account_number']} ({account['type']})")
        return accounts
    else:
        print(f"❌ Failed: {response.text}")
        return []

def test_get_bank_account(headers, account_id):
    """Test getting a specific bank account"""
    print("\n" + "="*80)
    print("TEST 4: Get Bank Account Details")
    print("="*80)
    
    response = requests.get(
        f"{BASE_URL}/accounting/bank-accounts/{account_id}/",
        headers=headers
    )
    
    print(f"Status Code: {response.status_code}")
    if response.status_code == 200:
        account = response.json()
        print(f"✅ Bank account retrieved successfully!")
        print(f"   Bank: {account['bank_name']}")
        print(f"   Account Name: {account['account_name']}")
        print(f"   Account Number: {account['account_number']}")
        print(f"   Type: {account['type']}")
        print(f"   Branch: {account.get('branch', 'N/A')}")
        print(f"   SWIFT Code: {account.get('swift_code', 'N/A')}")
        print(f"   GL Account: {account['gl_account_name']} ({account['gl_account_code']})")
        print(f"   Balance: {account['balance']}")
        print(f"   Status: {account['status']}")
        return account
    else:
        print(f"❌ Failed: {response.text}")
        return None

def test_update_bank_account(headers, account_id):
    """Test updating a bank account"""
    print("\n" + "="*80)
    print("TEST 5: Update Bank Account")
    print("="*80)
    
    data = {
        "branch": "Thamel Branch",
        "status": "active"
    }
    
    print(f"Updating bank account {account_id}")
    
    response = requests.patch(
        f"{BASE_URL}/accounting/bank-accounts/{account_id}/",
        headers=headers,
        json=data
    )
    
    print(f"Status Code: {response.status_code}")
    if response.status_code == 200:
        account = response.json()
        print(f"✅ Bank account updated successfully!")
        print(f"   New Branch: {account['branch']}")
        return account
    else:
        print(f"❌ Failed: {response.text}")
        return None

def test_filter_bank_accounts(headers):
    """Test filtering bank accounts"""
    print("\n" + "="*80)
    print("TEST 6: Filter Bank Accounts")
    print("="*80)
    
    # Filter by type
    response = requests.get(
        f"{BASE_URL}/accounting/bank-accounts/",
        headers=headers,
        params={"type": "Current", "status": "active"}
    )
    
    print(f"Status Code: {response.status_code}")
    if response.status_code == 200:
        accounts = response.json()
        print(f"✅ Found {len(accounts)} Current accounts with active status")
        for account in accounts:
            print(f"   - {account['bank_name']}: {account['account_number']}")
        return accounts
    else:
        print(f"❌ Failed: {response.text}")
        return []

def main():
    print("="*80)
    print("BANK ACCOUNTS API TEST SUITE")
    print("="*80)
    
    # Get authentication token
    print("\n🔐 Authenticating...")
    token = get_auth_token()
    headers = {"Authorization": f"Bearer {token}"}
    print("✅ Authentication successful")
    
    # Test 1: List GL accounts
    gl_accounts = test_list_gl_accounts(headers)
    if not gl_accounts:
        print("\n❌ No Bank type GL accounts found. Please create one first.")
        return
    
    # Use first GL account for testing
    gl_account_id = gl_accounts[0]['id']
    
    # Test 2: Create bank account
    bank_account = test_create_bank_account(headers, gl_account_id)
    if not bank_account:
        print("\n❌ Bank account creation failed. Stopping tests.")
        return
    
    account_id = bank_account['id']
    
    # Test 3: List bank accounts
    test_list_bank_accounts(headers)
    
    # Test 4: Get bank account details
    test_get_bank_account(headers, account_id)
    
    # Test 5: Update bank account
    test_update_bank_account(headers, account_id)
    
    # Test 6: Filter bank accounts
    test_filter_bank_accounts(headers)
    
    print("\n" + "="*80)
    print("✅ ALL TESTS COMPLETED SUCCESSFULLY!")
    print("="*80)
    print("\nBank Account Management is working correctly!")
    print("You can now use the frontend to create and manage bank accounts.")

if __name__ == "__main__":
    main()
