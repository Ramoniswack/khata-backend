#!/usr/bin/env python
"""
Test script for journal entry creation
"""
import os
import sys
import django

# Add the backend directory to the path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core_backend.settings')
django.setup()

from accounting.models import Account, JournalEntry, JournalLine
from accounting.serializers import JournalEntrySerializer
from tenants.models import Tenant
from users.models import User

def test_journal_entry_creation():
    """Test creating a journal entry"""
    
    # Get a tenant and user
    tenant = Tenant.objects.first()
    if not tenant:
        print("❌ No tenant found. Please create a tenant first.")
        return
    
    user = User.objects.filter(tenant=tenant).first()
    if not user:
        print("❌ No user found for tenant. Please create a user first.")
        return
    
    print(f"✓ Using tenant: {tenant.name}")
    print(f"✓ Using user: {user.username}")
    
    # Get some accounts
    accounts = Account.objects.filter(tenant=tenant, level__gt=0)[:2]
    if accounts.count() < 2:
        print("❌ Need at least 2 accounts. Please create accounts first.")
        return
    
    print(f"✓ Found {accounts.count()} accounts")
    for acc in accounts:
        print(f"  - {acc.code}: {acc.name}")
    
    # Test payload
    payload = {
        'date': '2024-01-15',
        'type': 'Manual',
        'reference': 'TEST-001',
        'description': 'Test journal entry',
        'status': 'draft',
        'lines': [
            {
                'account': str(accounts[0].id),
                'description': 'Debit line',
                'debit': 1000,
                'credit': 0
            },
            {
                'account': str(accounts[1].id),
                'description': 'Credit line',
                'debit': 0,
                'credit': 1000
            }
        ]
    }
    
    print("\n📝 Testing journal entry creation...")
    print(f"Payload: {payload}")
    
    # Create serializer with context
    serializer = JournalEntrySerializer(data=payload, context={'request': type('obj', (object,), {'user': user, 'tenant': tenant})()})
    
    if serializer.is_valid():
        print("✓ Serializer validation passed")
        
        # Manually set tenant before saving (like perform_create does)
        journal_entry = serializer.save(tenant=tenant)
        print(f"✓ Journal entry created: {journal_entry.entry_number}")
        print(f"  - Total Debit: {journal_entry.total_debit}")
        print(f"  - Total Credit: {journal_entry.total_credit}")
        print(f"  - Lines: {journal_entry.lines.count()}")
        
        # Clean up
        journal_entry.delete()
        print("✓ Test entry deleted")
        
    else:
        print("❌ Serializer validation failed:")
        for field, errors in serializer.errors.items():
            print(f"  - {field}: {errors}")

if __name__ == '__main__':
    test_journal_entry_creation()
