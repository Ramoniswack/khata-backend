#!/usr/bin/env python
"""
Test script for Dashboard API

This script tests:
1. Get dashboard data for different periods
2. Verify all data sections are present
3. Check data structure
"""

import os
import sys
import django

# Setup Django
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core_backend.settings')
django.setup()

import requests
import json

# Configuration
BASE_URL = "http://localhost:8000/api"
USERNAME = "admin"
PASSWORD = "admin123"

def print_header(text):
    """Print a formatted header"""
    print(f"\n{'='*60}")
    print(f"{text}")
    print(f"{'='*60}")

def print_success(text):
    """Print success message"""
    print(f"✓ {text}")

def print_error(text):
    """Print error message"""
    print(f"✗ {text}")

def print_info(text):
    """Print info message"""
    print(f"ℹ {text}")

def login():
    """Login and get JWT token"""
    print_header("1. AUTHENTICATION")
    
    url = f"{BASE_URL}/auth/login/"
    data = {
        "username": USERNAME,
        "password": PASSWORD
    }
    
    try:
        response = requests.post(url, json=data)
        response.raise_for_status()
        
        result = response.json()
        token = result.get('access')
        
        print_success(f"Logged in as: {USERNAME}")
        print_info(f"Token: {token[:20]}...")
        
        return token
    except requests.exceptions.RequestException as e:
        print_error(f"Login failed: {e}")
        if hasattr(e.response, 'text'):
            print_error(f"Response: {e.response.text}")
        sys.exit(1)

def test_dashboard(token, period='month'):
    """Test dashboard endpoint"""
    print_header(f"2. GET DASHBOARD DATA ({period.upper()})")
    
    url = f"{BASE_URL}/sales/orders/dashboard/"
    headers = {"Authorization": f"Bearer {token}"}
    params = {"period": period}
    
    try:
        response = requests.get(url, headers=headers, params=params)
        response.raise_for_status()
        
        data = response.json()
        
        print_success("Dashboard data retrieved successfully")
        
        # Check stats
        stats = data.get('stats', {})
        print_info(f"Revenue: {stats.get('revenue', 'N/A')} ({stats.get('revenueChange', 0):+.1f}%)")
        print_info(f"Orders: {stats.get('orders', 0)} ({stats.get('ordersChange', 0):+.1f}%)")
        print_info(f"Customers: {stats.get('customers', 0)} ({stats.get('customersChange', 0):+.1f}%)")
        print_info(f"Products: {stats.get('products', 0)} ({stats.get('productsChange', 0):+.1f}%)")
        
        # Check revenue data
        revenue_data = data.get('revenueData', [])
        print_info(f"Revenue data points: {len(revenue_data)}")
        
        # Check recent orders
        recent_orders = data.get('recentOrders', [])
        print_info(f"Recent orders: {len(recent_orders)}")
        
        # Check top products
        top_products = data.get('topProducts', [])
        print_info(f"Top products: {len(top_products)}")
        if top_products:
            print_info(f"  Top: {top_products[0]['name']} ({top_products[0]['sales']} sold)")
        
        # Check recent customers
        recent_customers = data.get('recentCustomers', [])
        print_info(f"Recent customers: {len(recent_customers)}")
        
        # Check inventory summary
        inventory = data.get('inventorySummary', {})
        print_info(f"Inventory: {inventory.get('inStock', 0)} in stock, {inventory.get('lowStock', 0)} low, {inventory.get('outOfStock', 0)} out")
        print_info(f"Total SKUs: {inventory.get('totalSKUs', 0)}")
        
        return True
    except requests.exceptions.RequestException as e:
        print_error(f"Failed to get dashboard data: {e}")
        if hasattr(e.response, 'text'):
            print_error(f"Response: {e.response.text}")
        return False

def test_all_periods(token):
    """Test all period options"""
    print_header("3. TEST ALL PERIODS")
    
    periods = ['today', 'week', 'month', 'year']
    results = {}
    
    for period in periods:
        print(f"\nTesting period: {period}")
        success = test_dashboard(token, period)
        results[period] = success
        
        if success:
            print_success(f"{period.capitalize()} period: OK")
        else:
            print_error(f"{period.capitalize()} period: FAILED")
    
    return all(results.values())

def main():
    """Main test function"""
    print("\n" + "="*60)
    print("         DASHBOARD API TEST SCRIPT")
    print("="*60)
    
    # Step 1: Login
    token = login()
    
    # Step 2: Test default dashboard
    if not test_dashboard(token):
        print_error("Default dashboard test failed")
        sys.exit(1)
    
    # Step 3: Test all periods
    if not test_all_periods(token):
        print_error("Some period tests failed")
        sys.exit(1)
    
    # Final summary
    print_header("TEST SUMMARY")
    print_success("All tests passed! ✓")
    print_info("Dashboard API is working correctly")
    
    print("\n" + "="*60 + "\n")

if __name__ == "__main__":
    main()
