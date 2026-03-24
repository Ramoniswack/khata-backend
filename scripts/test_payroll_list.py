#!/usr/bin/env python
"""Test script for payroll list API endpoint"""
import os
import sys
import django

# Setup Django
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core_backend.settings')
django.setup()

import requests
from users.models import User

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

def test_list_payroll(token):
    """Test list payroll endpoint"""
    print("\n📋 Testing List Payroll...")
    
    headers = {"Authorization": f"Bearer {token}"}
    response = requests.get(f"{BASE_URL}/hr/payroll/", headers=headers)
    
    if response.status_code == 200:
        result = response.json()
        records = result.get('results', [])
        print(f"✅ Found {len(records)} payroll records")
        
        # Group by month
        months = {}
        for record in records:
            key = f"{record['month']} {record['year']}"
            if key not in months:
                months[key] = {
                    'employees': 0,
                    'gross': 0,
                    'deductions': 0,
                    'net': 0
                }
            months[key]['employees'] += 1
            months[key]['gross'] += float(record['gross_salary'])
            months[key]['deductions'] += float(record['deductions'])
            months[key]['net'] += float(record['net_salary'])
        
        print(f"\n📊 Grouped by Month:")
        for month, data in months.items():
            print(f"   {month}:")
            print(f"      Employees: {data['employees']}")
            print(f"      Gross: Rs. {data['gross']:,.2f}")
            print(f"      Deductions: Rs. {data['deductions']:,.2f}")
            print(f"      Net: Rs. {data['net']:,.2f}")
        
        return True
    else:
        print(f"❌ Failed: {response.status_code}")
        print(response.text)
        return False

def test_filter_by_month(token):
    """Test filtering payroll by month"""
    print("\n🔍 Testing Filter by Month...")
    
    headers = {"Authorization": f"Bearer {token}"}
    response = requests.get(f"{BASE_URL}/hr/payroll/?month=Shrawan", headers=headers)
    
    if response.status_code == 200:
        result = response.json()
        records = result.get('results', [])
        print(f"✅ Found {len(records)} records for Shrawan")
        for record in records[:3]:
            print(f"   - {record['employee_name']}: Rs. {float(record['net_salary']):,.2f}")
        return True
    else:
        print(f"❌ Failed: {response.status_code}")
        return False

def main():
    print("🚀 Starting Payroll List API Tests...\n")
    
    token = get_auth_token()
    if not token:
        return
    
    test_list_payroll(token)
    test_filter_by_month(token)
    
    print("\n✅ All tests completed!")

if __name__ == "__main__":
    main()
