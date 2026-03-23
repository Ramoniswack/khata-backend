"""
Seed basic inventory master data (Categories and Units) for a tenant
Run this to populate your tenant with essential data before creating products
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
    print(f"\n{'='*60}")
    print(f"Seeding inventory data for: {tenant.name}")
    print(f"{'='*60}")
    
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
    
    print("\nCreating Categories...")
    created_categories = 0
    for cat_data in categories_data:
        cat, created = Category.objects.get_or_create(
            tenant=tenant,
            name=cat_data['name'],
            defaults={'description': cat_data['description']}
        )
        if created:
            print(f"  ✓ Created: {cat.name}")
            created_categories += 1
        else:
            print(f"  - Exists: {cat.name}")
    
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
    
    print("\nCreating Units of Measure...")
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
            print(f"  ✓ Created: {unit.name} ({unit.abbreviation})")
            created_units += 1
        else:
            print(f"  - Exists: {unit.name} ({unit.abbreviation})")
    
    print(f"\n{'='*60}")
    print(f"Summary:")
    print(f"  Categories created: {created_categories}/{len(categories_data)}")
    print(f"  Units created: {created_units}/{len(units_data)}")
    print(f"{'='*60}\n")
    
    return created_categories, created_units


if __name__ == '__main__':
    print("\n" + "="*60)
    print("INVENTORY MASTER DATA SEEDER")
    print("="*60)
    
    # List all tenants
    tenants = Tenant.objects.all()
    print(f"\nFound {tenants.count()} tenant(s):\n")
    
    for idx, tenant in enumerate(tenants, 1):
        users_count = User.objects.filter(tenant=tenant).count()
        categories_count = Category.objects.filter(tenant=tenant).count()
        units_count = UnitOfMeasure.objects.filter(tenant=tenant).count()
        
        print(f"{idx}. {tenant.name}")
        print(f"   Business Type: {tenant.business_type}")
        print(f"   Users: {users_count}")
        print(f"   Categories: {categories_count}")
        print(f"   Units: {units_count}")
        
        if categories_count == 0 or units_count == 0:
            print(f"   ⚠️  Missing master data!")
        print()
    
    # Ask which tenant to seed
    print("="*60)
    choice = input("Enter tenant number to seed (or 'all' for all tenants, 'q' to quit): ").strip().lower()
    
    if choice == 'q':
        print("Cancelled.")
        exit(0)
    
    if choice == 'all':
        print("\nSeeding all tenants...")
        for tenant in tenants:
            seed_tenant_inventory_data(tenant)
    else:
        try:
            tenant_idx = int(choice) - 1
            if 0 <= tenant_idx < tenants.count():
                tenant = list(tenants)[tenant_idx]
                seed_tenant_inventory_data(tenant)
            else:
                print("Invalid tenant number!")
        except ValueError:
            print("Invalid input!")
    
    print("\n✅ Seeding complete!")
    print("You can now create products in the frontend.\n")
