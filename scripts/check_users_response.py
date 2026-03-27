#!/usr/bin/env python
"""
Check what the /api/auth/users/ endpoint actually returns
"""
import os
import sys
import django
import json

# Setup Django
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core_backend.settings')
django.setup()

from django.test import RequestFactory
from users.views import UserViewSet
from users.models import User
from rest_framework.test import force_authenticate

def check_response_structure():
    """Check the actual response structure"""
    print("=" * 80)
    print("CHECKING /api/auth/users/ RESPONSE STRUCTURE")
    print("=" * 80)
    
    # Get user1@test.com
    user = User.objects.get(email='user1@test.com')
    print(f"\n✓ Testing with user: {user.email}")
    
    # Create a fake request
    factory = RequestFactory()
    request = factory.get('/api/auth/users/')
    force_authenticate(request, user=user)
    
    # Create viewset instance
    viewset = UserViewSet.as_view({'get': 'list'})
    
    # Call the viewset
    response = viewset(request)
    
    print(f"\n✓ Response status: {response.status_code}")
    print(f"\n✓ Response data type: {type(response.data)}")
    
    if isinstance(response.data, dict):
        print(f"\n✓ Response is a DICT with keys: {list(response.data.keys())}")
        print(f"\n✓ Full response structure:")
        print(json.dumps(response.data, indent=2, default=str))
    elif isinstance(response.data, list):
        print(f"\n✓ Response is a LIST with {len(response.data)} items")
        if response.data:
            print(f"\n✓ First item keys: {list(response.data[0].keys())}")
    else:
        print(f"\n✗ Unexpected response type: {type(response.data)}")
    
    print("\n" + "=" * 80)


if __name__ == '__main__':
    check_response_structure()
