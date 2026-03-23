"""
Create categories and units for a specific tenant
"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core_backend.settings')
django.setup()

from inventory.models import Category, UnitOfMeasure
from tenants.models import Tenant
from users.models import User

# Get the tenant - you can specify by name or get from a user
tenant_name = input("Enter tenant name (or press Enter for first tenant): ").strip()

if tenant_name:
    tenant = Tenant.objects.filter(name__icontains=tenant_name).first()
else:
    tenant = Tenant.objects.first()

if not tenant:
    print("ERROR: No tenant found")
    exit(1)

print(f"\nCreating data for tenant: {tenant.name} (ID: {tenant.id})")

# Create categories
categories_data = [
    {'name': 'Hardware', 'description': 'Hardware items'},
    {'name': 'Cement', 'description': 'Cement and related products'},
    {'name': 'Steel', 'description': 'Steel and iron products'},
    {'name': 'Paint', 'description': 'Paints and coatings'},
    {'name': 'Electrical', 'description': 'Electrical items'},
    {'name': 'Plumbing', 'description': 'Plumbing supplies'},
    {'name': 'Tools', 'description': 'Tools and equipment'},
]

print("\nCreating categories...")
for cat_data in categories_data:
    category, created = Category.objects.get_or_create(
        tenant=tenant,
        name=cat_data['name'],
        defaults={'description': cat_data['description']}
    )
    if created:
        print(f"  ✓ Created: {category.name}")
    else:
        print(f"  - Already exists: {category.name}")

# Create units
units_data = [
    {'name': 'Piece', 'abbreviation': 'pcs', 'type': 'count'},
    {'name': 'Kilogram', 'abbreviation': 'kg', 'type': 'weight'},
    {'name': 'Bag', 'abbreviation': 'bag', 'type': 'count'},
    {'name': 'Ton', 'abbreviation': 'ton', 'type': 'weight'},
    {'name': 'Meter', 'abbreviation': 'm', 'type': 'length'},
    {'name': 'Liter', 'abbreviation': 'L', 'type': 'volume'},
    {'name': 'Box', 'abbreviation': 'box', 'type': 'count'},
]

print("\nCreating units...")
for unit_data in units_data:
    unit, created = UnitOfMeasure.objects.get_or_create(
        tenant=tenant,
        name=unit_data['name'],
        defaults={
            'abbreviation': unit_data['abbreviation'],
            'type': unit_data['type']
        }
    )
    if created:
        print(f"  ✓ Created: {unit.name} ({unit.abbreviation})")
    else:
        print(f"  - Already exists: {unit.name} ({unit.abbreviation})")

print(f"\n✅ Done! Tenant '{tenant.name}' now has:")
print(f"   - {Category.objects.filter(tenant=tenant).count()} categories")
print(f"   - {UnitOfMeasure.objects.filter(tenant=tenant).count()} units")
