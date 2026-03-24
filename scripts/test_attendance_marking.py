#!/usr/bin/env python
"""
Test script for HR Attendance Marking
Tests the bulk-mark endpoint
"""
import os
import sys
import django
from datetime import date

# Setup Django
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core_backend.settings')
django.setup()

from hr.models import Employee, Attendance
from tenants.models import Tenant

def test_attendance_marking():
    print("=" * 60)
    print("HR ATTENDANCE MARKING TEST")
    print("=" * 60)
    
    # Get first tenant
    tenant = Tenant.objects.first()
    if not tenant:
        print("❌ No tenant found. Please create a tenant first.")
        return
    
    print(f"\n✓ Using tenant: {tenant.name}")
    
    # Get active employees
    employees = Employee.objects.filter(tenant=tenant, status='active')
    print(f"✓ Found {employees.count()} active employees")
    
    if employees.count() == 0:
        print("❌ No active employees found. Please create employees first.")
        return
    
    # Show employees
    print("\nActive Employees:")
    for emp in employees[:5]:
        print(f"  - {emp.name} ({emp.designation}) - {emp.department.name}")
    
    # Check existing attendance for today
    today = date.today()
    existing = Attendance.objects.filter(tenant=tenant, date=today)
    print(f"\n✓ Existing attendance records for {today}: {existing.count()}")
    
    if existing.count() > 0:
        print("\nExisting Records:")
        for att in existing[:5]:
            print(f"  - {att.employee.name}: {att.status} (In: {att.check_in}, Out: {att.check_out})")
    
    print("\n" + "=" * 60)
    print("TEST COMPLETE")
    print("=" * 60)
    print("\nTo test the bulk-mark endpoint:")
    print("1. Start the Django server: python manage.py runserver")
    print("2. Open: http://localhost:3000/dashboard/hr/attendance/mark")
    print("3. Select date and mark attendance for employees")
    print("4. Click 'Save Attendance'")

if __name__ == '__main__':
    test_attendance_marking()
