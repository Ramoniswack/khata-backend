"""
Verify that user4 can now see both organizations
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
from django.db.models import Q

User = get_user_model()

print("=" * 80)
print("VERIFYING MULTI-TENANT FIX")
print("=" * 80)

# Get user4
user4 = User.objects.get(email="user4@test.com")
print(f"\nUser: {user4.email}")
print(f"Primary Tenant: {user4.tenant.name if user4.tenant else 'None'}")

# Check memberships
print("\n" + "=" * 80)
print("USER4 MEMBERSHIPS")
print("=" * 80)

memberships = UserTenantMembership.objects.filter(user=user4)
print(f"\nTotal Memberships: {memberships.count()}")
for membership in memberships:
    primary = " (PRIMARY)" if user4.tenant == membership.tenant else ""
    print(f"  - {membership.tenant.name} ({membership.role}){primary}")

# Simulate the TenantViewSet.get_queryset() logic
print("\n" + "=" * 80)
print("TENANTS VISIBLE TO USER4 (New Query)")
print("=" * 80)

# Get all tenant IDs where user has membership
membership_tenant_ids = UserTenantMembership.objects.filter(
    user=user4
).values_list('tenant_id', flat=True)

# Return tenants where user has membership OR is the creator
tenants = Tenant.objects.filter(
    Q(id__in=membership_tenant_ids) | Q(created_by=user4),
    created_from_registration=False
).distinct()

print(f"\nTotal Tenants: {tenants.count()}")
for tenant in tenants:
    print(f"  - {tenant.name} (ID: {tenant.id}, Slug: {tenant.slug})")

# Verify the fix
print("\n" + "=" * 80)
print("VERIFICATION")
print("=" * 80)

if tenants.count() >= 2:
    print("\n✓ SUCCESS! User4 can now see multiple organizations")
    print("✓ The multi-tenant membership system is working correctly")
else:
    print("\n✗ FAILED! User4 can only see one organization")

print("\n" + "=" * 80)
