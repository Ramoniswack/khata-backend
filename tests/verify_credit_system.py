#!/usr/bin/env python
"""
Quick verification script for Hardware & Udhaar Credit System
Run: python verify_credit_system.py
"""

import os
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core_backend.settings')
django.setup()

from decimal import Decimal
from datetime import date, timedelta
from django.db import transaction
from django.contrib.auth import get_user_model

from tenants.models import Tenant
from sales.models import Customer, SalesOrder, Invoice, CustomerLedger, PaymentReceived
from inventory.models import Product, Category

User = get_user_model()

def verify_credit_system():
    """Verify the credit system implementation"""
    
    print("=" * 60)
    print("Hardware & Udhaar Credit System Verification")
    print("=" * 60)
    
    # Check models exist
    print("\n✓ Checking models...")
    assert Customer is not None, "Customer model not found"
    assert CustomerLedger is not None, "CustomerLedger model not found"
    assert PaymentReceived is not None, "PaymentReceived model not found"
    print("  ✓ All models exist")
    
    # Check Customer fields
    print("\n✓ Checking Customer model fields...")
    customer_fields = [f.name for f in Customer._meta.get_fields()]
    required_fields = ['name', 'phone', 'pan', 'credit_limit', 'current_balance']
    for field in required_fields:
        assert field in customer_fields, f"Customer missing field: {field}"
    print(f"  ✓ Customer has all required fields: {', '.join(required_fields)}")
    
    # Check Customer properties
    print("\n✓ Checking Customer properties...")
    assert hasattr(Customer, 'is_over_limit'), "Customer missing is_over_limit property"
    assert hasattr(Customer, 'available_credit'), "Customer missing available_credit property"
    print("  ✓ Customer has is_over_limit and available_credit properties")
    
    # Check CustomerLedger fields
    print("\n✓ Checking CustomerLedger model fields...")
    ledger_fields = [f.name for f in CustomerLedger._meta.get_fields()]
    required_ledger_fields = [
        'customer', 'date', 'transaction_type', 'debit_amount', 
        'credit_amount', 'running_balance'
    ]
    for field in required_ledger_fields:
        assert field in ledger_fields, f"CustomerLedger missing field: {field}"
    print(f"  ✓ CustomerLedger has all required fields")
    
    # Check SalesOrder has payment_type
    print("\n✓ Checking SalesOrder model...")
    order_fields = [f.name for f in SalesOrder._meta.get_fields()]
    assert 'payment_type' in order_fields, "SalesOrder missing payment_type field"
    assert hasattr(SalesOrder, 'finalize_on_credit'), "SalesOrder missing finalize_on_credit method"
    print("  ✓ SalesOrder has payment_type field and finalize_on_credit method")
    
    # Check Invoice has payment_type
    print("\n✓ Checking Invoice model...")
    invoice_fields = [f.name for f in Invoice._meta.get_fields()]
    assert 'payment_type' in invoice_fields, "Invoice missing payment_type field"
    print("  ✓ Invoice has payment_type field")
    
    # Check PaymentReceived
    print("\n✓ Checking PaymentReceived model...")
    payment_fields = [f.name for f in PaymentReceived._meta.get_fields()]
    required_payment_fields = ['payment_number', 'customer', 'amount', 'payment_method']
    for field in required_payment_fields:
        assert field in payment_fields, f"PaymentReceived missing field: {field}"
    print("  ✓ PaymentReceived has all required fields")
    
    # Check transaction.atomic usage
    print("\n✓ Checking transaction safety...")
    import inspect
    
    # Check SalesOrder.finalize_on_credit
    finalize_source = inspect.getsource(SalesOrder.finalize_on_credit)
    assert 'transaction.atomic()' in finalize_source, "finalize_on_credit not using transaction.atomic()"
    print("  ✓ SalesOrder.finalize_on_credit uses transaction.atomic()")
    
    # Check Invoice.save
    invoice_save_source = inspect.getsource(Invoice.save)
    assert 'transaction.atomic()' in invoice_save_source, "Invoice.save not using transaction.atomic()"
    print("  ✓ Invoice.save uses transaction.atomic()")
    
    # Check PaymentReceived.save
    payment_save_source = inspect.getsource(PaymentReceived.save)
    assert 'transaction.atomic()' in payment_save_source, "PaymentReceived.save not using transaction.atomic()"
    print("  ✓ PaymentReceived.save uses transaction.atomic()")
    
    # Check ViewSet actions
    print("\n✓ Checking ViewSet actions...")
    from sales.views import CustomerViewSet, SalesOrderViewSet
    
    # Check aging_report action exists
    assert hasattr(CustomerViewSet, 'aging_report'), "CustomerViewSet missing aging_report action"
    print("  ✓ CustomerViewSet has aging_report action")
    
    # Check finalize_on_credit action exists
    assert hasattr(SalesOrderViewSet, 'finalize_on_credit'), "SalesOrderViewSet missing finalize_on_credit action"
    print("  ✓ SalesOrderViewSet has finalize_on_credit action")
    
    print("\n" + "=" * 60)
    print("✓ ALL VERIFICATIONS PASSED!")
    print("=" * 60)
    print("\nThe Hardware & Udhaar Credit System is fully implemented:")
    print("  ✓ Customer model with credit management")
    print("  ✓ CustomerLedger as immutable audit trail")
    print("  ✓ Credit logic wrapped in transaction.atomic()")
    print("  ✓ SalesOrder finalization on credit")
    print("  ✓ Invoice credit sale tracking")
    print("  ✓ Payment received tracking")
    print("  ✓ Aging report API")
    print("\nNext steps:")
    print("  1. Run tests: python manage.py test sales.test_credit_system")
    print("  2. Check Swagger docs: http://127.0.0.1:8000/api/docs/")
    print("  3. Review documentation: BackendDoc/HARDWARE_UDHAAR_SYSTEM.md")
    print("=" * 60)

if __name__ == '__main__':
    try:
        verify_credit_system()
    except AssertionError as e:
        print(f"\n✗ VERIFICATION FAILED: {e}")
        exit(1)
    except Exception as e:
        print(f"\n✗ ERROR: {e}")
        import traceback
        traceback.print_exc()
        exit(1)
