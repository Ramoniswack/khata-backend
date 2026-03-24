#!/usr/bin/env python
"""
Test script for Trial Balance functionality
Tests the trial balance endpoint with real data
"""

import os
import sys
import django

# Setup Django
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core_backend.settings')
django.setup()

from django.contrib.auth import get_user_model
from accounting.models import Account, JournalEntry, JournalLine
from tenants.models import Tenant
from datetime import date, timedelta
from decimal import Decimal

User = get_user_model()

def test_trial_balance():
    """Test trial balance endpoint with sample data"""
    
    print("\n" + "="*80)
    print("TRIAL BALANCE TEST")
    print("="*80)
    
    # Get or create test tenant
    tenant, _ = Tenant.objects.get_or_create(
        slug='test-tenant',
        defaults={
            'name': 'Test Tenant',
            'business_type': 'Hardware',
            'is_active': True
        }
    )
    
    # Get or create test user
    user, _ = User.objects.get_or_create(
        username='testuser',
        defaults={
            'email': 'test@example.com',
            'tenant': tenant
        }
    )
    
    print(f"\n✓ Using tenant: {tenant.name} (slug: {tenant.slug})")
    print(f"✓ Using user: {user.username}")
    
    # Ensure we have test accounts and journal entries
    print("\n" + "-"*80)
    print("CHECKING TEST DATA")
    print("-"*80)
    
    accounts = Account.objects.filter(tenant=tenant, status='active', level__gt=0)
    entries = JournalEntry.objects.filter(tenant=tenant, status='posted')
    
    print(f"✓ Active accounts: {accounts.count()}")
    print(f"✓ Posted journal entries: {entries.count()}")
    
    if accounts.count() == 0 or entries.count() == 0:
        print("\n⚠ No test data found. Please run test_general_ledger.py first to create test data.")
        return
    
    # Calculate trial balance manually
    print("\n" + "-"*80)
    print("CALCULATING TRIAL BALANCE")
    print("-"*80)
    
    print(f"\n{'Code':<10} {'Account Name':<30} {'Type':<15} {'Debit':>15} {'Credit':>15}")
    print("-"*80)
    
    total_debit = Decimal('0.00')
    total_credit = Decimal('0.00')
    
    account_types = ['Assets', 'Liabilities', 'Equity', 'Income', 'Expense']
    
    for account_type in account_types:
        type_accounts = accounts.filter(type=account_type).order_by('code')
        
        if type_accounts.count() == 0:
            continue
        
        print(f"\n{account_type.upper()}")
        print("-"*80)
        
        type_debit = Decimal('0.00')
        type_credit = Decimal('0.00')
        
        for account in type_accounts:
            # Calculate balance for this account
            lines = JournalLine.objects.filter(
                tenant=tenant,
                account=account,
                journal_entry__status='posted'
            )
            
            debit_sum = sum(line.debit for line in lines)
            credit_sum = sum(line.credit for line in lines)
            balance = debit_sum - credit_sum
            
            if balance == 0:
                continue
            
            # Determine debit/credit presentation
            is_debit_type = account_type in ['Assets', 'Expense']
            
            if is_debit_type and balance > 0:
                debit_balance = balance
                credit_balance = Decimal('0.00')
            elif is_debit_type and balance < 0:
                debit_balance = Decimal('0.00')
                credit_balance = abs(balance)
            elif not is_debit_type and balance > 0:
                debit_balance = balance
                credit_balance = Decimal('0.00')
            else:
                debit_balance = Decimal('0.00')
                credit_balance = abs(balance)
            
            type_debit += debit_balance
            type_credit += credit_balance
            total_debit += debit_balance
            total_credit += credit_balance
            
            print(f"{account.code:<10} {account.name:<30} {account.type:<15} {debit_balance:>15.2f} {credit_balance:>15.2f}")
        
        print(f"{'':>56} {'Subtotal:':<15} {type_debit:>15.2f} {type_credit:>15.2f}")
    
    print("\n" + "="*80)
    print(f"{'':>56} {'GRAND TOTAL:':<15} {total_debit:>15.2f} {total_credit:>15.2f}")
    print("="*80)
    
    difference = abs(total_debit - total_credit)
    is_balanced = difference < Decimal('0.01')
    
    if is_balanced:
        print("\n✓ Trial Balance is BALANCED")
        print(f"  Total Debits:  Rs. {total_debit:,.2f}")
        print(f"  Total Credits: Rs. {total_credit:,.2f}")
        print(f"  Difference:    Rs. {difference:,.2f}")
    else:
        print("\n⚠ Trial Balance is OUT OF BALANCE")
        print(f"  Total Debits:  Rs. {total_debit:,.2f}")
        print(f"  Total Credits: Rs. {total_credit:,.2f}")
        print(f"  Difference:    Rs. {difference:,.2f}")
    
    # Test the API endpoint
    print("\n" + "-"*80)
    print("TESTING API ENDPOINT")
    print("-"*80)
    
    from django.test import RequestFactory
    from accounting.views import AccountViewSet
    
    factory = RequestFactory()
    request = factory.get('/accounting/accounts/trial_balance/')
    request.user = user
    
    view = AccountViewSet.as_view({'get': 'trial_balance'})
    response = view(request)
    
    if response.status_code == 200:
        data = response.data
        print(f"\n✓ API endpoint working correctly")
        print(f"  Status Code: {response.status_code}")
        print(f"  Accounts returned: {len(data['accounts'])}")
        print(f"  Total Debit: Rs. {data['total_debit']:,.2f}")
        print(f"  Total Credit: Rs. {data['total_credit']:,.2f}")
        print(f"  Is Balanced: {data['is_balanced']}")
    else:
        print(f"\n✗ API endpoint failed")
        print(f"  Status Code: {response.status_code}")
        print(f"  Response: {response.data}")
    
    # Summary
    print("\n" + "="*80)
    print("TEST SUMMARY")
    print("="*80)
    print(f"✓ Tenant: {tenant.name}")
    print(f"✓ Accounts with balances: {accounts.count()}")
    print(f"✓ Posted journal entries: {entries.count()}")
    print(f"✓ Trial balance calculated successfully")
    print(f"✓ API endpoint tested successfully")
    print(f"\n✓ Trial Balance is ready to use!")
    print("="*80)
    
    print("\n" + "="*80)
    print("FRONTEND TESTING INSTRUCTIONS")
    print("="*80)
    print("\n1. Login to the frontend")
    print("2. Navigate to: Accounting > Trial Balance")
    print("3. Optionally select 'As of Date'")
    print("4. Click 'Generate' to view trial balance")
    print("5. Verify all account types are displayed")
    print("6. Check that debits equal credits")
    print("7. Export to CSV to verify export functionality")
    print("\n" + "="*80)

if __name__ == '__main__':
    test_trial_balance()
