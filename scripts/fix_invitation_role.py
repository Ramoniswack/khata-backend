#!/usr/bin/env python
"""
Fix invitation role - update sonik@gmail.com's role from admin to manager
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

def fix_role():
    """Fix the role for sonik@gmail.com"""
    
    print("\n" + "="*80)
    print("FIXING INVITATION ROLE")
    print("="*80)
    
    # Find the users
    try:
        inviter = User.objects.get(email='mr.bishal.baniya@gmail.com')
        invitee = User.objects.get(email='sonik@gmail.com')
        tenant = Tenant.objects.get(id=128)  # abc construction
        
        print(f"\n✅ Found:")
        print(f"   - Inviter: {inviter.username}")
        print(f"   - Invitee: {invitee.username}")
        print(f"   - Tenant: {tenant.name}")
        
    except Exception as e:
        print(f"\n❌ Error finding users/tenant: {e}")
        return
    
    # Check current state
    print("\n" + "-"*80)
    print("CURRENT STATE")
    print("-"*80)
    
    # Check invitation
    try:
        invitation = OrganizationInvitation.objects.get(
            tenant=tenant,
            invited_user=invitee,
            status='accepted'
        )
        print(f"\n✅ Invitation found:")
        print(f"   - Role in invitation: {invitation.role}")
        print(f"   - Status: {invitation.status}")
    except OrganizationInvitation.DoesNotExist:
        print("\n❌ No accepted invitation found")
        invitation = None
    
    # Check membership
    try:
        membership = UserTenantMembership.objects.get(
            user=invitee,
            tenant=tenant
        )
        print(f"\n✅ Membership found:")
        print(f"   - Current role: {membership.role}")
        print(f"   - Is active: {membership.is_active}")
    except UserTenantMembership.DoesNotExist:
        print("\n❌ No membership found")
        membership = None
    
    # Check user's role field (if exists)
    if hasattr(invitee, 'role'):
        print(f"\n  User.role field: {invitee.role}")
    
    # Fix the role
    print("\n" + "-"*80)
    print("APPLYING FIX")
    print("-"*80)
    
    if invitation and membership:
        if invitation.role != membership.role:
            print(f"\n❌ Mismatch detected!")
            print(f"   Invitation role: {invitation.role}")
            print(f"   Membership role: {membership.role}")
            
            # Update membership to match invitation
            membership.role = invitation.role
            membership.save()
            print(f"\n✅ Updated membership role to: {invitation.role}")
            
            # Update user's role field if it exists
            if hasattr(invitee, 'role'):
                invitee.role = invitation.role
                invitee.save()
                print(f"✅ Updated user role field to: {invitation.role}")
        else:
            print(f"\n✅ Roles already match: {membership.role}")
    elif not membership and invitation:
        print("\n⚠️  Membership missing - creating it")
        membership = UserTenantMembership.objects.create(
            user=invitee,
            tenant=tenant,
            role=invitation.role
        )
        print(f"✅ Created membership with role: {invitation.role}")
    
    # Verify fix
    print("\n" + "-"*80)
    print("VERIFICATION")
    print("-"*80)
    
    membership = UserTenantMembership.objects.get(user=invitee, tenant=tenant)
    print(f"\n✅ Final membership role: {membership.role}")
    
    if hasattr(invitee, 'role'):
        invitee.refresh_from_db()
        print(f"✅ Final user role: {invitee.role}")
    
    print("\n" + "="*80)
    print("FIX COMPLETE")
    print("="*80)

if __name__ == '__main__':
    fix_role()
