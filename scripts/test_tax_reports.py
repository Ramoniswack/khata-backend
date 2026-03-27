#!/usr/bin/env python
"""
Test script for Tax Reports API endpoint
Tests the /api/reports/tax-reports/ endpoint
"""

import os
import sys
import django

# Add the backend directory to the Python path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core_backend.settings')
django.setup()

import requests
from datetime import datetime, timedelta

# Configuration
BASE_URL = "http://localhost:8000"
API_URL = f"{BASE_URL}/api/reports/tax-reports/"

def get_auth_token():
    """Get authentication token"""
    login_url = f"{BASE_URL}/api/auth/login/"
    credentials = {
        "username": "admin",
        "password": "admin123"
    }
    
    try:
        response = requests.post(login_url, json=credentials)
        response.raise_for_status()
        data = response.json()
        return data.get('access')
    except Exception as e:
        print(f"❌ Failed to get auth token: {e}")
        return None

def test_tax_reports():
    """Test tax reports endpoint"""
    print("\n" + "="*80)
    print("TESTING TAX REPORTS API")
    print("="*80)
    
    # Get auth token
    print("\n1. Getting authentication token...")
    token = get_auth_token()
    if not token:
        print("❌ Cannot proceed without authentication")
        return
    print("✅ Authentication successful")
    
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    
    # Test 1: Get tax reports with default dates
    print("\n2. Testing tax reports endpoint (default dates)...")
    try:
        response = requests.get(API_URL, headers=headers)
        response.raise_for_status()
        data = response.json()
        
        print("✅ Tax reports retrieved successfully")
        print(f"\n📊 PERIOD:")
        print(f"   From: {data['period']['from_date']}")
        print(f"   To: {data['period']['to_date']}")
        
        print(f"\n📊 VAT REPORT:")
        print(f"   Output VAT: Rs. {data['vat']['output_vat']:,.2f}")
        print(f"   Input VAT: Rs. {data['vat']['input_vat']:,.2f}")
        print(f"   Net Payable: Rs. {data['vat']['net_payable']:,.2f}")
        print(f"   Returns Filed: {data['vat']['returns_filed']}")
        print(f"   Monthly Records: {len(data['vat']['monthly'])}")
        
        print(f"\n📊 TDS REPORT:")
        print(f"   Total Deducted: Rs. {data['tds']['total_deducted']:,.2f}")
        print(f"   On Services: Rs. {data['tds']['on_services']:,.2f}")
        print(f"   On Rent: Rs. {data['tds']['on_rent']:,.2f}")
        print(f"   On Goods: Rs. {data['tds']['on_goods']:,.2f}")
        print(f"   Detail Records: {len(data['tds']['details'])}")
        
        print(f"\n📊 INCOME TAX REPORT:")
        print(f"   Employees: {len(data['income_tax']['employees'])}")
        
        if data['vat']['monthly']:
            print(f"\n📋 Sample VAT Monthly Data:")
            month = data['vat']['monthly'][0]
            print(f"   Month: {month['month']}")
            print(f"   Sales (Ex VAT): Rs. {month['sales_ex_vat']:,.2f}")
            print(f"   Output VAT: Rs. {month['output_vat']:,.2f}")
            print(f"   Net VAT: Rs. {month['net_vat']:,.2f}")
            print(f"   Status: {month['status']}")
        
        if data['tds']['details']:
            print(f"\n📋 Sample TDS Detail:")
            detail = data['tds']['details'][0]
            print(f"   Supplier: {detail['supplier']}")
            print(f"   Type: {detail['type']}")
            print(f"   Gross: Rs. {detail['gross']:,.2f}")
            print(f"   TDS Rate: {detail['rate']}%")
            print(f"   TDS Amount: Rs. {detail['tds']:,.2f}")
        
        if data['income_tax']['employees']:
            print(f"\n📋 Sample Income Tax Employee:")
            emp = data['income_tax']['employees'][0]
            print(f"   Employee: {emp['employee']}")
            print(f"   Gross Salary YTD: Rs. {emp['gross_salary_ytd']:,.2f}")
            print(f"   Tax Slab: {emp['tax_slab']}")
            print(f"   Tax Amount: Rs. {emp['tax_amount']:,.2f}")
        
    except requests.exceptions.HTTPError as e:
        print(f"❌ HTTP Error: {e}")
        print(f"Response: {e.response.text}")
    except Exception as e:
        print(f"❌ Error: {e}")
    
    # Test 2: Get tax reports with custom dates
    print("\n3. Testing tax reports endpoint (custom dates)...")
    today = datetime.now()
    from_date = (today - timedelta(days=90)).strftime('%Y-%m-%d')
    to_date = today.strftime('%Y-%m-%d')
    
    params = {
        'from_date': from_date,
        'to_date': to_date
    }
    try:
        response = requests.get(API_URL, headers=headers, params=params)
        response.raise_for_status()
        data = response.json()
        
        print("✅ Tax reports with custom dates retrieved successfully")
        print(f"   Requested period: {from_date} to {to_date}")
        print(f"   VAT Monthly Records: {len(data['vat']['monthly'])}")
        
    except requests.exceptions.HTTPError as e:
        print(f"❌ HTTP Error: {e}")
        print(f"Response: {e.response.text}")
    except Exception as e:
        print(f"❌ Error: {e}")
    
    print("\n" + "="*80)
    print("TAX REPORTS API TEST COMPLETE")
    print("="*80 + "\n")

if __name__ == "__main__":
    test_tax_reports()
