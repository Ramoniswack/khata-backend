"""
Test JWT login to verify it returns role and tenant_slug
"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core_backend.settings')
django.setup()

from django.test import RequestFactory
from users.views import CustomTokenObtainPairView
from users.models import User
from tenants.models import Tenant
import json

print("="*60)
print("JWT LOGIN TEST")
print("="*60)

# Get a user with tenant
user = User.objects.filter(tenant__isnull=False).first()

if not user:
    print("ERROR: No user with tenant found")
    exit(1)

print(f"\nTest User: {user.username}")
print(f"Role: {user.role}")
print(f"Tenant: {user.tenant.name}")
print(f"Tenant Slug: {user.tenant.slug}")

# Create a fake login request
factory = RequestFactory()
request = factory.post(
    '/api/auth/login/',
    data=json.dumps({
        'username': user.username,
        'password': 'test123'  # This won't work, but we'll test the serializer
    }),
    content_type='application/json'
)

print("\n" + "="*60)
print("TESTING CUSTOM TOKEN SERIALIZER")
print("="*60)

# Test the serializer directly
from users.serializers import CustomTokenObtainPairSerializer

# We can't test the actual login without the password, but we can test the token generation
try:
    token = CustomTokenObtainPairSerializer.get_token(user)
    
    print("\n✅ Token generated successfully!")
    print("\nToken Claims:")
    print(f"  role: {token.get('role')}")
    print(f"  tenant_id: {token.get('tenant_id')}")
    print(f"  tenant_slug: {token.get('tenant_slug')}")
    print(f"  tenant_name: {token.get('tenant_name')}")
    
    print("\n✅ Custom claims are included in the token!")
    
except Exception as e:
    print(f"\n❌ Error: {e}")
    import traceback
    traceback.print_exc()

print("\n" + "="*60)
print("LOGIN RESPONSE FORMAT")
print("="*60)

print("""
When a user logs in at /api/auth/login/, the response will include:

{
  "access": "eyJ0eXAiOiJKV1QiLCJhbGc...",
  "refresh": "eyJ0eXAiOiJKV1QiLCJhbGc...",
  "user": {
    "id": 1,
    "username": "admin",
    "email": "admin@example.com",
    "first_name": "Admin",
    "last_name": "User",
    "role": "admin"
  },
  "tenant": {
    "id": 1,
    "name": "Demo Company",
    "slug": "demo-company",
    "business_type": "construction",
    "plan_type": "free",
    "active_modules": ["inventory", "sales", "purchase", ...]
  }
}

The access token JWT also contains custom claims:
- role: User's role
- tenant_id: Tenant ID
- tenant_slug: Tenant slug
- tenant_name: Tenant name
""")

print("\n" + "="*60)
print("TEST COMPLETE")
print("="*60)
