"""
Debug script to check invitation status and tenant visibility
"""
import os
import sys
import django

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core_backend.settings')
django.setup()

from django.contrib.auth import get_user_model
from tenants.models import Tenant
from tenants.invitation_models import OrganizationInvitation

User = get_user_model()

print("=" * 80)
print("DEBUGGING INVITATION AND TENANT VISIBILITY")
print("=" * 80)

# Get the users
try:
    inviter = User.objects.get(email="user2@test.com")
    invited = User.objects.get(email="user4@test.com")
    
    print(f"\n✓ Inviter: {inviter.email}")
    print(f"  - ID: {inviter.id}")
    print(f"  - Tenant: {inviter.tenant}")
    print(f"  - Tenant ID: {inviter.tenant.id if inviter.tenant else None}")
    print(f"  - Tenant Name: {inviter.tenant.name if inviter.tenant else None}")
    
    print(f"\n✓ Invited User: {invited.email}")
    print(f"  - ID: {invited.id}")
    print(f"  - Tenant: {invited.tenant}")
    print(f"  - Tenant ID: {invited.tenant.id if invited.tenant else None}")
    print(f"  - Tenant Name: {invited.tenant.name if invited.tenant else None}")
    
except User.DoesNotExist as e:
    print(f"\n✗ User not found: {e}")
    exit(1)

# Check invitations
print("\n" + "=" * 80)
print("INVITATIONS")
print("=" * 80)

invitations = OrganizationInvitation.objects.filter(
    invited_user=invited
).order_by('-created_at')

if invitations.exists():
    for inv in invitations:
        print(f"\nInvitation #{inv.id}:")
        print(f"  - Tenant: {inv.tenant.name} (ID: {inv.tenant.id})")
        print(f"  - Invited by: {inv.invited_by.email}")
        print(f"  - Role: {inv.role}")
        print(f"  - Status: {inv.status}")
        print(f"  - Created: {inv.created_at}")
        print(f"  - Expires: {inv.expires_at}")
        print(f"  - Is Expired: {inv.is_expired}")
else:
    print("\n✗ No invitations found for user4@test.com")

# Check all tenants user4 should see
print("\n" + "=" * 80)
print("TENANTS VISIBLE TO USER4")
print("=" * 80)

# Get all tenants where user4 is a member
tenants = Tenant.objects.filter(
    members=invited,
    created_from_registration=False
).distinct()

print(f"\nTotal tenants: {tenants.count()}")
for tenant in tenants:
    print(f"\nTenant: {tenant.name}")
    print(f"  - ID: {tenant.id}")
    print(f"  - Slug: {tenant.slug}")
    print(f"  - Created from registration: {tenant.created_from_registration}")
    print(f"  - Is active: {tenant.is_active}")
    print(f"  - Members count: {tenant.members.count()}")
    
    # Check if user4 is in members
    is_member = tenant.members.filter(id=invited.id).exists()
    print(f"  - User4 is member: {is_member}")

# Check user4's primary tenant
print("\n" + "=" * 80)
print("USER4 PRIMARY TENANT")
print("=" * 80)

if invited.tenant:
    print(f"\nPrimary Tenant: {invited.tenant.name}")
    print(f"  - ID: {invited.tenant.id}")
    print(f"  - Slug: {invited.tenant.slug}")
    print(f"  - Created from registration: {invited.tenant.created_from_registration}")
else:
    print("\n✗ User4 has no primary tenant assigned")

# Check if inviter's tenant has user4 as member
print("\n" + "=" * 80)
print("INVITER'S TENANT MEMBERSHIP")
print("=" * 80)

if inviter.tenant:
    inviter_tenant = inviter.tenant
    print(f"\nInviter's Tenant: {inviter_tenant.name}")
    print(f"  - ID: {inviter_tenant.id}")
    print(f"  - Members:")
    for member in inviter_tenant.members.all():
        print(f"    - {member.email} (ID: {member.id})")
    
    is_user4_member = inviter_tenant.members.filter(id=invited.id).exists()
    print(f"\n  - User4 is member: {is_user4_member}")
else:
    print("\n✗ Inviter has no tenant")

print("\n" + "=" * 80)
print("SUMMARY")
print("=" * 80)

if invited.tenant and invited.tenant == inviter.tenant:
    print("\n✓ User4 is assigned to inviter's tenant")
    if inviter.tenant.members.filter(id=invited.id).exists():
        print("✓ User4 is in the tenant's members list")
    else:
        print("✗ User4 is NOT in the tenant's members list (THIS IS THE PROBLEM)")
else:
    print("\n✗ User4 is not assigned to inviter's tenant")

print("\n" + "=" * 80)
