#!/usr/bin/env python
"""
Test script for Financial Reports API endpoint
Tests the /api/reports/financial-reports/ endpoint
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
API_URL = f"{BASE_URL}/api/reports/financial-reports/"

def get_auth_token():
    """Get authentication token"""
    login_url = f"{BASE_URL}/api/users/login/"
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

def test_financial_reports():
    """Test financial reports endpoint"""
    print("\n" + "="*80)
    print("TESTING FINANCIAL REPORTS API")
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
    
    # Calculate date range (current month)
    today = datetime.now()
    from_date = today.replace(day=1).strftime('%Y-%m-%d')
    to_date = today.strftime('%Y-%m-%d')
    as_of_date = today.strftime('%Y-%m-%d')
    
    # Test 1: Get financial reports with default dates
    print("\n2. Testing financial reports endpoint (default dates)...")
    try:
        response = requests.get(API_URL, headers=headers)
        response.raise_for_status()
        data = response.json()
        
        print("✅ Financial reports retrieved successfully")
        print(f"\n📊 PROFIT & LOSS:")
        print(f"   Period: {data['profit_and_loss']['period']['from_date']} to {data['profit_and_loss']['period']['to_date']}")
        print(f"   Total Income: Rs. {data['profit_and_loss']['total_income']:,.2f}")
        print(f"   Total Expenses: Rs. {data['profit_and_loss']['total_expenses']:,.2f}")
        print(f"   Net Profit: Rs. {data['profit_and_loss']['net_profit']:,.2f}")
        print(f"   Income Accounts: {len(data['profit_and_loss']['income'])}")
        print(f"   Expense Accounts: {len(data['profit_and_loss']['expenses'])}")
        
        print(f"\n📊 BALANCE SHEET:")
        print(f"   As of: {data['balance_sheet']['as_of_date']}")
        print(f"   Total Assets: Rs. {data['balance_sheet']['total_assets']:,.2f}")
        print(f"   Total Liabilities: Rs. {data['balance_sheet']['total_liabilities']:,.2f}")
        print(f"   Total Equity: Rs. {data['balance_sheet']['total_equity']:,.2f}")
        print(f"   Asset Accounts: {len(data['balance_sheet']['assets'])}")
        print(f"   Liability Accounts: {len(data['balance_sheet']['liabilities'])}")
        print(f"   Equity Accounts: {len(data['balance_sheet']['equity'])}")
        
        print(f"\n📊 TRIAL BALANCE:")
        print(f"   As of: {data['trial_balance']['as_of_date']}")
        print(f"   Total Debit: Rs. {data['trial_balance']['total_debit']:,.2f}")
        print(f"   Total Credit: Rs. {data['trial_balance']['total_credit']:,.2f}")
        print(f"   Accounts: {len(data['trial_balance']['accounts'])}")
        balanced = data['trial_balance']['total_debit'] == data['trial_balance']['total_credit']
        print(f"   Balanced: {'✅ Yes' if balanced else '❌ No'}")
        
        print(f"\n📊 CASH FLOW:")
        print(f"   Period: {data['cash_flow']['period']['from_date']} to {data['cash_flow']['period']['to_date']}")
        print(f"   Operating Activities: Rs. {data['cash_flow']['operating_activities']:,.2f}")
        print(f"   Investing Activities: Rs. {data['cash_flow']['investing_activities']:,.2f}")
        print(f"   Financing Activities: Rs. {data['cash_flow']['financing_activities']:,.2f}")
        print(f"   Net Cash Change: Rs. {data['cash_flow']['net_cash_change']:,.2f}")
        print(f"   Opening Cash: Rs. {data['cash_flow']['opening_cash']:,.2f}")
        print(f"   Closing Cash: Rs. {data['cash_flow']['closing_cash']:,.2f}")
        
    except requests.exceptions.HTTPError as e:
        print(f"❌ HTTP Error: {e}")
        print(f"Response: {e.response.text}")
    except Exception as e:
        print(f"❌ Error: {e}")
    
    # Test 2: Get financial reports with custom dates
    print("\n3. Testing financial reports endpoint (custom dates)...")
    params = {
        'from_date': from_date,
        'to_date': to_date,
        'as_of_date': as_of_date
    }
    try:
        response = requests.get(API_URL, headers=headers, params=params)
        response.raise_for_status()
        data = response.json()
        
        print("✅ Financial reports with custom dates retrieved successfully")
        print(f"   Requested period: {from_date} to {to_date}")
        print(f"   As of date: {as_of_date}")
        
    except requests.exceptions.HTTPError as e:
        print(f"❌ HTTP Error: {e}")
        print(f"Response: {e.response.text}")
    except Exception as e:
        print(f"❌ Error: {e}")
    
    print("\n" + "="*80)
    print("FINANCIAL REPORTS API TEST COMPLETE")
    print("="*80 + "\n")

if __name__ == "__main__":
    test_financial_reports()
