#!/usr/bin/env python
"""
Seed sales orders for testing sales reports
"""
import os
import sys
import django
from datetime import datetime, timedelta
from decimal import Decimal

# Setup Django
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core_backend.settings')
django.setup()

from sales.models import SalesOrder, SalesOrderLine, Customer
from inventory.models import Product
from tenants.models import Tenant

def seed_sales_orders():
    """Create sample sales orders for City Hardware tenant"""
    
    # Get the hardware tenant
    tenant = Tenant.objects.get(name='City Hardware & Suppliers')
    
    # Get customers
    customers = list(Customer.objects.filter(tenant=tenant))
    if not customers:
        print("❌ No customers found. Please run seed_demo_data first.")
        return
    
    # Get products
    products = list(Product.objects.filter(tenant=tenant))
    if not products:
        print("❌ No products found. Please run seed_demo_data first.")
        return
    
    print(f"Creating sales orders for {tenant.name}...")
    print(f"Found {len(customers)} customers and {len(products)} products")
    
    # Create sales orders for the last 3 months
    orders_created = 0
    end_date = datetime.now().date()
    
    for i in range(15):  # Create 15 orders
        # Random date in last 90 days
        days_ago = (i * 6) % 90
        order_date = end_date - timedelta(days=days_ago)
        
        # Pick a customer
        customer = customers[i % len(customers)]
        
        # Generate unique order number
        order_number = f"SO-TEST-{i+1:04d}"
        
        # Create order (order_number will be auto-generated)
        order = SalesOrder(
            tenant=tenant,
            customer=customer,
            order_number=order_number,
            date=order_date,
            status='Confirmed',
            payment_type='cash',
            notes=f'Test order {i+1}'
        )
        order.save()
        
        # Add 2-4 line items
        num_items = 2 + (i % 3)
        for j in range(num_items):
            product = products[(i + j) % len(products)]
            quantity = Decimal(str(1 + (j * 2)))
            unit_price = Decimal(str(1000 + (i * 100)))
            
            SalesOrderLine.objects.create(
                tenant=tenant,
                sales_order=order,
                product=product,
                quantity=quantity,
                unit_price=unit_price,
                discount_percent=Decimal('0'),
                tax_percent=Decimal('13')
            )
        
        # Calculate totals
        order.calculate_totals()
        order.save()
        
        orders_created += 1
        print(f"✅ Created order {order.order_number} for {customer.name} - Rs. {order.total}")
    
    print(f"\n✅ Successfully created {orders_created} sales orders!")

if __name__ == "__main__":
    seed_sales_orders()
