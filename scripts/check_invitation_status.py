#!/usr/bin/env python
"""
Check the invitation status and user tenant assignment
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
from tenants.invitation_models import OrganizationInvitation

def check_invitation():
    print("=" * 80)
    print("CHECKING INVITATION STATUS")
    print("=" * 80)
    
    # Check user2@test.com
    try:
        user2 = User.objects.get(email='user2@test.com')
        print(f"\n✓ user2@test.com found")
        print(f"  - Tenant: {user2.tenant}")
        print(f"  - Tenant ID: {user2.tenant.id if user2.tenant else None}")
        print(f"  - Role: {user2.role}")
    except User.DoesNotExist:
        print("\n✗ user2@test.com not found!")
        return
    
    # Check user4@test.com
    try:
        user4 = User.objects.get(email='user4@test.com')
        print(f"\n✓ user4@test.com found")
        print(f"  - Tenant: {user4.tenant}")
        print(f"  - Tenant ID: {user4.tenant.id if user4.tenant else None}")
        print(f"  - Role: {user4.role}")
    except User.DoesNotExist:
        print("\n✗ user4@test.com not found!")
        user4 = None
    
    # Check invitations
    print("\n" + "=" * 80)
    print("CHECKING INVITATIONS")
    print("=" * 80)
    
    if user2.tenant:
        invitations = OrganizationInvitation.objects.filter(
            tenant=user2.tenant
        ).order_by('-created_at')
        
        print(f"\n✓ Found {invitations.count()} invitations for tenant '{user2.tenant.name}'")
        
        for inv in invitations:
            print(f"\n  Invitation #{inv.id}:")
            print(f"    - Email: {inv.invited_user_email}")
            print(f"    - Status: {inv.status}")
            print(f"    - Role: {inv.role}")
            print(f"    - Invited by: {inv.invited_by.email if inv.invited_by else 'Unknown'}")
            print(f"    - Created: {inv.created_at}")
            print(f"    - Expires: {inv.expires_at}")
            
            # Check if invited user exists
            try:
                invited_user = User.objects.get(email=inv.invited_user_email)
                print(f"    - User exists: YES")
                print(f"    - User tenant: {invited_user.tenant}")
                print(f"    - User role: {invited_user.role}")
            except User.DoesNotExist:
                print(f"    - User exists: NO")
    
    # Check if user4 can see the tenant
    if user4 and user4.tenant:
        print("\n" + "=" * 80)
        print("CHECKING TENANT VISIBILITY FOR user4@test.com")
        print("=" * 80)
        
        # Check if tenant is visible (not created_from_registration)
        tenant = user4.tenant
        print(f"\n  Tenant: {tenant.name}")
        print(f"  - ID: {tenant.id}")
        print(f"  - Slug: {tenant.slug}")
        print(f"  - Created from registration: {tenant.created_from_registration}")
        print(f"  - Is active: {tenant.is_active}")
        
        if tenant.created_from_registration:
            print(f"\n  ⚠️  WARNING: This tenant is marked as 'created_from_registration=True'")
            print(f"     This means it will be HIDDEN from the /erp page!")
            print(f"     The TenantViewSet filters out these tenants.")
    
    print("\n" + "=" * 80)
    print("CHECK COMPLETE")
    print("=" * 80)


if __name__ == '__main__':
    check_invitation()
