#!/usr/bin/env python
"""
Test script to verify department employee filtering
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

def test_get_departments(token):
    """Get all departments"""
    print("\n" + "="*60)
    print("TEST 1: Get All Departments")
    print("="*60)
    
    headers = {"Authorization": f"Bearer {token}"}
    response = requests.get(
        f"{BASE_URL}/hr/departments/",
        headers=headers
    )
    
    print(f"Status Code: {response.status_code}")
    
    if response.status_code == 200:
        data = response.json()
        departments = data.get('results', data) if isinstance(data, dict) else data
        print(f"✅ Found {len(departments)} departments")
        for dept in departments:
            print(f"\n  Department: {dept['name']}")
            print(f"  ID: {dept['id']}")
            print(f"  Employee Count: {dept.get('employee_count', 0)}")
            print(f"  Head: {dept.get('head_name', 'None')}")
        return departments
    else:
        print("❌ Failed to get departments")
        print(response.text)
        return []

def test_get_employees_by_department(token, department_id, department_name):
    """Get employees filtered by department"""
    print("\n" + "="*60)
    print(f"TEST 2: Get Employees for Department: {department_name}")
    print("="*60)
    
    headers = {"Authorization": f"Bearer {token}"}
    response = requests.get(
        f"{BASE_URL}/hr/employees/",
        headers=headers,
        params={"department": department_id}
    )
    
    print(f"Status Code: {response.status_code}")
    print(f"URL: {response.url}")
    
    if response.status_code == 200:
        data = response.json()
        employees = data.get('results', [])
        print(f"✅ Found {len(employees)} employees in this department")
        
        if len(employees) == 0:
            print("  ⚠️  No employees in this department")
        else:
            for emp in employees:
                print(f"\n  Employee: {emp['name']}")
                print(f"  ID: {emp['id']}")
                print(f"  Designation: {emp['designation']}")
                print(f"  Department: {emp.get('department_name', 'N/A')}")
                print(f"  Phone: {emp['phone']}")
                print(f"  Email: {emp['email']}")
        
        return employees
    else:
        print("❌ Failed to get employees")
        print(response.text)
        return []

def test_get_all_employees(token):
    """Get all employees (no filter)"""
    print("\n" + "="*60)
    print("TEST 3: Get All Employees (No Filter)")
    print("="*60)
    
    headers = {"Authorization": f"Bearer {token}"}
    response = requests.get(
        f"{BASE_URL}/hr/employees/",
        headers=headers
    )
    
    print(f"Status Code: {response.status_code}")
    
    if response.status_code == 200:
        data = response.json()
        employees = data.get('results', [])
        print(f"✅ Found {len(employees)} total employees")
        
        # Group by department
        dept_groups = {}
        for emp in employees:
            dept_name = emp.get('department_name', 'Unknown')
            if dept_name not in dept_groups:
                dept_groups[dept_name] = []
            dept_groups[dept_name].append(emp['name'])
        
        print("\nEmployees by Department:")
        for dept, emps in dept_groups.items():
            print(f"  {dept}: {len(emps)} employees")
            for emp_name in emps:
                print(f"    - {emp_name}")
        
        return employees
    else:
        print("❌ Failed to get employees")
        print(response.text)
        return []

def main():
    print("🚀 Starting Department Employees Filter Test")
    print("="*60)
    
    # Get authentication token
    print("\n📝 Authenticating...")
    token = get_auth_token()
    print("✅ Authentication successful")
    
    # Get all departments
    departments = test_get_departments(token)
    
    # Get all employees
    all_employees = test_get_all_employees(token)
    
    # Test filtering for each department
    if departments:
        for dept in departments:
            test_get_employees_by_department(token, dept['id'], dept['name'])
    
    print("\n" + "="*60)
    print("✅ All tests completed!")
    print("="*60)

if __name__ == "__main__":
    main()
