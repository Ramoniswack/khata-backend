#!/usr/bin/env python
"""
Test script to debug daily log 400 error
"""
import os
import sys
import django
import json

# Setup Django
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core_backend.settings')
django.setup()

from django.contrib.auth import get_user_model
from construction.models import Site
from rest_framework.test import APIClient
from datetime import date, timedelta

User = get_user_model()

def test_daily_log_api():
    """Test daily log creation via API to see 400 error"""
    print("\n" + "="*80)
    print("TESTING DAILY LOG API - 400 ERROR DEBUG")
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
    
    print(f"✓ Using site: {site.name} (ID: {site.id})")
    
    # Create API client and authenticate
    client = APIClient()
    client.force_authenticate(user=user)
    
    # Test with a new date
    test_date = date.today() + timedelta(days=10)
    
    # Prepare data (matching frontend payload)
    data = {
        'site': str(site.id),
        'date': str(test_date),
        'work_description': 'Test work from API',
        'progress_notes': 'Test notes',
        'weather': 'Sunny',
        'other_expenses': 0,
        'other_expenses_description': '',
    }
    
    print(f"\n📝 Sending data:")
    print(json.dumps(data, indent=2))
    
    # Make POST request
    print(f"\n🔍 Making POST request to /api/construction/daily-logs/")
    response = client.post('/api/construction/daily-logs/', data, format='json', HTTP_HOST='localhost')
    
    print(f"\n📊 Response Status: {response.status_code}")
    
    if response.status_code == 201:
        print("✓ Daily log created successfully!")
        if hasattr(response, 'data'):
            print(json.dumps(response.data, indent=2, default=str))
        else:
            print(response.content.decode())
    elif response.status_code == 400:
        print("❌ 400 Bad Request - Validation Error:")
        if hasattr(response, 'data'):
            print(json.dumps(response.data, indent=2, default=str))
        else:
            print(response.content.decode())
    else:
        print(f"❌ Unexpected status code: {response.status_code}")
        if hasattr(response, 'data'):
            print(response.data)
        else:
            print(response.content.decode())
    
    print("\n" + "="*80)

if __name__ == '__main__':
    test_daily_log_api()
