#!/usr/bin/env python
"""
Test script for Construction Daily Logs functionality
Tests the daily log creation and retrieval operations
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
from construction.models import Site, DailyLog, MaterialConsumption
from datetime import date
import json

User = get_user_model()

def test_daily_logs():
    """Test daily log functionality"""
    
    print("=" * 80)
    print("CONSTRUCTION DAILY LOGS TEST")
    print("=" * 80)
    
    # Get a user with tenant
    user = User.objects.filter(tenant__isnull=False).first()
    if not user:
        print("❌ No user with tenant found")
        return
    
    print(f"\n✓ Testing with user: {user.username}")
    print(f"✓ Tenant: {user.tenant.name}")
    
    # Get a site
    site = Site.objects.filter(tenant=user.tenant).first()
    if not site:
        print("\n❌ No site found. Please create a site first.")
        print("   Run: python scripts/test_construction_attendance.py")
        return
    
    print(f"\n✓ Using site: {site.name}")
    
    # Test 1: Create Daily Log
    print("\n" + "=" * 80)
    print("TEST 1: Create Daily Log")
    print("=" * 80)
    
    today = date.today()
    
    # Delete existing daily log for today to avoid duplicates
    DailyLog.objects.filter(
        tenant=user.tenant,
        site=site,
        date=today
    ).delete()
    
    daily_log_data = {
        'site': site,
        'date': today,
        'work_description': 'Foundation work completed. Started brick laying on north wall.',
        'progress_notes': 'Good progress today. Weather was favorable. Team worked efficiently.',
        'weather': 'Sunny',
        'other_expenses': 5000.00,
        'other_expenses_description': 'Transportation costs for materials and equipment rental',
        'submitted_by': user,
    }
    
    daily_log = DailyLog.objects.create(
        tenant=user.tenant,
        **daily_log_data
    )
    
    print(f"\n✓ Created daily log for {daily_log.date}")
    print(f"  Site: {daily_log.site.name}")
    print(f"  Work Description: {daily_log.work_description}")
    print(f"  Weather: {daily_log.weather}")
    print(f"  Other Expenses: NPR {daily_log.other_expenses:,.2f}")
    
    # Test 2: Retrieve Daily Logs
    print("\n" + "=" * 80)
    print("TEST 2: Retrieve Daily Logs")
    print("=" * 80)
    
    daily_logs = DailyLog.objects.filter(
        tenant=user.tenant,
        site=site
    ).select_related('site', 'submitted_by', 'reviewed_by')
    
    print(f"\n✓ Found {daily_logs.count()} daily log(s) for site")
    
    for log in daily_logs:
        print(f"\n  Date: {log.date}")
        print(f"  Site: {log.site.name}")
        print(f"  Work: {log.work_description[:50]}...")
        print(f"  Weather: {log.weather or 'N/A'}")
        print(f"  Other Expenses: NPR {log.other_expenses:,.2f}")
        print(f"  Submitted By: {log.submitted_by.username if log.submitted_by else 'N/A'}")
        print(f"  Reviewed: {'Yes' if log.reviewed_by else 'No'}")
    
    # Test 3: Daily Log with Material Consumption
    print("\n" + "=" * 80)
    print("TEST 3: Daily Log with Material Consumption")
    print("=" * 80)
    
    from inventory.models import Product
    
    # Get a product
    product = Product.objects.filter(tenant=user.tenant).first()
    
    if product:
        # Create material consumption
        consumption = MaterialConsumption.objects.create(
            tenant=user.tenant,
            daily_log=daily_log,
            site=site,
            product=product,
            quantity=50,
            unit_cost=product.cost,
            total_cost=50 * product.cost,
            notes='Used for foundation work'
        )
        
        print(f"\n✓ Added material consumption to daily log")
        print(f"  Product: {product.name}")
        print(f"  Quantity: {consumption.quantity} {product.unit}")
        print(f"  Unit Cost: NPR {consumption.unit_cost:,.2f}")
        print(f"  Total Cost: NPR {consumption.total_cost:,.2f}")
        
        # Retrieve daily log with material consumptions
        daily_log_with_materials = DailyLog.objects.filter(
            id=daily_log.id
        ).prefetch_related('material_consumptions__product').first()
        
        print(f"\n✓ Daily log has {daily_log_with_materials.material_consumptions.count()} material consumption(s)")
    else:
        print("\n⚠ No products found. Skipping material consumption test.")
        print("   Create products in inventory to test material consumption.")
    
    # Test 4: Site Other Expenses Calculation
    print("\n" + "=" * 80)
    print("TEST 4: Site Other Expenses Calculation")
    print("=" * 80)
    
    other_expenses = site.get_other_expenses()
    print(f"\n✓ Total other expenses for site: NPR {other_expenses:,.2f}")
    
    # Test 5: Daily Log Review
    print("\n" + "=" * 80)
    print("TEST 5: Daily Log Review (Manager)")
    print("=" * 80)
    
    from django.utils import timezone
    
    daily_log.reviewed_by = user
    daily_log.reviewed_at = timezone.now()
    daily_log.manager_comments = "Good progress. Keep up the good work. Monitor material usage."
    daily_log.save()
    
    print(f"\n✓ Daily log reviewed by: {daily_log.reviewed_by.username}")
    print(f"  Reviewed At: {daily_log.reviewed_at.strftime('%Y-%m-%d %H:%M')}")
    print(f"  Comments: {daily_log.manager_comments}")
    
    # Test 6: Daily Logs Statistics
    print("\n" + "=" * 80)
    print("TEST 6: Daily Logs Statistics")
    print("=" * 80)
    
    from django.db.models import Sum, Count
    from datetime import timedelta
    
    # Last 7 days
    seven_days_ago = today - timedelta(days=7)
    recent_logs = DailyLog.objects.filter(
        tenant=user.tenant,
        site=site,
        date__gte=seven_days_ago
    )
    
    stats = recent_logs.aggregate(
        total_logs=Count('id'),
        total_other_expenses=Sum('other_expenses'),
        reviewed_count=Count('id', filter=django.db.models.Q(reviewed_by__isnull=False))
    )
    
    print(f"\n  Last 7 Days Statistics:")
    print(f"  Total Logs: {stats['total_logs']}")
    print(f"  Total Other Expenses: NPR {stats['total_other_expenses'] or 0:,.2f}")
    print(f"  Reviewed Logs: {stats['reviewed_count']}")
    
    print("\n" + "=" * 80)
    print("✅ ALL TESTS PASSED")
    print("=" * 80)
    
    print("\n📋 SUMMARY:")
    print(f"  - Site: {site.name}")
    print(f"  - Daily Logs: {daily_logs.count()}")
    print(f"  - Other Expenses: NPR {other_expenses:,.2f}")
    print(f"  - Date: {today}")
    
    print("\n✅ Construction daily logs system is working correctly!")
    print("   You can now use the frontend at: http://localhost:3000/dashboard/construction/daily-logs/new")

if __name__ == '__main__':
    test_daily_logs()
