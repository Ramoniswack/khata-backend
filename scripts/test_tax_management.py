#!/usr/bin/env python
"""
Test script for Tax Management endpoints
Tests Tax Rules and VAT Returns functionality
"""

import os
import sys
import django

# Setup Django
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core_backend.settings')
django.setup()

from django.contrib.auth import get_user_model
from accounting.models import Account, TaxRule, VATReturn
from tenants.models import Tenant
from decimal import Decimal
from datetime import date, timedelta

User = get_user_model()

def test_tax_management():
    """Test tax management functionality"""
    
    print("=" * 80)
    print("TAX MANAGEMENT TEST")
    print("=" * 80)
    
    # Get or create test tenant
    tenant, _ = Tenant.objects.get_or_create(
        slug='test-tenant',
        defaults={
            'name': 'Test Tenant',
            'business_type': 'Hardware',
            'is_active': True
        }
    )
    print(f"\n✓ Using tenant: {tenant.name}")
    
    # Get or create test user
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
    print(f"✓ Using user: {user.username}")
    
    # Create VAT account if it doesn't exist
    vat_account, created = Account.objects.get_or_create(
        tenant=tenant,
        code='2300',
        defaults={
            'name': 'VAT Payable',
            'type': 'Liabilities',
            'sub_type': 'Current Liabilities',
            'level': 1,
            'status': 'active',
            'balance': Decimal('0.00')
        }
    )
    print(f"✓ VAT Account: {vat_account.name} ({vat_account.code})")
    
    # Create TDS account if it doesn't exist
    tds_account, created = Account.objects.get_or_create(
        tenant=tenant,
        code='2310',
        defaults={
            'name': 'TDS Payable',
            'type': 'Liabilities',
            'sub_type': 'Current Liabilities',
            'level': 1,
            'status': 'active',
            'balance': Decimal('0.00')
        }
    )
    print(f"✓ TDS Account: {tds_account.name} ({tds_account.code})")
    
    print("\n" + "=" * 80)
    print("TAX RULES")
    print("=" * 80)
    
    # Create tax rules
    tax_rules_data = [
        {
            'name': 'Standard VAT',
            'type': 'VAT',
            'rate': Decimal('13.00'),
            'applicable_on': 'Both',
            'account': vat_account,
            'status': 'active',
            'description': 'Standard VAT rate for goods and services'
        },
        {
            'name': 'TDS on Professional Services',
            'type': 'TDS',
            'rate': Decimal('10.00'),
            'applicable_on': 'Purchase',
            'account': tds_account,
            'status': 'active',
            'description': 'TDS deduction on professional service payments'
        },
        {
            'name': 'Zero-rated VAT',
            'type': 'VAT',
            'rate': Decimal('0.00'),
            'applicable_on': 'Sales',
            'account': vat_account,
            'status': 'active',
            'description': 'Zero-rated VAT for exports'
        }
    ]
    
    created_rules = []
    for rule_data in tax_rules_data:
        rule, created = TaxRule.objects.get_or_create(
            tenant=tenant,
            name=rule_data['name'],
            defaults=rule_data
        )
        created_rules.append(rule)
        status = "Created" if created else "Exists"
        print(f"\n{status}: {rule.name}")
        print(f"  Type: {rule.type}")
        print(f"  Rate: {rule.rate}%")
        print(f"  Applicable On: {rule.applicable_on}")
        print(f"  Account: {rule.account.name}")
        print(f"  Status: {rule.status}")
    
    print("\n" + "=" * 80)
    print("VAT RETURNS")
    print("=" * 80)
    
    # Create VAT returns
    today = date.today()
    last_month_start = date(today.year, today.month - 1 if today.month > 1 else 12, 1)
    last_month_end = date(today.year, today.month, 1) - timedelta(days=1)
    
    vat_returns_data = [
        {
            'return_number': 'VAT-2024-01',
            'period': 'January 2024',
            'from_date': date(2024, 1, 1),
            'to_date': date(2024, 1, 31),
            'output_tax': Decimal('15000.00'),
            'input_tax': Decimal('8000.00'),
            'net_payable': Decimal('7000.00'),
            'status': 'paid',
            'filed_date': date(2024, 2, 15),
            'paid_date': date(2024, 2, 20),
            'notes': 'January 2024 VAT return - paid on time'
        },
        {
            'return_number': 'VAT-2024-02',
            'period': 'February 2024',
            'from_date': date(2024, 2, 1),
            'to_date': date(2024, 2, 29),
            'output_tax': Decimal('18000.00'),
            'input_tax': Decimal('9500.00'),
            'net_payable': Decimal('8500.00'),
            'status': 'filed',
            'filed_date': date(2024, 3, 15),
            'notes': 'February 2024 VAT return - awaiting payment'
        },
        {
            'return_number': 'VAT-2024-03',
            'period': 'March 2024',
            'from_date': date(2024, 3, 1),
            'to_date': date(2024, 3, 31),
            'output_tax': Decimal('20000.00'),
            'input_tax': Decimal('11000.00'),
            'net_payable': Decimal('9000.00'),
            'status': 'draft',
            'notes': 'March 2024 VAT return - draft'
        }
    ]
    
    created_returns = []
    for return_data in vat_returns_data:
        vat_return, created = VATReturn.objects.get_or_create(
            tenant=tenant,
            return_number=return_data['return_number'],
            defaults=return_data
        )
        created_returns.append(vat_return)
        status = "Created" if created else "Exists"
        print(f"\n{status}: {vat_return.return_number}")
        print(f"  Period: {vat_return.period}")
        print(f"  From: {vat_return.from_date.strftime('%d/%m/%Y')}")
        print(f"  To: {vat_return.to_date.strftime('%d/%m/%Y')}")
        print(f"  Output Tax: Rs. {vat_return.output_tax:,.2f}")
        print(f"  Input Tax: Rs. {vat_return.input_tax:,.2f}")
        print(f"  Net Payable: Rs. {vat_return.net_payable:,.2f}")
        print(f"  Status: {vat_return.status.upper()}")
        if vat_return.filed_date:
            print(f"  Filed Date: {vat_return.filed_date.strftime('%d/%m/%Y')}")
        if vat_return.paid_date:
            print(f"  Paid Date: {vat_return.paid_date.strftime('%d/%m/%Y')}")
    
    print("\n" + "=" * 80)
    print("SUMMARY")
    print("=" * 80)
    
    # Summary statistics
    total_rules = TaxRule.objects.filter(tenant=tenant).count()
    active_rules = TaxRule.objects.filter(tenant=tenant, status='active').count()
    total_returns = VATReturn.objects.filter(tenant=tenant).count()
    draft_returns = VATReturn.objects.filter(tenant=tenant, status='draft').count()
    filed_returns = VATReturn.objects.filter(tenant=tenant, status='filed').count()
    paid_returns = VATReturn.objects.filter(tenant=tenant, status='paid').count()
    
    print(f"\nTax Rules:")
    print(f"  Total: {total_rules}")
    print(f"  Active: {active_rules}")
    print(f"  Inactive: {total_rules - active_rules}")
    
    print(f"\nVAT Returns:")
    print(f"  Total: {total_returns}")
    print(f"  Draft: {draft_returns}")
    print(f"  Filed: {filed_returns}")
    print(f"  Paid: {paid_returns}")
    
    # Calculate total VAT
    total_output = VATReturn.objects.filter(tenant=tenant).aggregate(
        total=django.db.models.Sum('output_tax')
    )['total'] or Decimal('0.00')
    
    total_input = VATReturn.objects.filter(tenant=tenant).aggregate(
        total=django.db.models.Sum('input_tax')
    )['total'] or Decimal('0.00')
    
    total_payable = VATReturn.objects.filter(tenant=tenant).aggregate(
        total=django.db.models.Sum('net_payable')
    )['total'] or Decimal('0.00')
    
    print(f"\nVAT Totals:")
    print(f"  Total Output Tax: Rs. {total_output:,.2f}")
    print(f"  Total Input Tax: Rs. {total_input:,.2f}")
    print(f"  Total Net Payable: Rs. {total_payable:,.2f}")
    
    print("\n" + "=" * 80)
    print("TEST COMPLETED SUCCESSFULLY!")
    print("=" * 80)
    print("\nYou can now test the Tax Management page at:")
    print("http://localhost:3000/dashboard/accounting/tax-management")
    print("\nFeatures to test:")
    print("  1. View Tax Rules list")
    print("  2. View VAT Returns list")
    print("  3. Switch between tabs")
    print("  4. File draft VAT return")
    print("  5. Mark filed return as paid")
    print("  6. Deactivate tax rule")
    print("=" * 80)

if __name__ == '__main__':
    import django.db.models
    test_tax_management()
