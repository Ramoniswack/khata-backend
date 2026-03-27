#!/usr/bin/env python
"""
Test script for new Sales Reports API endpoints
Tests all 5 report types: Sales Summary, By Customer, By Product, By Category, Tax Report
"""
import os
import sys
import django
from datetime import datetime, timedelta

# Setup Django
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core_backend.settings')
django.setup()

import requests
from users.models import User
from tenants.models import Tenant

# Configuration
BASE_URL = "http://localhost:8000"
API_BASE = f"{BASE_URL}/api"


def get_auth_token():
    """Get authentication token"""
    print("🔐 Authenticating...")
    
    # Try to get existing user (hardware_admin has sales data)
    try:
        user = User.objects.filter(email="admin@cityhardware.com.np").first()
        if not user:
            print("❌ Test user not found. Please run seed_demo_data first.")
            sys.exit(1)
        
        # Login
        response = requests.post(
            f"{API_BASE}/auth/login/",
            json={"email": "admin@cityhardware.com.np", "password": "demo123"}
        )
        
        if response.status_code == 200:
            token = response.json()['access']
            print(f"✅ Authenticated as {user.email}")
            return token
        else:
            print(f"❌ Login failed: {response.text}")
            sys.exit(1)
    except Exception as e:
        print(f"❌ Authentication error: {str(e)}")
        sys.exit(1)


def test_sales_summary(token):
    """Test Sales Summary Report"""
    print("\n" + "="*60)
    print("📊 Testing Sales Summary Report")
    print("="*60)
    
    # Calculate date range (last 6 months)
    end_date = datetime.now().date()
    start_date = end_date - timedelta(days=180)
    
    url = f"{API_BASE}/sales/reports/sales-summary/"
    headers = {"Authorization": f"Bearer {token}"}
    params = {
        "start_date": start_date.isoformat(),
        "end_date": end_date.isoformat()
    }
    
    response = requests.get(url, headers=headers, params=params)
    
    if response.status_code == 200:
        data = response.json()
        print("✅ Sales Summary Report loaded successfully")
        print(f"\n📈 Summary:")
        print(f"   Total Sales: Rs. {data['summary']['total_sales']:,.2f}")
        print(f"   Total Orders: {data['summary']['total_orders']}")
        print(f"   Avg Order Value: Rs. {data['summary']['avg_order_value']:,.2f}")
        print(f"   Cash Collected: Rs. {data['summary']['cash_collected']:,.2f}")
        print(f"   Collection Rate: {data['summary']['collection_rate']}%")
        
        print(f"\n📅 Monthly Trend ({len(data['monthly_trend'])} months):")
        for month in data['monthly_trend'][-3:]:  # Show last 3 months
            print(f"   {month['month']}: Rs. {month['sales']:,.0f} ({month['orders']} orders)")
        
        return True
    else:
        print(f"❌ Failed: {response.status_code}")
        print(f"   Error: {response.text}")
        return False


def test_by_customer(token):
    """Test By Customer Report"""
    print("\n" + "="*60)
    print("👥 Testing By Customer Report")
    print("="*60)
    
    end_date = datetime.now().date()
    start_date = end_date - timedelta(days=90)
    
    url = f"{API_BASE}/sales/reports/by-customer/"
    headers = {"Authorization": f"Bearer {token}"}
    params = {
        "start_date": start_date.isoformat(),
        "end_date": end_date.isoformat()
    }
    
    response = requests.get(url, headers=headers, params=params)
    
    if response.status_code == 200:
        data = response.json()
        print(f"✅ By Customer Report loaded successfully")
        print(f"\n📊 Top Customers ({len(data['customers'])} total):")
        
        for i, customer in enumerate(data['customers'][:5], 1):
            print(f"   {i}. {customer['customer_name']}")
            print(f"      Orders: {customer['orders']}, Revenue: Rs. {customer['revenue']:,.2f}")
            print(f"      Avg Order: Rs. {customer['avg_order']:,.2f}, Status: {customer['status']}")
        
        return True
    else:
        print(f"❌ Failed: {response.status_code}")
        print(f"   Error: {response.text}")
        return False


