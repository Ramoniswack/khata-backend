#!/usr/bin/env python
"""
Test script for HR Attendance Stats
Tests the stats endpoint
"""
import os
import sys
import django
from datetime import date, timedelta

# Setup Django
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core_backend.settings')
django.setup()

from hr.models import Employee, Attendance
from tenants.models import Tenant

def test_attendance_stats():
    print("=" * 60)
    print("HR ATTENDANCE STATS TEST")
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
    
    # Create some test attendance records for current month
    today = date.today()
    first_day = date(today.year, today.month, 1)
    
    print(f"\n✓ Creating test attendance records for {today.year}-{today.month:02d}")
    
    created_count = 0
    for emp in employees:
        # Create attendance for first 10 days
        for day in range(1, min(11, today.day + 1)):
            att_date = date(today.year, today.month, day)
            _, created = Attendance.objects.get_or_create(
                tenant=tenant,
                employee=emp,
                date=att_date,
                defaults={
                    'status': 'present' if day % 5 != 0 else 'absent',
                    'check_in': '09:00:00' if day % 5 != 0 else None,
                    'check_out': '17:00:00' if day % 5 != 0 else None
                }
            )
            if created:
                created_count += 1
    
    print(f"✓ Created {created_count} new attendance records")
    
    # Check stats
    month_str = f"{today.year}-{today.month:02d}"
    attendance_count = Attendance.objects.filter(
        tenant=tenant,
        date__year=today.year,
        date__month=today.month
    ).count()
    
    present_count = Attendance.objects.filter(
        tenant=tenant,
        date__year=today.year,
        date__month=today.month,
        status='present'
    ).count()
    
    absent_count = Attendance.objects.filter(
        tenant=tenant,
        date__year=today.year,
        date__month=today.month,
        status='absent'
    ).count()
    
    print(f"\nAttendance Summary for {month_str}:")
    print(f"  - Total records: {attendance_count}")
    print(f"  - Present: {present_count}")
    print(f"  - Absent: {absent_count}")
    
    print("\n" + "=" * 60)
    print("TEST COMPLETE")
    print("=" * 60)
    print("\nTo test the stats endpoint:")
    print("1. Start the Django server: python manage.py runserver")
    print(f"2. GET: http://localhost:8000/api/hr/attendance/stats/?month={month_str}")
    print("3. Open: http://localhost:3000/dashboard/hr/attendance")

if __name__ == '__main__':
    test_attendance_stats()
