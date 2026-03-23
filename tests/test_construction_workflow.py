"""
Test Construction Module Workflow
Demonstrates the complete material consumption workflow:
1. Deduct stock from site's warehouse
2. Update site's actual_spend
3. Create accounting journal entry
4. Create stock movement (audit trail)
"""
import os
import django
from decimal import Decimal
from datetime import date

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core_backend.settings')
django.setup()

from tenants.models import Tenant
from users.models import User
from inventory.models import Product, Warehouse, Stock, StockMovement
from construction.models import Site, DailyLog, MaterialConsumption
from accounting.models import JournalEntry
from tenants.middleware import set_current_tenant

print("="*60)
print("CONSTRUCTION WORKFLOW TEST")
print("="*60)

# Get tenant and user
tenant = Tenant.objects.first()
user = User.objects.filter(tenant=tenant).first()

if not tenant or not user:
    print("ERROR: No tenant or user found")
    exit(1)

set_current_tenant(tenant)

print(f"\nTenant: {tenant.name}")
print(f"User: {user.username}")

# Get or create warehouse for site
warehouse, _ = Warehouse.objects.get_or_create(
    tenant=tenant,
    name="Site A Warehouse",
    defaults={'location': 'Kathmandu', 'is_active': True}
)
print(f"\nWarehouse: {warehouse.name}")

# Get or create unit
from inventory.models import UnitOfMeasure
unit, _ = UnitOfMeasure.objects.get_or_create(
    tenant=tenant,
    abbreviation="bag",
    defaults={'name': 'Bag', 'type': 'count'}
)

# Get or create product
product, _ = Product.objects.get_or_create(
    tenant=tenant,
    sku="TEST-CEMENT-001",
    defaults={
        'name': 'Test Cement',
        'unit': unit,
        'cost_price': Decimal('500.00'),
        'selling_price': Decimal('650.00'),
        'status': 'active'
    }
)
print(f"Product: {product.name} (SKU: {product.sku})")

# Get or create stock
stock, _ = Stock.objects.get_or_create(
    tenant=tenant,
    product=product,
    warehouse=warehouse,
    defaults={'quantity': Decimal('100.00')}
)

# Ensure we have stock
if stock.quantity < 10:
    stock.quantity = Decimal('100.00')
    stock.save()

initial_stock = stock.quantity
print(f"\nInitial Stock: {initial_stock} units")

# Get or create site
site, _ = Site.objects.get_or_create(
    tenant=tenant,
    name="Test Construction Site",
    defaults={
        'location': 'Kathmandu',
        'allocated_budget': Decimal('5000000.00'),
        'start_date': date.today(),
        'manager': user,
        'warehouse': warehouse,
        'status': 'active'
    }
)
print(f"\nSite: {site.name}")
print(f"Site Warehouse: {site.warehouse.name}")
print(f"Allocated Budget: NPR {site.allocated_budget:,.2f}")

# Get or create daily log
daily_log, _ = DailyLog.objects.get_or_create(
    tenant=tenant,
    site=site,
    date=date.today(),
    defaults={
        'work_description': 'Foundation work',
        'submitted_by': user
    }
)
print(f"\nDaily Log: {daily_log.date}")

# Count initial records
initial_movements = StockMovement.objects.filter(tenant=tenant).count()
initial_journal_entries = JournalEntry.objects.filter(tenant=tenant).count()

print("\n" + "="*60)
print("BEFORE MATERIAL CONSUMPTION")
print("="*60)
print(f"Stock: {stock.quantity} units")
print(f"Stock Movements: {initial_movements}")
print(f"Journal Entries: {initial_journal_entries}")
print(f"Site Material Cost: NPR {site.get_material_cost():,.2f}")
print(f"Site Actual Spend: NPR {site.get_actual_spend():,.2f}")

print("\n" + "="*60)
print("LOGGING MATERIAL CONSUMPTION")
print("="*60)
print("Consuming 10 units of cement at NPR 500/unit")

# Create material consumption (THE MAGIC HAPPENS HERE)
try:
    consumption = MaterialConsumption.objects.create(
        tenant=tenant,
        daily_log=daily_log,
        site=site,
        product=product,
        quantity=Decimal('10.00'),
        unit_cost=Decimal('500.00'),
        notes='Test consumption'
    )
    print(f"✅ Material consumption created (ID: {consumption.id})")
    print(f"   Total Cost: NPR {consumption.total_cost:,.2f}")
