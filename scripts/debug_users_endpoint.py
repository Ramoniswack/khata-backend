#!/usr/bin/env python
"""
Debug script to identify the exact cause of 500 error on /api/auth/users/ endpoint
"""
import os
import sys
import django

# Setup Django
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core_backend.settings')
django.setup()

from users.models import User
from users.serializers import UserSerializer

def test_user_serialization():
    """Test serializing each user to find which one causes the error"""
    print("=" * 80)
    print("TESTING USER SERIALIZATION")
    print("=" * 80)
    
    # Get user1@test.com's tenant
    try:
        current_user = User.objects.get(email='user1@test.com')
        print(f"\n✓ Current user: {current_user.email}")
        print(f"  - Tenant: {current_user.tenant}")
        print(f"  - Tenant ID: {current_user.tenant.id if current_user.tenant else None}")
        print(f"  - Role: {current_user.role}")
    except User.DoesNotExist:
        print("\n✗ user1@test.com not found!")
        return
    
    # Get all users in the same tenant
    if current_user.tenant:
        users = User.objects.filter(tenant=current_user.tenant)
        print(f"\n✓ Found {users.count()} users in tenant '{current_user.tenant.name}'")
    else:
        print("\n✗ Current user has no tenant!")
        return
    
    # Try to serialize each user
    print("\n" + "=" * 80)
    print("SERIALIZING EACH USER")
    print("=" * 80)
    
    for user in users:
        print(f"\n{'='*60}")
        print(f"Testing user: {user.email}")
        print(f"{'='*60}")
        print(f"  - ID: {user.id}")
        print(f"  - Username: {user.username}")
        print(f"  - Role: {user.role}")
        print(f"  - Tenant: {user.tenant}")
        print(f"  - Tenant ID: {user.tenant.id if user.tenant else None}")
        
        if user.tenant:
            print(f"  - Tenant name: {user.tenant.name}")
            print(f"  - Tenant slug: {user.tenant.slug}")
            print(f"  - Tenant active_modules type: {type(user.tenant.active_modules)}")
            print(f"  - Tenant active_modules: {user.tenant.active_modules}")
        
        try:
            # Try to serialize
            serializer = UserSerializer(user)
            data = serializer.data
            print(f"\n  ✓ Serialization SUCCESS")
            print(f"  - Serialized keys: {list(data.keys())}")
            
            # Check permissions field specifically
            if 'permissions' in data:
                print(f"  - Permissions keys: {list(data['permissions'].keys())}")
                if 'modules' in data['permissions']:
                    print(f"  - Module access: {data['permissions']['modules']}")
            
        except Exception as e:
            print(f"\n  ✗ Serialization FAILED!")
            print(f"  - Error type: {type(e).__name__}")
            print(f"  - Error message: {str(e)}")
            
            # Print full traceback
            import traceback
            print(f"\n  Full traceback:")
            traceback.print_exc()
            
            # Try to identify the specific issue
            print(f"\n  Debugging user.has_module_access():")
            try:
                result = user.has_module_access('sales')
                print(f"    - has_module_access('sales'): {result}")
            except Exception as e2:
                print(f"    - has_module_access() ERROR: {e2}")
                traceback.print_exc()
    
    print("\n" + "=" * 80)
    print("TEST COMPLETE")
    print("=" * 80)


if __name__ == '__main__':
    test_user_serialization()
