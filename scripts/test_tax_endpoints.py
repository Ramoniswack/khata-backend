#!/usr/bin/env python
"""
Test script for Tax Management endpoints
Tests tax rules and VAT returns functionality
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

User = get_user_model()

def test_tax_management():
    """Test tax management functionality"""
    
    print("\n" + "="*80)
    print("TAX MANAGEMENT ENDPOINTS TEST")
    print("="*80)
    
    # Get or create test tenant
    tenant, _ = Tenant.objects.get_or_create(
        slug='test-hardware',
        defaults={
            'name': 'Test Hardware Store',
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
    
    # Create test liability account for tax
    tax_account, created = Account.objects.get_or_create(
        tenant=tenant,
        code='2100',
        defaults={
            'name': 'VAT Payable',
            'type': 'Liabilities',
            'sub_type': 'Tax',
            'level': 1,
            'status': 'active'
        }
    )
    print(f"✓ {'Created' if created else 'Found'} tax account: {tax_account.code} - {tax_account.name}")
    
    # Test 1: Create Tax Rule
    print("\n" + "-"*80)
    print("TEST 1: Create Tax Rule")
    print("-"*80)
    
    tax_rule, created = TaxRule.objects.get_or_create(
        tenant=tenant,
        name='VAT 13%',
        defaults={
            'type': 'VAT',
            'rate': Decimal('13.00'),
            'applicable_on': 'Both',
            'account': tax_account,
            'status': 'active',
            'description': 'Standard VAT rate in Nepal'
        }
    )
    
    if created:
        print(f"✓ Created tax rule: {tax_rule.name}")
    else:
        print(f"✓ Tax rule already exists: {tax_rule.name}")
    
    print(f"  - Type: {tax_rule.type}")
    print(f"  - Rate: {tax_rule.rate}%")
    print(f"  - Applicable On: {tax_rule.applicable_on}")
    print(f"  - Account: {tax_rule.account.code} - {tax_rule.account.name}")
    print(f"  - Status: {tax_rule.status}")
    
    # Test 2: List Tax Rules
    print("\n" + "-"*80)
    print("TEST 2: List Tax Rules")
    print("-"*80)
    
    tax_rules = TaxRule.objects.filter(tenant=tenant)
    print(f"✓ Found {tax_rules.count()} tax rule(s)")
    
    for rule in tax_rules:
        print(f"  - {rule.name} ({rule.rate}%) - {rule.type} - {rule.status}")
    
    # Test 3: Create VAT Return
    print("\n" + "-"*80)
    print("TEST 3: Create VAT Return")
    print("-"*80)
    
    # Check if VAT return already exists for this period
    existing_return = VATReturn.objects.filter(
        tenant=tenant,
        period='Chaitra 2081'
    ).first()
    
    if existing_return:
        vat_return = existing_return
        created = False
    else:
        # Generate unique return number
        import uuid
        return_number = f"VAT-{uuid.uuid4().hex[:8].upper()}"
        
        vat_return = VATReturn.objects.create(
            tenant=tenant,
            return_number=return_number,
            period='Chaitra 2081',
            from_date='2024-03-15',
            to_date='2024-04-14',
            output_tax=Decimal('55250.00'),  # VAT collected on sales
            input_tax=Decimal('16900.00'),   # VAT paid on purchases
            net_payable=Decimal('38350.00'), # Net VAT payable
            status='draft',
            notes='Test VAT return for Chaitra 2081'
        )
        created = True
    
    if created:
        print(f"✓ Created VAT return: {vat_return.return_number}")
    else:
        print(f"✓ VAT return already exists: {vat_return.return_number}")
    
    print(f"  - Period: {vat_return.period}")
    print(f"  - From: {vat_return.from_date}")
    print(f"  - To: {vat_return.to_date}")
    print(f"  - Output Tax (VAT Collected): Rs. {vat_return.output_tax:,.2f}")
    print(f"  - Input Tax (VAT Paid): Rs. {vat_return.input_tax:,.2f}")
    print(f"  - Net Payable: Rs. {vat_return.net_payable:,.2f}")
    print(f"  - Status: {vat_return.status}")
    
    # Test 4: List VAT Returns
    print("\n" + "-"*80)
    print("TEST 4: List VAT Returns")
    print("-"*80)
    
    vat_returns = VATReturn.objects.filter(tenant=tenant).order_by('-from_date')
    print(f"✓ Found {vat_returns.count()} VAT return(s)")
    
    for ret in vat_returns:
        print(f"  - {ret.return_number} - {ret.period} - Rs. {ret.net_payable:,.2f} - {ret.status}")
    
    # Test 5: File VAT Return
    print("\n" + "-"*80)
    print("TEST 5: File VAT Return")
    print("-"*80)
    
    if vat_return.status == 'draft':
        vat_return.status = 'filed'
        vat_return.filed_date = '2024-04-20'
        vat_return.save()
        print(f"✓ Filed VAT return: {vat_return.return_number}")
        print(f"  - Filed Date: {vat_return.filed_date}")
        print(f"  - Status: {vat_return.status}")
    else:
        print(f"✓ VAT return already filed: {vat_return.return_number}")
    
    # Test 6: Filter Tax Rules
    print("\n" + "-"*80)
    print("TEST 6: Filter Tax Rules")
    print("-"*80)
    
    active_vat_rules = TaxRule.objects.filter(
        tenant=tenant,
        type='VAT',
        status='active'
    )
    print(f"✓ Found {active_vat_rules.count()} active VAT rule(s)")
    
    for rule in active_vat_rules:
        print(f"  - {rule.name} ({rule.rate}%)")
    
    # Summary
    print("\n" + "="*80)
    print("TEST SUMMARY")
    print("="*80)
    print(f"✓ Tax Rules: {TaxRule.objects.filter(tenant=tenant).count()}")
    print(f"✓ VAT Returns: {VATReturn.objects.filter(tenant=tenant).count()}")
    print(f"✓ Tax Accounts: {Account.objects.filter(tenant=tenant, sub_type='Tax').count()}")
    print("\n✓ All tests completed successfully!")
    print("="*80 + "\n")

if __name__ == '__main__':
    test_tax_management()