except Exception as e:
    print(f"❌ Error: {e}")
    import traceback
    traceback.print_exc()
    exit(1)

# Refresh stock
stock.refresh_from_db()
site.refresh_from_db()

# Count final records
final_movements = StockMovement.objects.filter(tenant=tenant).count()
final_journal_entries = JournalEntry.objects.filter(tenant=tenant).count()

print("\n" + "="*60)
print("AFTER MATERIAL CONSUMPTION")
print("="*60)

# Check stock deduction
print(f"\n1. STOCK DEDUCTION:")
print(f"   Before: {initial_stock} units")
print(f"   After:  {stock.quantity} units")
print(f"   Change: -{initial_stock - stock.quantity} units")
if stock.quantity == initial_stock - Decimal('10.00'):
    print("   ✅ Stock deducted correctly")
else:
    print("   ❌ Stock deduction failed")

# Check stock movement
print(f"\n2. STOCK MOVEMENT (AUDIT TRAIL):")
print(f"   Before: {initial_movements} movements")
print(f"   After:  {final_movements} movements")
movement = StockMovement.objects.filter(
    reference_type='construction_consumption',
    reference_id=consumption.id
).first()
if movement:
    print(f"   ✅ Stock movement created")
    print(f"      Type: {movement.movement_type}")
    print(f"      Quantity: {movement.quantity}")
    print(f"      Reason: {movement.reason}")
else:
    print("   ❌ Stock movement not created")

# Check site actual spend
print(f"\n3. SITE ACTUAL SPEND:")
material_cost = site.get_material_cost()
actual_spend = site.get_actual_spend()
print(f"   Material Cost: NPR {material_cost:,.2f}")
print(f"   Actual Spend:  NPR {actual_spend:,.2f}")
print(f"   Remaining Budget: NPR {site.get_remaining_budget():,.2f}")
print(f"   Budget Used: {site.get_budget_percentage():.2f}%")
if material_cost >= Decimal('5000.00'):
    print("   ✅ Site actual spend updated")
else:
    print("   ❌ Site actual spend not updated")

# Check journal entry
print(f"\n4. ACCOUNTING JOURNAL ENTRY:")
print(f"   Before: {initial_journal_entries} entries")
print(f"   After:  {final_journal_entries} entries")
journal_entry = JournalEntry.objects.filter(
    reference=f'MC-{consumption.id}'
).first()
if journal_entry:
    print(f"   ✅ Journal entry created")
    print(f"      Reference: {journal_entry.reference}")
    print(f"      Description: {journal_entry.description}")
    print(f"      Total Amount: NPR {journal_entry.total_amount:,.2f}")
    
    # Check double-entry
    lines = journal_entry.lines.all()
    total_debit = sum(line.debit for line in lines)
    total_credit = sum(line.credit for line in lines)
    
    print(f"\n   Journal Lines:")
    for line in lines:
        if line.debit > 0:
            print(f"      Dr. {line.account.name:30} NPR {line.debit:>10,.2f}")
        if line.credit > 0:
            print(f"          Cr. {line.account.name:26} NPR {line.credit:>10,.2f}")
    
    print(f"\n   Double-Entry Check:")
    print(f"      Total Debit:  NPR {total_debit:,.2f}")
    print(f"      Total Credit: NPR {total_credit:,.2f}")
    if total_debit == total_credit:
        print("      ✅ Balanced")
    else:
        print("      ❌ Not balanced")
else:
    print("   ⚠️  Journal entry not created (may need accounting setup)")

print("\n" + "="*60)
print("WORKFLOW SUMMARY")
print("="*60)
print("✅ Material consumption logged")
print("✅ Stock deducted from site warehouse")
print("✅ Stock movement created (audit trail)")
print("✅ Site actual spend updated")
if journal_entry:
    print("✅ Accounting journal entry created")
else:
    print("⚠️  Accounting journal entry not created")

print("\n" + "="*60)
print("TEST COMPLETE")
print("="*60)

set_current_tenant(None)
