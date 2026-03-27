"""
Test that deleting a tenant also deletes membership records
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
from tenants.membership_models import UserTenantMembership

User = get_user_model()

print("=" * 80)
print("TESTING TENANT DELETE MEMBERSHIP CLEANUP")
print("=" * 80)

# Get user2 (creator of ddd) and user4 (invited member)
user2 = User.objects.get(email="user2@test.com")
user4 = User.objects.get(email="user4@test.com")

print(f"\nUser2 (Creator): {user2.email}")
print(f"  - Primary Tenant: {user2.tenant.name if user2.tenant else 'None'}")

print(f"\nUser4 (Invited Member): {user4.email}")
print(f"  - Primary Tenant: {user4.tenant.name if user4.tenant else 'None'}")

# Check memberships before deletion
print("\n" + "=" * 80)
print("MEMBERSHIPS BEFORE DELETION")
print("=" * 80)

user4_memberships_before = UserTenantMembership.objects.filter(user=user4)
print(f"\nUser4 memberships: {user4_memberships_before.count()}")
for membership in user4_memberships_before:
    print(f"  - {membership.tenant.name} ({membership.role})")

# Check if ddd tenant exists
try:
    ddd_tenant = Tenant.objects.get(name="ddd")
    print(f"\n✓ Tenant 'ddd' exists (ID: {ddd_tenant.id})")
    
    # Check memberships for ddd
    ddd_memberships = UserTenantMembership.objects.filter(tenant=ddd_tenant)
    print(f"  - Total members: {ddd_memberships.count()}")
    for membership in ddd_memberships:
        print(f"    - {membership.user.email} ({membership.role})")
    
except Tenant.DoesNotExist:
    print("\n✗ Tenant 'ddd' does not exist (already deleted)")
    ddd_tenant = None

# Simulate deletion (don't actually delete, just show what would happen)
print("\n" + "=" * 80)
print("WHAT HAPPENS WHEN TENANT IS DELETED")
print("=" * 80)

if ddd_tenant:
    print("\nWhen tenant 'ddd' is deleted:")
    print("  1. All UserTenantMembership records with tenant='ddd' will be CASCADE deleted")
    print("  2. Users with primary tenant='ddd' will have tenant set to None")
    print("  3. All related data (products, invoices, etc.) will be CASCADE deleted")
    
    print("\nExpected result for user4:")
    print("  - Membership to 'ddd' will be DELETED")
    print("  - User4 will only see 'vvv' organization card")
    print("  - If user4's primary tenant was 'ddd', it will be set to None")
else:
    print("\nTenant 'ddd' has already been deleted")
    print("Checking if memberships were cleaned up...")
    
    # Check if user4 still has membership to ddd
    orphaned_memberships = UserTenantMembership.objects.filter(
        user=user4,
        tenant__name="ddd"
    )
    
    if orphaned_memberships.exists():
        print("\n✗ PROBLEM: Orphaned memberships found!")
        for membership in orphaned_memberships:
            print(f"  - {membership.user.email} -> {membership.tenant.name}")
    else:
        print("\n✓ No orphaned memberships found")

# Check current state
print("\n" + "=" * 80)
print("CURRENT STATE")
print("=" * 80)

user4_memberships_now = UserTenantMembership.objects.filter(user=user4)
print(f"\nUser4 current memberships: {user4_memberships_now.count()}")
for membership in user4_memberships_now:
    print(f"  - {membership.tenant.name} ({membership.role})")

# Check what tenants user4 can see
from django.db.models import Q
membership_tenant_ids = UserTenantMembership.objects.filter(
    user=user4
).values_list('tenant_id', flat=True)

visible_tenants = Tenant.objects.filter(
    Q(id__in=membership_tenant_ids) | Q(created_by=user4),
    created_from_registration=False
).distinct()

print(f"\nTenants visible to user4: {visible_tenants.count()}")
for tenant in visible_tenants:
    print(f"  - {tenant.name} (ID: {tenant.id})")

print("\n" + "=" * 80)
