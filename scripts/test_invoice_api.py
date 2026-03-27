#!/usr/bin/env python
"""
Test script to debug invoice API creation
"""
import os
import sys
import django
import json

# Setup Django
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core_backend.settings')
django.setup()

from rest_framework.test import APIRequestFactory, force_authenticate
from users.models import User
from tenants.models import Tenant
from sales.models import Customer
from sales.views import InvoiceViewSet
from datetime import date, timedelta

def test_invoice_api():
    """Test invoice API creation"""
    print("\n" + "="*80)
    print("TESTING INVOICE API")
    print("="*80)
    
    # Clean up existing test invoices first
    print("\n[0] Cleaning up existing test data...")
    from sales.models import Invoice, CustomerLedger, CreditNote
    CreditNote.objects.all().delete()
    CustomerLedger.objects.all().delete()
    Invoice.objects.all().delete()
    print("   ✓ Cleanup complete")
    
    # Get or create test data
    print("\n[1] Setting up test data...")
    tenant, _ = Tenant.objects.get_or_create(
        name="Test Company",
        defaults={'business_type': 'retail'}
    )
    
    user, _ = User.objects.get_or_create(
        username='testuser',
        defaults={
            'email': 'test@example.com',
            'tenant': tenant
        }
    )
    
    if not user.tenant:
        user.tenant = tenant
        user.save()
    
    customer, _ = Customer.objects.get_or_create(
        tenant=tenant,
        email='customer@test.com',
        defaults={
            'name': 'Test Customer',
            'phone': '1234567890',
            'type': 'Business',
            'payment_terms': 'Net 30',
        }
    )
    
    print(f"   ✓ Tenant: {tenant.name}")
    print(f"   ✓ User: {user.username}")
    print(f"   ✓ Customer: {customer.name}")
    
    # Create API request
    factory = APIRequestFactory()
    
    # Test invoice creation
    print("\n[2] Testing invoice creation via API...")
    
    invoice_data = {
        'customer': str(customer.id),
        'date': date.today().isoformat(),
        'due_date': (date.today() + timedelta(days=30)).isoformat(),
        'amount': 5000.00,
        'payment_type': 'cash',
        'status': 'Draft',
        'notes': 'Test invoice via API'
    }
    
    print(f"   Request data: {json.dumps(invoice_data, indent=2)}")
    
    try:
        request = factory.post('/api/sales/invoices/', invoice_data, format='json')
        force_authenticate(request, user=user)
        
        view = InvoiceViewSet.as_view({'post': 'create'})
        response = view(request)
        
        print(f"\n   Response status: {response.status_code}")
        
        if hasattr(response, 'data'):
            print(f"   Response data: {json.dumps(response.data, indent=2, default=str)}")
        
        if response.status_code == 201:
            print("\n   ✅ SUCCESS: Invoice created successfully!")
            return True
        else:
            print(f"\n   ❌ FAILED: Status {response.status_code}")
            if hasattr(response, 'data'):
                print(f"   Error details: {response.data}")
            return False
            
    except Exception as e:
        print(f"\n   ❌ ERROR: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == '__main__':
    success = test_invoice_api()
    sys.exit(0 if success else 1)
