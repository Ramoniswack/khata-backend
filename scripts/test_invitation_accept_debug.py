#!/usr/bin/env python
"""
Test script to debug invitation accept 500 error
"""
import os
import sys
import django

# Setup Django
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core_backend.settings')
django.setup()

from django.contrib.auth import get_user_model
from tenants.models import Tenant
from tenants.invitation_models import OrganizationInvitation
from tenants.membership_models import UserTenantMembership
from django.utils import timezone
from datetime import timedelta

User = get_user_model()

def test_invitation_accept():
    """Test accepting an invitation"""
    print("\n" + "="*60)
    print("TESTING INVITATION ACCEPT")
    print("="*60)
    
    # Get or create test users
    inviter = User.objects.filter(email='admin@test.com').first()
    invitee = User.objects.filter(email='user@test.com').first()
    
    if not inviter:
        print("❌ Inviter not found. Creating test user...")
        inviter = User.objects.create_user(
            email='admin@test.com',
            username='admin',
            password='test123',
            first_name='Admin',
            last_name='User',
            role='admin'
        )
    
    if not invitee:
        print("❌ Invitee not found. Creating test user...")
        invitee = User.objects.create_user(
            email='user@test.com',
            username='testuser',
            password='test123',
            first_name='Test',
            last_name='User',
            role='viewer'
        )
    
    # Get or create test tenant
    tenant = Tenant.objects.filter(name='Test Organization').first()
    if not tenant:
        print("❌ Tenant not found. Creating test tenant...")
        tenant = Tenant.objects.create(
            name='Test Organization',
            slug='test-org',
            business_type='hardware',
            created_by=inviter,
            created_from_registration=False
        )
        # Create membership for inviter
        UserTenantMembership.objects.create(
            user=inviter,
            tenant=tenant,
            role='admin'
        )
        inviter.tenant = tenant
        inviter.save()
    
    print(f"\n✓ Inviter: {inviter.email} (ID: {inviter.id})")
    print(f"✓ Invitee: {invitee.email} (ID: {invitee.id})")
    print(f"✓ Tenant: {tenant.name} (ID: {tenant.id})")
    
    # Check if invitation already exists
    existing_invitation = OrganizationInvitation.objects.filter(
        tenant=tenant,
        invited_user=invitee,
        status='pending'
    ).first()
    
    if existing_invitation:
        print(f"\n✓ Using existing invitation (ID: {existing_invitation.id})")
        invitation = existing_invitation
    else:
        # Create invitation
        print("\n📧 Creating invitation...")
        invitation = OrganizationInvitation.objects.create(
            tenant=tenant,
            invited_user=invitee,
            invited_by=inviter,
            role='manager',
            message='Join our team!',
            expires_at=timezone.now() + timedelta(days=7)
        )
        print(f"✓ Invitation created (ID: {invitation.id})")
    
    print(f"\nInvitation details:")
    print(f"  - Status: {invitation.status}")
    print(f"  - Role: {invitation.role}")
    print(f"  - Expired: {invitation.is_expired}")
    print(f"  - Expires at: {invitation.expires_at}")
    
    # Check invitee's current tenant
    print(f"\nInvitee current state:")
    print(f"  - Current tenant: {invitee.tenant}")
    print(f"  - Current role: {invitee.role}")
    
    # Check existing memberships
    existing_memberships = UserTenantMembership.objects.filter(user=invitee)
    print(f"  - Existing memberships: {existing_memberships.count()}")
    for membership in existing_memberships:
        print(f"    * {membership.tenant.name} ({membership.role})")
    
    # Try to accept invitation
    print("\n🔄 Attempting to accept invitation...")
    try:
        result = invitation.accept()
        print(f"✅ SUCCESS! Invitation accepted: {result}")
        
        # Refresh from database
        invitation.refresh_from_db()
        invitee.refresh_from_db()
        
        print(f"\nAfter acceptance:")
        print(f"  - Invitation status: {invitation.status}")
        print(f"  - Invitee tenant: {invitee.tenant}")
        print(f"  - Invitee role: {invitee.role}")
        
        # Check memberships
        memberships = UserTenantMembership.objects.filter(user=invitee)
        print(f"  - Total memberships: {memberships.count()}")
        for membership in memberships:
            print(f"    * {membership.tenant.name} ({membership.role})")
        
    except Exception as e:
        print(f"❌ ERROR: {type(e).__name__}: {str(e)}")
        import traceback
        print("\nFull traceback:")
        traceback.print_exc()
        return False
    
    return True

if __name__ == '__main__':
    success = test_invitation_accept()
    sys.exit(0 if success else 1)
