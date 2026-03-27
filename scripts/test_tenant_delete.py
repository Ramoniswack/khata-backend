#!/usr/bin/env python
"""
Test tenant deletion to identify the 500 error
"""
import os
import sys
import django

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core_backend.settings')
django.setup()

from django.contrib.auth import get_user_model
from tenants.models import Tenant
from django.db import transaction

User = get_user_model()

def test_tenant_delete():
    print("=" * 60)
    print("Testing Tenant Deletion")
    print("=" * 60)
    
    # Create a test tenant
    print("\n1. Creating test tenant...")
    tenant = Tenant.objects.create(
        name="Test Delete Tenant",
        business_type="construction",
        created_from_registration=False
    )
    print(f"✅ Created tenant: {tenant.name} (slug: {tenant.slug})")
    
    # Create a user assigned to this tenant
    print("\n2. Creating user assigned to tenant...")
    user = User.objects.create_user(
        username="test_delete_user",
        email="test_delete@example.com",
        password="test123",
        tenant=tenant
    )
    print(f"✅ Created user: {user.email} (tenant: {user.tenant.name})")
    
    # Try to delete the tenant
    print("\n3. Attempting to delete tenant...")
    try:
        tenant_slug = tenant.slug
        tenant.delete()
        print(f"✅ Tenant deleted successfully")
        
        # Check if user still exists
        user.refresh_from_db()
        print(f"   User still exists: {user.email}")
        print(f"   User tenant: {user.tenant}")
        
    except Exception as e:
        print(f"❌ Error deleting tenant: {type(e).__name__}: {e}")
        import traceback
        traceback.print_exc()
    
    # Cleanup
    print("\n4. Cleanup...")
    try:
        if User.objects.filter(username="test_delete_user").exists():
            User.objects.filter(username="test_delete_user").delete()
            print("✅ Cleaned up test user")
    except Exception as e:
        print(f"⚠️  Cleanup warning: {e}")
    
    print("\n" + "=" * 60)
    print("Test Complete")
    print("=" * 60)

if __name__ == "__main__":
    test_tenant_delete()
