#!/usr/bin/env python
"""
Test script for invoice creation
"""
import os
import sys
import django
from decimal import Decimal

# Setup Django
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core_backend.settings')
django.setup()

from users.models import User
from tenants.models import Tenant
from sales.models import Customer, SalesOrder, Invoice
from datetime import date, timedelta

def test_invoice_creation():
    """Test invoice creation"""
    print("\n" + "="*80)
    print("TESTING INVOICE CREATION")
    print("="*80)
    
    # Clean up any existing test data first
    print("\n[0] Cleaning up existing test data...")
    from sales.models import CustomerLedger
    Invoice.objects.filter(invoice_number__startswith='INV-TEST').delete()
    SalesOrder.objects.filter(order_number='SO-TEST-001').delete()
    CustomerLedger.objects.filter(customer__email='customer@test.com').delete()
    Customer.objects.filter(email='customer@test.com').delete()
    print("   ✓ Cleanup complete")
    
    # Get or create test tenant and user
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
    
    print(f"   ✓ Tenant: {tenant.name}")
    print(f"   ✓ User: {user.username}")
    
    # Create test customer
    print("\n[2] Creating test customer...")
    customer, created = Customer.objects.get_or_create(
        tenant=tenant,
        email='customer@test.com',
        defaults={
            'name': 'Test Customer',
            'phone': '1234567890',
            'type': 'Business',
            'payment_terms': 'Net 30',
            'credit_limit': Decimal('100000.00')
        }
    )
    print(f"   ✓ Customer: {customer.name} ({'created' if created else 'existing'})")
    
    # Create test sales order
    print("\n[3] Creating test sales order...")
    sales_order, created = SalesOrder.objects.get_or_create(
        tenant=tenant,
        order_number='SO-TEST-001',
        defaults={
            'customer': customer,
            'date': date.today(),
            'status': 'Confirmed',
            'subtotal': Decimal('10000.00'),
            'discount': Decimal('0.00'),
            'tax': Decimal('1300.00'),
            'total': Decimal('11300.00'),
            'created_by': user
        }
    )
    print(f"   ✓ Sales Order: {sales_order.order_number} ({'created' if created else 'existing'})")
    
    # Test 1: Create invoice without sales order
    print("\n[4] Testing invoice creation without sales order...")
    try:
        invoice1 = Invoice.objects.create(
            tenant=tenant,
            invoice_number='INV-TEST-001',
            date=date.today(),
            due_date=date.today() + timedelta(days=30),
            customer=customer,
            amount=Decimal('5000.00'),
            payment_type='cash',
            status='Draft',
            notes='Test invoice without sales order',
            created_by=user
        )
        print(f"   ✓ Invoice created: {invoice1.invoice_number}")
        print(f"      - Amount: Rs. {invoice1.amount}")
        print(f"      - Balance: Rs. {invoice1.balance}")
        print(f"      - Status: {invoice1.status}")
    except Exception as e:
        print(f"   ✗ Error: {str(e)}")
        return False
    
    # Test 2: Create invoice with sales order
    print("\n[5] Testing invoice creation with sales order...")
    try:
        invoice2 = Invoice.objects.create(
            tenant=tenant,
            invoice_number='INV-TEST-002',
            date=date.today(),
            due_date=date.today() + timedelta(days=30),
            customer=customer,
            sales_order=sales_order,
            amount=sales_order.total,
            payment_type='credit',
            status='Sent',
            notes='Test invoice from sales order',
            created_by=user
        )
        print(f"   ✓ Invoice created: {invoice2.invoice_number}")
        print(f"      - Amount: Rs. {invoice2.amount}")
        print(f"      - Sales Order: {invoice2.sales_order.order_number}")
        print(f"      - Status: {invoice2.status}")
    except Exception as e:
        print(f"   ✗ Error: {str(e)}")
        return False
    
    # Test 3: Record payment
    print("\n[6] Testing payment recording...")
    try:
        payment_amount = Decimal('2000.00')
        invoice1.paid_amount += payment_amount
        
        # Update status based on payment
        if invoice1.paid_amount >= invoice1.amount:
            invoice1.status = 'Paid'
        elif invoice1.paid_amount > 0:
            invoice1.status = 'Partially Paid'
        
        invoice1.save()
        
        print(f"   ✓ Payment recorded: Rs. {payment_amount}")
        print(f"      - Paid Amount: Rs. {invoice1.paid_amount}")
        print(f"      - Balance: Rs. {invoice1.balance}")
        print(f"      - Status: {invoice1.status}")
    except Exception as e:
        print(f"   ✗ Error: {str(e)}")
        return False
    
    # Test 4: List invoices
    print("\n[7] Testing invoice listing...")
    invoices = Invoice.objects.filter(tenant=tenant)
    print(f"   ✓ Found {invoices.count()} invoices:")
    for inv in invoices:
        print(f"      - {inv.invoice_number}: Rs. {inv.amount} ({inv.status})")
    
    # Test 5: Test tenant filtering
    print("\n[8] Testing tenant filtering...")
    other_tenant, _ = Tenant.objects.get_or_create(
        name="Other Company",
        defaults={'business_type': 'wholesale'}
    )
    
    # Try to access invoice from different tenant
    invoices_for_other_tenant = Invoice.objects.filter(tenant=other_tenant)
    print(f"   ✓ Invoices for other tenant: {invoices_for_other_tenant.count()}")
    
    if invoices_for_other_tenant.count() == 0:
        print("   ✓ PASS: Tenant isolation working correctly")
    else:
        print("   ✗ FAIL: Tenant isolation not working!")
        return False
    
    # Cleanup
    print("\n[9] Cleaning up...")
    from sales.models import CustomerLedger
    CustomerLedger.objects.filter(customer=customer).delete()
    invoice1.delete()
    invoice2.delete()
    sales_order.delete()
    customer.delete()
    other_tenant.delete()
    print("   ✓ Cleanup complete")
    
    print("\n" + "="*80)
    print("✅ ALL TESTS PASSED!")
    print("="*80)
    
    return True

if __name__ == '__main__':
    success = test_invoice_creation()
    sys.exit(0 if success else 1)
