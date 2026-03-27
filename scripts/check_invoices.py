#!/usr/bin/env python
import os
import sys
import django

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core_backend.settings')
django.setup()

from sales.models import Invoice

print("Total invoices:", Invoice.objects.count())
print("\nLast 10 invoices:")
for inv in Invoice.objects.all().order_by('-id')[:10]:
    print(f"  {inv.invoice_number} - {inv.tenant.name} - Status: {inv.status}")
