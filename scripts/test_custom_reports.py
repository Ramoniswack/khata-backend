#!/usr/bin/env python
"""
Test script for Custom Reports API endpoints
Tests the /api/reports/custom-reports/ endpoints
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
from datetime import datetime

# Configuration
BASE_URL = "http://localhost:8000"
API_URL = f"{BASE_URL}/api/reports/custom-reports/"

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
        print(f"Failed to get auth token: {e}")
        return None

def test_custom_reports():
    """Test custom reports endpoints"""
    print("\n" + "="*80)
    print("TESTING CUSTOM REPORTS API")
    print("="*80)
    
    # Get auth token
    print("\n1. Getting authentication token...")
    token = get_auth_token()
    if not token:
        print("Cannot proceed without authentication")
        return
    print("Authentication successful")
    
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    
    # Test 1: List custom reports (should be empty initially)
    print("\n2. Testing list custom reports...")
    try:
        response = requests.get(API_URL, headers=headers)
        response.raise_for_status()
        data = response.json()
        
        print(f"Custom reports count: {data['count']}")
        print(f"Reports: {len(data['results'])}")
    except requests.exceptions.HTTPError as e:
        print(f"HTTP Error: {e}")
        print(f"Response: {e.response.text}")
    except Exception as e:
        print(f"Error: {e}")
    
    # Test 2: Create a custom report
    print("\n3. Testing create custom report...")
    report_data = {
        "name": "Test Sales Report",
        "description": "A test report for sales data",
        "report_type": "table",
        "module": "sales",
        "fields": ["date", "customer", "amount", "status"],
        "filters": [],
        "grouping": {},
        "sorting": {"field": "date", "order": "desc"},
        "chart_config": {},
        "schedule": "weekly"
    }
    
    try:
        response = requests.post(f"{API_URL}create/", json=report_data, headers=headers)
        response.raise_for_status()
        data = response.json()
        
        print(f"Message: {data['message']}")
        report_id = data['report']['id']
        print(f"Created report ID: {report_id}")
        print(f"Report name: {data['report']['name']}")
        print(f"Module: {data['report']['module']}")
        
        # Test 3: Get report details
        print("\n4. Testing get report details...")
        response = requests.get(f"{API_URL}{report_id}/", headers=headers)
        response.raise_for_status()
        report = response.json()
        
        print(f"Report: {report['name']}")
        print(f"Created by: {report['created_by_name']}")
        print(f"Fields: {report['fields']}")
        
        # Test 4: Run the report
        print("\n5. Testing run report...")
        run_params = {
            "from_date": "2082-01-01",
            "to_date": "2082-01-31"
        }
        response = requests.post(f"{API_URL}{report_id}/run/", json=run_params, headers=headers)
        response.raise_for_status()
        result = response.json()
        
        print(f"Report executed: {result['report_name']}")
        print(f"Executed at: {result['executed_at']}")
        print(f"Rows returned: {len(result['data']['rows'])}")
        print(f"Summary: {result['data']['summary']}")
        
        # Test 5: Duplicate the report
        print("\n6. Testing duplicate report...")
        response = requests.post(f"{API_URL}{report_id}/duplicate/", headers=headers)
        response.raise_for_status()
        data = response.json()
        
        print(f"Message: {data['message']}")
        duplicate_id = data['report']['id']
        print(f"Duplicate report ID: {duplicate_id}")
        print(f"Duplicate name: {data['report']['name']}")
        
        # Test 6: Update the report
        print("\n7. Testing update report...")
        update_data = {
            "name": "Updated Test Sales Report",
            "schedule": "monthly"
        }
        response = requests.patch(f"{API_URL}{report_id}/update/", json=update_data, headers=headers)
        response.raise_for_status()
        data = response.json()
        
        print(f"Message: {data['message']}")
        print(f"Updated name: {data['report']['name']}")
        print(f"Updated schedule: {data['report']['schedule']}")
        
        # Test 7: List reports again (should have 2 now)
        print("\n8. Testing list custom reports again...")
        response = requests.get(API_URL, headers=headers)
        response.raise_for_status()
        data = response.json()
        
        print(f"Custom reports count: {data['count']}")
        for report in data['results']:
            print(f"  - {report['name']} ({report['module']})")
        
        # Test 8: Delete the duplicate report
        print("\n9. Testing delete report...")
        response = requests.delete(f"{API_URL}{duplicate_id}/delete/", headers=headers)
        response.raise_for_status()
        data = response.json()
        
        print(f"Message: {data['message']}")
        
        # Test 9: Delete the original report
        print("\n10. Testing delete original report...")
        response = requests.delete(f"{API_URL}{report_id}/delete/", headers=headers)
        response.raise_for_status()
        data = response.json()
        
        print(f"Message: {data['message']}")
        
    except requests.exceptions.HTTPError as e:
        print(f"HTTP Error: {e}")
        print(f"Response: {e.response.text}")
    except Exception as e:
        print(f"Error: {e}")
    
    print("\n" + "="*80)
    print("CUSTOM REPORTS API TEST COMPLETE")
    print("="*80 + "\n")

if __name__ == "__main__":
    test_custom_reports()
