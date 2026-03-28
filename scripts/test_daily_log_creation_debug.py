#!/usr/bin/env python
"""
Test script to debug daily log creation 500 error
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
from datetime import date

User = get_user_model()

def test_daily_log_creation():
    """Test daily log creation with the serializer"""
    print("\n" + "="*80)
    print("TESTING DAILY LOG CREATION")
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
    
    # Prepare data (matching frontend payload)
    from datetime import timedelta
    tomorrow = date.today() + timedelta(days=1)
    
    data = {
        'site': str(site.id),
        'date': str(tomorrow),  # Use tomorrow's date to avoid conflict
        'work_description': 'Test work description',
        'progress_notes': 'Test progress notes',
        'weather': 'Sunny',
        'other_expenses': 0,  # Number, not string
        'other_expenses_description': '',
    }
    
    print(f"\n📝 Data to send:")
    for key, value in data.items():
        print(f"   {key}: {value} (type: {type(value).__name__})")
    
    # Create a fake request
    factory = APIRequestFactory()
    request = factory.post('/construction/daily-logs/', data)
    request.user = user
    
    # Test serializer
    print(f"\n🔍 Testing DailyLogCreateSerializer...")
    serializer = DailyLogCreateSerializer(data=data, context={'request': request})
    
    if serializer.is_valid():
        print("✓ Serializer validation passed")
        try:
            daily_log = serializer.save()
            print(f"✓ Daily log created successfully: {daily_log.id}")
            print(f"   - Site: {daily_log.site.name}")
            print(f"   - Date: {daily_log.date}")
            print(f"   - Submitted by: {daily_log.submitted_by.username}")
            print(f"   - Tenant: {daily_log.tenant.name}")
            print(f"   - Other expenses: {daily_log.other_expenses}")
        except Exception as e:
            print(f"❌ Error during save: {str(e)}")
            print(f"   Error type: {type(e).__name__}")
            import traceback
            traceback.print_exc()
    else:
        print("❌ Serializer validation failed:")
        for field, errors in serializer.errors.items():
            print(f"   {field}: {errors}")
    
    print("\n" + "="*80)

if __name__ == '__main__':
    test_daily_log_creation()
