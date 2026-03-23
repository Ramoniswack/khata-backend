"""
Debug script to test product creation and see actual validation errors
"""
import os
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core_backend.settings')
django.setup()

from django.contrib.auth import get_user_model
from inventory.models import Product, Category, UnitOfMeasure
from inventory.serializers import ProductDetailSerializer
from tenants.models import Tenant

User = get_user_model()

print("="*60)
print("PRODUCT CREATION DEBUG TEST")
print("="*60)

# Get or create test tenant
tenant, _ = Tenant.objects.get_or_create(
    name='Test Tenant',
    defaults={'business_type': 'construction'}
)
print(f"\n✓ Tenant: {tenant.name} (ID: {tenant.id})")

# Get or create test user
user, _ = User.objects.get_or_create(
    username='testuser',
    defaults={
        'tenant': tenant,
        'role': 'admin',
        'email': 'test@example.com'
    }
)
if not user.tenant:
    user.tenant = tenant
    user.save()
print(f"✓ User: {user.username} (Tenant: {user.tenant.name})")

# Check categories
categories = Category.objects.filter(tenant=tenant)
print(f"\n✓ Categories for tenant: {categories.count()}")
for cat in categories[:5]:
    print(f"  - {cat.name} (ID: {cat.id})")

# Check units
units = UnitOfMeasure.objects.filter(tenant=tenant)
print(f"\n✓ Units for tenant: {units.count()}")
for unit in units[:5]:
    print(f"  - {unit.name} ({unit.abbreviation}) (ID: {unit.id})")

# Test payload (same as frontend sends)
test_payload = {
    'name': 'Debug Test Product',
    'sku': 'DEBUG-TEST-001',
    'category': categories.first().id if categories.exists() else None,
    'unit': units.first().id if units.exists() else None,
    'cost_price': 100.00,
    'selling_price': 150.00,
    'reorder_level': 10,
    'description': 'Test product description',
    'status': 'active'
}

print("\n" + "="*60)
print("TEST PAYLOAD:")
print("="*60)
for key, value in test_payload.items():
    print(f"{key}: {value} (type: {type(value).__name__})")

# Set tenant context (simulate middleware)
from tenants.middleware import set_current_tenant
set_current_tenant(tenant)

print("\n" + "="*60)
print("ATTEMPTING TO CREATE PRODUCT...")
print("="*60)

try:
    serializer = ProductDetailSerializer(data=test_payload)
    
    if serializer.is_valid():
        print("\n✅ Serializer validation PASSED")
        product = serializer.save()
        print(f"✅ Product created successfully!")
        print(f"   ID: {product.id}")
        print(f"   Name: {product.name}")
        print(f"   SKU: {product.sku}")
        print(f"   Tenant: {product.tenant.name}")
    else:
        print("\n❌ Serializer validation FAILED")
        print("\nValidation Errors:")
        for field, errors in serializer.errors.items():
            print(f"  {field}:")
            for error in errors:
                print(f"    - {error}")
        
except Exception as e:
    print(f"\n❌ EXCEPTION: {e}")
    import traceback
    traceback.print_exc()

finally:
    set_current_tenant(None)

print("\n" + "="*60)
print("TEST COMPLETE")
print("="*60)
