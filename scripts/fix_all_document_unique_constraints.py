"""
Script to fix all document number unique constraints to be per-tenant
This addresses the same issue found in Quotation model across all document models
"""

# Models to fix in sales app
SALES_MODELS_TO_FIX = [
    ('SalesOrder', 'order_number'),
    ('Invoice', 'invoice_number'),
    ('CreditNote', 'credit_note_number'),
    ('Payment', 'payment_number'),
]

# Models to fix in purchase app
PURCHASE_MODELS_TO_FIX = [
    ('MaterialRequest', 'request_number'),
    ('PurchaseOrder', 'po_number'),
    ('PurchaseInvoice', 'invoice_number'),
    ('DebitNote', 'debit_note_number'),
]

# Models to fix in accounting app
ACCOUNTING_MODELS_TO_FIX = [
    ('JournalEntry', 'entry_number'),
    ('TaxReturn', 'return_number'),
]

print("=" * 80)
print("DOCUMENT NUMBER UNIQUE CONSTRAINT FIX")
print("=" * 80)
print()
print("This script will update all document models to use per-tenant unique constraints")
print("instead of global unique constraints.")
print()
print("Models to fix:")
print()
print("Sales Module:")
for model, field in SALES_MODELS_TO_FIX:
    print(f"  - {model}.{field}")
print()
print("Purchase Module:")
for model, field in PURCHASE_MODELS_TO_FIX:
    print(f"  - {model}.{field}")
print()
print("Accounting Module:")
for model, field in ACCOUNTING_MODELS_TO_FIX:
    print(f"  - {model}.{field}")
print()
print("=" * 80)
print()
print("Steps to apply fix:")
print()
print("1. Update model definitions to remove unique=True from document number fields")
print("2. Add unique_together = [['tenant', 'document_number']] to Meta class")
print("3. Generate migrations for each app:")
print("   python manage.py makemigrations sales -n fix_document_unique_constraints")
print("   python manage.py makemigrations purchase -n fix_document_unique_constraints")
print("   python manage.py makemigrations accounting -n fix_document_unique_constraints")
print("4. Apply migrations:")
print("   python manage.py migrate")
print()
print("=" * 80)
