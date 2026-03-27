#!/usr/bin/env python
"""
Test script to verify dashboard behavior when user has no tenant
"""
import os
import sys
import django

# Setup Django
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core_backend.settings')
django.setup()

from django.contrib.auth import get_user_model
from rest_framework.test import APIClient
from tenants.models import Tenant

User = get_user_model()

def test_dashboard_no_tenant():
    """Test dashboard API when user has no tenant"""
    
    print("\n" + "="*80)
    print("TESTING DASHBOARD WITH NO TENANT")
    print("="*80)
    
    # Find a user with no tenant
    user = User.objects.filter(tenant__isnull=True).first()
    
    if not user:
        print("\n❌ No user found without tenant")
        print("Creating test user without tenant...")
        user = User.objects.create_user(
            username='test_no_tenant',
            email='test_no_tenant@example.com',
            password='testpass123',
            tenant=None
        )
        print(f"✅ Created user: {user.username}")
    else:
        print(f"\n✅ Found user without tenant: {user.username}")
    
    print(f"   - User ID: {user.id}")
    print(f"   - Email: {user.email}")
    print(f"   - Tenant: {user.tenant}")
    
    # Create API client and authenticate
    client = APIClient()
    client.force_authenticate(user=user)
    
    # Try to access dashboard
    print("\n" + "-"*80)
    print("TESTING DASHBOARD API CALL")
    print("-"*80)
    
    response = client.get('/api/sales/orders/dashboard/')
    
    print(f"\nResponse Status: {response.status_code}")
    print(f"Response Data: {response.data if hasattr(response, 'data') else response.content}")
    
    # Expected behavior: Should return error (500 or 403)
    if response.status_code in [500, 403, 400]:
        print("\n✅ Dashboard correctly returns error when user has no tenant")
        
        # Check error message
        if hasattr(response, 'data'):
            error_msg = str(response.data)
            print(f"\nError message: {error_msg}")
            
            # Check if error message contains tenant-related keywords
            keywords = ['tenant', 'organization', 'nonetype', 'null']
            found_keywords = [kw for kw in keywords if kw in error_msg.lower()]
            
            if found_keywords:
                print(f"✅ Error message contains tenant-related keywords: {found_keywords}")
                print("   Frontend will detect this and redirect to /erp")
            else:
                print("⚠️  Error message doesn't contain obvious tenant keywords")
                print("   Frontend might not detect this as a no-tenant error")
    else:
        print(f"\n⚠️  Unexpected response status: {response.status_code}")
    
    print("\n" + "="*80)
    print("TEST SUMMARY")
    print("="*80)
    print("\nExpected Frontend Behavior:")
    print("1. Dashboard page calls /api/sales/orders/dashboard/")
    print("2. API returns error because user.tenant is None")
    print("3. useApi hook catches error and creates Error object with message")
    print("4. Dashboard checks error.message for tenant-related keywords")
    print("5. If found, shows 'No organization selected. Redirecting...'")
    print("6. Redirects to /erp after 1.5 seconds")
    print("\nUser Actions:")
    print("- User can create new organization on /erp page")
    print("- User can accept pending invitations")
    print("- User can select from existing organizations (if member of multiple)")
    
    print("\n" + "="*80)

if __name__ == '__main__':
    test_dashboard_no_tenant()
