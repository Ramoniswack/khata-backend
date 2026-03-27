"""
Migrate existing user-tenant relationships to the new membership system
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
from tenants.invitation_models import OrganizationInvitation

User = get_user_model()

print("=" * 80)
print("MIGRATING TO MEMBERSHIP SYSTEM")
print("=" * 80)

# Step 1: Create memberships for all users with a tenant assigned
print("\nStep 1: Creating memberships for users with assigned tenants...")
users_with_tenant = User.objects.filter(tenant__isnull=False).exclude(
    tenant__created_from_registration=True
)

created_count = 0
for user in users_with_tenant:
    membership, created = UserTenantMembership.objects.get_or_create(
        user=user,
        tenant=user.tenant,
        defaults={'role': user.role}
    )
    if created:
        created_count += 1
        print(f"  ✓ Created membership: {user.email} -> {user.tenant.name} ({user.role})")
    else:
        print(f"  - Membership already exists: {user.email} -> {user.tenant.name}")

print(f"\nCreated {created_count} new memberships")

# Step 2: Create memberships for all accepted invitations
print("\n" + "=" * 80)
print("Step 2: Creating memberships for accepted invitations...")
print("=" * 80)

accepted_invitations = OrganizationInvitation.objects.filter(status='accepted')
invitation_count = 0

for invitation in accepted_invitations:
    membership, created = UserTenantMembership.objects.get_or_create(
        user=invitation.invited_user,
        tenant=invitation.tenant,
        defaults={'role': invitation.role}
    )
    if created:
        invitation_count += 1
        print(f"  ✓ Created membership from invitation: {invitation.invited_user.email} -> {invitation.tenant.name} ({invitation.role})")
    else:
        # Update role if it changed
        if membership.role != invitation.role:
            membership.role = invitation.role
            membership.save()
            print(f"  ✓ Updated role: {invitation.invited_user.email} -> {invitation.tenant.name} ({invitation.role})")
        else:
            print(f"  - Membership already exists: {invitation.invited_user.email} -> {invitation.tenant.name}")

print(f"\nCreated {invitation_count} memberships from invitations")

# Step 3: Summary
print("\n" + "=" * 80)
print("SUMMARY")
print("=" * 80)

total_memberships = UserTenantMembership.objects.count()
print(f"\nTotal memberships: {total_memberships}")

# Show memberships by user
print("\nMemberships by user:")
for user in User.objects.filter(tenant_memberships__isnull=False).distinct():
    memberships = UserTenantMembership.objects.filter(user=user)
    print(f"\n{user.email}:")
    for membership in memberships:
        primary = " (PRIMARY)" if user.tenant == membership.tenant else ""
        print(f"  - {membership.tenant.name} ({membership.role}){primary}")

print("\n" + "=" * 80)
print("MIGRATION COMPLETE")
print("=" * 80)
