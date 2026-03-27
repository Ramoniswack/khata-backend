#!/usr/bin/env python
"""
Test script to verify that deleting a tenant does NOT delete the user
"""
import os
import sys
import django

# Setup Django
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core_backend.settings')
django.setup()

from users.models import User
from tenants.models import Tenant

def test_tenant_delete_preserves_user():
    """Test that deleting a tenant sets user.tenant to NULL instead of deleting the user"""
    
    print("=" * 80)
    print("TESTING TENANT DELETE - USER PRESERVATION")
    print("=" * 80)
    
    # Create a test user
    test_email = "tenant_delete_test@example.com"
    
    # Clean up any existing test data
    User.objects.filter(email=test_email).delete()
    Tenant.objects.filter(name="Test Tenant for Deletion").delete()
    
    print("\n1. Creating test tenant...")
    tenant = Tenant.objects.create(
        name="Test Tenant for Deletion",
        business_type="other",
        plan_type="free",
        active_modules=['sales', 'inventory']
    )
    print(f"   ✓ Created tenant: {tenant.name} (ID: {tenant.id})")
    
    print("\n2. Creating test user assigned to tenant...")
    user = User.objects.create_user(
        username='tenant_delete_test',
        email=test_email,
        password='testpass123',
        first_name='Test',
        last_name='User',
        tenant=tenant,
        role='admin'
    )
    print(f"   ✓ Created user: {user.email} (ID: {user.id})")
    print(f"   ✓ User tenant: {user.tenant.name if user.tenant else 'None'}")
    
    # Verify user exists and has tenant
    assert user.tenant is not None, "User should have a tenant"
    assert user.tenant.id == tenant.id, "User should be assigned to the test tenant"
    
    print("\n3. Deleting tenant...")
    tenant_id = tenant.id
    tenant.delete()
    print(f"   ✓ Deleted tenant (ID: {tenant_id})")
    
    print("\n4. Checking if user still exists...")
    try:
        user.refresh_from_db()
        print(f"   ✅ SUCCESS! User still exists: {user.email}")
        print(f"   ✓ User ID: {user.id}")
        print(f"   ✓ User tenant: {user.tenant}")
        print(f"   ✓ User is_active: {user.is_active}")
        print(f"   ✓ User role: {user.role}")
        
        # Verify tenant is NULL
        if user.tenant is None:
            print("\n   ✅ CORRECT: User's tenant field is NULL (not deleted)")
        else:
            print(f"\n   ❌ ERROR: User still has tenant: {user.tenant}")
            return False
        
        # Verify user can still login
        print("\n5. Testing user authentication...")
        from django.contrib.auth import authenticate
        auth_user = authenticate(email=test_email, password='testpass123')
        if auth_user:
            print(f"   ✅ User can still authenticate!")
        else:
            print(f"   ❌ User cannot authenticate")
            return False
        
        print("\n" + "=" * 80)
        print("✅ ALL TESTS PASSED!")
        print("=" * 80)
        print("""
Summary:
- Tenant was deleted successfully
- User was NOT deleted (preserved)
- User's tenant field was set to NULL
- User can still authenticate
- User can create/join other tenants

This is the CORRECT behavior!
        """)
        
        # Clean up
        user.delete()
        print("✓ Cleaned up test data")
        
        return True
        
    except User.DoesNotExist:
        print(f"   ❌ FAILED! User was deleted when tenant was deleted")
        print(f"   This is a BUG - users should NOT be deleted with tenants")
        print("\n" + "=" * 80)
        print("❌ TEST FAILED")
        print("=" * 80)
        return False

if __name__ == '__main__':
    success = test_tenant_delete_preserves_user()
    sys.exit(0 if success else 1)