def test_by_product(token):
    """Test By Product Report"""
    print("\n" + "="*60)
    print("📦 Testing By Product Report")
    print("="*60)
    
    end_date = datetime.now().date()
    start_date = end_date - timedelta(days=90)
    
    url = f"{API_BASE}/sales/reports/by-product/"
    headers = {"Authorization": f"Bearer {token}"}
    params = {
        "start_date": start_date.isoformat(),
        "end_date": end_date.isoformat()
    }
    
    response = requests.get(url, headers=headers, params=params)
    
    if response.status_code == 200:
        data = response.json()
        print(f"✅ By Product Report loaded successfully")
        print(f"\n📊 Top Products ({len(data['products'])} total):")
        print(f"   Total Revenue: Rs. {data['total_revenue']:,.2f}")
        
        for i, product in enumerate(data['products'][:5], 1):
            print(f"\n   {i}. {product['product_name']}")
            print(f"      Unit Price: Rs. {product['unit_price']:,.2f}")
            print(f"      Qty Sold: {product['qty_sold']} {product['unit']}")
            print(f"      Revenue: Rs. {product['revenue']:,.2f} ({product['percentage']:.1f}%)")
        
        return True
    else:
        print(f"❌ Failed: {response.status_code}")
        print(f"   Error: {response.text}")
        return False


def test_by_category(token):
    """Test By Category Report"""
    print("\n" + "="*60)
    print("🏷️  Testing By Category Report")
    print("="*60)
    
    end_date = datetime.now().date()
    start_date = end_date - timedelta(days=90)
    
    url = f"{API_BASE}/sales/reports/by-category/"
    headers = {"Authorization": f"Bearer {token}"}
    params = {
        "start_date": start_date.isoformat(),
        "end_date": end_date.isoformat()
    }
    
    response = requests.get(url, headers=headers, params=params)
    
    if response.status_code == 200:
        data = response.json()
        print(f"✅ By Category Report loaded successfully")
        print(f"\n📊 Categories ({len(data['categories'])} total):")
        print(f"   Total Revenue: Rs. {data['total_revenue']:,.2f}")
        
        for i, category in enumerate(data['categories'], 1):
            print(f"\n   {i}. {category['category_name']}")
            print(f"      Revenue: Rs. {category['revenue']:,.2f} ({category['percentage']:.1f}%)")
            print(f"      Orders: {category['orders']}")
        
        return True
    else:
        print(f"❌ Failed: {response.status_code}")
        print(f"   Error: {response.text}")
        return False


def test_tax_report(token):
    """Test Tax Report"""
    print("\n" + "="*60)
    print("💰 Testing Tax Report")
    print("="*60)
    
    end_date = datetime.now().date()
    start_date = end_date - timedelta(days=120)
    
    url = f"{API_BASE}/sales/reports/tax-report/"
    headers = {"Authorization": f"Bearer {token}"}
    params = {
        "start_date": start_date.isoformat(),
        "end_date": end_date.isoformat()
    }
    
    response = requests.get(url, headers=headers, params=params)
    
    if response.status_code == 200:
        data = response.json()
        print(f"✅ Tax Report loaded successfully")
        print(f"\n📊 Summary:")
        print(f"   Total Taxable Sales: Rs. {data['summary']['total_taxable_sales']:,.2f}")
        print(f"   Total VAT Collected: Rs. {data['summary']['total_vat_collected']:,.2f}")
        print(f"   Net VAT Payable: Rs. {data['summary']['net_vat_payable']:,.2f}")
        print(f"   VAT Rate: {data['summary']['vat_rate']}%")
        
        print(f"\n📅 Monthly Data ({len(data['monthly_data'])} months):")
        for month in data['monthly_data']:
            print(f"   {month['month']} {month['year']}: Taxable Rs. {month['taxable_sales']:,.0f}, VAT Rs. {month['vat_collected']:,.0f} ({month['status']})")
        
        return True
    else:
        print(f"❌ Failed: {response.status_code}")
        print(f"   Error: {response.text}")
        return False


def main():
    """Main test function"""
    print("🚀 Starting Sales Reports API Tests")
    print("="*60)
    
    # Get authentication token
    token = get_auth_token()
    
    # Run all tests
    results = {
        "Sales Summary": test_sales_summary(token),
        "By Customer": test_by_customer(token),
        "By Product": test_by_product(token),
        "By Category": test_by_category(token),
        "Tax Report": test_tax_report(token),
    }
    
    # Print summary
    print("\n" + "="*60)
    print("📋 TEST SUMMARY")
    print("="*60)
    
    passed = sum(1 for v in results.values() if v)
    total = len(results)
    
    for test_name, result in results.items():
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status} - {test_name}")
    
    print(f"\n🎯 Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("✅ All tests passed!")
        return 0
    else:
        print("❌ Some tests failed")
        return 1


if __name__ == "__main__":
    sys.exit(main())
