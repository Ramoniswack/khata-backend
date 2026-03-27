#!/usr/bin/env python
"""Test script for sales reports API endpoints"""
import os
import sys
import django

# Setup Django
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core_backend.settings')
django.setup()

import requests
from users.models import User
from datetime import datetime, timedelta

# Configuration
BASE_URL = "http://localhost:8000/api"

def get_auth_token():
    """Get authentication token"""
    user = User.objects.filter(is_superuser=True).first()
    if not user:
        print("❌ No superuser found")
        return None
    
    response = requests.post(f"{BASE_URL}/auth/login/", json={
        "username": user.username,
        "password": "admin123"
    })
    
    if response.status_code == 200:
        token = response.json().get('access')
        print(f"✅ Logged in as: {user.username}")
        return token
    else:
        print(f"❌ Login failed: {response.status_code}")
        return None

def test_sales_performance(token):
    """Test sales performance endpoint"""
    print("\n📊 Testing Sales Performance...")
    
    headers = {"Authorization": f"Bearer {token}"}
    
    # Calculate date range (last 30 days)
    end_date = datetime.now().date()
    start_date = end_date - timedelta(days=30)
    
    params = {
        'start_date': start_date.strftime('%Y-%m-%d'),
        'end_date': end_date.strftime('%Y-%m-%d')
    }
    
    response = requests.get(f"{BASE_URL}/reports/sales-performance/", headers=headers, params=params)
    
    if response.status_code == 200:
        data = response.json()
        print(f"✅ Sales Performance retrieved successfully")
        print(f"   Total Sales: Rs. {data['total_sales']:,.2f}")
        print(f"   Total Orders: {data['total_orders']}")
        print(f"   Avg Order Value: Rs. {data['average_order_value']:,.2f}")
        print(f"\n   Top Customers:")
        for customer in data['top_customers'][:3]:
            print(f"   - {customer['customer_name']}: {customer['total_orders']} orders, Rs. {customer['total_amount']:,.2f}")
        return True
    else:
        print(f"❌ Failed: {response.status_code}")
        print(response.text)
        return False

def test_revenue_expense_trend(token):
    """Test revenue expense trend endpoint"""
    print("\n📈 Testing Revenue Expense Trend...")
    
    headers = {"Authorization": f"Bearer {token}"}
    params = {'months': 6}
    
    response = requests.get(f"{BASE_URL}/reports/revenue-expense-trend/", headers=headers, params=params)
    
    if response.status_code == 200:
        data = response.json()
        print(f"✅ Revenue Expense Trend retrieved successfully")
        print(f"\n   Monthly Data (Last 6 months):")
        for month_data in data['monthly_data']:
            print(f"   {month_data['month']}:")
            print(f"      Revenue: Rs. {month_data['revenue']:,.2f}")
            print(f"      Expenses: Rs. {month_data['expenses']:,.2f}")
            print(f"      Profit: Rs. {month_data['profit']:,.2f}")
        return True
    else:
        print(f"❌ Failed: {response.status_code}")
        print(response.text)
        return False

def main():
    print("🚀 Starting Sales Reports API Tests...\n")
    
    token = get_auth_token()
    if not token:
        return
    
    test_sales_performance(token)
    test_revenue_expense_trend(token)
    
    print("\n✅ All tests completed!")

if __name__ == "__main__":
    main()
