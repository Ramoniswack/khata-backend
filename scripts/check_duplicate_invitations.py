#!/usr/bin/env python
"""
Check for duplicate invitations that might cause unique constraint violations
"""
import os
import sys
import django

# Setup Django
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core_backend.settings')
django.setup()

from django.contrib.auth import get_user_model
from tenants.invitation_models import OrganizationInvitation
from django.db.models import Count

User = get_user_model()

def check_duplicates():
    """Check for duplicate invitations"""
    print("\n" + "="*60)
    print("CHECKING FOR DUPLICATE INVITATIONS")
    print("="*60)
    
    # Check for duplicate invitations (same tenant, user, status)
    duplicates = OrganizationInvitation.objects.values(
        'tenant', 'invited_user', 'status'
    ).annotate(
        count=Count('id')
    ).filter(count__gt=1)
    
    if duplicates:
        print(f"\n⚠️  Found {len(duplicates)} duplicate invitation combinations:")
        for dup in duplicates:
            print(f"\n  Tenant ID: {dup['tenant']}, User ID: {dup['invited_user']}, Status: {dup['status']}")
            print(f"  Count: {dup['count']}")
            
            # Show the actual invitations
            invitations = OrganizationInvitation.objects.filter(
                tenant_id=dup['tenant'],
                invited_user_id=dup['invited_user'],
                status=dup['status']
            )
            for inv in invitations:
                print(f"    - ID: {inv.id}, Created: {inv.created_at}, Expires: {inv.expires_at}")
    else:
        print("\n✅ No duplicate invitations found")
    
    # List all invitations
    print("\n" + "="*60)
    print("ALL INVITATIONS")
    print("="*60)
    
    invitations = OrganizationInvitation.objects.all().order_by('-created_at')
    print(f"\nTotal invitations: {invitations.count()}")
    
    for inv in invitations:
        print(f"\nID: {inv.id}")
        print(f"  Tenant: {inv.tenant.name} (ID: {inv.tenant_id})")
        print(f"  Invited User: {inv.invited_user.email} (ID: {inv.invited_user_id})")
        print(f"  Status: {inv.status}")
        print(f"  Role: {inv.role}")
        print(f"  Created: {inv.created_at}")
        print(f"  Expires: {inv.expires_at}")
        print(f"  Expired: {inv.is_expired}")

if __name__ == '__main__':
    check_duplicates()
