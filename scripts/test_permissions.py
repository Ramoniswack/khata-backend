#!/usr/bin/env python
"""
Test script for Permissions Management API

This script tests:
1. Get permissions matrix
2. Update permissions
3. Verify updates
"""

import os
import sys
import django

# Setup Django
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core_backend.settings')
django.setup()

import requests
import json

# Configuration
BASE_URL = "http://localhost:8000/api"
USERNAME = "admin"
PASSWORD = "admin123"

def print_header(text):
    """Print a formatted header"""
    print(f"\n{'='*60}")
    print(f"{text}")
    print(f"{'='*60}")

def print_success(text):
    """Print success message"""
    print(f"✓ {text}")

def print_error(text):
    """Print error message"""
    print(f"✗ {text}")

def print_info(text):
    """Print info message"""
    print(f"ℹ {text}")

def login():
    """Login and get JWT token"""
    print_header("1. AUTHENTICATION")
    
    url = f"{BASE_URL}/auth/login/"
    data = {
        "username": USERNAME,
        "password": PASSWORD
    }
    
    try:
        response = requests.post(url, json=data)
        response.raise_for_status()
        
        result = response.json()
        token = result.get('access')
        
        print_success(f"Logged in as: {USERNAME}")
        print_info(f"Token: {token[:20]}...")
        
        return token
    except requests.exceptions.RequestException as e:
        print_error(f"Login failed: {e}")
        if hasattr(e.response, 'text'):
            print_error(f"Response: {e.response.text}")
        sys.exit(1)

def get_permissions(token):
    """Get current permissions matrix"""
    print_header("2. GET PERMISSIONS MATRIX")
    
    url = f"{BASE_URL}/auth/permissions/"
    headers = {"Authorization": f"Bearer {token}"}
    
    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        
        permissions = response.json()
        
        print_success("Permissions retrieved successfully")
        print_info(f"Roles: {', '.join(permissions.keys())}")
        
        # Count permissions per role
        for role, perms in permissions.items():
            enabled_count = sum(1 for v in perms.values() if v)
            total_count = len(perms)
            print_info(f"{role}: {enabled_count}/{total_count} permissions enabled")
        
        return permissions
    except requests.exceptions.RequestException as e:
        print_error(f"Failed to get permissions: {e}")
        if hasattr(e.response, 'text'):
            print_error(f"Response: {e.response.text}")
        return None

def update_permissions(token, permissions):
    """Update permissions matrix"""
    print_header("3. UPDATE PERMISSIONS")
    
    # Modify some permissions for testing
    print_info("Modifying permissions for testing...")
    
    # Give Supervisor access to Sales-View
    if 'Supervisor' in permissions:
        permissions['Supervisor']['Sales-View'] = True
        print_info("Added: Supervisor -> Sales-View")
    
    # Remove Accountant's Purchase-View
    if 'Accountant' in permissions:
        permissions['Accountant']['Purchase-View'] = False
        print_info("Removed: Accountant -> Purchase-View")
    
    url = f"{BASE_URL}/auth/permissions/update/"
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    
    try:
        response = requests.post(url, headers=headers, json=permissions)
        response.raise_for_status()
        
        result = response.json()
        
        print_success(result.get('message', 'Permissions updated'))
        print_info(f"Updated count: {result.get('updated_count', 0)}")
        
        return True
    except requests.exceptions.RequestException as e:
        print_error(f"Failed to update permissions: {e}")
        if hasattr(e.response, 'text'):
            print_error(f"Response: {e.response.text}")
        return False

def verify_updates(token):
    """Verify that updates were applied"""
    print_header("4. VERIFY UPDATES")
    
    url = f"{BASE_URL}/auth/permissions/"
    headers = {"Authorization": f"Bearer {token}"}
    
    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        
        permissions = response.json()
        
        # Check if our changes were applied
        supervisor_has_sales_view = permissions.get('Supervisor', {}).get('Sales-View', False)
        accountant_has_purchase_view = permissions.get('Accountant', {}).get('Purchase-View', True)
        
        if supervisor_has_sales_view:
            print_success("Supervisor has Sales-View permission ✓")
        else:
            print_error("Supervisor does NOT have Sales-View permission ✗")
        
        if not accountant_has_purchase_view:
            print_success("Accountant does NOT have Purchase-View permission ✓")
        else:
            print_error("Accountant still has Purchase-View permission ✗")
        
        return supervisor_has_sales_view and not accountant_has_purchase_view
    except requests.exceptions.RequestException as e:
        print_error(f"Failed to verify updates: {e}")
        return False

def restore_defaults(token):
    """Restore default permissions"""
    print_header("5. RESTORE DEFAULTS")
    
    # Get current permissions
    url = f"{BASE_URL}/auth/permissions/"
    headers = {"Authorization": f"Bearer {token}"}
    
    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        permissions = response.json()
        
        # Restore the changes we made
        if 'Supervisor' in permissions:
            permissions['Supervisor']['Sales-View'] = False
            print_info("Restored: Supervisor -> Sales-View = False")
        
        if 'Accountant' in permissions:
            permissions['Accountant']['Purchase-View'] = True
            print_info("Restored: Accountant -> Purchase-View = True")
        
        # Update
        url = f"{BASE_URL}/auth/permissions/update/"
        headers["Content-Type"] = "application/json"
        
        response = requests.post(url, headers=headers, json=permissions)
        response.raise_for_status()
        
        print_success("Default permissions restored")
        return True
    except requests.exceptions.RequestException as e:
        print_error(f"Failed to restore defaults: {e}")
        return False

def main():
    """Main test function"""
    print("\n" + "="*60)
    print("         PERMISSIONS MANAGEMENT API TEST SCRIPT")
    print("="*60)
    
    # Step 1: Login
    token = login()
    
    # Step 2: Get permissions
    permissions = get_permissions(token)
    if not permissions:
        print_error("Cannot proceed without permissions data")
        sys.exit(1)
    
    # Step 3: Update permissions
    if not update_permissions(token, permissions):
        print_error("Failed to update permissions")
        sys.exit(1)
    
    # Step 4: Verify updates
    if not verify_updates(token):
        print_error("Verification failed")
        sys.exit(1)
    
    # Step 5: Restore defaults
    if not restore_defaults(token):
        print_error("Failed to restore defaults")
        sys.exit(1)
    
    # Final summary
    print_header("TEST SUMMARY")
    print_success("All tests passed! ✓")
    print_info("Permissions management is working correctly")
    
    print("\n" + "="*60 + "\n")

if __name__ == "__main__":
    main()
