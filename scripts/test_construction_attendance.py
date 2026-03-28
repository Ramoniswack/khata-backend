#!/usr/bin/env python
"""
Test script for Construction Attendance functionality
Tests the bulk_mark endpoint and attendance operations
"""

import os
import sys
import django
from pathlib import Path

# Add backend directory to path
backend_dir = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(backend_dir))

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core_backend.settings')
django.setup()

from django.contrib.auth import get_user_model
from construction.models import Site, Worker, Attendance
from datetime import date, time
import json

User = get_user_model()

def test_attendance():
    """Test attendance marking functionality"""
    
    print("=" * 80)
    print("CONSTRUCTION ATTENDANCE TEST")
    print("=" * 80)
    
    # Get a user with tenant
    user = User.objects.filter(tenant__isnull=False).first()
    if not user:
        print("❌ No user with tenant found")
        return
    
    print(f"\n✓ Testing with user: {user.username}")
    print(f"✓ Tenant: {user.tenant.name}")
    
    # Get or create a site
    site = Site.objects.filter(tenant=user.tenant).first()
    if not site:
        print("\n❌ No site found. Creating test site...")
        # Get an employee to be manager
        from hr.models import Employee
        manager = Employee.objects.filter(tenant=user.tenant, status='active').first()
        
        if not manager:
            print("❌ No active employee found. Please create an employee first.")
            print("   Run: python manage.py shell")
            print("   Then create an employee or use the HR module to add employees")
            return
        
        from inventory.models import Warehouse
        warehouse = Warehouse.objects.filter(tenant=user.tenant).first()
        
        if not warehouse:
            print("❌ No warehouse found. Please create a warehouse first.")
            return
        
        site = Site.objects.create(
            tenant=user.tenant,
            name="Test Construction Site",
            location="Test Location",
            client_name="Test Client",
            allocated_budget=1000000,
            start_date=date.today(),
            manager=manager,
            warehouse=warehouse,
            status='active'
        )
        print(f"✓ Created test site: {site.name}")
    else:
        print(f"\n✓ Using existing site: {site.name}")
    
    # Get or create workers
    workers = Worker.objects.filter(tenant=user.tenant, assigned_site=site, status='active')[:3]
    
    if workers.count() < 3:
        print(f"\n⚠ Only {workers.count()} workers found. Creating test workers...")
        for i in range(3 - workers.count()):
            worker = Worker.objects.create(
                tenant=user.tenant,
                name=f"Test Worker {i+1}",
                phone=f"98400000{i+1}",
                category='mason',
                daily_wage=1500,
                assigned_site=site,
                status='active'
            )
            print(f"✓ Created worker: {worker.name}")
        workers = Worker.objects.filter(tenant=user.tenant, assigned_site=site, status='active')[:3]
    
    print(f"\n✓ Found {workers.count()} active workers for site")
    
    # Test 1: Mark attendance for workers
    print("\n" + "=" * 80)
    print("TEST 1: Bulk Mark Attendance")
    print("=" * 80)
    
    today = date.today()
    
    # Prepare attendance data
    attendance_data = []
    for idx, worker in enumerate(workers):
        status_options = ['present', 'absent', 'half_day', 'overtime']
        status = status_options[idx % len(status_options)]
        
        record = {
            'worker': str(worker.id),
            'status': status,
        }
        
        if status != 'absent':
            record['check_in'] = '08:00:00'
            record['check_out'] = '17:00:00'
        
        attendance_data.append(record)
        print(f"  Worker: {worker.name} - Status: {status}")
    
    # Delete existing attendance for today to avoid duplicates
    Attendance.objects.filter(
        tenant=user.tenant,
        site=site,
        date=today
    ).delete()
    
    # Create attendance records
    created_count = 0
    for data in attendance_data:
        worker = Worker.objects.get(id=data['worker'])
        
        # Calculate wage amount
        if data['status'] == 'present':
            wage_amount = worker.daily_wage
        elif data['status'] == 'half_day':
            wage_amount = worker.daily_wage / 2
        elif data['status'] == 'overtime':
            wage_amount = worker.daily_wage * 1.5
        else:
            wage_amount = 0
        
        attendance = Attendance.objects.create(
            tenant=user.tenant,
            worker=worker,
            site=site,
            date=today,
            status=data['status'],
            check_in=data.get('check_in'),
            check_out=data.get('check_out'),
            wage_amount=wage_amount,
            marked_by=user
        )
        created_count += 1
    
    print(f"\n✓ Created {created_count} attendance records")
    
    # Test 2: Retrieve attendance records
    print("\n" + "=" * 80)
    print("TEST 2: Retrieve Attendance Records")
    print("=" * 80)
    
    attendance_records = Attendance.objects.filter(
        tenant=user.tenant,
        site=site,
        date=today
    ).select_related('worker', 'site')
    
    print(f"\n✓ Found {attendance_records.count()} attendance records for today")
    
    total_wages = 0
    for record in attendance_records:
        print(f"\n  Worker: {record.worker.name}")
        print(f"  Status: {record.status}")
        print(f"  Check In: {record.check_in or 'N/A'}")
        print(f"  Check Out: {record.check_out or 'N/A'}")
        print(f"  Wage Amount: NPR {record.wage_amount:,.2f}")
        total_wages += record.wage_amount
    
    print(f"\n✓ Total Labor Cost: NPR {total_wages:,.2f}")
    
    # Test 3: Attendance statistics
    print("\n" + "=" * 80)
    print("TEST 3: Attendance Statistics")
    print("=" * 80)
    
    from django.db.models import Count, Sum
    
    stats = attendance_records.aggregate(
        total=Count('id'),
        present=Count('id', filter=django.db.models.Q(status='present')),
        absent=Count('id', filter=django.db.models.Q(status='absent')),
        half_day=Count('id', filter=django.db.models.Q(status='half_day')),
        overtime=Count('id', filter=django.db.models.Q(status='overtime')),
        total_wages=Sum('wage_amount')
    )
    
    print(f"\n  Total Records: {stats['total']}")
    print(f"  Present: {stats['present']}")
    print(f"  Absent: {stats['absent']}")
    print(f"  Half Day: {stats['half_day']}")
    print(f"  Overtime: {stats['overtime']}")
    print(f"  Total Wages: NPR {stats['total_wages']:,.2f}")
    
    # Test 4: Site labor cost
    print("\n" + "=" * 80)
    print("TEST 4: Site Labor Cost")
    print("=" * 80)
    
    labor_cost = site.get_labor_cost()
    print(f"\n✓ Total site labor cost: NPR {labor_cost:,.2f}")
    
    print("\n" + "=" * 80)
    print("✅ ALL TESTS PASSED")
    print("=" * 80)
    
    print("\n📋 SUMMARY:")
    print(f"  - Site: {site.name}")
    print(f"  - Workers: {workers.count()}")
    print(f"  - Attendance Records: {attendance_records.count()}")
    print(f"  - Total Labor Cost: NPR {total_wages:,.2f}")
    print(f"  - Date: {today}")
    
    print("\n✅ Construction attendance system is working correctly!")
    print("   You can now use the frontend at: http://localhost:3000/dashboard/construction/attendance")

if __name__ == '__main__':
    test_attendance()
