#!/usr/bin/env python
"""
Test script for Leave Request Creation
"""
import os
import sys
import django
from datetime import date, timedelta

# Setup Django
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core_backend.settings')
django.setup()

from hr.models import Employee, LeaveType, LeaveRequest
from tenants.models import Tenant

def test_leave_request():
    print("=" * 60)
    print("LEAVE REQUEST TEST")
    print("=" * 60)
    
    # Get first tenant
    tenant = Tenant.objects.first()
    if not tenant:
        print("❌ No tenant found. Please create a tenant first.")
        return
    
    print(f"\n✓ Using tenant: {tenant.name}")
    
    # Get an employee
    employee = Employee.objects.filter(tenant=tenant, status='active').first()
    if not employee:
        print("❌ No active employee found. Please create an employee first.")
        return
    
    print(f"✓ Using employee: {employee.name}")
    
    # Get leave types
    leave_types = LeaveType.objects.filter(tenant=tenant)
    print(f"✓ Found {leave_types.count()} leave types")
    
    if leave_types.count() == 0:
        print("❌ No leave types found. Run seed_leave_types.py first.")
        return
    
    # Show leave types
    print("\nAvailable Leave Types:")
    for lt in leave_types:
        print(f"  - {lt.name}: {lt.days_allowed} days ({'Paid' if lt.is_paid else 'Unpaid'})")
    
    # Create a test leave request
    leave_type = leave_types.first()
    today = date.today()
    start_date = today + timedelta(days=7)
    end_date = start_date + timedelta(days=2)
    
    leave_request, created = LeaveRequest.objects.get_or_create(
        tenant=tenant,
        employee=employee,
        leave_type=leave_type,
        start_date=start_date,
        defaults={
            'end_date': end_date,
            'reason': 'Test leave request for personal reasons',
            'status': 'pending'
        }
    )
    
    if created:
        print(f"\n✓ Created test leave request:")
    else:
        print(f"\n✓ Found existing leave request:")
    
    print(f"  - Employee: {leave_request.employee.name}")
    print(f"  - Leave Type: {leave_request.leave_type.name}")
    print(f"  - Dates: {leave_request.start_date} to {leave_request.end_date}")
    print(f"  - Days: {leave_request.days_requested}")
    print(f"  - Status: {leave_request.status}")
    print(f"  - Reason: {leave_request.reason}")
    
    # Check all leave requests
    all_requests = LeaveRequest.objects.filter(tenant=tenant)
    print(f"\n✓ Total leave requests: {all_requests.count()}")
    
    print("\n" + "=" * 60)
    print("TEST COMPLETE")
    print("=" * 60)
    print("\nTo test the API:")
    print("1. Start the Django server: python manage.py runserver")
    print("2. GET: http://localhost:8000/api/hr/leave-types/")
    print("3. POST: http://localhost:8000/api/hr/leave-requests/")
    print("4. Open: http://localhost:3000/dashboard/hr/leave/requests/new")

if __name__ == '__main__':
    test_leave_request()
