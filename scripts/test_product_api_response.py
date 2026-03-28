#!/usr/bin/env python
"""
Test script to check what the products API returns
"""
import os
import sys
import django
import json

# Setup Django
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core_backend.settings')
django.setup()

from django.contrib.auth import get_user_model
from inventory.models import Product
from inventory.serializers import ProductListSerializer

User = get_user_model()

def test_product_api():
    """Test what the products API returns"""
    print("\n" + "="*80)
    print("TESTING PRODUCT API RESPONSE")
    print("="*80)
    
    # Get user and tenant
    user = User.objects.filter(tenant__isnull=False).first()
    if not user:
        print("❌ No user with tenant found")
        return
    
    tenant = user.tenant
    print(f"\n✓ Using tenant: {tenant.name}")
    
    # Get products
    products = Product.objects.filter(tenant=tenant)
    print(f"\n📦 Found {products.count()} products")
    
    if products.count() == 0:
        print("\n⚠️  No products found. Run seed script first:")
        print("   python scripts/seed_construction_test_data.py")
        return
    
    # Serialize products
    serializer = ProductListSerializer(products, many=True)
    data = serializer.data
    
    print(f"\n📋 Serialized {len(data)} products")
    
    # Show first product in detail
    if data:
        print("\n" + "="*80)
        print("FIRST PRODUCT DATA (as returned by API):")
        print("="*80)
        print(json.dumps(data[0], indent=2, default=str))
        
        # Check for cost_price field
        first_product = data[0]
        if 'cost_price' in first_product:
            print(f"\n✓ cost_price field exists: {first_product['cost_price']}")
            print(f"  Type: {type(first_product['cost_price'])}")
        else:
            print("\n❌ cost_price field NOT found in response!")
            print(f"   Available fields: {list(first_product.keys())}")
    
    # Show all products summary
    print("\n" + "="*80)
    print("ALL PRODUCTS SUMMARY:")
    print("="*80)
    for product in data:
        print(f"\nID: {product['id']}")
        print(f"  Name: {product['name']}")
        print(f"  SKU: {product['sku']}")
        print(f"  Cost Price: {product.get('cost_price', 'NOT FOUND')}")
        print(f"  Selling Price: {product.get('selling_price', 'NOT FOUND')}")
        print(f"  Unit: {product.get('unit_name', 'NOT FOUND')}")

if __name__ == '__main__':
    test_product_api()
