#!/usr/bin/env python
"""
Test the /api/auth/users/ endpoint directly to see the actual error
"""
import os
import sys
import django

# Setup Django
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core_backend.settings')
django.setup()

from django.test import RequestFactory
from users.views import UserViewSet
from users.models import User
from rest_framework.test import force_authenticate

def test_users_list_endpoint():
    """Test the users list endpoint directly"""
    print("=" * 80)
    print("TESTING /api/auth/users/ ENDPOINT")
    print("=" * 80)
    
    # Get user1@test.com
    try:
        user = User.objects.get(email='user1@test.com')
        print(f"\n✓ Testing with user: {user.email}")
        print(f"  - Tenant: {user.tenant}")
        print(f"  - Role: {user.role}")
    except User.DoesNotExist:
        print("\n✗ user1@test.com not found!")
        return
    
    # Create a fake request
    factory = RequestFactory()
    request = factory.get('/api/auth/users/')
    force_authenticate(request, user=user)
    
    # Create viewset instance
    viewset = UserViewSet.as_view({'get': 'list'})
    
    print("\n" + "=" * 80)
    print("CALLING VIEWSET")
    print("=" * 80)
    
    try:
        # Call the viewset
        response = viewset(request)
        print(f"\n✓ Response status: {response.status_code}")
        
        if response.status_code == 200:
            print(f"✓ SUCCESS! Got {len(response.data)} users")
            for user_data in response.data:
                print(f"  - {user_data.get('email')} ({user_data.get('role')})")
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
    test_users_list_endpoint()
