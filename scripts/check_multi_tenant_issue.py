"""
Check the multi-tenant membership issue
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
print("MULTI-TENANT MEMBERSHIP ISSUE")
print("=" * 80)

# Get users
user2 = User.objects.get(email="user2@test.com")
user4 = User.objects.get(email="user4@test.com")

print(f"\nUser2 (Inviter):")
print(f"  - Email: {user2.email}")
print(f"  - Current Tenant: {user2.tenant.name if user2.tenant else 'None'} (ID: {user2.tenant.id if user2.tenant else 'None'})")
print(f"  - Role: {user2.role}")

print(f"\nUser4 (Invited):")
print(f"  - Email: {user4.email}")
print(f"  - Current Tenant: {user4.tenant.name if user4.tenant else 'None'} (ID: {user4.tenant.id if user4.tenant else 'None'})")
print(f"  - Role: {user4.role}")

# Check all invitations for user4
print("\n" + "=" * 80)
print("ALL INVITATIONS FOR USER4")
print("=" * 80)

invitations = OrganizationInvitation.objects.filter(invited_user=user4).order_by('-created_at')
for inv in invitations:
    print(f"\nInvitation #{inv.id}:")
    print(f"  - Tenant: {inv.tenant.name} (ID: {inv.tenant.id})")
    print(f"  - Invited by: {inv.invited_by.email if inv.invited_by else 'Unknown'}")
    print(f"  - Role: {inv.role}")
    print(f"  - Status: {inv.status}")
    print(f"  - Created: {inv.created_at}")

# Check what tenants user4 can see with current query
print("\n" + "=" * 80)
print("TENANTS USER4 CAN SEE (Current Query)")
print("=" * 80)

from django.db.models import Q
tenants = Tenant.objects.filter(
    Q(users=user4) | Q(created_by=user4),
    created_from_registration=False
).distinct()

print(f"\nTotal: {tenants.count()}")
for tenant in tenants:
    print(f"  - {tenant.name} (ID: {tenant.id})")

# The problem
print("\n" + "=" * 80)
print("THE PROBLEM")
print("=" * 80)

print("\nThe User model has a single 'tenant' ForeignKey field.")
print("When a user accepts an invitation, their tenant is OVERWRITTEN.")
print("This means users can only be in ONE organization at a time.")
print("\nCurrent Design:")
print("  - User.tenant = ForeignKey (ONE tenant)")
print("  - When invitation accepted: user.tenant = invitation.tenant")
print("  - Previous tenant assignment is LOST")

print("\n" + "=" * 80)
print("SOLUTION OPTIONS")
print("=" * 80)

print("\n1. MULTI-TENANT MEMBERSHIP (Recommended)")
print("   - Add a UserTenantMembership model with ManyToMany relationship")
print("   - Keep User.tenant as the 'active' tenant")
print("   - Users can switch between their organizations")
print("   - /erp page shows ALL organizations user is a member of")

print("\n2. SINGLE TENANT ONLY (Current Behavior)")
print("   - Keep current design")
print("   - Users can only be in ONE organization")
print("   - Accepting a new invitation removes them from previous org")
print("   - Simpler but less flexible")

print("\n" + "=" * 80)
