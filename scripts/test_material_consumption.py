#!/usr/bin/env python
"""
Test script for material consumption functionality
"""
import os
import sys
import django

# Setup Django
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core_backend.settings')
django.setup()

from django.contrib.auth import get_user_model
from construction.models import Site, MaterialConsumption
from inventory.models import Product, Stock, Warehouse
from rest_framework.test import APIClient
import json

User = get_user_model()

def test_material_consumption():
    """Test material consumption creation and stock deduction"""
    print("\n" + "="*80)
    print("MATERIAL CONSUMPTION - COMPREHENSIVE TEST")
    print("="*80)
    
    # Get a user with tenant
    user = User.objects.filter(tenant__isnull=False).first()
    if not user:
        print("❌ No user with tenant found")
        return
    
    print(f"\n✓ Using user: {user.username} (tenant: {user.tenant.name})")
    
    # Get a site with warehouse
    site = Site.objects.filter(tenant=user.tenant, warehouse__isnull=False).first()
    if not site:
        print("❌ No site with warehouse found")
        return
    
    print(f"✓ Using site: {site.name} (warehouse: {site.warehouse.name})")
    
    # Get a product with stock
    stock = Stock.objects.filter(
        tenant=user.tenant,
        warehouse=site.warehouse,
        quantity__gt=0
    ).first()
    
    if not stock:
        print("❌ No products with stock found at this warehouse")
        return
    
    product = stock.product
    initial_stock = float(stock.quantity)
    
    print(f"✓ Using product: {product.name} (SKU: {product.sku})")
    print(f"✓ Initial stock: {initial_stock} {product.unit.abbreviation}")
    
    # Create API client
    client = APIClient()
    client.force_authenticate(user=user)
    
    # Test 1: Create material consumption
    print("\n" + "-"*80)
    print("TEST 1: Create material consumption")
    print("-"*80)
    
    consumption_qty = 5.0
    unit_cost = 100.0
    
    data = {
        'site': str(site.id),
        'product': str(product.id),
        'quantity': consumption_qty,
        'unit_cost': unit_cost,
        'notes': 'Test consumption for foundation work',
    }
    
    print(f"\n📝 Creating consumption:")
    print(f"   - Quantity: {consumption_qty} {product.unit.abbreviation}")
    print(f"   - Unit cost: NPR {unit_cost}")
    print(f"   - Total cost: NPR {consumption_qty * unit_cost}")
    
    response = client.post('/api/construction/material-consumption/', data, format='json', HTTP_HOST='localhost')
    
    if response.status_code == 201:
        print("✓ Material consumption created successfully")
        consumption_data = response.data
        print(f"   - ID: {consumption_data['id']}")
        print(f"   - Total cost: NPR {consumption_data['total_cost']}")
        
        # Verify stock was deducted
        stock.refresh_from_db()
        new_stock = float(stock.quantity)
        expected_stock = initial_stock - consumption_qty
        
        print(f"\n📊 Stock verification:")
        print(f"   - Initial stock: {initial_stock}")
        print(f"   - Consumed: {consumption_qty}")
        print(f"   - Expected remaining: {expected_stock}")
        print(f"   - Actual remaining: {new_stock}")
        
        if abs(new_stock - expected_stock) < 0.01:
            print("✓ Stock deducted correctly!")
        else:
            print("❌ Stock deduction mismatch!")
        
        consumption_id = consumption_data['id']
    else:
        print(f"❌ Failed to create consumption: {response.status_code}")
        if hasattr(response, 'data'):
            print(json.dumps(response.data, indent=2, default=str))
        else:
            print(response.content.decode())
        return
    
    # Test 2: List material consumptions
    print("\n" + "-"*80)
    print("TEST 2: List material consumptions")
    print("-"*80)
    
    response = client.get(f'/api/construction/material-consumption/?site={site.id}', HTTP_HOST='localhost')
    
    if response.status_code == 200:
        consumptions = response.data if isinstance(response.data, list) else response.data.get('results', [])
        print(f"✓ Found {len(consumptions)} consumption(s) for this site")
        
        for cons in consumptions[:3]:  # Show first 3
            print(f"   - {cons['product_name']}: {cons['quantity']} {cons['product_unit']} @ NPR {cons['unit_cost']}")
    else:
        print(f"❌ Failed to list consumptions: {response.status_code}")
    
    # Test 3: Try to consume more than available stock (should fail)
    print("\n" + "-"*80)
    print("TEST 3: Try to consume more than available stock (should fail)")
    print("-"*80)
    
    stock.refresh_from_db()
    excessive_qty = float(stock.quantity) + 100
    
    data_excessive = {
        'site': str(site.id),
        'product': str(product.id),
        'quantity': excessive_qty,
        'unit_cost': unit_cost,
        'notes': 'This should fail',
    }
    
    print(f"\n📝 Attempting to consume {excessive_qty} (available: {stock.quantity})")
    
    response = client.post('/api/construction/material-consumption/', data_excessive, format='json', HTTP_HOST='localhost')
    
    if response.status_code == 400:
        print("✓ Correctly rejected excessive consumption")
        if hasattr(response, 'data'):
            print(f"   Error: {response.data}")
    else:
        print(f"⚠️  Unexpected response: {response.status_code}")
    
    # Test 4: Get consumption details
    print("\n" + "-"*80)
    print("TEST 4: Get consumption details")
    print("-"*80)
    
    response = client.get(f'/api/construction/material-consumption/{consumption_id}/', HTTP_HOST='localhost')
    
    if response.status_code == 200:
        print("✓ Retrieved consumption details")
        cons = response.data
        print(f"   - Product: {cons['product_name']}")
        print(f"   - Quantity: {cons['quantity']} {cons['product_unit']}")
        print(f"   - Total cost: NPR {cons['total_cost']}")
        print(f"   - Site: {cons.get('site_name', 'N/A')}")
    else:
        print(f"❌ Failed to get details: {response.status_code}")
    
    # Test 5: Delete consumption (should restore stock)
    print("\n" + "-"*80)
    print("TEST 5: Delete consumption (stock should be restored)")
    print("-"*80)
    
    stock.refresh_from_db()
    stock_before_delete = float(stock.quantity)
    
    response = client.delete(f'/api/construction/material-consumption/{consumption_id}/', HTTP_HOST='localhost')
    
    if response.status_code == 204:
        print("✓ Consumption deleted successfully")
        
        # Verify stock was restored
        stock.refresh_from_db()
        stock_after_delete = float(stock.quantity)
        expected_restored = stock_before_delete + consumption_qty
        
        print(f"\n📊 Stock restoration:")
        print(f"   - Before delete: {stock_before_delete}")
        print(f"   - After delete: {stock_after_delete}")
        print(f"   - Expected: {expected_restored}")
        
        if abs(stock_after_delete - expected_restored) < 0.01:
            print("✓ Stock restored correctly!")
        else:
            print("❌ Stock restoration mismatch!")
    else:
        print(f"❌ Failed to delete: {response.status_code}")
    
    print("\n" + "="*80)
    print("ALL TESTS COMPLETED")
    print("="*80)

if __name__ == '__main__':
    test_material_consumption()
