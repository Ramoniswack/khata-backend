"""
Test script to debug product creation
Run with: python manage.py shell < test_product_creation.py
"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core_backend.settings')
django.setup()

from inventory.models import Product, Category, UnitOfMeasure
from tenants.models import Tenant

# Get first tenant
tenant = Tenant.objects.first()
if not tenant:
    print("ERROR: No tenant found. Please create a tenant first.")
    exit(1)

print(f"Using tenant: {tenant.name} (ID: {tenant.id})")

# Get first category and unit
category = Category.objects.filter(tenant=tenant).first()
unit = UnitOfMeasure.objects.filter(tenant=tenant).first()

if not category:
    print("ERROR: No category found. Please create a category first.")
    exit(1)

if not unit:
    print("ERROR: No unit found. Please create a unit first.")
    exit(1)

print(f"Using category: {category.name} (ID: {category.id})")
print(f"Using unit: {unit.name} (ID: {unit.id})")

# Try to create a product
try:
    product = Product.objects.create(
        tenant=tenant,
        name="Test Product",
        sku="TEST-001",
        description="Test product description",
        category=category,
        unit=unit,
        cost_price=100.00,
        selling_price=150.00,
        reorder_level=10,
        status='active'
    )
    print(f"\nSUCCESS: Product created with ID: {product.id}")
    print(f"Product: {product.name} ({product.sku})")
    
    # Clean up
    product.delete()
    print("Product deleted (cleanup)")
    
except Exception as e:
    print(f"\nERROR: Failed to create product")
    print(f"Error type: {type(e).__name__}")
    print(f"Error message: {str(e)}")
    import traceback
    traceback.print_exc()
