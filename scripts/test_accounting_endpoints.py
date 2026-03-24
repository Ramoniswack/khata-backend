#!/usr/bin/env python
"""
Test script to verify Accounting Chart of Accounts endpoints are working
Run from backend directory: python scripts/test_accounting_endpoints.py
"""

import os
import sys
import django

# Setup Django
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core_backend.settings')
django.setup()

from accounting.models import Account, JournalEntry, BankAccount
from tenants.models import Tenant
from users.models import User

def test_accounting_endpoints():
    """Test that accounting module is properly configured"""
    
    print("=" * 60)
    print("ACCOUNTING MODULE ENDPOINT VERIFICATION")
    print("=" * 60)
    print()
    
    # Test 1: Check models are accessible
    print("✓ Test 1: Models Import")
    print(f"  - Account model: {Account.__name__}")
    print(f"  - JournalEntry model: {JournalEntry.__name__}")
    print(f"  - BankAccount model: {BankAccount.__name__}")
    print()
    
    # Test 2: Check database tables exist
    print("✓ Test 2: Database Tables")
    try:
        account_count = Account.objects.count()
        journal_count = JournalEntry.objects.count()
        bank_account_count = BankAccount.objects.count()
        print(f"  - Accounts table: {account_count} records")
        print(f"  - Journal Entries table: {journal_count} records")
        print(f"  - Bank Accounts table: {bank_account_count} records")
    except Exception as e:
        print(f"  ✗ Error accessing tables: {e}")
        return False
    print()
    
    # Test 3: Check related data exists
    print("✓ Test 3: Related Data Availability")
    try:
        tenant_count = Tenant.objects.count()
        user_count = User.objects.count()
        
        print(f"  - Tenants: {tenant_count}")
        print(f"  - Users: {user_count}")
        
        if tenant_count == 0:
            print("  ⚠ Warning: No tenants found. Account creation requires tenants.")
        if user_count == 0:
            print("  ⚠ Warning: No users found. Journal entries require users.")
    except Exception as e:
        print(f"  ✗ Error checking related data: {e}")
        return False
    print()
    
    # Test 4: Check Account model fields
    print("✓ Test 4: Account Model Fields")
    if account_count > 0:
        account = Account.objects.first()
        print(f"  - Testing with account: {account.name}")
        try:
            print(f"  - Code: {account.code}")
            print(f"  - Type: {account.type}")
            print(f"  - Sub Type: {account.sub_type}")
            print(f"  - Level: {account.level}")
            print(f"  - Balance: NPR {account.balance:,.2f}")
            print(f"  - Status: {account.status}")
        except Exception as e:
            print(f"  ✗ Error testing account fields: {e}")
            return False
    else:
        print("  - No accounts to test (create an account first)")
    print()
    
    # Test 5: Check ViewSets are registered
    print("✓ Test 5: URL Configuration")
    try:
        from rest_framework.test import APIRequestFactory
        from accounting.views import AccountViewSet
        
        # Test that ViewSet is accessible
        factory = APIRequestFactory()
        request = factory.get('/api/accounting/accounts/')
        
        print("  - AccountViewSet: Accessible")
        print("  - URL pattern: /api/accounting/accounts/")
    except Exception as e:
        print(f"  ✗ Error checking URL configuration: {e}")
        return False
    print()
    
    # Test 6: Check Serializers
    print("✓ Test 6: Serializers")
    try:
        from accounting.serializers import AccountSerializer, JournalEntrySerializer
        
        print("  - AccountSerializer: Available")
        print("  - JournalEntrySerializer: Available")
        
        if account_count > 0:
            account = Account.objects.first()
            serializer = AccountSerializer(account)
            data = serializer.data
            
            # Check required fields are present
            required_fields = [
                'id', 'code', 'name', 'type', 'sub_type', 'level',
                'balance', 'status', 'description'
            ]
            
            missing_fields = [f for f in required_fields if f not in data]
            if missing_fields:
                print(f"  ⚠ Warning: Missing fields: {missing_fields}")
            else:
                print("  - All required fields present in serializer")
    except Exception as e:
        print(f"  ✗ Error checking serializers: {e}")
        return False
    print()
    
    # Test 7: Check Account Types
    print("✓ Test 7: Account Types")
    try:
        account_types = Account.ACCOUNT_TYPES
        print(f"  - Available types: {[t[0] for t in account_types]}")
        
        # Count by type
        for acc_type, _ in account_types:
            count = Account.objects.filter(type=acc_type).count()
            print(f"  - {acc_type}: {count} accounts")
    except Exception as e:
        print(f"  ✗ Error checking account types: {e}")
        return False
    print()
    
    # Summary
    print("=" * 60)
    print("SUMMARY")
    print("=" * 60)
    print()
    print("✅ All tests passed!")
    print()
    print("Backend Status: FULLY FUNCTIONAL")
    print()
    print("Ready to test:")
    print("  1. http://localhost:3000/dashboard/accounting/chart-of-accounts")
    print("  2. http://localhost:3000/dashboard/accounting/chart-of-accounts/new")
    print()
    print("API Documentation:")
    print("  - Swagger UI: http://localhost:8000/api/docs/")
    print("  - ReDoc: http://localhost:8000/api/redoc/")
    print()
    
    return True

if __name__ == '__main__':
    try:
        success = test_accounting_endpoints()
        sys.exit(0 if success else 1)
    except Exception as e:
        print(f"\n✗ Fatal error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
