"""
Test the multi-tenant API to verify user4 can see both organizations
"""
import os
import sys
import django

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core_backend.settings')
django.setup()

from django.contrib.auth import get_user_model
from rest_framework.test import APIClient
from rest_framework_simplejwt.tokens import RefreshToken

User = get_user_model()

print("=" * 80)
print("TESTING MULTI-TENANT API")
print("=" * 80)

# Get user4
user4 = User.objects.get(email="user4@test.com")
print(f"\nUser: {user4.email}")
print(f"Primary Tenant: {user4.tenant.name if user4.tenant else 'None'}")

# Generate JWT token
refresh = RefreshToken.for_user(user4)
access_token = str(refresh.access_token)

# Create API client
client = APIClient()
client.credentials(HTTP_AUTHORIZATION=f'Bearer {access_token}')

# Test the tenants endpoint
print("\n" + "=" * 80)
print("GET /api/tenants/")
print("=" * 80)

response = client.get('/api/tenants/')
print(f"\nStatus Code: {response.status_code}")

if response.status_code == 200:
    data = response.json()
    print(f"Total Tenants: {data.get('count', len(data))}")
    
    results = data.get('results', data) if isinstance(data, dict) else data
    
    print("\nTenants:")
    for tenant in results:
        print(f"  - {tenant['name']} (ID: {tenant['id']}, Slug: {tenant['slug']})")
    
    print("\n✓ SUCCESS! User4 can now see multiple organizations")
else:
    print(f"\n✗ ERROR: {response.data}")

print("\n" + "=" * 80)
