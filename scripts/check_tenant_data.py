"""
Check what data exists for each tenant
"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core_backend.settings')
django.setup()

from tenants.models import Tenant
from inventory.models import Category, UnitOfMeasure, Product
from django.contrib.auth import get_user_model

User = get_user_model()

print("="*60)
print("TENANT DATA AUDIT")
print("="*60)

tenants = Tenant.objects.all()
print(f"\nTotal Tenants: {tenants.count()}\n")

for tenant in tenants:
    print(f"\n{'='*60}")
    print(f"Tenant: {tenant.name} (ID: {tenant.id})")
    print(f"Business Type: {tenant.business_type}")
    print(f"{'='*60}")
    
    # Users
    users = User.objects.filter(tenant=tenant)
    print(f"\nUsers: {users.count()}")
    for user in users[:3]:
        print(f"  - {user.username} ({user.role})")
    
    # Categories
    categories = Category.objects.filter(tenant=tenant)
    print(f"\nCategories: {categories.count()}")
    for cat in categories[:5]:
        print(f"  - {cat.name} (ID: {cat.id})")
    
    # Units
    units = UnitOfMeasure.objects.filter(tenant=tenant)
    print(f"\nUnits: {units.count()}")
    for unit in units[:5]:
        print(f"  - {unit.name} ({unit.abbreviation}) (ID: {unit.id})")
    
    # Products
    products = Product.objects.filter(tenant=tenant)
    print(f"\nProducts: {products.count()}")
    for prod in products[:3]:
        print(f"  - {prod.name} ({prod.sku})")
    
    if categories.count() == 0 or units.count() == 0:
        print(f"\n⚠️  WARNING: This tenant is missing required data!")
        if categories.count() == 0:
            print("   - No categories found")
        if units.count() == 0:
            print("   - No units found")

print("\n" + "="*60)
print("AUDIT COMPLETE")
print("="*60)
