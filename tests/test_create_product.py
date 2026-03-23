import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core_backend.settings')
django.setup()

from inventory.models import Product, Category, UnitOfMeasure
from tenants.models import Tenant

# Get tenant
tenant = Tenant.objects.first()
print(f"Tenant: {tenant.name}")

# Get category and unit
category = Category.objects.filter(tenant=tenant).first()
unit = UnitOfMeasure.objects.filter(tenant=tenant).first()

print(f"Category: {category.name if category else 'None'}")
print(f"Unit: {unit.name if unit else 'None'}")

if not category or not unit:
    print("ERROR: Missing category or unit")
    exit(1)

# Try to create product
try:
    product = Product.objects.create(
        tenant=tenant,
        name="Test Product",
        sku="TEST-UNIQUE-001",
        description="Test description",
        category=category,
        unit=unit,
        cost_price=100.00,
        selling_price=150.00,
        reorder_level=10,
        status='active'
    )
    print(f"\n✅ SUCCESS! Product created: {product.id}")
    print(f"   Name: {product.name}")
    print(f"   SKU: {product.sku}")
    
    # Clean up
    product.delete()
    print("   Product deleted (cleanup)")
    
except Exception as e:
    print(f"\n❌ ERROR: {e}")
    import traceback
    traceback.print_exc()
