#!/usr/bin/env python
"""
Test script to check product price fields in the API response.
"""

import os
import sys
import django

# Setup Django
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core_backend.settings')
django.setup()

from inventory.models import Product
from inventory.serializers import ProductListSerializer
from django.contrib.auth import get_user_model

User = get_user_model()

def test_product_price():
    """Test that product serializer includes selling_price"""
    
    print("\n" + "="*60)
    print("TESTING PRODUCT PRICE FIELD")
    print("="*60)
    
    # Get a product
    products = Product.objects.all()[:3]
    
    if not products:
        print("\n✗ No products found in database")
        return
    
    print(f"\n✓ Found {products.count()} products")
    
    for product in products:
        print(f"\n" + "-"*60)
        print(f"Product: {product.name}")
        print(f"  - ID: {product.id}")
        print(f"  - SKU: {product.sku}")
        print(f"  - Cost Price: Rs. {product.cost_price}")
        print(f"  - Selling Price: Rs. {product.selling_price}")
        print(f"  - Unit: {product.unit.name if product.unit else 'None'}")
        
        # Serialize the product
        serializer = ProductListSerializer(product)
        data = serializer.data
        
        print(f"\nSerialized data:")
        print(f"  - id: {data.get('id')} (type: {type(data.get('id')).__name__})")
        print(f"  - name: {data.get('name')}")
        print(f"  - sku: {data.get('sku')}")
        print(f"  - cost_price: {data.get('cost_price')}")
        print(f"  - selling_price: {data.get('selling_price')}")
        print(f"  - unit: {data.get('unit')}")
        print(f"  - unit_name: {data.get('unit_name')}")
        
        # Check if selling_price is present and not 0
        if 'selling_price' not in data:
            print(f"\n✗ ERROR: selling_price field is missing!")
        elif data['selling_price'] == 0:
            print(f"\n⚠ WARNING: selling_price is 0")
        else:
            print(f"\n✓ selling_price is present and non-zero")
    
    print("\n" + "="*60)
    print("TEST COMPLETE")
    print("="*60 + "\n")

if __name__ == '__main__':
    test_product_price()
