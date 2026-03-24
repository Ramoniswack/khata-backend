#!/usr/bin/env python
"""
Create test accounts for journal entry testing
"""
import os
import sys
import django

# Add the backend directory to the path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core_backend.settings')
django.setup()

from accounting.models import Account
from tenants.models import Tenant
from users.models import User

def create_test_accounts():
    """Create basic test accounts"""
    
    tenant = Tenant.objects.first()
    if not tenant:
        print("❌ No tenant found")
        return
    
    user = User.objects.filter(tenant=tenant).first()
    if not user:
        print("❌ No user found")
        return
    
    print(f"Creating accounts for tenant: {tenant.name}")
    
    # Create basic accounts
    accounts_data = [
        {'code': '1000', 'name': 'Cash', 'type': 'Assets', 'sub_type': 'Cash', 'level': 1},
        {'code': '1100', 'name': 'Bank Account', 'type': 'Assets', 'sub_type': 'Bank', 'level': 1},
        {'code': '2000', 'name': 'Accounts Payable', 'type': 'Liabilities', 'sub_type': 'Payable', 'level': 1},
        {'code': '3000', 'name': 'Capital', 'type': 'Equity', 'sub_type': 'Capital', 'level': 1},
        {'code': '4000', 'name': 'Sales Revenue', 'type': 'Income', 'sub_type': 'Revenue', 'level': 1},
        {'code': '5000', 'name': 'Operating Expenses', 'type': 'Expense', 'sub_type': 'Operating', 'level': 1},
    ]
    
    created = 0
    for acc_data in accounts_data:
        acc, created_new = Account.objects.get_or_create(
            tenant=tenant,
            code=acc_data['code'],
            defaults={
                'name': acc_data['name'],
                'type': acc_data['type'],
                'sub_type': acc_data['sub_type'],
                'level': acc_data['level'],
                'status': 'active'
            }
        )
        if created_new:
            print(f"✓ Created: {acc.code} - {acc.name}")
            created += 1
        else:
            print(f"  Exists: {acc.code} - {acc.name}")
    
    print(f"\n✓ Total accounts: {Account.objects.filter(tenant=tenant).count()}")
    print(f"✓ New accounts created: {created}")

if __name__ == '__main__':
    create_test_accounts()
