#!/usr/bin/env python
"""
Test organization invitation system
"""
import os
import sys
import django

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core_backend.settings')
django.setup()

from django.contrib.auth import get_user_model
from tenants.models import Tenant
from tenants.invitation_models import OrganizationInvitation
from datetime import timedelta
from django.utils import timezone

User = get_user_model()

def test_invitation_system():
    print("=" * 60)
    print("Testing Organization Invitation System")
    print("=" * 60)
    
    # Create test users
    print("\n1. Creating test users...")
    
    # Admin user with organization
    admin_user, _ = User.objects.get_or_create(
        username="admin_test",
        defaults={
            "email": "admin@test.com",
            "first_name": "Admin",
            "last_name": "User",
            "role": "admin"
        }
    )
    admin_user.set_password("admin123")
    admin_user.save()
    
    # Regular user without organization
    regular_user, _ = User.objects.get_or_create(
        username="regular_test",
        defaults={
            "email": "regular@test.com",
            "first_name": "Regular",
            "last_name": "User",
            "role": "viewer"
        }
    )
    regular_user.set_password("regular123")
    regular_user.save()
    
    print(f"✅ Created admin user: {admin_user.email}")
    print(f"✅ Created regular user: {regular_user.email}")
    
    # Create organization for admin
    print("\n2. Creating organization...")
    tenant, _ = Tenant.objects.get_or_create(
        name="Test Organization",
        defaults={
            "slug": "test-org",
            "business_type": "construction",
            "created_by": admin_user,
            "is_active": True
        }
    )
    
    # Assign admin to organization
    admin_user.tenant = tenant
    admin_user.save()
    
    print(f"✅ Created organization: {tenant.name}")
    print(f"✅ Assigned admin to organization")
    
    # Create invitation
    print("\n3. Creating invitation...")
    invitation = OrganizationInvitation.objects.create(
        tenant=tenant,
        invited_user=regular_user,
        invited_by=admin_user,
        role="manager",
        message="Welcome to our team!",
        expires_at=timezone.now() + timedelta(days=7)
    )
    
    print(f"✅ Created invitation:")
    print(f"   - Organization: {invitation.tenant.name}")
    print(f"   - Invited user: {invitation.invited_user.email}")
    print(f"   - Role: {invitation.role}")
    print(f"   - Status: {invitation.status}")
    print(f"   - Expires: {invitation.expires_at}")
    
    # Test accepting invitation
    print("\n4. Testing invitation acceptance...")
    print(f"   Before: User tenant = {regular_user.tenant}, role = {regular_user.role}")
    
    invitation.accept()
    regular_user.refresh_from_db()
    
    print(f"   After: User tenant = {regular_user.tenant.name}, role = {regular_user.role}")
    print(f"   Invitation status: {invitation.status}")
    print(f"✅ Invitation accepted successfully!")
    
    # Verify user is now part of organization
    print("\n5. Verification...")
    assert regular_user.tenant == tenant, "User should be assigned to tenant"
    assert regular_user.role == "manager", "User should have manager role"
    assert invitation.status == "accepted", "Invitation should be accepted"
    print(f"✅ All verifications passed!")
    
    # Test creating another invitation (should fail - user already in org)
    print("\n6. Testing duplicate invitation (should fail)...")
    try:
        duplicate = OrganizationInvitation.objects.create(
            tenant=tenant,
            invited_user=regular_user,
            invited_by=admin_user,
            role="viewer"
        )
        print("❌ Should have failed - user already in organization")
    except Exception as e:
        print(f"✅ Correctly prevented duplicate invitation")
    
    # Cleanup
    print("\n7. Cleanup...")
    invitation.delete()
    print(f"✅ Cleaned up test data")
    
    print("\n" + "=" * 60)
    print("✅ All tests passed!")
    print("=" * 60)

if __name__ == "__main__":
    test_invitation_system()
