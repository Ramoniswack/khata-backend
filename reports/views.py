from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from drf_spectacular.utils import extend_schema, extend_schema_view, OpenApiParameter
from django.db.models import Sum, Count, F, Q, DecimalField, Value
from django.db.models.functions import Coalesce
from decimal import Decimal
from datetime import datetime, timedelta

from sales.models import SalesOrder, Invoice, Customer, PaymentReceived
from purchase.models import PurchaseInvoice
from construction.models import Site, MaterialConsumption, Attendance
from inventory.models import Product, Stock
from accounting.models import JournalEntry
from users.permissions import ReportsPermission, CanViewFinancials


@extend_schema_view(
    list=extend_schema(tags=['Reports'], summary='List available reports'),
)
class ReportViewSet(viewsets.ViewSet):
    """
    ViewSet for cross-module reporting and analytics.
    All reports use database-level aggregations for performance.
    
    Permissions:
    - Dashboard Summary: All authenticated users
    - Financial Reports: Admin, Manager, Accountant only
    """
    permission_classes = [IsAuthenticated, ReportsPermission]
    
    def get_tenant(self):
        """Get current user's tenant"""
        return self.request.user.tenant
    
    def parse_date_params(self, request):
        """Parse start_date and end_date from query params"""
        start_date = request.query_params.get('start_date')
        end_date = request.query_params.get('end_date')
        
        if start_date:
            start_date = datetime.strptime(start_date, '%Y-%m-%d').date()
        if end_date:
            end_date = datetime.strptime(end_date, '%Y-%m-%d').date()
        
        return start_date, end_date
    
    def list(self, request):
        """List available report endpoints"""
        reports = [
            {'name': 'dashboard-summary', 'description': 'Complete dashboard overview'},
            {'name': 'profit-and-loss', 'description': 'Detailed P&L statement'},
            {'name': 'summary', 'description': 'Executive dashboard summary'},
            {'name': 'construction-profitability', 'description': 'Construction site P&L'},
            {'name': 'inventory-valuation', 'description': 'Inventory value by product'},
            {'name': 'credit-summary', 'description': 'Customer credit exposure'},
            {'name': 'revenue-expense-trend', 'description': 'Monthly revenue vs expenses'},
            {'name': 'sales-performance', 'description': 'Sales metrics and top customers'},
        ]
        return Response(reports)
    
    @extend_schema(
        tags=['Reports'],
        summary='Dashboard Summary',
        description='Complete dashboard overview with financials, inventory alerts, and construction budget warnings',
    )
    @action(detail=False, methods=['get'], url_path='dashboard-summary')
    def dashboard_summary(self, request):
        """Complete dashboard summary for main dashboard page"""
        tenant = self.get_tenant()
        
        # ===== FINANCIALS =====
        # Total Receivables (Customer Credit Outstanding)
        total_receivables = Customer.objects.filter(tenant=tenant).aggregate(
            total=Coalesce(Sum('current_balance'), Value(Decimal('0.00')))
        )['total']
        
        # Total Payables (Supplier Credit Outstanding) - Import Supplier model
        try:
            from purchase.models import Supplier
            total_payables = Supplier.objects.filter(tenant=tenant).aggregate(
                total=Coalesce(Sum('current_balance'), Value(Decimal('0.00')))
            )['total']
        except:
            total_payables = Decimal('0.00')
        
        # Revenue calculation
        sales_revenue = SalesOrder.objects.filter(
            tenant=tenant, status='Delivered'
        ).aggregate(
            total=Coalesce(Sum('total'), Value(Decimal('0.00')))
        )['total']
        
        invoice_revenue = Invoice.objects.filter(tenant=tenant).exclude(
            status='Draft'
        ).aggregate(
            total=Coalesce(Sum('amount'), Value(Decimal('0.00')))
        )['total']
        
        total_revenue = sales_revenue + invoice_revenue
        
        # Expenses calculation
        purchase_expenses = PurchaseInvoice.objects.filter(
            tenant=tenant, status='Paid'
        ).aggregate(
            total=Coalesce(Sum('amount'), Value(Decimal('0.00')))
        )['total']
        
        material_expenses = MaterialConsumption.objects.filter(
            tenant=tenant
        ).aggregate(
            total=Coalesce(Sum(F('quantity') * F('unit_cost'), output_field=DecimalField()), Value(Decimal('0.00')))
        )['total']
        
        labor_expenses = Attendance.objects.filter(tenant=tenant).aggregate(
            total=Coalesce(Sum('wage_amount'), Value(Decimal('0.00')))
        )['total']
        
        total_expenses = purchase_expenses + material_expenses + labor_expenses
        net_profit = total_revenue - total_expenses
        profit_margin = (net_profit / total_revenue * 100) if total_revenue > 0 else Decimal('0.00')
        
        # ===== INVENTORY - LOW STOCK ALERTS =====
        low_stock_products = Product.objects.filter(tenant=tenant).annotate(
            total_stock=Coalesce(Sum('stocks__quantity'), Value(Decimal('0.00')))
        ).filter(
            total_stock__lt=F('reorder_level')
        ).order_by('total_stock')[:5]
        
        low_stock_items = []
        for product in low_stock_products:
            stock_deficit = product.reorder_level - product.total_stock
            urgency = 'critical' if product.total_stock < (product.reorder_level * Decimal('0.5')) else 'low'
            
            # Get warehouse breakdown
            warehouses = Stock.objects.filter(
                tenant=tenant, product=product
            ).values('warehouse__name').annotate(
                quantity=Sum('quantity')
            )
            
            low_stock_items.append({
                'product_id': str(product.id),
                'product_name': product.name,
                'sku': product.sku,
                'current_stock': float(product.total_stock),
                'reorder_level': float(product.reorder_level),
                'unit': product.unit.name if product.unit else 'unit',
                'stock_deficit': float(stock_deficit),
                'urgency': urgency,
                'warehouses': list(warehouses),
            })
        
        critical_items = sum(1 for item in low_stock_items if item['urgency'] == 'critical')
        
        # ===== CONSTRUCTION - BUDGET ALERTS =====
        sites = Site.objects.filter(tenant=tenant, status='active')
        budget_alert_sites = []
        
        for site in sites:
            # Calculate actual spend
            material_cost = MaterialConsumption.objects.filter(
                tenant=tenant, site=site
            ).aggregate(
                total=Coalesce(Sum(F('quantity') * F('unit_cost'), output_field=DecimalField()), Value(Decimal('0.00')))
            )['total']
            
            labor_cost = Attendance.objects.filter(
                tenant=tenant, site=site
            ).aggregate(
                total=Coalesce(Sum('wage_amount'), Value(Decimal('0.00')))
            )['total']
            
            other_expenses = site.dailylog_set.aggregate(
                total=Coalesce(Sum('other_expenses'), Value(Decimal('0.00')))
            )['total']
            
            actual_spend = material_cost + labor_cost + other_expenses
            budget_utilization = (actual_spend / site.allocated_budget * 100) if site.allocated_budget > 0 else Decimal('0.00')
            
            # Only include sites with >80% budget utilization
            if budget_utilization > 80:
                remaining_budget = site.allocated_budget - actual_spend
                
                if budget_utilization > 100:
                    alert_level = 'critical'
                elif budget_utilization > 95:
                    alert_level = 'high'
                else:
                    alert_level = 'warning'
                
                budget_alert_sites.append({
                    'site_id': str(site.id),
                    'site_name': site.name,
                    'location': site.location,
                    'status': site.status,
                    'allocated_budget': float(site.allocated_budget),
                    'actual_spend': float(actual_spend),
                    'budget_utilization_percentage': float(round(budget_utilization, 2)),
                    'remaining_budget': float(remaining_budget),
                    'alert_level': alert_level,
                    'breakdown': {
                        'material_cost': float(material_cost),
                        'labor_cost': float(labor_cost),
                        'other_expenses': float(other_expenses),
                    }
                })
        
        critical_sites = sum(1 for site in budget_alert_sites if site['alert_level'] == 'critical')
        total_active_sites = sites.count()
        
        return Response({
            'financials': {
                'total_receivables': float(total_receivables),
                'total_payables': float(total_payables),
                'total_revenue': float(total_revenue),
                'total_expenses': float(total_expenses),
                'net_profit': float(net_profit),
                'profit_margin_percentage': float(round(profit_margin, 2)),
                'breakdown': {
                    'sales_revenue': float(sales_revenue),
                    'invoice_revenue': float(invoice_revenue),
                    'purchase_expenses': float(purchase_expenses),
                    'material_expenses': float(material_expenses),
                    'labor_expenses': float(labor_expenses),
                }
            },
            'inventory': {
                'low_stock_items': low_stock_items,
                'total_low_stock_items': len(low_stock_items),
                'critical_items': critical_items,
            },
            'construction': {
                'budget_alert_sites': budget_alert_sites,
                'total_alert_sites': len(budget_alert_sites),
                'critical_sites': critical_sites,
                'total_active_sites': total_active_sites,
            },
            'generated_at': datetime.now().isoformat(),
        })
    
    @extend_schema(
        tags=['Reports'],
        summary='Main Dashboard Data',
        description='Dashboard data matching frontend structure with stats, revenue chart, recent orders, top products, customers, and inventory',
        parameters=[
            OpenApiParameter('period', str, description='Period for revenue chart: today, week, month, year (default: month)'),
        ]
    )
    @action(detail=False, methods=['get'], url_path='main-dashboard')
    def main_dashboard(self, request):
        """Main dashboard data for /dashboard page"""
        try:
            from django.utils import timezone
            from datetime import timedelta
            from inventory.models import Product
            
            tenant = self.get_tenant()
            period = request.query_params.get('period', 'month')
            
            # Calculate date ranges
            now = timezone.now()
            today_start = now.replace(hour=0, minute=0, second=0, microsecond=0)
            
            if period == 'today':
                start_date = today_start
                previous_start = start_date - timedelta(days=1)
                previous_end = start_date
            elif period == 'week':
                start_date = today_start - timedelta(days=now.weekday())
                previous_start = start_date - timedelta(days=7)
                previous_end = start_date
            elif period == 'year':
                start_date = now.replace(month=1, day=1, hour=0, minute=0, second=0, microsecond=0)
                previous_start = start_date.replace(year=start_date.year - 1)
                previous_end = start_date
            else:  # month (default)
                start_date = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
                if start_date.month == 1:
                    previous_start = start_date.replace(year=start_date.year - 1, month=12)
                else:
                    previous_start = start_date.replace(month=start_date.month - 1)
                previous_end = start_date
            
            # Current period stats
            current_orders = SalesOrder.objects.filter(tenant=tenant, date__gte=start_date)
            current_revenue = current_orders.aggregate(total=Sum('total'))['total'] or Decimal('0')
            current_order_count = current_orders.count()
            
            # Previous period stats
            previous_orders = SalesOrder.objects.filter(
                tenant=tenant,
                date__gte=previous_start,
                date__lt=previous_end
            )
            previous_revenue = previous_orders.aggregate(total=Sum('total'))['total'] or Decimal('0')
            previous_order_count = previous_orders.count()
            
            # Calculate percentage changes
            revenue_change = 0
            if previous_revenue > 0:
                revenue_change = float(((current_revenue - previous_revenue) / previous_revenue) * 100)
            
            orders_change = 0
            if previous_order_count > 0:
                orders_change = ((current_order_count - previous_order_count) / previous_order_count) * 100
            
            # Customer stats
            total_customers = Customer.objects.filter(tenant=tenant).count()
            new_customers = Customer.objects.filter(tenant=tenant, created_at__gte=start_date).count()
            previous_new_customers = Customer.objects.filter(
                tenant=tenant,
                created_at__gte=previous_start,
                created_at__lt=previous_end
            ).count()
            customers_change = 0
            if previous_new_customers > 0:
                customers_change = ((new_customers - previous_new_customers) / previous_new_customers) * 100
            
            # Product stats
            total_products = Product.objects.filter(tenant=tenant).count()
            new_products = Product.objects.filter(tenant=tenant, created_at__gte=start_date).count()
            previous_new_products = Product.objects.filter(
                tenant=tenant,
                created_at__gte=previous_start,
                created_at__lt=previous_end
            ).count()
            products_change = 0
            if previous_new_products > 0:
                products_change = ((new_products - previous_new_products) / previous_new_products) * 100
            
            # Revenue chart data
            revenue_data = []
            if period == 'today':
                # Hourly data for today
                for hour in range(0, 24, 3):
                    hour_start = today_start + timedelta(hours=hour)
                    hour_end = hour_start + timedelta(hours=3)
                    revenue = SalesOrder.objects.filter(
                        tenant=tenant,
                        date__gte=hour_start,
                        date__lt=hour_end
                    ).aggregate(total=Sum('total'))['total'] or Decimal('0')
                    time_label = f"{hour % 12 if hour % 12 != 0 else 12} {'AM' if hour < 12 else 'PM'}"
                    revenue_data.append({
                        'time': time_label,
                        'value': float(revenue)
                    })
            elif period == 'week':
                # Daily data for the week
                for day in range(7):
                    day_start = start_date + timedelta(days=day)
                    day_end = day_start + timedelta(days=1)
                    revenue = SalesOrder.objects.filter(
                        tenant=tenant,
                        date__gte=day_start,
                        date__lt=day_end
                    ).aggregate(total=Sum('total'))['total'] or Decimal('0')
                    revenue_data.append({
                        'time': day_start.strftime('%a'),
                        'value': float(revenue)
                    })
            elif period == 'year':
                # Monthly data for the year
                for month in range(1, 13):
                    month_start = start_date.replace(month=month)
                    if month == 12:
                        month_end = month_start.replace(year=month_start.year + 1, month=1)
                    else:
                        month_end = month_start.replace(month=month + 1)
                    revenue = SalesOrder.objects.filter(
                        tenant=tenant,
                        date__gte=month_start,
                        date__lt=month_end
                    ).aggregate(total=Sum('total'))['total'] or Decimal('0')
                    revenue_data.append({
                        'time': month_start.strftime('%b'),
                        'value': float(revenue)
                    })
            else:  # month
                # Weekly data for the month
                week_num = 1
                current = start_date
                while current < now:
                    week_end = min(current + timedelta(days=7), now)
                    revenue = SalesOrder.objects.filter(
                        tenant=tenant,
                        date__gte=current,
                        date__lt=week_end
                    ).aggregate(total=Sum('total'))['total'] or Decimal('0')
                    revenue_data.append({
                        'time': f"Week {week_num}",
                        'value': float(revenue)
                    })
                    current = week_end
                    week_num += 1
            
            # Recent orders (last 5)
            recent_orders = SalesOrder.objects.filter(tenant=tenant).select_related('customer').order_by('-date')[:5]
            recent_orders_data = [{
                'id': order.order_number,
                'customer': order.customer.name if order.customer else 'Walk-in Customer',
                'amount': f"Rs. {order.total:,.0f}",
                'status': order.status
            } for order in recent_orders]
            
            # Top products (by quantity sold)
            from sales.models import SalesOrderLine
            top_products_data = []
            top_products = SalesOrderLine.objects.filter(
                order__tenant=tenant,
                order__date__gte=start_date
            ).values('product__name').annotate(
                total_qty=Sum('quantity')
            ).order_by('-total_qty')[:5]
            
            max_qty = top_products[0]['total_qty'] if top_products else 1
            for item in top_products:
                top_products_data.append({
                    'name': item['product__name'],
                    'sales': int(item['total_qty']),
                    'max': int(max_qty)
                })
            
            # Recent customers (last 5)
            recent_customers = Customer.objects.filter(tenant=tenant).order_by('-created_at')[:5]
            recent_customers_data = []
            for customer in recent_customers:
                # Calculate time ago
                time_diff = now - customer.created_at
                if time_diff.days == 0:
                    joined = "Today"
                elif time_diff.days == 1:
                    joined = "Yesterday"
                elif time_diff.days < 7:
                    joined = f"{time_diff.days} days ago"
                elif time_diff.days < 30:
                    joined = f"{time_diff.days // 7} week{'s' if time_diff.days // 7 > 1 else ''} ago"
                else:
                    joined = f"{time_diff.days // 30} month{'s' if time_diff.days // 30 > 1 else ''} ago"
                
                # Get initials
                name_parts = customer.name.split()
                initials = ''.join([part[0].upper() for part in name_parts[:2]])
                
                recent_customers_data.append({
                    'name': customer.name,
                    'email': customer.email or 'No email',
                    'initials': initials,
                    'joined': joined
                })
            
            # Inventory summary
            in_stock = Product.objects.filter(tenant=tenant, current_stock__gt=F('reorder_level')).count()
            low_stock = Product.objects.filter(
                tenant=tenant,
                current_stock__lte=F('reorder_level'),
                current_stock__gt=0
            ).count()
            out_of_stock = Product.objects.filter(tenant=tenant, current_stock=0).count()
            
            return Response({
                'stats': {
                    'revenue': f"Rs. {current_revenue:,.0f}",
                    'revenueChange': round(revenue_change, 1),
                    'orders': current_order_count,
                    'ordersChange': round(orders_change, 1),
                    'customers': total_customers,
                    'customersChange': round(customers_change, 1),
                    'products': total_products,
                    'productsChange': round(products_change, 1),
                },
                'revenueData': {
                    period: revenue_data
                },
                'recentOrders': recent_orders_data,
                'topProducts': top_products_data,
                'recentCustomers': recent_customers_data,
                'inventorySummary': {
                    'inStock': in_stock,
                    'lowStock': low_stock,
                    'outOfStock': out_of_stock,
                    'totalSKUs': total_products
                }
            })
        except Exception as e:
            import traceback
            print(f"[Main Dashboard Error] {str(e)}")
            print(traceback.format_exc())
            return Response(
                {'error': str(e), 'detail': 'Failed to load dashboard data'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    @extend_schema(
        tags=['Reports'],
        summary='Profit and Loss Statement',
        description='Detailed P&L report with date range filtering',
        parameters=[
            OpenApiParameter('start_date', str, description='Start date (YYYY-MM-DD)', required=True),
            OpenApiParameter('end_date', str, description='End date (YYYY-MM-DD)', required=True),
        ]
    )
    @action(detail=False, methods=['get'], url_path='profit-and-loss')
    def profit_and_loss(self, request):
        """Detailed Profit & Loss statement"""
        tenant = self.get_tenant()
        start_date, end_date = self.parse_date_params(request)
        
        if not start_date or not end_date:
            return Response(
                {'error': 'Both start_date and end_date are required (YYYY-MM-DD)'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        days_in_period = (end_date - start_date).days + 1
        
        # ===== REVENUE =====
        sales_qs = SalesOrder.objects.filter(
            tenant=tenant, date__gte=start_date, date__lte=end_date, status='Delivered'
        )
        sales_revenue_amount = sales_qs.aggregate(
            total=Coalesce(Sum('total'), Value(Decimal('0.00')))
        )['total']
        sales_revenue_count = sales_qs.count()
        
        invoice_qs = Invoice.objects.filter(
            tenant=tenant, date__gte=start_date, date__lte=end_date
        ).exclude(status='Draft')
        invoice_revenue_amount = invoice_qs.aggregate(
            total=Coalesce(Sum('amount'), Value(Decimal('0.00')))
        )['total']
        invoice_revenue_count = invoice_qs.count()
        
        payments_qs = PaymentReceived.objects.filter(
            tenant=tenant, date__gte=start_date, date__lte=end_date
        )
        payments_received_amount = payments_qs.aggregate(
            total=Coalesce(Sum('amount'), Value(Decimal('0.00')))
        )['total']
        payments_received_count = payments_qs.count()
        
        total_revenue = sales_revenue_amount + invoice_revenue_amount
        
        # ===== EXPENSES =====
        purchase_qs = PurchaseInvoice.objects.filter(
            tenant=tenant, date__gte=start_date, date__lte=end_date, status='Paid'
        )
        purchase_expenses_amount = purchase_qs.aggregate(
            total=Coalesce(Sum('amount'), Value(Decimal('0.00')))
        )['total']
        purchase_expenses_count = purchase_qs.count()
        
        material_qs = MaterialConsumption.objects.filter(
            tenant=tenant, daily_log__date__gte=start_date, daily_log__date__lte=end_date
        )
        material_expenses_amount = material_qs.aggregate(
            total=Coalesce(Sum(F('quantity') * F('unit_cost'), output_field=DecimalField()), Value(Decimal('0.00')))
        )['total']
        material_expenses_count = material_qs.count()
        
        labor_qs = Attendance.objects.filter(
            tenant=tenant, date__gte=start_date, date__lte=end_date
        )
        labor_expenses_amount = labor_qs.aggregate(
            total=Coalesce(Sum('wage_amount'), Value(Decimal('0.00')))
        )['total']
        labor_expenses_count = labor_qs.count()
        
        # Other expenses from daily logs
        other_expenses_amount = Decimal('0.00')
        other_expenses_count = 0
        
        total_expenses = purchase_expenses_amount + material_expenses_amount + labor_expenses_amount + other_expenses_amount
        
        # ===== PROFIT METRICS =====
        gross_profit = total_revenue - total_expenses
        gross_profit_margin = (gross_profit / total_revenue * 100) if total_revenue > 0 else Decimal('0.00')
        
        # EBITDA (simplified - same as gross profit for now)
        ebitda = gross_profit
        ebitda_margin = gross_profit_margin
        
        net_profit = gross_profit
        net_profit_margin = gross_profit_margin
        
        # ===== METRICS =====
        average_daily_revenue = total_revenue / days_in_period if days_in_period > 0 else Decimal('0.00')
        average_daily_expenses = total_expenses / days_in_period if days_in_period > 0 else Decimal('0.00')
        expense_ratio = (total_expenses / total_revenue * 100) if total_revenue > 0 else Decimal('0.00')
        
        return Response({
            'period': {
                'start_date': start_date.isoformat(),
                'end_date': end_date.isoformat(),
                'days': days_in_period,
            },
            'revenue': {
                'sales_revenue': {
                    'amount': float(sales_revenue_amount),
                    'count': sales_revenue_count,
                },
                'invoice_revenue': {
                    'amount': float(invoice_revenue_amount),
                    'count': invoice_revenue_count,
                },
                'payments_received': {
                    'amount': float(payments_received_amount),
                    'count': payments_received_count,
                },
                'total_revenue': float(total_revenue),
            },
            'expenses': {
                'purchase_expenses': {
                    'amount': float(purchase_expenses_amount),
                    'count': purchase_expenses_count,
                },
                'material_expenses': {
                    'amount': float(material_expenses_amount),
                    'count': material_expenses_count,
                },
                'labor_expenses': {
                    'amount': float(labor_expenses_amount),
                    'count': labor_expenses_count,
                },
                'other_expenses': {
                    'amount': float(other_expenses_amount),
                    'count': other_expenses_count,
                },
                'total_expenses': float(total_expenses),
            },
            'profit': {
                'gross_profit': float(gross_profit),
                'gross_profit_margin_percentage': float(round(gross_profit_margin, 2)),
                'ebitda': float(ebitda),
                'ebitda_margin_percentage': float(round(ebitda_margin, 2)),
                'net_profit': float(net_profit),
                'net_profit_margin_percentage': float(round(net_profit_margin, 2)),
            },
            'metrics': {
                'days_in_period': days_in_period,
                'average_daily_revenue': float(round(average_daily_revenue, 2)),
                'average_daily_expenses': float(round(average_daily_expenses, 2)),
                'expense_ratio_percentage': float(round(expense_ratio, 2)),
            },
        })
    
    
    @extend_schema(
        tags=['Reports'],
        summary='Executive Dashboard Summary',
        description='High-level financial overview across all modules',
        parameters=[
            OpenApiParameter('start_date', str, description='Start date (YYYY-MM-DD)'),
            OpenApiParameter('end_date', str, description='End date (YYYY-MM-DD)'),
        ]
    )
    @action(detail=False, methods=['get'])
    def summary(self, request):
        """Executive dashboard summary with key financial metrics"""
        tenant = self.get_tenant()
        start_date, end_date = self.parse_date_params(request)
        
        # Base querysets
        sales_qs = SalesOrder.objects.filter(tenant=tenant)
        invoice_qs = Invoice.objects.filter(tenant=tenant)
        purchase_qs = PurchaseInvoice.objects.filter(tenant=tenant)
        
        # Apply date filters
        if start_date:
            sales_qs = sales_qs.filter(date__gte=start_date)
            invoice_qs = invoice_qs.filter(date__gte=start_date)
            purchase_qs = purchase_qs.filter(date__gte=start_date)
        if end_date:
            sales_qs = sales_qs.filter(date__lte=end_date)
            invoice_qs = invoice_qs.filter(date__lte=end_date)
            purchase_qs = purchase_qs.filter(date__lte=end_date)
        
        # Revenue calculation
        sales_revenue = sales_qs.filter(status='Delivered').aggregate(
            total=Coalesce(Sum('total'), Value(Decimal('0.00')))
        )['total']
        
        invoice_revenue = invoice_qs.exclude(status='Draft').aggregate(
            total=Coalesce(Sum('amount'), Value(Decimal('0.00')))
        )['total']
        
        total_revenue = sales_revenue + invoice_revenue
        
        # Expenses calculation
        purchase_expenses = purchase_qs.filter(status='Paid').aggregate(
            total=Coalesce(Sum('amount'), Value(Decimal('0.00')))
        )['total']
        
        # Material consumption expenses
        material_qs = MaterialConsumption.objects.filter(tenant=tenant)
        if start_date:
            material_qs = material_qs.filter(daily_log__date__gte=start_date)
        if end_date:
            material_qs = material_qs.filter(daily_log__date__lte=end_date)
        
        material_expenses = material_qs.aggregate(
            total=Coalesce(Sum(F('quantity') * F('unit_cost'), output_field=DecimalField()), Value(Decimal('0.00')))
        )['total']
        
        # Labor expenses
        attendance_qs = Attendance.objects.filter(tenant=tenant)
        if start_date:
            attendance_qs = attendance_qs.filter(date__gte=start_date)
        if end_date:
            attendance_qs = attendance_qs.filter(date__lte=end_date)
        
        labor_expenses = attendance_qs.aggregate(
            total=Coalesce(Sum('wage_amount'), Value(Decimal('0.00')))
        )['total']
        
        total_expenses = purchase_expenses + material_expenses + labor_expenses
        
        # Net profit
        net_profit = total_revenue - total_expenses
        
        # Cash on hand
        payment_qs = PaymentReceived.objects.filter(tenant=tenant)
        if start_date:
            payment_qs = payment_qs.filter(date__gte=start_date)
        if end_date:
            payment_qs = payment_qs.filter(date__lte=end_date)
        
        cash_on_hand = payment_qs.aggregate(
            total=Coalesce(Sum('amount'), Value(Decimal('0.00')))
        )['total']
        
        # Counts
        total_sales_orders = sales_qs.count()
        total_invoices = invoice_qs.count()
        total_customers = Customer.objects.filter(tenant=tenant).count()
        active_sites = Site.objects.filter(tenant=tenant, status='active').count()
        
        return Response({
            'total_revenue': total_revenue,
            'total_expenses': total_expenses,
            'net_profit': net_profit,
            'cash_on_hand': cash_on_hand,
            'total_sales_orders': total_sales_orders,
            'total_invoices': total_invoices,
            'total_customers': total_customers,
            'active_construction_sites': active_sites,
            'period': {
                'start_date': start_date.isoformat() if start_date else None,
                'end_date': end_date.isoformat() if end_date else None,
            }
        })

    @extend_schema(
        tags=['Reports'],
        summary='Construction Profitability Report',
        description='Multi-site P&L analysis for construction projects',
        parameters=[
            OpenApiParameter('status', str, description='Filter by site status'),
        ]
    )
    @action(detail=False, methods=['get'], url_path='construction-profitability')
    def construction_profitability(self, request):
        """Construction site profitability analysis"""
        tenant = self.get_tenant()
        status_filter = request.query_params.get('status')
        
        sites_qs = Site.objects.filter(tenant=tenant)
        if status_filter:
            sites_qs = sites_qs.filter(status=status_filter)
        
        sites_data = []
        total_budget = Decimal('0.00')
        total_spent = Decimal('0.00')
        
        for site in sites_qs:
            # Material costs
            material_cost = MaterialConsumption.objects.filter(
                tenant=tenant, site=site
            ).aggregate(
                total=Coalesce(Sum(F('quantity') * F('unit_cost'), output_field=DecimalField()), Value(Decimal('0.00')))
            )['total']
            
            # Labor costs
            labor_cost = Attendance.objects.filter(
                tenant=tenant, site=site
            ).aggregate(
                total=Coalesce(Sum('wage_amount'), Value(Decimal('0.00')))
            )['total']
            
            # Other expenses from daily logs
            other_expenses = site.dailylog_set.aggregate(
                total=Coalesce(Sum('other_expenses'), Value(Decimal('0.00')))
            )['total']
            
            total_cost = material_cost + labor_cost + other_expenses
            budget_utilized = (total_cost / site.allocated_budget * 100) if site.allocated_budget > 0 else Decimal('0.00')
            remaining_budget = site.allocated_budget - total_cost
            
            # Budget health
            if budget_utilized < 80:
                budget_health = 'green'
            elif budget_utilized <= 100:
                budget_health = 'yellow'
            else:
                budget_health = 'red'
            
            sites_data.append({
                'site_id': str(site.id),
                'site_name': site.name,
                'location': site.location,
                'status': site.status,
                'allocated_budget': site.allocated_budget,
                'material_cost': material_cost,
                'labor_cost': labor_cost,
                'other_expenses': other_expenses,
                'total_cost': total_cost,
                'budget_utilized_percentage': round(budget_utilized, 2),
                'remaining_budget': remaining_budget,
                'budget_health': budget_health,
            })
            
            total_budget += site.allocated_budget
            total_spent += total_cost
        
        return Response({
            'sites': sites_data,
            'total_sites': len(sites_data),
            'total_budget': total_budget,
            'total_spent': total_spent,
        })
    
    @extend_schema(
        tags=['Reports'],
        summary='Inventory Valuation Report',
        description='Calculate total inventory value using cost price',
        parameters=[
            OpenApiParameter('warehouse', str, description='Filter by warehouse ID'),
        ]
    )
    @action(detail=False, methods=['get'], url_path='inventory-valuation')
    def inventory_valuation(self, request):
        """Inventory valuation by product"""
        tenant = self.get_tenant()
        warehouse_id = request.query_params.get('warehouse')
        
        stocks_qs = Stock.objects.filter(tenant=tenant).select_related('product')
        if warehouse_id:
            stocks_qs = stocks_qs.filter(warehouse_id=warehouse_id)
        
        # Group by product and calculate total value
        product_valuations = stocks_qs.values(
            'product__id', 'product__name', 'product__sku', 'product__cost_price'
        ).annotate(
            total_quantity=Sum('quantity')
        ).annotate(
            total_value=F('total_quantity') * F('product__cost_price')
        )
        
        products_data = []
        total_inventory_value = Decimal('0.00')
        
        for item in product_valuations:
            products_data.append({
                'product_id': str(item['product__id']),
                'product_name': item['product__name'],
                'sku': item['product__sku'],
                'total_quantity': item['total_quantity'],
                'cost_price': item['product__cost_price'],
                'total_value': item['total_value'],
            })
            total_inventory_value += item['total_value'] or Decimal('0.00')
        
        return Response({
            'total_inventory_value': total_inventory_value,
            'products': products_data,
            'total_products': len(products_data),
        })
    
    @extend_schema(
        tags=['Reports'],
        summary='Credit Summary Report',
        description='Customer credit exposure and top debtors',
        parameters=[
            OpenApiParameter('limit', int, description='Number of top debtors (default: 5)'),
        ]
    )
    @action(detail=False, methods=['get'], url_path='credit-summary')
    def credit_summary(self, request):
        """Customer credit exposure summary"""
        tenant = self.get_tenant()
        limit = int(request.query_params.get('limit', 5))
        
        # Get customers with outstanding balance
        customers_with_credit = Customer.objects.filter(
            tenant=tenant,
            current_balance__gt=0
        ).order_by('-current_balance')
        
        total_outstanding = customers_with_credit.aggregate(
            total=Coalesce(Sum('current_balance'), Value(Decimal('0.00')))
        )['total']
        
        # Top debtors
        top_debtors = []
        for customer in customers_with_credit[:limit]:
            available_credit = customer.credit_limit - customer.current_balance
            top_debtors.append({
                'customer_id': str(customer.id),
                'customer_name': customer.name,
                'phone': customer.phone,
                'outstanding_balance': customer.current_balance,
                'credit_limit': customer.credit_limit,
                'is_over_limit': customer.current_balance > customer.credit_limit,
                'available_credit': available_credit,
            })
        
        return Response({
            'total_outstanding': total_outstanding,
            'total_customers_with_credit': customers_with_credit.count(),
            'top_debtors': top_debtors,
        })
    
    @extend_schema(
        tags=['Reports'],
        summary='Revenue vs Expense Trend',
        description='Monthly revenue and expense data for charts',
        parameters=[
            OpenApiParameter('months', int, description='Number of months (default: 6)'),
        ]
    )
    @action(detail=False, methods=['get'], url_path='revenue-expense-trend')
    def revenue_expense_trend(self, request):
        """Monthly revenue vs expense trend"""
        tenant = self.get_tenant()
        months = int(request.query_params.get('months', 6))
        
        monthly_data = []
        
        for i in range(months - 1, -1, -1):
            # Calculate month start and end
            month_end = datetime.now().date().replace(day=1) - timedelta(days=i * 30)
            month_start = month_end.replace(day=1)
            
            # Revenue for the month
            sales_revenue = SalesOrder.objects.filter(
                tenant=tenant,
                date__gte=month_start,
                date__lt=month_end,
                status='Delivered'
            ).aggregate(
                total=Coalesce(Sum('total'), Value(Decimal('0.00')))
            )['total']
            
            invoice_revenue = Invoice.objects.filter(
                tenant=tenant,
                date__gte=month_start,
                date__lt=month_end
            ).exclude(status='Draft').aggregate(
                total=Coalesce(Sum('amount'), Value(Decimal('0.00')))
            )['total']
            
            revenue = sales_revenue + invoice_revenue
            
            # Expenses for the month
            purchase_expenses = PurchaseInvoice.objects.filter(
                tenant=tenant,
                date__gte=month_start,
                date__lt=month_end,
                status='Paid'
            ).aggregate(
                total=Coalesce(Sum('amount'), Value(Decimal('0.00')))
            )['total']
            
            material_expenses = MaterialConsumption.objects.filter(
                tenant=tenant,
                daily_log__date__gte=month_start,
                daily_log__date__lt=month_end
            ).aggregate(
                total=Coalesce(Sum(F('quantity') * F('unit_cost'), output_field=DecimalField()), Value(Decimal('0.00')))
            )['total']
            
            labor_expenses = Attendance.objects.filter(
                tenant=tenant,
                date__gte=month_start,
                date__lt=month_end
            ).aggregate(
                total=Coalesce(Sum('wage_amount'), Value(Decimal('0.00')))
            )['total']
            
            expenses = purchase_expenses + material_expenses + labor_expenses
            profit = revenue - expenses
            
            monthly_data.append({
                'month': month_start.strftime('%b %Y'),
                'month_date': month_start.isoformat(),
                'revenue': revenue,
                'expenses': expenses,
                'profit': profit,
            })
        
        return Response({
            'monthly_data': monthly_data
        })
    
    @extend_schema(
        tags=['Reports'],
        summary='Sales Performance Report',
        description='Sales metrics and top customers',
        parameters=[
            OpenApiParameter('start_date', str, description='Start date (YYYY-MM-DD)'),
            OpenApiParameter('end_date', str, description='End date (YYYY-MM-DD)'),
        ]
    )
    @action(detail=False, methods=['get'], url_path='sales-performance')
    def sales_performance(self, request):
        """Sales performance metrics"""
        tenant = self.get_tenant()
        start_date, end_date = self.parse_date_params(request)
        
        # Base queryset
        sales_qs = SalesOrder.objects.filter(tenant=tenant)
        if start_date:
            sales_qs = sales_qs.filter(date__gte=start_date)
        if end_date:
            sales_qs = sales_qs.filter(date__lte=end_date)
        
        # Total sales and orders
        total_sales = sales_qs.aggregate(
            total=Coalesce(Sum('total'), Value(Decimal('0.00')))
        )['total']
        
        total_orders = sales_qs.count()
        average_order_value = (total_sales / total_orders) if total_orders > 0 else Decimal('0.00')
        
        # Top customers
        top_customers_data = sales_qs.values(
            'customer__id', 'customer__name'
        ).annotate(
            total_orders=Count('id'),
            total_amount=Sum('total')
        ).order_by('-total_amount')[:5]
        
        top_customers = []
        for item in top_customers_data:
            top_customers.append({
                'customer_id': str(item['customer__id']),
                'customer_name': item['customer__name'],
                'total_orders': item['total_orders'],
                'total_amount': item['total_amount'],
            })
        
        return Response({
            'total_sales': total_sales,
            'total_orders': total_orders,
            'average_order_value': round(average_order_value, 2),
            'top_customers': top_customers,
            'period': {
                'start_date': start_date.isoformat() if start_date else None,
                'end_date': end_date.isoformat() if end_date else None,
            }
        })
