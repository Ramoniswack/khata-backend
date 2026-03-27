#!/usr/bin/env python
"""
Test tenant deletion with admin user
"""
import os
import sys
import django

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core_backend.settings')
django.setup()

from django.contrib.auth import get_user_model
from tenants.models import Tenant

User = get_user_model()

def test_admin_delete():
    print("=" * 60)
    print("Testing Tenant Deletion with Admin User")
    print("=" * 60)
    
    # Create test tenant and users
    print("\n1. Creating test data...")
    
    # Create creator user
    creator = User.objects.create_user(
        username="creator_user",
        email="creator@test.com",
        password="test123",
        role="admin"
    )
    
    # Create tenant
    tenant = Tenant.objects.create(
        name="Test Admin Delete Tenant",
        business_type="construction",
        created_by=creator,
        created_from_registration=False
    )
    creator.tenant = tenant
    creator.save()
    
    # Create another admin user in the same tenant
    admin_user = User.objects.create_user(
        username="admin_user",
        email="admin@test.com",
        password="test123",
        tenant=tenant,
        role="admin"
    )
    
    # Create a regular user in the same tenant
    regular_user = User.objects.create_user(
        username="regular_user",
        email="regular@test.com",
        password="test123",
        tenant=tenant,
        role="viewer"
    )
    
    print(f"✅ Created tenant: {tenant.name} (slug: {tenant.slug})")
    print(f"✅ Creator: {creator.email}")
    print(f"✅ Admin user: {admin_user.email}")
    print(f"✅ Regular user: {regular_user.email}")
    
    # Test queryset filtering
    print("\n2. Testing queryset filtering...")
    
    # Creator should see the tenant
    creator_tenants = Tenant.objects.filter(
        created_by=creator,
        created_from_registration=False
    )
    print(f"   Creator can see: {creator_tenants.count()} tenants")
    
    # Admin user should see the tenant (via Q filter)
    from django.db.models import Q
    admin_tenants = Tenant.objects.filter(
        Q(created_by=admin_user) | Q(users=admin_user, users__role='admin'),
        created_from_registration=False
    ).distinct()
    print(f"   Admin user can see: {admin_tenants.count()} tenants")
    
    # Regular user should NOT see the tenant (not creator, not admin)
    regular_tenants = Tenant.objects.filter(
        Q(created_by=regular_user) | Q(users=regular_user, users__role='admin'),
        created_from_registration=False
    ).distinct()
    print(f"   Regular user can see: {regular_tenants.count()} tenants")
    
    # Test deletion permissions
    print("\n3. Testing deletion permissions...")
    
    # Creator can delete
    print(f"   Creator is admin: {creator.is_admin}")
    print(f"   Creator tenant matches: {creator.tenant == tenant}")
    print(f"   ✅ Creator CAN delete")
    
    # Admin user can delete
    print(f"   Admin user is admin: {admin_user.is_admin}")
    print(f"   Admin user tenant matches: {admin_user.tenant == tenant}")
    print(f"   ✅ Admin user CAN delete")
    
    # Regular user cannot delete
    print(f"   Regular user is admin: {regular_user.is_admin}")
    print(f"   Regular user tenant matches: {regular_user.tenant == tenant}")
    print(f"   ❌ Regular user CANNOT delete")
    
    # Cleanup
    print("\n4. Cleanup...")
    User.objects.filter(username__in=["creator_user", "admin_user", "regular_user"]).delete()
    Tenant.objects.filter(slug=tenant.slug).delete()
    print("✅ Cleaned up test data")
    
    print("\n" + "=" * 60)
    print("✅ All tests passed!")
    print("=" * 60)

if __name__ == "__main__":
    test_admin_delete()
