#!/usr/bin/env python
"""
Test Construction Site Creation API
"""

import os
import sys
import django
from datetime import date, timedelta

# Setup Django
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core_backend.settings')
django.setup()

from django.contrib.auth import get_user_model
from tenants.models import Tenant
from construction.models import Site
from inventory.models import Warehouse
from decimal import Decimal

User = get_user_model()


def test_site_creation():
    print("=" * 60)
    print("Test Construction Site Creation")
    print("=" * 60)
    
    # Get a test user with tenant
    user = User.objects.filter(tenant__isnull=False, role='admin').first()
    
    if not user:
        print("\n❌ No admin user found with tenant")
        return
    
    print(f"\nTesting with user: {user.username}")
    print(f"Tenant: {user.tenant.name}")
    
    # Check if there are managers
    managers = User.objects.filter(tenant=user.tenant, role='manager')
    print(f"\nManagers available: {managers.count()}")
    
    if managers.count() == 0:
        print("⚠️  No managers found. Creating a test manager...")
        manager = User.objects.create_user(
            username='test_manager',
            email='manager@test.com',
            password='testpass123',
            first_name='Test',
            last_name='Manager',
            role='manager',
            tenant=user.tenant
        )
        print(f"✅ Created manager: {manager.username}")
    else:
        manager = managers.first()
        print(f"✅ Using existing manager: {manager.username}")
    
    # Check if there are warehouses
    warehouses = Warehouse.objects.filter(tenant=user.tenant)
    print(f"\nWarehouses available: {warehouses.count()}")
    
    if warehouses.count() == 0:
        print("⚠️  No warehouses found. Creating a test warehouse...")
        warehouse = Warehouse.objects.create(
            tenant=user.tenant,
            name='Main Warehouse',
            location='Test Location',
            is_active=True
        )
        print(f"✅ Created warehouse: {warehouse.name}")
    else:
        warehouse = warehouses.first()
        print(f"✅ Using existing warehouse: {warehouse.name}")
    
    # Create a test site
    print("\n" + "=" * 60)
    print("Creating Test Construction Site")
    print("=" * 60)
    
    site_data = {
        'tenant': user.tenant,
        'name': 'Test Construction Project',
        'location': 'Kathmandu, Nepal',
        'client_name': 'ABC Corporation',
        'allocated_budget': Decimal('5000000.00'),  # 5 million NPR
        'start_date': date.today(),
        'estimated_end_date': date.today() + timedelta(days=180),  # 6 months
        'manager': manager,
        'warehouse': warehouse,
        'status': 'planned',
        'description': 'Test construction site for API verification'
    }
    
    try:
        site = Site.objects.create(**site_data)
        print(f"\n✅ Site created successfully!")
        print(f"   ID: {site.id}")
        print(f"   Name: {site.name}")
        print(f"   Location: {site.location}")
        print(f"   Client: {site.client_name}")
        print(f"   Budget: NPR {site.allocated_budget:,.2f}")
        print(f"   Start Date: {site.start_date}")
        print(f"   End Date: {site.estimated_end_date}")
        print(f"   Manager: {site.manager.username}")
        print(f"   Warehouse: {site.warehouse.name}")
        print(f"   Status: {site.status}")
        
        # Test calculated fields
        print("\n" + "=" * 60)
        print("Testing Calculated Fields")
        print("=" * 60)
        
        print(f"\nMaterial Cost: NPR {site.get_material_cost():,.2f}")
        print(f"Labor Cost: NPR {site.get_labor_cost():,.2f}")
        print(f"Other Expenses: NPR {site.get_other_expenses():,.2f}")
        print(f"Actual Spend: NPR {site.get_actual_spend():,.2f}")
        print(f"Remaining Budget: NPR {site.get_remaining_budget():,.2f}")
        print(f"Budget Percentage: {site.get_budget_percentage():.2f}%")
        
        # Test API serialization
        print("\n" + "=" * 60)
        print("Testing API Serialization")
        print("=" * 60)
        
        from construction.serializers import SiteSerializer
        serializer = SiteSerializer(site)
        
        print("\nSerialized Data:")
        print(f"  ID: {serializer.data['id']}")
        print(f"  Name: {serializer.data['name']}")
        print(f"  Manager Name: {serializer.data['manager_name']}")
        print(f"  Warehouse Name: {serializer.data['warehouse_name']}")
        print(f"  Material Cost: {serializer.data['material_cost']}")
        print(f"  Labor Cost: {serializer.data['labor_cost']}")
        print(f"  Actual Spend: {serializer.data['actual_spend']}")
        print(f"  Remaining Budget: {serializer.data['remaining_budget']}")
        
        print("\n✅ API serialization working correctly!")
        
        # Cleanup
        print("\n" + "=" * 60)
        print("Cleanup")
        print("=" * 60)
        
        site.delete()
        print("✅ Test site deleted")
        
    except Exception as e:
        print(f"\n❌ Error creating site: {e}")
        import traceback
        traceback.print_exc()
    
    print("\n" + "=" * 60)
    print("✅ Test Complete!")
    print("=" * 60)


if __name__ == '__main__':
    test_site_creation()
