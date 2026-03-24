import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core_backend.settings')
django.setup()

from rest_framework.test import APIClient
from users.models import User
from tenants.models import Tenant
from hr.models import LeaveType

# Get tenant and user
tenant = Tenant.objects.first()
user = User.objects.filter(is_superuser=True).first()

if not user:
    print("No superuser found. Creating one...")
    user = User.objects.create_superuser(
        username='admin',
        email='admin@test.com',
        password='admin123',
        tenant=tenant
    )

print(f"Tenant: {tenant.name}")
print(f"User: {user.username}")

# Get leave type
leave_type = LeaveType.objects.filter(tenant=tenant).first()
if not leave_type:
    print("\n⚠ No leave types found. Run seed_leave_types.py first.")
    sys.exit(1)

print(f"Leave Type: {leave_type.name} (ID: {leave_type.id})")

# Create API client
client = APIClient()
client.force_authenticate(user=user)

# Test leave request creation
data = {
    'leave_type': leave_type.id,
    'start_date': '2024-03-25',
    'end_date': '2024-03-27',
    'reason': 'Test leave request via API'
}

print(f"\nSending POST request to /api/hr/leave-requests/")
print(f"Data: {data}")

response = client.post('/api/hr/leave-requests/', data, format='json')

print(f"\nResponse Status: {response.status_code}")
print(f"Response Data: {response.data}")

if response.status_code == 201:
    print("\n✓ Leave request created successfully!")
    # Clean up
    from hr.models import LeaveRequest
    LeaveRequest.objects.filter(id=response.data['id']).delete()
    print("✓ Test leave request deleted")
else:
    print("\n✗ Failed to create leave request")
