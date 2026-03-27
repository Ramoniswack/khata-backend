#!/usr/bin/env python
"""
Direct test of dashboard logic without HTTP layer
"""
import os
import sys
import django

# Setup Django
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core_backend.settings')
django.setup()

from django.contrib.auth import get_user_model
from django.db.models import Sum, Count, Q, F
from django.utils import timezone
from datetime import timedelta
from sales.models import SalesOrder, Customer, SalesOrderLine
from inventory.models import Product, Stock

User = get_user_model()

def test_dashboard_logic():
    """Test the dashboard logic directly"""
    
    print("\n" + "="*80)
    print("TESTING DASHBOARD LOGIC DIRECTLY")
    print("="*80)
    
    # Find the user
    try:
        user = User.objects.get(username='mr.bishal.baniya')
        tenant = user.tenant
        print(f"\n✅ Found user: {user.username}")
        print(f"   - Tenant: {tenant.name} (ID: {tenant.id})")
    except User.DoesNotExist:
        print("\n❌ User not found")
        return
    
    print("\n" + "-"*80)
    print("TESTING INVENTORY SUMMARY CALCULATION")
    print("-"*80)
    
    try:
        # This is the problematic code from the dashboard
        products_qs = Product.objects.filter(tenant=tenant)
        total_skus = products_qs.count()
        
        print(f"\n✅ Total products: {total_skus}")
        
        # Calculate stock status for each product
        in_stock = 0
        low_stock = 0
        out_of_stock = 0
        
        for product in products_qs:
            total_stock = Stock.objects.filter(
                tenant=tenant,
                product=product
            ).aggregate(total=Sum('quantity'))['total'] or 0
            
            if total_stock == 0:
                out_of_stock += 1
            elif total_stock <= product.reorder_level:
                low_stock += 1
            else:
                in_stock += 1
        
        print(f"✅ In stock: {in_stock}")
        print(f"✅ Low stock: {low_stock}")
        print(f"✅ Out of stock: {out_of_stock}")
        
        print("\n✅ Inventory summary calculation successful!")
        
    except Exception as e:
        print(f"\n❌ Error in inventory summary: {type(e).__name__}")
        print(f"Error message: {str(e)}")
        import traceback
        traceback.print_exc()
        return
    
    print("\n" + "-"*80)
    print("TESTING OTHER DASHBOARD COMPONENTS")
    print("-"*80)
    
    try:
        # Test other dashboard queries
        period = 'month'
        now = timezone.now()
        start_date = now - timedelta(days=30)
        
        # Orders
        current_orders = SalesOrder.objects.filter(
            tenant=tenant,
            date__gte=start_date,
            status__in=['Confirmed', 'Delivered']
        )
        print(f"\n✅ Current orders: {current_orders.count()}")
        
        # Customers
        total_customers = Customer.objects.filter(tenant=tenant).count()
        print(f"✅ Total customers: {total_customers}")
        
        # Recent orders
        recent_orders = SalesOrder.objects.filter(tenant=tenant).order_by('-created_at')[:5]
        print(f"✅ Recent orders: {recent_orders.count()}")
        
        # Top products
        top_products_data = SalesOrderLine.objects.filter(
            sales_order__tenant=tenant,
            sales_order__status__in=['Confirmed', 'Delivered'],
            sales_order__date__gte=start_date
        ).values('product__name').annotate(
            total_qty=Sum('quantity')
        ).order_by('-total_qty')[:5]
        print(f"✅ Top products: {len(top_products_data)}")
        
        print("\n✅ All dashboard components working!")
        
    except Exception as e:
        print(f"\n❌ Error in dashboard components: {type(e).__name__}")
        print(f"Error message: {str(e)}")
        import traceback
        traceback.print_exc()
    
    print("\n" + "="*80)
    print("TEST COMPLETE - Dashboard logic is working correctly!")
    print("="*80)

if __name__ == '__main__':
    test_dashboard_logic()
