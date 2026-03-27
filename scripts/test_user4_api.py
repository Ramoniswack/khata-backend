#!/usr/bin/env python
"""
Test the /api/tenants/ endpoint for user4@test.com
"""
import os
import sys
import django

# Setup Django
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core_backend.settings')
django.setup()

from django.test import RequestFactory
from tenants.views import TenantViewSet
from users.models import User
from rest_framework.test import force_authenticate

def test_tenants_api():
    print("=" * 80)
    print("TESTING /api/tenants/ FOR user4@test.com")
    print("=" * 80)
    
    try:
        user4 = User.objects.get(email='user4@test.com')
        print(f"\n✓ Testing with user: {user4.email}")
        print(f"  - Tenant: {user4.tenant}")
        print(f"  - Role: {user4.role}")
    except User.DoesNotExist:
        print("\n✗ user4@test.com not found!")
        return
    
    # Create a fake request
    factory = RequestFactory()
    request = factory.get('/api/tenants/')
    force_authenticate(request, user=user4)
    
    # Create viewset instance
    viewset = TenantViewSet.as_view({'get': 'list'})
    
    print("\n" + "=" * 80)
    print("CALLING VIEWSET")
    print("=" * 80)
    
    try:
        # Call the viewset
        response = viewset(request)
        print(f"\n✓ Response status: {response.status_code}")
        
        if response.status_code == 200:
            print(f"✓ SUCCESS! Got {len(response.data)} tenants")
            for tenant_data in response.data:
                print(f"\n  Tenant:")
                print(f"    - ID: {tenant_data.get('id')}")
                print(f"    - Name: {tenant_data.get('name')}")
                print(f"    - Slug: {tenant_data.get('slug')}")
                print(f"    - Business type: {tenant_data.get('business_type')}")
                print(f"    - Is active: {tenant_data.get('is_active')}")
                print(f"    - Created from registration: {tenant_data.get('created_from_registration')}")
        else:
            print(f"✗ FAILED with status {response.status_code}")
            print(f"Response data: {response.data}")
            
    except Exception as e:
        print(f"\n✗ EXCEPTION OCCURRED!")
        print(f"  - Error type: {type(e).__name__}")
        print(f"  - Error message: {str(e)}")
        
        # Print full traceback
        import traceback
        print(f"\n  Full traceback:")
        traceback.print_exc()
    
    print("\n" + "=" * 80)
    print("TEST COMPLETE")
    print("=" * 80)


if __name__ == '__main__':
    test_tenants_api()
