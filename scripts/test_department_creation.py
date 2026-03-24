#!/usr/bin/env python
"""
Test script for Department Creation API
Tests the department creation endpoint with various scenarios
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

# Configuration
BASE_URL = "http://localhost:8000/api"
USERNAME = "admin@example.com"
PASSWORD = "admin123"

def get_auth_token():
    """Get authentication token"""
    response = requests.post(
        f"{BASE_URL}/users/login/",
        json={"email": USERNAME, "password": PASSWORD}
    )
    if response.status_code == 200:
        return response.json()['access']
    else:
        print(f"❌ Login failed: {response.status_code}")
        print(response.text)
        sys.exit(1)

def test_create_department(token):
    """Test creating a new department"""
    print("\n" + "="*60)
    print("TEST 1: Create Department (Basic)")
    print("="*60)
    
    headers = {"Authorization": f"Bearer {token}"}
    data = {
        "name": "Engineering",
        "description": "Software Engineering Department"
    }
    
    response = requests.post(
        f"{BASE_URL}/hr/departments/",
        headers=headers,
        json=data
    )
    
    print(f"Status Code: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")
    
    if response.status_code == 201:
        print("✅ Department created successfully")
        return response.json()['id']
    else:
        print("❌ Failed to create department")
        return None

def test_create_department_with_head(token, employee_id):
    """Test creating a department with a head"""
    print("\n" + "="*60)
    print("TEST 2: Create Department with Head")
    print("="*60)
    
    headers = {"Authorization": f"Bearer {token}"}
    data = {
        "name": "Human Resources",
        "description": "HR Department",
        "head": employee_id
    }
    
    response = requests.post(
        f"{BASE_URL}/hr/departments/",
        headers=headers,
        json=data
    )
    
    print(f"Status Code: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")
    
    if response.status_code == 201:
        print("✅ Department with head created successfully")
        return response.json()['id']
    else:
        print("❌ Failed to create department with head")
        return None

def test_duplicate_department(token):
    """Test creating a duplicate department"""
    print("\n" + "="*60)
    print("TEST 3: Create Duplicate Department (Should Fail)")
    print("="*60)
    
    headers = {"Authorization": f"Bearer {token}"}
    data = {
        "name": "Engineering",  # Duplicate
        "description": "Another Engineering Department"
    }
    
    response = requests.post(
        f"{BASE_URL}/hr/departments/",
        headers=headers,
        json=data
    )
    
    print(f"Status Code: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")
    
    if response.status_code == 400:
        print("✅ Duplicate department correctly rejected")
    else:
        print("❌ Duplicate department should have been rejected")

def test_list_departments(token):
    """Test listing all departments"""
    print("\n" + "="*60)
    print("TEST 4: List All Departments")
    print("="*60)
    
    headers = {"Authorization": f"Bearer {token}"}
    response = requests.get(
        f"{BASE_URL}/hr/departments/",
        headers=headers
    )
    
    print(f"Status Code: {response.status_code}")
    data = response.json()
    
    if response.status_code == 200:
        departments = data.get('results', data)
        print(f"✅ Found {len(departments)} departments")
        for dept in departments:
            print(f"  - {dept['name']} (ID: {dept['id']}, Employees: {dept.get('employee_count', 0)})")
    else:
        print("❌ Failed to list departments")

def get_first_employee(token):
    """Get the first active employee for testing"""
    headers = {"Authorization": f"Bearer {token}"}
    response = requests.get(
        f"{BASE_URL}/hr/employees/?status=active",
        headers=headers
    )
    
    if response.status_code == 200:
        data = response.json()
        employees = data.get('results', [])
        if employees:
            return employees[0]['id']
    return None

def main():
    print("🚀 Starting Department Creation API Tests")
    print("="*60)
    
    # Get authentication token
    print("\n📝 Authenticating...")
    token = get_auth_token()
    print("✅ Authentication successful")
    
    # Get an employee for testing department head
    print("\n📝 Getting employee for testing...")
    employee_id = get_first_employee(token)
    if employee_id:
        print(f"✅ Found employee: {employee_id}")
    else:
        print("⚠️  No employees found, skipping head assignment test")
    
    # Run tests
    dept_id = test_create_department(token)
    
    if employee_id:
        test_create_department_with_head(token, employee_id)
    
    test_duplicate_department(token)
    test_list_departments(token)
    
    print("\n" + "="*60)
    print("✅ All tests completed!")
    print("="*60)

if __name__ == "__main__":
    main()
