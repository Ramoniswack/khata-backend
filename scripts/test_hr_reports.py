#!/usr/bin/env python
"""Test script for HR reports API endpoint"""
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

def test_hr_reports(token):
    """Test HR reports endpoint"""
    print("\n📊 Testing HR Reports...")
    
    headers = {"Authorization": f"Bearer {token}"}
    response = requests.get(f"{BASE_URL}/hr/reports/", headers=headers)
    
    if response.status_code == 200:
        data = response.json()
        
        print(f"✅ HR Reports retrieved successfully\n")
        
        # Summary
        summary = data.get('summary', {})
        print(f"📈 Summary:")
        print(f"   Total Employees: {summary.get('total_employees', 0)}")
        print(f"   Active Employees: {summary.get('active_employees', 0)}")
        print(f"   On Leave: {summary.get('on_leave', 0)}")
        print(f"   Avg Salary: Rs. {summary.get('avg_salary', 0):,.2f}")
        
        # Department breakdown
        dept_data = data.get('department_data', [])
        print(f"\n🏢 Department Breakdown:")
        for dept in dept_data[:5]:
            print(f"   {dept['name']}: {dept['employee_count']} employees")
        
        # Attendance trend
        attendance = data.get('attendance_trend', [])
        print(f"\n📅 Attendance Trend (Last 7 days):")
        for att in attendance:
            print(f"   {att['date']}: {att['rate']}%")
        
        # Employment type
        emp_types = data.get('employment_type_data', [])
        print(f"\n👥 Employment Type Distribution:")
        for emp_type in emp_types:
            print(f"   {emp_type['employment_type']}: {emp_type['count']} ({emp_type['percentage']}%)")
        
        return True
    else:
        print(f"❌ Failed: {response.status_code}")
        print(response.text)
        return False

def main():
    print("🚀 Starting HR Reports API Test...\n")
    
    token = get_auth_token()
    if not token:
        return
    
    test_hr_reports(token)
    
    print("\n✅ Test completed!")

if __name__ == "__main__":
    main()
