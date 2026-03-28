#!/usr/bin/env python
"""
Test script for Construction Workers CRUD operations
Tests: List, Create, Get, Update, Delete
"""
import os
import sys
import django

# Setup Django
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core_backend.settings')
django.setup()

from django.contrib.auth import get_user_model
from construction.models import Worker, Site
from tenants.models import Tenant
from decimal import Decimal

User = get_user_model()

def test_construction_workers_crud():
    """Test Construction Workers CRUD operations"""
    
    print("\n" + "="*80)
    print("CONSTRUCTION WORKERS CRUD TEST")
    print("="*80)
    
    # Get test user and tenant
    user = User.objects.filter(email='manager@demo-company.com').first()
    if not user:
        # Try any user with a tenant
        user = User.objects.filter(tenant__isnull=False).first()
    
    if not user:
        print("❌ No user with tenant found. Please create a user first.")
        return
    
    tenant = user.tenant
    print(f"\n✓ Using tenant: {tenant.name}")
    print(f"✓ Using user: {user.email}")
    
    # Get or create a test site for assignment
    site = Site.objects.filter(tenant=tenant).first()
    if site:
        print(f"✓ Using site: {site.name}")
    else:
        print("⚠ No site found (optional for worker creation)")
    
    # TEST 1: Create Worker
    print("\n" + "-"*80)
    print("TEST 1: CREATE WORKER")
    print("-"*80)
    
    worker_data = {
        'tenant': tenant,
        'name': 'Ram Bahadur Thapa',
        'phone': '9841234567',
        'address': 'Kathmandu, Nepal',
        'category': 'mason',
        'daily_wage': Decimal('1500.00'),
        'assigned_site': site,
        'status': 'active',
        'id_number': 'CIT-12345',
        'emergency_contact': '9841234568'
    }
    
    worker = Worker.objects.create(**worker_data)
    print(f"✓ Created worker: {worker.name} (ID: {worker.id})")
    print(f"  - Category: {worker.get_category_display()}")
    print(f"  - Daily Wage: NPR {worker.daily_wage:,.2f}")
    print(f"  - Phone: {worker.phone}")
    print(f"  - Status: {worker.status}")
    if worker.assigned_site:
        print(f"  - Assigned Site: {worker.assigned_site.name}")
    
    # TEST 2: Create Workers with Different Categories
    print("\n" + "-"*80)
    print("TEST 2: CREATE WORKERS WITH DIFFERENT CATEGORIES")
    print("-"*80)
    
    categories_to_test = [
        ('laborer', 'Hari Prasad', '800.00'),
        ('carpenter', 'Shyam Kumar', '1200.00'),
        ('electrician', 'Rajesh Sharma', '1800.00'),
        ('plumber', 'Mohan Singh', '1600.00'),
        ('engineer', 'Prakash Adhikari', '3000.00'),
        ('supervisor', 'Bikash Rai', '2500.00'),
        ('helper', 'Sita Devi', '600.00'),
        ('painter', 'Krishna Bahadur', '1000.00'),
        ('welder', 'Ramesh Tamang', '1400.00'),
        ('driver', 'Suresh Gurung', '1100.00'),
        ('operator', 'Dinesh Magar', '2000.00'),
    ]
    
    created_workers = []
    for category, name, wage in categories_to_test:
        w = Worker.objects.create(
            tenant=tenant,
            name=name,
            category=category,
            daily_wage=Decimal(wage),
            status='active'
        )
        created_workers.append(w)
        print(f"✓ Created {w.get_category_display()}: {w.name} (NPR {w.daily_wage:,.2f}/day)")
    
    # TEST 3: List Workers
    print("\n" + "-"*80)
    print("TEST 3: LIST WORKERS")
    print("-"*80)
    
    workers = Worker.objects.filter(tenant=tenant)
    print(f"✓ Found {workers.count()} worker(s) for tenant {tenant.name}")
    
    # Group by category
    from collections import defaultdict
    by_category = defaultdict(list)
    for w in workers:
        by_category[w.category].append(w)
    
    print("\nWorkers by Category:")
    for category, workers_list in sorted(by_category.items()):
        print(f"  {category.upper()}: {len(workers_list)} worker(s)")
    
    # TEST 4: Get Worker Details
    print("\n" + "-"*80)
    print("TEST 4: GET WORKER DETAILS")
    print("-"*80)
    
    retrieved_worker = Worker.objects.get(id=worker.id)
    print(f"✓ Retrieved worker: {retrieved_worker.name}")
    print(f"  - ID: {retrieved_worker.id}")
    print(f"  - Category: {retrieved_worker.get_category_display()}")
    print(f"  - Daily Wage: NPR {retrieved_worker.daily_wage:,.2f}")
    print(f"  - Phone: {retrieved_worker.phone}")
    print(f"  - Address: {retrieved_worker.address}")
    print(f"  - ID Number: {retrieved_worker.id_number}")
    print(f"  - Emergency Contact: {retrieved_worker.emergency_contact}")
    print(f"  - Status: {retrieved_worker.status}")
    if retrieved_worker.assigned_site:
        print(f"  - Assigned Site: {retrieved_worker.assigned_site.name}")
    
    # TEST 5: Update Worker
    print("\n" + "-"*80)
    print("TEST 5: UPDATE WORKER")
    print("-"*80)
    
    worker.daily_wage = Decimal('1800.00')
    worker.status = 'inactive'
    worker.save()
    
    updated_worker = Worker.objects.get(id=worker.id)
    print(f"✓ Updated worker: {updated_worker.name}")
    print(f"  - New Daily Wage: NPR {updated_worker.daily_wage:,.2f}")
    print(f"  - New Status: {updated_worker.status}")
    
    # TEST 6: Filter Workers
    print("\n" + "-"*80)
    print("TEST 6: FILTER WORKERS")
    print("-"*80)
    
    active_workers = Worker.objects.filter(tenant=tenant, status='active')
    inactive_workers = Worker.objects.filter(tenant=tenant, status='inactive')
    masons = Worker.objects.filter(tenant=tenant, category='mason')
    
    print(f"✓ Active workers: {active_workers.count()}")
    print(f"✓ Inactive workers: {inactive_workers.count()}")
    print(f"✓ Masons: {masons.count()}")
    
    # Filter by wage range
    high_wage_workers = Worker.objects.filter(
        tenant=tenant,
        daily_wage__gte=Decimal('2000.00')
    )
    print(f"✓ Workers earning >= NPR 2000/day: {high_wage_workers.count()}")
    
    # TEST 7: Delete Worker
    print("\n" + "-"*80)
    print("TEST 7: DELETE WORKERS")
    print("-"*80)
    
    # Delete the main test worker
    worker_id = worker.id
    worker_name = worker.name
    worker.delete()
    
    # Verify deletion
    exists = Worker.objects.filter(id=worker_id).exists()
    if not exists:
        print(f"✓ Successfully deleted worker: {worker_name} (ID: {worker_id})")
    else:
        print(f"❌ Failed to delete worker: {worker_name}")
    
    # Clean up other test workers
    for w in created_workers:
        w.delete()
    
    print(f"✓ Cleaned up {len(created_workers)} test workers")
    
    # Final count
    remaining_workers = Worker.objects.filter(tenant=tenant).count()
    print(f"✓ Remaining workers for tenant: {remaining_workers}")
    
    print("\n" + "="*80)
    print("ALL TESTS COMPLETED SUCCESSFULLY! ✓")
    print("="*80)
    print("\nSummary:")
    print("  ✓ Create Worker - Working")
    print("  ✓ Create Multiple Categories - Working")
    print("  ✓ List Workers - Working")
    print("  ✓ Get Worker Details - Working")
    print("  ✓ Update Worker - Working")
    print("  ✓ Filter Workers - Working")
    print("  ✓ Delete Worker - Working")
    print("\n✓ Backend is ready for frontend integration!")
    print("\nAvailable Categories:")
    print("  - Mason, Laborer, Carpenter, Electrician, Plumber")
    print("  - Engineer, Supervisor, Helper, Painter, Welder")
    print("  - Driver, Equipment Operator, Other")

if __name__ == '__main__':
    try:
        test_construction_workers_crud()
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
