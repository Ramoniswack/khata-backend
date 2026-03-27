#!/usr/bin/env python
"""
Cleanup script for invoices and related data
Use this if you're getting UNIQUE constraint errors
"""
import os
import sys
import django

# Setup Django
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core_backend.settings')
django.setup()

from sales.models import Invoice, CreditNote, CustomerLedger

print("\n" + "="*80)
print("CLEANING UP INVOICES AND RELATED DATA")
print("="*80)

print("\n⚠️  WARNING: This will delete ALL invoices, credit notes, and ledger entries!")
print("This is useful for development/testing but should NOT be used in production.")

response = input("\nAre you sure you want to continue? (yes/no): ")

if response.lower() != 'yes':
    print("\n❌ Cleanup cancelled.")
    sys.exit(0)

print("\n[1] Deleting credit notes...")
count = CreditNote.objects.count()
CreditNote.objects.all().delete()
print(f"   ✓ Deleted {count} credit notes")

print("\n[2] Deleting customer ledger entries...")
count = CustomerLedger.objects.count()
CustomerLedger.objects.all().delete()
print(f"   ✓ Deleted {count} ledger entries")

print("\n[3] Deleting invoices...")
count = Invoice.objects.count()
Invoice.objects.all().delete()
print(f"   ✓ Deleted {count} invoices")

print("\n" + "="*80)
print("✅ CLEANUP COMPLETE!")
print("="*80)
print("\nYou can now create new invoices without UNIQUE constraint errors.")
