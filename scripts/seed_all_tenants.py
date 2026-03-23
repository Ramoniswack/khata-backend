"""
Automatically seed all tenants that are missing inventory master data
"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core_backend.settings')
django.setup()

from tenants.models import Tenant
from inventory.models import Category, UnitOfMeasure
from django.contrib.auth import get_user_model

User = get_user_model()

def seed_tenant_inventory_data(tenant):
    """Seed basic categories and units for a tenant"""
    
    # Basic Categories
    categories_data = [
        {'name': 'Construction Materials', 'description': 'Basic construction materials'},
        {'name': 'Cement', 'description': 'All types of cement'},
        {'name': 'Steel', 'description': 'Steel bars, rods, and sheets'},
        {'name': 'Hardware', 'description': 'General hardware items'},
        {'name': 'Electrical', 'description': 'Electrical supplies'},
        {'name': 'Plumbing', 'description': 'Plumbing supplies'},
        {'name': 'Paint', 'description': 'Paints and finishes'},
        {'name': 'Tools', 'description': 'Hand and power tools'},
    ]
    
    created_categories = 0
    for cat_data in categories_data:
        cat, created = Category.objects.get_or_create(
            tenant=tenant,
            name=cat_data['name'],
            defaults={'description': cat_data['description']}
        )
        if created:
            created_categories += 1
    
    # Basic Units of Measure
    units_data = [
        {'name': 'Piece', 'abbreviation': 'pcs', 'type': 'count'},
        {'name': 'Bag', 'abbreviation': 'bag', 'type': 'count'},
        {'name': 'Box', 'abbreviation': 'box', 'type': 'count'},
        {'name': 'Kilogram', 'abbreviation': 'kg', 'type': 'weight'},
        {'name': 'Ton', 'abbreviation': 'ton', 'type': 'weight'},
        {'name': 'Meter', 'abbreviation': 'm', 'type': 'length'},
        {'name': 'Feet', 'abbreviation': 'ft', 'type': 'length'},
        {'name': 'Liter', 'abbreviation': 'L', 'type': 'volume'},
        {'name': 'Square Meter', 'abbreviation': 'sqm', 'type': 'area'},
        {'name': 'Square Feet', 'abbreviation': 'sqft', 'type': 'area'},
    ]
    
    created_units = 0
    for unit_data in units_data:
        unit, created = UnitOfMeasure.objects.get_or_create(
            tenant=tenant,
            abbreviation=unit_data['abbreviation'],
            defaults={
                'name': unit_data['name'],
                'type': unit_data['type']
            }
        )
        if created:
            created_units += 1
    
    return created_categories, created_units


if __name__ == '__main__':
    print("\n" + "="*60)
    print("AUTO-SEEDING INVENTORY MASTER DATA")
    print("="*60)
    
    tenants = Tenant.objects.all()
    print(f"\nFound {tenants.count()} tenant(s)\n")
    
    seeded_count = 0
    skipped_count = 0
    
    for tenant in tenants:
        categories_count = Category.objects.filter(tenant=tenant).count()
        units_count = UnitOfMeasure.objects.filter(tenant=tenant).count()
        
        if categories_count == 0 or units_count == 0:
            print(f"Seeding: {tenant.name}")
            print(f"  Before: {categories_count} categories, {units_count} units")
            
            created_cats, created_units = seed_tenant_inventory_data(tenant)
            
            new_cats = Category.objects.filter(tenant=tenant).count()
            new_units = UnitOfMeasure.objects.filter(tenant=tenant).count()
            
            print(f"  After:  {new_cats} categories (+{created_cats}), {new_units} units (+{created_units})")
            print(f"  ✅ Seeded successfully!\n")
            seeded_count += 1
        else:
            print(f"Skipping: {tenant.name} (already has {categories_count} categories, {units_count} units)")
            skipped_count += 1
    
    print("\n" + "="*60)
    print(f"Summary:")
    print(f"  Tenants seeded: {seeded_count}")
    print(f"  Tenants skipped: {skipped_count}")
    print(f"  Total tenants: {tenants.count()}")
    print("="*60)
    print("\n✅ All tenants now have inventory master data!")
    print("Users can now create products in the frontend.\n")
