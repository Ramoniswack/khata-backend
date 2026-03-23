"""
Test API request with tenant context
"""
import os
import django
import time

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core_backend.settings')
django.setup()

from django.test import RequestFactory
from django.contrib.auth import get_user_model
from rest_framework.test import force_authenticate
from inventory.views import ProductViewSet
from inventory.models import Category, UnitOfMeasure
from tenants.models import Tenant
from tenants.middleware import TenantMiddleware, get_current_tenant
import json

User = get_user_model()

print("="*60)
print("API REQUEST TENANT CONTEXT TEST")
print("="*60)

# Get a tenant and user
tenant = Tenant.objects.first()
user = User.objects.filter(tenant=tenant).first()

if not user:
    print("ERROR: No user found")
    exit(1)

print(f"\nUser: {user.username}")
print(f"User Tenant: {user.tenant.name} (ID: {user.tenant.id})")

# Get categories for this tenant
categories = Category.objects.filter(tenant=tenant)
units = UnitOfMeasure.objects.filter(tenant=tenant)

print(f"\nCategories for tenant: {categories.count()}")
if categories.exists():
    cat = categories.first()
    print(f"  Using category: {cat.name} (ID: {cat.id})")
else:
    print("  ERROR: No categories found")
    exit(1)

print(f"\nUnits for tenant: {units.count()}")
if units.exists():
    unit = units.first()
    print(f"  Using unit: {unit.name} (ID: {unit.id})")
else:
    print("  ERROR: No units found")
    exit(1)

# Create a fake request
factory = RequestFactory()
request = factory.post(
    '/api/inventory/products/',
    data=json.dumps({
        'name': 'API Test Product',
        'sku': f'API-TEST-{int(time.time())}',  # Unique SKU
        'category': cat.id,
        'unit': unit.id,
        'cost_price': 100.00,
        'selling_price': 150.00,
        'reorder_level': 10,
        'description': 'Test',
        'status': 'active'
    }),
    content_type='application/json'
)

# Authenticate the request
force_authenticate(request, user=user)
request.user = user

print("\n" + "="*60)
print("BEFORE MIDDLEWARE")
print("="*60)
print(f"Request user: {request.user.username}")
print(f"Request user tenant: {request.user.tenant.name}")
print(f"Current tenant (thread-local): {get_current_tenant()}")

# Apply middleware
middleware = TenantMiddleware(lambda r: None)
middleware.process_request(request)

print("\n" + "="*60)
print("AFTER MIDDLEWARE")
print("="*60)
print(f"Request user: {request.user.username}")
print(f"Request user tenant: {request.user.tenant.name}")
print(f"Request.tenant: {getattr(request, 'tenant', 'NOT SET')}")
print(f"Current tenant (thread-local): {get_current_tenant()}")

# Now test the view
print("\n" + "="*60)
print("TESTING VIEW CREATE METHOD")
print("="*60)

view = ProductViewSet.as_view({'post': 'create'})
response = view(request)

print(f"Response status: {response.status_code}")
print(f"Response data: {response.data}")

# Clean up
from tenants.middleware import set_current_tenant
set_current_tenant(None)

print("\n" + "="*60)
print("TEST COMPLETE")
print("="*60)
