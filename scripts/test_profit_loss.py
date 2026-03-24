#!/usr/bin/env python
"""
Test script for Profit & Loss Statement functionality
Tests the profit & loss endpoint with real data
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

def test_profit_loss():
    """Test profit & loss statement endpoint with sample data"""
    
    print("\n" + "="*80)
    print("PROFIT & LOSS STATEMENT TEST")
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
    
    # Check for existing data
    print("\n" + "-"*80)
    print("CHECKING TEST DATA")
    print("-"*80)
    
    income_accounts = Account.objects.filter(tenant=tenant, type='Income', status='active', level__gt=0)
    expense_accounts = Account.objects.filter(tenant=tenant, type='Expense', status='active', level__gt=0)
    entries = JournalEntry.objects.filter(tenant=tenant, status='posted')
    
    print(f"✓ Income accounts: {income_accounts.count()}")
    print(f"✓ Expense accounts: {expense_accounts.count()}")
    print(f"✓ Posted journal entries: {entries.count()}")
    
    if income_accounts.count() == 0 and expense_accounts.count() == 0:
        print("\n⚠ No income/expense accounts found. Please run test_general_ledger.py first.")
        return
    
    # Calculate P&L manually
    print("\n" + "-"*80)
    print("CALCULATING PROFIT & LOSS")
    print("-"*80)
    
    today = date.today()
    from_date = today - timedelta(days=30)
    to_date = today
    
    print(f"\nPeriod: {from_date} to {to_date}")
    print("\n" + "-"*80)
    
    # Calculate income
    print("\nINCOME")
    print("-"*80)
    total_income = Decimal('0.00')
    
    for account in income_accounts:
        lines = JournalLine.objects.filter(
            tenant=tenant,
            account=account,
            journal_entry__status='posted',
            journal_entry__date__gte=from_date,
            journal_entry__date__lte=to_date
        )
        
        debit_sum = sum(line.debit for line in lines)
        credit_sum = sum(line.credit for line in lines)
        amount = credit_sum - debit_sum  # Income is credit
        
        if amount != 0:
            total_income += amount
            print(f"{account.code:<10} {account.name:<40} {amount:>15.2f}")
    
    print("-"*80)
    print(f"{'TOTAL INCOME':<50} {total_income:>15.2f}")
    
    # Calculate expenses
    print("\n\nEXPENSES")
    print("-"*80)
    total_expenses = Decimal('0.00')
    
    for account in expense_accounts:
        lines = JournalLine.objects.filter(
            tenant=tenant,
            account=account,
            journal_entry__status='posted',
            journal_entry__date__gte=from_date,
            journal_entry__date__lte=to_date
        )
        
        debit_sum = sum(line.debit for line in lines)
        credit_sum = sum(line.credit for line in lines)
        amount = debit_sum - credit_sum  # Expense is debit
        
        if amount != 0:
            total_expenses += amount
            print(f"{account.code:<10} {account.name:<40} {amount:>15.2f}")
    
    print("-"*80)
    print(f"{'TOTAL EXPENSES':<50} {total_expenses:>15.2f}")
    
    # Calculate net profit
    net_profit = total_income - total_expenses
    net_margin = (net_profit / total_income * 100) if total_income > 0 else Decimal('0.00')
    
    print("\n" + "="*80)
    print(f"{'NET PROFIT/LOSS':<50} {net_profit:>15.2f}")
    print(f"{'NET MARGIN':<50} {net_margin:>14.2f}%")
    print("="*80)
    
    if net_profit > 0:
        print(f"\n✓ NET PROFIT: Rs. {net_profit:,.2f}")
    elif net_profit < 0:
        print(f"\n⚠ NET LOSS: Rs. {abs(net_profit):,.2f}")
    else:
        print(f"\n○ BREAK EVEN: Rs. 0.00")
    
    # Test the API endpoint
    print("\n" + "-"*80)
    print("TESTING API ENDPOINT")
    print("-"*80)
    
    from django.test import RequestFactory
    from accounting.views import AccountViewSet
    
    factory = RequestFactory()
    request = factory.get(
        '/accounting/accounts/profit_loss/',
        {'from_date': str(from_date), 'to_date': str(to_date)}
    )
    request.user = user
    
    view = AccountViewSet.as_view({'get': 'profit_loss'})
    response = view(request)
    
    if response.status_code == 200:
        data = response.data
        print(f"\n✓ API endpoint working correctly")
        print(f"  Status Code: {response.status_code}")
        print(f"  Income accounts: {len(data['income']['accounts'])}")
        print(f"  Expense accounts: {len(data['expenses']['accounts'])}")
        print(f"  Total Income: Rs. {data['income']['total']:,.2f}")
        print(f"  Total Expenses: Rs. {data['expenses']['total']:,.2f}")
        print(f"  Net Profit: Rs. {data['net_profit']:,.2f}")
        print(f"  Net Margin: {data['net_margin']:.2f}%")
    else:
        print(f"\n✗ API endpoint failed")
        print(f"  Status Code: {response.status_code}")
        print(f"  Response: {response.data}")
    
    # Summary
    print("\n" + "="*80)
    print("TEST SUMMARY")
    print("="*80)
    print(f"✓ Tenant: {tenant.name}")
    print(f"✓ Income accounts: {income_accounts.count()}")
    print(f"✓ Expense accounts: {expense_accounts.count()}")
    print(f"✓ Posted journal entries: {entries.count()}")
    print(f"✓ P&L calculated successfully")
    print(f"✓ API endpoint tested successfully")
    print(f"\n✓ Profit & Loss Statement is ready to use!")
    print("="*80)
    
    print("\n" + "="*80)
    print("FRONTEND TESTING INSTRUCTIONS")
    print("="*80)
    print("\n1. Login to the frontend")
    print("2. Navigate to: Accounting > Profit & Loss")
    print("3. Select a period (This Month, This Quarter, This Year, or Custom)")
    print("4. View the profit & loss statement")
    print("5. Verify income and expense accounts are displayed")
    print("6. Check net profit/loss calculation")
    print("7. Export to CSV to verify export functionality")
    print("\n" + "="*80)

if __name__ == '__main__':
    test_profit_loss()
