#!/usr/bin/env python
"""
Test script to debug the dashboard 500 error
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

def test_dashboard_with_tenant():
    """Test dashboard API when user has a tenant"""
    
    print("\n" + "="*80)
    print("TESTING DASHBOARD WITH TENANT (User: mr.bishal.baniya)")
    print("="*80)
    
    # Find the user
    try:
        user = User.objects.get(username='mr.bishal.baniya')
        print(f"\n✅ Found user: {user.username}")
        print(f"   - User ID: {user.id}")
        print(f"   - Email: {user.email}")
        print(f"   - Tenant: {user.tenant}")
        if user.tenant:
            print(f"   - Tenant ID: {user.tenant.id}")
            print(f"   - Tenant Name: {user.tenant.name}")
    except User.DoesNotExist:
        print("\n❌ User not found")
        return
    
    # Create API client and authenticate
    client = APIClient()
    client.force_authenticate(user=user)
    
    # Try to access dashboard
    print("\n" + "-"*80)
    print("TESTING DASHBOARD API CALL")
    print("-"*80)
    
    try:
        response = client.get('/api/sales/orders/dashboard/?period=month')
        
        print(f"\nResponse Status: {response.status_code}")
        
        if response.status_code == 200:
            print("✅ Dashboard loaded successfully")
            print(f"Response keys: {response.data.keys() if hasattr(response, 'data') else 'N/A'}")
        else:
            print(f"❌ Dashboard returned error: {response.status_code}")
            if hasattr(response, 'data'):
                print(f"Error data: {response.data}")
            else:
                print(f"Response content: {response.content[:500]}")
    except Exception as e:
        print(f"\n❌ Exception occurred: {type(e).__name__}")
        print(f"Error message: {str(e)}")
        import traceback
        print("\nFull traceback:")
        traceback.print_exc()
    
    print("\n" + "="*80)

if __name__ == '__main__':
    test_dashboard_with_tenant()
