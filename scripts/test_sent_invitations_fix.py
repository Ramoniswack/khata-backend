"""
Test the sent invitations endpoint fix
"""
import os
import sys
import django

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core_backend.settings')
django.setup()

from django.contrib.auth import get_user_model
from rest_framework.test import APIRequestFactory, force_authenticate
from tenants.views import OrganizationInvitationViewSet
from tenants.membership_models import UserTenantMembership

User = get_user_model()

print("=" * 80)
print("TESTING SENT INVITATIONS ENDPOINT FIX")
print("=" * 80)

# Get user2 (admin of ddd)
user2 = User.objects.get(email="user2@test.com")
print(f"\nUser: {user2.email}")
print(f"Primary Tenant: {user2.tenant.name if user2.tenant else 'None'}")
print(f"Role: {user2.role}")

# Check memberships
memberships = UserTenantMembership.objects.filter(user=user2)
print(f"\nMemberships:")
for membership in memberships:
    print(f"  - {membership.tenant.name} ({membership.role})")

# Test the sent endpoint
print("\n" + "=" * 80)
print("TESTING /api/tenants/invitations/sent/")
print("=" * 80)

factory = APIRequestFactory()
request = factory.get('/api/tenants/invitations/sent/')
force_authenticate(request, user=user2)

view = OrganizationInvitationViewSet.as_view({'get': 'sent'})
response = view(request)

print(f"\nStatus Code: {response.status_code}")

if response.status_code == 200:
    print(f"✓ SUCCESS! Invitations returned: {len(response.data)}")
    for inv in response.data:
        print(f"  - {inv['invited_user_name']} to {inv['tenant_name']} ({inv['status']})")
else:
    print(f"✗ ERROR: {response.data}")

print("\n" + "=" * 80)
