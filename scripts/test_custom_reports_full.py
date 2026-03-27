#!/usr/bin/env python
"""
Test script for Custom Reports API
Tests all CRUD operations and report execution
"""

import os
import sys
import django

# Setup Django
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core_backend.settings')
django.setup()

import requests
import json
from datetime import datetime

# Configuration
BASE_URL = "http://localhost:8000/api"
USERNAME = "testreports"
PASSWORD = "test123"

def get_auth_token():
    """Get authentication token"""
    response = requests.post(
        f"{BASE_URL}/auth/login/",
        json={"username": USERNAME, "password": PASSWORD}
    )
    if response.status_code == 200:
        data = response.json()
        return data.get('access')
    else:
        print(f"❌ Login failed: {response.status_code}")
        print(response.text)
        return None

def test_custom_reports():
    """Test custom reports functionality"""
    print("\n" + "="*80)
    print("CUSTOM REPORTS API TEST")
    print("="*80)
    
    # Get auth token
    print("\n1. Getting authentication token...")
    token = get_auth_token()
    if not token:
        return
    
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    
    print("✅ Authentication successful")
    
    # Test 1: List custom reports (should be empty initially)
    print("\n2. Listing custom reports...")
    response = requests.get(
        f"{BASE_URL}/reports/custom-reports/",
        headers=headers
    )
    print(f"Status: {response.status_code}")
    if response.status_code == 200:
        data = response.json()
        print(f"✅ Found {data['count']} custom reports")
        print(json.dumps(data, indent=2))
    else:
        print(f"❌ Failed: {response.text}")
        return
    
    # Test 2: Create a new custom report
    print("\n3. Creating a new custom report...")
    report_data = {
        "name": "Sales Performance Report",
        "description": "Monthly sales performance analysis",
        "report_type": "both",
        "module": "sales",
        "fields": ["date", "customer", "amount", "status"],
        "filters": [
            {"field": "status", "operator": "equals", "value": "completed"}
        ],
        "grouping": {"field": "customer"},
        "sorting": {"field": "amount", "order": "desc"},
        "chart_config": {
            "type": "bar",
            "x_axis": "customer",
            "y_axis": "amount"
        },
        "schedule": "monthly",
        "is_shared": False
    }
    
    response = requests.post(
        f"{BASE_URL}/reports/custom-reports/create/",
        headers=headers,
        json=report_data
    )
    print(f"Status: {response.status_code}")
    if response.status_code == 201:
        data = response.json()
        print(f"✅ Report created: {data['report']['name']}")
        report_id = data['report']['id']
        print(f"Report ID: {report_id}")
        print(json.dumps(data, indent=2))
    else:
        print(f"❌ Failed: {response.text}")
        return
    
    # Test 3: Get report details
    print(f"\n4. Getting report details for ID: {report_id}...")
    response = requests.get(
        f"{BASE_URL}/reports/custom-reports/{report_id}/",
        headers=headers
    )
    print(f"Status: {response.status_code}")
    if response.status_code == 200:
        data = response.json()
        print(f"✅ Report details retrieved")
        print(json.dumps(data, indent=2))
    else:
        print(f"❌ Failed: {response.text}")
    
    # Test 4: Run the report
    print(f"\n5. Running report ID: {report_id}...")
    response = requests.post(
        f"{BASE_URL}/reports/custom-reports/{report_id}/run/",
        headers=headers,
        json={
            "from_date": "2024-01-01",
            "to_date": "2024-12-31"
        }
    )
    print(f"Status: {response.status_code}")
    if response.status_code == 200:
        data = response.json()
        print(f"✅ Report executed successfully")
        print(f"Report: {data['report_name']}")
        print(f"Module: {data['module']}")
        print(f"Rows: {data['data']['summary']['total_rows']}")
        print(json.dumps(data, indent=2))
    else:
        print(f"❌ Failed: {response.text}")
    
    # Test 5: Update the report
    print(f"\n6. Updating report ID: {report_id}...")
    update_data = {
        "name": "Sales Performance Report (Updated)",
        "description": "Updated monthly sales performance analysis",
        "schedule": "weekly"
    }
    response = requests.put(
        f"{BASE_URL}/reports/custom-reports/{report_id}/update/",
        headers=headers,
        json=update_data
    )
    print(f"Status: {response.status_code}")
    if response.status_code == 200:
        data = response.json()
        print(f"✅ Report updated: {data['report']['name']}")
        print(json.dumps(data, indent=2))
    else:
        print(f"❌ Failed: {response.text}")
    
    # Test 6: Duplicate the report
    print(f"\n7. Duplicating report ID: {report_id}...")
    response = requests.post(
        f"{BASE_URL}/reports/custom-reports/{report_id}/duplicate/",
        headers=headers
    )
    print(f"Status: {response.status_code}")
    if response.status_code == 201:
        data = response.json()
        print(f"✅ Report duplicated: {data['report']['name']}")
        duplicate_id = data['report']['id']
        print(f"Duplicate ID: {duplicate_id}")
        print(json.dumps(data, indent=2))
    else:
        print(f"❌ Failed: {response.text}")
        duplicate_id = None
    
    # Test 7: List reports again (should show 2 now)
    print("\n8. Listing custom reports again...")
    response = requests.get(
        f"{BASE_URL}/reports/custom-reports/",
        headers=headers
    )
    print(f"Status: {response.status_code}")
    if response.status_code == 200:
        data = response.json()
        print(f"✅ Found {data['count']} custom reports")
        for report in data['results']:
            print(f"  - {report['name']} (ID: {report['id']})")
    else:
        print(f"❌ Failed: {response.text}")
    
    # Test 8: Filter by module
    print("\n9. Filtering reports by module (sales)...")
    response = requests.get(
        f"{BASE_URL}/reports/custom-reports/?module=sales",
        headers=headers
    )
    print(f"Status: {response.status_code}")
    if response.status_code == 200:
        data = response.json()
        print(f"✅ Found {data['count']} sales reports")
    else:
        print(f"❌ Failed: {response.text}")
    
    # Test 9: Delete the duplicate report
    if duplicate_id:
        print(f"\n10. Deleting duplicate report ID: {duplicate_id}...")
        response = requests.delete(
            f"{BASE_URL}/reports/custom-reports/{duplicate_id}/delete/",
            headers=headers
        )
        print(f"Status: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"✅ {data['message']}")
        else:
            print(f"❌ Failed: {response.text}")
    
    # Test 10: Delete the original report
    print(f"\n11. Deleting original report ID: {report_id}...")
    response = requests.delete(
        f"{BASE_URL}/reports/custom-reports/{report_id}/delete/",
        headers=headers
    )
    print(f"Status: {response.status_code}")
    if response.status_code == 200:
        data = response.json()
        print(f"✅ {data['message']}")
    else:
        print(f"❌ Failed: {response.text}")
    
    # Test 11: Verify deletion
    print("\n12. Verifying deletion...")
    response = requests.get(
        f"{BASE_URL}/reports/custom-reports/",
        headers=headers
    )
    print(f"Status: {response.status_code}")
    if response.status_code == 200:
        data = response.json()
        print(f"✅ Found {data['count']} custom reports (should be back to original count)")
    else:
        print(f"❌ Failed: {response.text}")
    
    print("\n" + "="*80)
    print("TEST COMPLETED")
    print("="*80)

if __name__ == "__main__":
    test_custom_reports()
