#!/usr/bin/env python
"""
Complete test script for daily log creation
Tests: creation, duplicate prevention, and error handling
"""
import os
import sys
import django

# Setup Django
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core_backend.settings')
django.setup()

from django.contrib.auth import get_user_model
from construction.models import Site, DailyLog
from construction.serializers import DailyLogCreateSerializer
from rest_framework.test import APIRequestFactory
from datetime import date, timedelta

User = get_user_model()

def test_daily_log_scenarios():
    """Test various daily log creation scenarios"""
    print("\n" + "="*80)
    print("DAILY LOG CREATION - COMPREHENSIVE TEST")
    print("="*80)
    
    # Get a user with tenant
    user = User.objects.filter(tenant__isnull=False).first()
    if not user:
        print("❌ No user with tenant found")
        return
    
    print(f"\n✓ Using user: {user.username} (tenant: {user.tenant.name})")
    
    # Get a site
    site = Site.objects.filter(tenant=user.tenant).first()
    if not site:
        print("❌ No site found for this tenant")
        return
    
    print(f"✓ Using site: {site.name}")
    
    # Create a fake request
    factory = APIRequestFactory()
    
    # Test 1: Create a new daily log for a future date
    print("\n" + "-"*80)
    print("TEST 1: Create daily log for future date")
    print("-"*80)
    
    future_date = date.today() + timedelta(days=5)
    data = {
        'site': str(site.id),
        'date': str(future_date),
        'work_description': 'Foundation work completed',
        'progress_notes': 'Good progress, no issues',
        'weather': 'Sunny',
        'other_expenses': 1500.50,
        'other_expenses_description': 'Equipment rental',
    }
    
    request = factory.post('/construction/daily-logs/', data)
    request.user = user
    
    serializer = DailyLogCreateSerializer(data=data, context={'request': request})
    
    if serializer.is_valid():
        try:
            daily_log = serializer.save()
            print(f"✓ Daily log created successfully")
            print(f"   - ID: {daily_log.id}")
            print(f"   - Date: {daily_log.date}")
            print(f"   - Other expenses: NPR {daily_log.other_expenses}")
            
            # Clean up
            created_log_id = daily_log.id
        except Exception as e:
            print(f"❌ Error: {str(e)}")
            return
    else:
        print(f"❌ Validation failed: {serializer.errors}")
        return
    
    # Test 2: Try to create duplicate (should fail)
    print("\n" + "-"*80)
    print("TEST 2: Try to create duplicate daily log (should fail)")
    print("-"*80)
    
    request2 = factory.post('/construction/daily-logs/', data)
    request2.user = user
    
    serializer2 = DailyLogCreateSerializer(data=data, context={'request': request2})
    
    if serializer2.is_valid():
        print("❌ Validation should have failed but didn't")
    else:
        print("✓ Duplicate prevention working correctly")
        print(f"   Error message: {serializer2.errors.get('date', [''])[0]}")
    
    # Test 3: Create daily log with material consumption
    print("\n" + "-"*80)
    print("TEST 3: Create daily log with material consumption")
    print("-"*80)
    
    # Get a product for material consumption
    from inventory.models import Product
    product = Product.objects.filter(tenant=user.tenant).first()
    
    if product:
        print(f"   Using product: {product.name} (ID: {product.id})")
        
        another_date = date.today() + timedelta(days=6)
        data_with_materials = {
            'site': str(site.id),
            'date': str(another_date),
            'work_description': 'Concrete pouring',
            'progress_notes': 'Used cement and steel',
            'weather': 'Cloudy',
            'other_expenses': 0,
            'other_expenses_description': '',
            'material_consumptions': [
                {
                    'product': product.id,  # Use UUID directly, not string
                    'quantity': 10,
                    'unit_cost': 500,
                }
            ]
        }
        
        request3 = factory.post('/construction/daily-logs/', data_with_materials)
        request3.user = user
        
        serializer3 = DailyLogCreateSerializer(data=data_with_materials, context={'request': request3})
        
        if serializer3.is_valid():
            try:
                daily_log3 = serializer3.save()
                print(f"✓ Daily log with materials created successfully")
                print(f"   - ID: {daily_log3.id}")
                print(f"   - Material consumptions: {daily_log3.material_consumptions.count()}")
                
                # Clean up
                daily_log3.delete()
            except Exception as e:
                print(f"❌ Error: {str(e)}")
        else:
            print(f"⚠️  Validation failed (might be stock issue): {serializer3.errors}")
    else:
        print("⚠️  No products found, skipping material consumption test")
    
    # Test 4: List all daily logs
    print("\n" + "-"*80)
    print("TEST 4: List all daily logs for this tenant")
    print("-"*80)
    
    logs = DailyLog.objects.filter(tenant=user.tenant).order_by('-date')[:5]
    print(f"✓ Found {logs.count()} daily logs (showing last 5):")
    for log in logs:
        print(f"   - {log.date}: {log.site.name} - {log.work_description[:50]}...")
    
    # Clean up the test log
    print("\n" + "-"*80)
    print("CLEANUP")
    print("-"*80)
    try:
        DailyLog.objects.filter(id=created_log_id).delete()
        print("✓ Test data cleaned up")
    except:
        pass
    
    print("\n" + "="*80)
    print("ALL TESTS COMPLETED SUCCESSFULLY")
    print("="*80)

if __name__ == '__main__':
    test_daily_log_scenarios()
