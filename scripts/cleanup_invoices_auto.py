#!/usr/bin/env python
"""
Automatic cleanup script for invoices and related data
This version doesn't require confirmation - use with caution!
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
print("CLEANING UP INVOICES AND RELATED DATA (AUTO MODE)")
print("="*80)

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
print("Try creating an invoice at: http://localhost:3000/dashboard/sales/invoices/new")
