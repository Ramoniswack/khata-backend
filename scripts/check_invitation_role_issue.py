#!/usr/bin/env python
"""
Check invitation role issue - invited as manager but showing as admin
"""
import os
import sys
import django

# Setup Django
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core_backend.settings')
django.setup()

from django.contrib.auth import get_user_model
from tenants.models import Tenant
from tenants.invitation_models import OrganizationInvitation
from tenants.membership_models import UserTenantMembership

User = get_user_model()

def check_invitation_role():
    """Check the invitation and membership for sonik@gmail.com"""
    
    print("\n" + "="*80)
    print("CHECKING INVITATION ROLE ISSUE")
    print("="*80)
    
    # Find the inviter
    try:
        inviter = User.objects.get(email='mr.bishal.baniya@gmail.com')
        print(f"\n✅ Inviter: {inviter.username} ({inviter.email})")
        print(f"   - User ID: {inviter.id}")
        if inviter.tenant:
            print(f"   - Tenant: {inviter.tenant.name} (ID: {inviter.tenant.id})")
    except User.DoesNotExist:
        print("\n❌ Inviter not found")
        return
    
    # Find the invitee
    try:
        invitee = User.objects.get(email='sonik@gmail.com')
        print(f"\n✅ Invitee: {invitee.username} ({invitee.email})")
        print(f"   - User ID: {invitee.id}")
        if invitee.tenant:
            print(f"   - Current Tenant: {invitee.tenant.name} (ID: {invitee.tenant.id})")
    except User.DoesNotExist:
        print("\n❌ Invitee not found")
        invitee = None
    
    # Check invitations
    print("\n" + "-"*80)
    print("CHECKING INVITATIONS")
    print("-"*80)
    
    invitations = OrganizationInvitation.objects.filter(invited_user__email='sonik@gmail.com')
    print(f"\nFound {invitations.count()} invitation(s) for sonik@gmail.com:")
    
    for inv in invitations:
        print(f"\n  Invitation ID: {inv.id}")
        print(f"  - Tenant: {inv.tenant.name} (ID: {inv.tenant.id})")
        print(f"  - Role: {inv.role}")
        print(f"  - Status: {inv.status}")
        print(f"  - Invited by: {inv.invited_by.username if inv.invited_by else 'N/A'}")
        print(f"  - Created: {inv.created_at}")
        print(f"  - Accepted: {inv.accepted_at if inv.accepted_at else 'Not yet'}")
    
    # Check memberships
    if invitee:
        print("\n" + "-"*80)
        print("CHECKING MEMBERSHIPS")
        print("-"*80)
        
        memberships = UserTenantMembership.objects.filter(user=invitee)
        print(f"\nFound {memberships.count()} membership(s) for {invitee.email}:")
        
        for mem in memberships:
            print(f"\n  Membership ID: {mem.id}")
            print(f"  - Tenant: {mem.tenant.name} (ID: {mem.tenant.id})")
            print(f"  - Role: {mem.role}")
            print(f"  - Is Active: {mem.is_active}")
            print(f"  - Created: {mem.created_at}")
    
    # Check if there's a mismatch
    print("\n" + "-"*80)
    print("ANALYSIS")
    print("-"*80)
    
    if invitations.exists() and invitee:
        latest_inv = invitations.order_by('-created_at').first()
        print(f"\nLatest invitation role: {latest_inv.role}")
        
        if invitee.tenant:
            try:
                membership = UserTenantMembership.objects.get(
                    user=invitee,
                    tenant=invitee.tenant,
                    is_active=True
                )
                print(f"Current membership role: {membership.role}")
                
                if latest_inv.role != membership.role:
                    print(f"\n❌ MISMATCH DETECTED!")
                    print(f"   Invited as: {latest_inv.role}")
                    print(f"   But showing as: {membership.role}")
                else:
                    print(f"\n✅ Roles match: {membership.role}")
            except UserTenantMembership.DoesNotExist:
                print("\n❌ No active membership found")
    
    print("\n" + "="*80)

if __name__ == '__main__':
    check_invitation_role()
