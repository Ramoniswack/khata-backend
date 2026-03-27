#!/usr/bin/env python
"""
Seed purchase data for testing purchase reports
"""
import os
import sys
import django

# Setup Django
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core_backend.settings')
django.setup()

from django.utils import timezone
from datetime import timedelta
from decimal import Decimal
from users.models import User
from purchase.models import Supplier, PurchaseOrder, PurchaseOrderLine, PurchaseInvoice
from inventory.models import Product, Category, UnitOfMeasure

def seed_purchase_data():
    """Seed purchase data for testing"""
    
    # Get admin user and tenant
    admin = User.objects.filter(is_superuser=True).first()
    if not admin or not admin.tenant:
        print("❌ No admin user with tenant found")
        return
    
    tenant = admin.tenant
    print(f"✓ Using tenant: {tenant.name}")
    
    # Create or get UOM
    uom, _ = UnitOfMeasure.objects.get_or_create(
        tenant=tenant,
        name="Piece",
        defaults={'abbreviation': 'pc'}
    )
    
    # Create or get category
    category, _ = Category.objects.get_or_create(
        tenant=tenant,
        name="Hardware",
        defaults={'description': 'Hardware items'}
    )
    
    # Create products
    products = []
    product_data = [
        {'name': 'Cement Bag', 'sku': 'CEM001', 'cost': 850},
        {'name': 'Steel Rod 12mm', 'sku': 'STL001', 'cost': 120},
        {'name': 'Bricks', 'sku': 'BRK001', 'cost': 15},
        {'name': 'Sand (per cft)', 'sku': 'SND001', 'cost': 80},
        {'name': 'Gravel (per cft)', 'sku': 'GRV001', 'cost': 90},
    ]
    
    for pd in product_data:
        product, created = Product.objects.get_or_create(
            tenant=tenant,
            sku=pd['sku'],
            defaults={
                'name': pd['name'],
                'category': category,
                'unit': uom,
                'cost_price': Decimal(str(pd['cost'])),
                'selling_price': Decimal(str(pd['cost'] * 1.3)),
                'reorder_level': Decimal('10'),
            }
        )
        products.append(product)
        if created:
            print(f"✓ Created product: {product.name}")
    
    # Create suppliers
    suppliers = []
    supplier_data = [
        {'name': 'ABC Hardware Suppliers', 'phone': '9841234567'},
        {'name': 'XYZ Building Materials', 'phone': '9851234567'},
        {'name': 'Nepal Construction Supply', 'phone': '9861234567'},
    ]
    
    for sd in supplier_data:
        supplier, created = Supplier.objects.get_or_create(
            tenant=tenant,
            name=sd['name'],
            defaults={
                'phone': sd['phone'],
                'email': f"{sd['name'].lower().replace(' ', '.')}@example.com",
                'address': 'Kathmandu, Nepal',
                'type': 'Company',
                'status': 'active',
            }
        )
        suppliers.append(supplier)
        if created:
            print(f"✓ Created supplier: {supplier.name}")
    
    # Create purchase orders and invoices for the last 3 months
    now = timezone.now()
    po_count = PurchaseOrder.objects.filter(tenant=tenant).count()
    invoice_count = PurchaseInvoice.objects.filter(tenant=tenant).count()
    
    for month_offset in range(3):
        month_start = now - timedelta(days=30 * (month_offset + 1))
        
        # Create 3-5 POs per month
        for i in range(3 + (month_offset % 3)):
            supplier = suppliers[i % len(suppliers)]
            po_date = month_start + timedelta(days=i * 7)
            expected_delivery = po_date + timedelta(days=7)
            
            # Create PO with unique number
            po_count += 1
            po = PurchaseOrder.objects.create(
                tenant=tenant,
                supplier=supplier,
                po_number=f"PO-{po_date.strftime('%Y%m%d')}-{po_count:04d}",
                date=po_date.date(),
                expected_delivery_date=expected_delivery.date(),
                payment_terms='Net 30',
                status='Received',
                notes=f"Purchase order for {supplier.name}",
                created_by=admin,
            )
            
            # Add 2-4 line items
            total = Decimal('0')
            for j in range(2 + (i % 3)):
                product = products[j % len(products)]
                quantity = Decimal(str(10 + (i * 5)))
                unit_price = product.cost_price
                
                PurchaseOrderLine.objects.create(
                    tenant=tenant,
                    purchase_order=po,
                    product=product,
                    quantity=quantity,
                    unit_price=unit_price,
                    tax_percent=Decimal('13'),
                    received_quantity=quantity,
                )
                # Calculate with tax
                base_amount = quantity * unit_price
                tax_amount = base_amount * Decimal('0.13')
                total += base_amount + tax_amount
            
            po.subtotal = total / Decimal('1.13')
            po.tax = total - po.subtotal
            po.total = total
            po.save()
            
            # Create invoice for the PO
            invoice_date = po_date + timedelta(days=2)
            due_date = invoice_date + timedelta(days=30)
            paid_amount = total if (i % 3 == 0) else total * Decimal('0.5')
            
            invoice_count += 1
            PurchaseInvoice.objects.create(
                tenant=tenant,
                supplier=supplier,
                purchase_order=po,
                invoice_number=f"PI-{invoice_date.strftime('%Y%m%d')}-{invoice_count:04d}",
                date=invoice_date.date(),
                due_date=due_date.date(),
                amount=total,
                paid_amount=paid_amount,
                status='paid' if paid_amount >= total else 'partial',
                notes=f"Invoice for {po.po_number}",
            )
    
    print(f"\n✓ Created {po_count} purchase orders")
    print(f"✓ Created {invoice_count} purchase invoices")
    print("\n✅ Purchase data seeding complete!")

if __name__ == '__main__':
    print("=" * 60)
    print("SEEDING PURCHASE DATA")
    print("=" * 60)
    seed_purchase_data()
