#!/usr/bin/env python
"""
Seed test data for construction material consumption testing
"""
import os
import sys
import django

# Setup Django
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core_backend.settings')
django.setup()

from django.contrib.auth import get_user_model
from construction.models import Site
from inventory.models import Product, Stock, Warehouse, Category, UnitOfMeasure
from decimal import Decimal

User = get_user_model()

def seed_test_data():
    """Seed test data for material consumption"""
    print("\n" + "="*80)
    print("SEEDING CONSTRUCTION TEST DATA")
    print("="*80)
    
    # Get user and tenant
    user = User.objects.filter(tenant__isnull=False).first()
    if not user:
        print("❌ No user with tenant found")
        return
    
    tenant = user.tenant
    print(f"\n✓ Using tenant: {tenant.name}")
    
    # Get or create warehouse
    warehouse = Warehouse.objects.filter(tenant=tenant).first()
    if not warehouse:
        warehouse = Warehouse.objects.create(
            tenant=tenant,
            name="Main Warehouse",
            location="Central Location",
            is_active=True
        )
        print(f"✓ Created warehouse: {warehouse.name}")
    else:
        print(f"✓ Using warehouse: {warehouse.name}")
    
    # Get or create site with warehouse
    site = Site.objects.filter(tenant=tenant, warehouse=warehouse).first()
    if not site:
        # Get a manager
        manager = User.objects.filter(tenant=tenant).first()
        site = Site.objects.create(
            tenant=tenant,
            name="Test Construction Site",
            location="Test Location",
            client_name="Test Client",
            allocated_budget=Decimal('1000000.00'),
            start_date="2026-01-01",
            manager=manager,
            warehouse=warehouse,
            status='active'
        )
        print(f"✓ Created site: {site.name}")
    else:
        # Update site to use warehouse
        site.warehouse = warehouse
        site.save()
        print(f"✓ Updated site: {site.name}")
    
    # Get or create category
    category = Category.objects.filter(tenant=tenant).first()
    if not category:
        category = Category.objects.create(
            tenant=tenant,
            name="Construction Materials",
            description="Materials for construction"
        )
        print(f"✓ Created category: {category.name}")
    else:
        print(f"✓ Using category: {category.name}")
    
    # Get or create UOM
    uom = UnitOfMeasure.objects.filter(tenant=tenant, abbreviation='pcs').first()
    if not uom:
        uom = UnitOfMeasure.objects.create(
            tenant=tenant,
            name="Pieces",
            abbreviation="pcs"
        )
        print(f"✓ Created UOM: {uom.name}")
    else:
        print(f"✓ Using UOM: {uom.name}")
    
    # Create test products with stock
    products_data = [
        {'name': 'Cement Bags', 'sku': 'CEM-001', 'cost': 500, 'stock': 100},
        {'name': 'Steel Rods', 'sku': 'STL-001', 'cost': 800, 'stock': 50},
        {'name': 'Bricks', 'sku': 'BRK-001', 'cost': 15, 'stock': 1000},
        {'name': 'Sand (Cubic Meter)', 'sku': 'SND-001', 'cost': 1200, 'stock': 20},
    ]
    
    print(f"\n📦 Creating products and stock...")
    
    for prod_data in products_data:
        # Get or create product
        product, created = Product.objects.get_or_create(
            tenant=tenant,
            sku=prod_data['sku'],
            defaults={
                'name': prod_data['name'],
                'category': category,
                'unit': uom,
                'cost_price': Decimal(str(prod_data['cost'])),
                'selling_price': Decimal(str(prod_data['cost'] * 1.2)),
                'reorder_level': Decimal('10'),
            }
        )
        
        if created:
            print(f"   ✓ Created product: {product.name}")
        else:
            print(f"   ✓ Using product: {product.name}")
        
        # Create or update stock
        stock, created = Stock.objects.get_or_create(
            tenant=tenant,
            product=product,
            warehouse=warehouse,
            defaults={
                'quantity': Decimal(str(prod_data['stock'])),
            }
        )
        
        if not created:
            stock.quantity = Decimal(str(prod_data['stock']))
            stock.save()
        
        print(f"      Stock: {stock.quantity} {product.unit.abbreviation}")
    
    print("\n" + "="*80)
    print("TEST DATA SEEDED SUCCESSFULLY")
    print("="*80)
    print(f"\nYou can now test material consumption at:")
    print(f"Site: {site.name} (ID: {site.id})")
    print(f"Warehouse: {warehouse.name}")
    print(f"Products: {len(products_data)} items with stock")

if __name__ == '__main__':
    seed_test_data()
