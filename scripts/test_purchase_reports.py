#!/usr/bin/env python
"""
Test script for purchase reports endpoint
"""
import os
import sys
import django

# Setup Django
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core_backend.settings')
django.setup()

from django.test import Client
from users.models import User

def test_purchase_reports():
    """Test purchase reports endpoint"""
    
    # Get admin user
    admin = User.objects.filter(is_superuser=True).first()
    if not admin:
        print("❌ No admin user found")
        return
    
    print(f"✓ Testing with user: {admin.email}")
    print(f"✓ Tenant: {admin.tenant.name if admin.tenant else 'None'}")
    
    # Create test client and force login
    client = Client()
    client.force_login(admin)
    
    # Test different date ranges
    date_ranges = ['week', 'month', 'quarter', 'year']
    
    for date_range in date_ranges:
        print(f"\n{'='*60}")
        print(f"Testing purchase reports ({date_range})")
        print('='*60)
        
        response = client.get(f'/api/reports/purchase-reports/?date_range={date_range}')
        
        if response.status_code == 200:
            data = response.json()
            print(f"✓ Purchase reports ({date_range}) retrieved successfully\n")
            
            print(f"Summary:")
            print(f"  - Total Purchases: Rs. {data['summary']['total_purchases']:,.2f}")
            print(f"  - Total Orders: {data['summary']['total_orders']}")
            print(f"  - Avg Order Value: Rs. {data['summary']['avg_order_value']:,.2f}")
            print(f"  - Payment Rate: {data['summary']['payment_rate_percentage']:.1f}%")
            
            print(f"\nBy Supplier: {len(data['by_supplier'])} suppliers")
            for supplier in data['by_supplier'][:3]:
                print(f"  - {supplier['supplier_name']}: Rs. {supplier['amount']:,.2f} ({supplier['orders']} orders)")
            
            print(f"\nBy Product: {len(data['by_product'])} products")
            for product in data['by_product'][:3]:
                print(f"  - {product['product_name']}: {product['qty']} {product['unit']} = Rs. {product['amount']:,.2f}")
            
            print(f"\nTax Report:")
            print(f"  - Total Taxable: Rs. {data['tax_report']['total_taxable']:,.2f}")
            print(f"  - Total VAT: Rs. {data['tax_report']['total_vat']:,.2f}")
            
            print(f"\nMonthly Trend: {len(data['monthly_trend'])} months")
            for month in data['monthly_trend']:
                print(f"  - {month['month']}: Rs. {month['purchases']:,.2f}")
            
            print(f"\nPeriod: {data['period']['start_date']} to {data['period']['end_date']}")
        else:
            print(f"❌ Failed to get purchase reports ({date_range}): {response.status_code}")
            print(response.content.decode())

if __name__ == '__main__':
    print("=" * 60)
    print("PURCHASE REPORTS ENDPOINT TEST")
    print("=" * 60)
    test_purchase_reports()
    print("\n" + "=" * 60)
    print("TEST COMPLETE")
    print("=" * 60)
