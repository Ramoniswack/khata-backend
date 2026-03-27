#!/usr/bin/env python
"""
Test script to debug invitation accept 500 error with real users
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
    """Test accepting an invitation with real users"""
    print("\n" + "="*60)
    print("TESTING INVITATION ACCEPT WITH REAL USERS")
    print("="*60)
    
    # List all users
    print("\nAvailable users:")
    users = User.objects.all()
    for user in users:
        print(f"  - {user.email} (ID: {user.id}, tenant: {user.tenant_id}, role: {user.role})")
    
    if users.count() < 2:
        print("\n❌ Need at least 2 users to test invitations")
        return False
    
    # Use first user as inviter (should have a tenant)
    inviter = users.filter(tenant__isnull=False).first()
    if not inviter:
        print("\n❌ No user with tenant found to be inviter")
        return False
    
    # Use another user as invitee
    invitee = users.exclude(id=inviter.id).first()
    if not invitee:
        print("\n❌ No second user found to be invitee")
        return False
    
    tenant = inviter.tenant
    
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
        try:
            invitation = OrganizationInvitation.objects.create(
                tenant=tenant,
                invited_user=invitee,
                invited_by=inviter,
                role='manager',
                message='Join our team!',
                expires_at=timezone.now() + timedelta(days=7)
            )
            print(f"✓ Invitation created (ID: {invitation.id})")
        except Exception as e:
            print(f"❌ Failed to create invitation: {e}")
            import traceback
            traceback.print_exc()
            return False
    
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
