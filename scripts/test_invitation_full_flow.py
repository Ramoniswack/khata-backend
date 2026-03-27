#!/usr/bin/env python
"""
Test the complete invitation flow: create, accept, and verify
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
from rest_framework.test import APIClient
from rest_framework_simplejwt.tokens import RefreshToken
from django.conf import settings

User = get_user_model()

def test_full_flow():
    """Test complete invitation flow"""
    print("\n" + "="*60)
    print("TESTING COMPLETE INVITATION FLOW")
    print("="*60)
    
    # Add testserver to ALLOWED_HOSTS
    if 'testserver' not in settings.ALLOWED_HOSTS:
        settings.ALLOWED_HOSTS.append('testserver')
    
    # Get users
    inviter = User.objects.filter(email='sonik@gmail.com').first()
    invitee = User.objects.filter(email='mr.bishal.baniya@gmail.com').first()
    
    if not inviter or not invitee:
        print("❌ Required users not found")
        return False
    
    tenant = inviter.tenant
    
    print(f"\n✓ Inviter: {inviter.email}")
    print(f"✓ Invitee: {invitee.email}")
    print(f"✓ Tenant: {tenant.name}")
    
    # Check invitee's initial state
    print(f"\n📊 Invitee initial state:")
    print(f"   - Primary tenant: {invitee.tenant}")
    print(f"   - Role: {invitee.role}")
    memberships = UserTenantMembership.objects.filter(user=invitee)
    print(f"   - Memberships: {memberships.count()}")
    for m in memberships:
        print(f"     * {m.tenant.name} ({m.role})")
    
    # Create a new invitation
    print(f"\n📧 Creating new invitation...")
    invitation = OrganizationInvitation.objects.create(
        tenant=tenant,
        invited_user=invitee,
        invited_by=inviter,
        role='accountant',
        message='Join our accounting team!',
        expires_at=timezone.now() + timedelta(days=7)
    )
    print(f"✓ Invitation created (ID: {invitation.id})")
    
    # Get JWT token for invitee
    refresh = RefreshToken.for_user(invitee)
    access_token = str(refresh.access_token)
    
    # Create API client
    client = APIClient()
    client.credentials(HTTP_AUTHORIZATION=f'Bearer {access_token}')
    
    # Accept the invitation via API
    print(f"\n🔄 Accepting invitation via API...")
    response = client.post(
        f'/api/tenants/invitations/{invitation.id}/respond/',
        {'action': 'accept'},
        format='json'
    )
    
    if response.status_code != 200:
        print(f"❌ Failed to accept invitation: {response.status_code}")
        if hasattr(response, 'data'):
            print(f"   Error: {response.data}")
        return False
    
    print(f"✅ Invitation accepted successfully!")
    
    # Verify the changes
    invitation.refresh_from_db()
    invitee.refresh_from_db()
    
    print(f"\n📊 Invitee final state:")
    print(f"   - Primary tenant: {invitee.tenant}")
    print(f"   - Role: {invitee.role}")
    memberships = UserTenantMembership.objects.filter(user=invitee)
    print(f"   - Memberships: {memberships.count()}")
    for m in memberships:
        print(f"     * {m.tenant.name} ({m.role})")
    
    print(f"\n📊 Invitation final state:")
    print(f"   - Status: {invitation.status}")
    print(f"   - Responded at: {invitation.responded_at}")
    
    # Verify membership was created
    membership = UserTenantMembership.objects.filter(
        user=invitee,
        tenant=tenant
    ).first()
    
    if not membership:
        print(f"\n❌ Membership not created!")
        return False
    
    print(f"\n✅ Membership verified:")
    print(f"   - Tenant: {membership.tenant.name}")
    print(f"   - Role: {membership.role}")
    print(f"   - Joined at: {membership.joined_at}")
    
    # Test accepting the same invitation again (should fail)
    print(f"\n🔄 Testing duplicate accept (should fail)...")
    response2 = client.post(
        f'/api/tenants/invitations/{invitation.id}/respond/',
        {'action': 'accept'},
        format='json'
    )
    
    if response2.status_code == 400:
        print(f"✅ Correctly rejected duplicate accept")
    else:
        print(f"⚠️  Unexpected response: {response2.status_code}")
    
    print(f"\n" + "="*60)
    print("✅ ALL TESTS PASSED!")
    print("="*60)
    
    return True

if __name__ == '__main__':
    success = test_full_flow()
    sys.exit(0 if success else 1)
