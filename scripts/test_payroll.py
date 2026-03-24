#!/usr/bin/env python
"""Test script for payroll API endpoints"""
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
    # Get first superuser
    user = User.objects.filter(is_superuser=True).first()
    if not user:
        print("❌ No superuser found. Please create one first.")
        return None
    
    # Login
    response = requests.post(f"{BASE_URL}/auth/login/", json={
        "username": user.username,
        "password": "admin123"  # Default password
    })
    
    if response.status_code == 200:
        token = response.json().get('access')
        print(f"✅ Logged in as: {user.username}")
        return token
    else:
        print(f"❌ Login failed: {response.status_code}")
        print(response.text)
        return None

def test_calculate_payroll(token):
    """Test calculate payroll endpoint"""
    print("\n📊 Testing Calculate Payroll...")
    
    headers = {"Authorization": f"Bearer {token}"}
    data = {
        "month": "Shrawan",
        "year": 2081
    }
    
    response = requests.post(f"{BASE_URL}/hr/payroll/calculate/", json=data, headers=headers)
    
    if response.status_code == 200:
        result = response.json()
        print(f"✅ Payroll calculated successfully")
        print(f"   Month: {result['month']} {result['year']}")
        print(f"   Total Employees: {result['total_employees']}")
        print(f"   Total Gross: Rs. {result['total_gross']:,.2f}")
        print(f"   Total Deductions: Rs. {result['total_deductions']:,.2f}")
        print(f"   Total Net: Rs. {result['total_net']:,.2f}")
        print(f"\n   Employee Details:")
        for emp in result['payroll_data'][:3]:  # Show first 3
            print(f"   - {emp['employee_name']}: Basic Rs. {emp['basic_salary']:,.2f}, Net Rs. {emp['net_salary']:,.2f}")
        return result
    else:
        print(f"❌ Failed: {response.status_code}")
        print(response.text)
        return None

def test_process_payroll(token, payroll_data):
    """Test process payroll endpoint"""
    print("\n💾 Testing Process Payroll...")
    
    headers = {"Authorization": f"Bearer {token}"}
    data = {
        "month": payroll_data['month'],
        "year": payroll_data['year'],
        "payroll_data": payroll_data['payroll_data']
    }
    
    response = requests.post(f"{BASE_URL}/hr/payroll/process/", json=data, headers=headers)
    
    if response.status_code == 201:
        result = response.json()
        print(f"✅ {result['message']}")
        print(f"   Records created: {len(result['records'])}")
        return True
    else:
        print(f"❌ Failed: {response.status_code}")
        print(response.text)
        return False

def test_list_payroll(token):
    """Test list payroll endpoint"""
    print("\n📋 Testing List Payroll...")
    
    headers = {"Authorization": f"Bearer {token}"}
    response = requests.get(f"{BASE_URL}/hr/payroll/", headers=headers)
    
    if response.status_code == 200:
        result = response.json()
        records = result.get('results', [])
        print(f"✅ Found {len(records)} payroll records")
        for record in records[:3]:  # Show first 3
            net_salary = float(record['net_salary'])
            print(f"   - {record['employee_name']}: {record['month']} {record['year']} - Rs. {net_salary:,.2f} ({record['status']})")
        return True
    else:
        print(f"❌ Failed: {response.status_code}")
        print(response.text)
        return False

def main():
    print("🚀 Starting Payroll API Tests...\n")
    
    # Get auth token
    token = get_auth_token()
    if not token:
        return
    
    # Test calculate payroll
    payroll_data = test_calculate_payroll(token)
    if not payroll_data:
        return
    
    # Test process payroll
    if not test_process_payroll(token, payroll_data):
        return
    
    # Test list payroll
    test_list_payroll(token)
    
    print("\n✅ All tests completed!")

if __name__ == "__main__":
    main()
