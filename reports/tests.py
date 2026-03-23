"""
Test cases for Reports & Analytics Engine
"""
from django.test import TestCase
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient
from decimal import Decimal
from datetime import date, timedelta

from tenants.models import Tenant
from sales.models import Customer, SalesOrder, Invoice
from purchase.models import Supplier, PurchaseInvoice
from construction.models import Site, MaterialConsumption, Attendance, DailyLog, Worker
from inventory.models import Product, Category, Warehouse, Stock

User = get_user_model()


class ReportsEngineTestCase(TestCase):
    """Test cases for Reports & Analytics Engine"""
    
    def setUp(self):
        """Set up test data"""
        # Create tenant
        self.tenant = Tenant.objects.create(
            name="Test Business",
            business_type='hardware'
        )
        
        # Create user
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123',
            tenant=self.tenant
        )
        
        # Setup API client
        self.client = APIClient()
        self.client.force_authenticate(user=self.user)
        
        # Create test data
        self._create_test_data()
    
    def _create_test_data(self):
        """Create comprehensive test data"""
        # Customer with balance
        self.customer = Customer.objects.create(
            tenant=self.tenant,
            name="Test Customer",
            phone="9841234567",
            credit_limit=Decimal('100000.00'),
            current_balance=Decimal('50000.00')
        )
        
        # Supplier with balance
        self.supplier = Supplier.objects.create(
            tenant=self.tenant,
            name="Test Supplier",
            phone="9851234567",
            current_balance=Decimal('30000.00')
        )
        
        # Sales Order
        self.sales_order = SalesOrder.objects.create(
            tenant=self.tenant,
            order_number="SO-TEST-001",
            date=date.today(),
            customer=self.customer,
            status='Delivered',
            total=Decimal('100000.00'),
            created_by=self.user
        )
        
        # Invoice
        self.invoice = Invoice.objects.create(
            tenant=self.tenant,
            invoice_number="INV-TEST-001",
            date=date.today(),
            due_date=date.today() + timedelta(days=30),
            customer=self.customer,
            amount=Decimal('50000.00'),
            status='Sent',
            created_by=self.user
        )
        
        # Purchase Invoice
        self.purchase_invoice = PurchaseInvoice.objects.create(
            tenant=self.tenant,
            invoice_number="PI-TEST-001",
            date=date.today(),
            supplier=self.supplier,
            total_amount=Decimal('60000.00'),
            status='Paid'
        )
        
        # Category and Product
        self.category = Category.objects.create(
            tenant=self.tenant,
            name="Building Materials"
        )
        
        self.product = Product.objects.create(
            tenant=self.tenant,
            name="Cement Bag",
            sku="CEM-001",
            category=self.category,
            unit='bag',
            cost_price=Decimal('600.00'),
            selling_price=Decimal('650.00'),
            reorder_level=Decimal('100.00')
        )
        
        # Warehouse and Stock
        self.warehouse = Warehouse.objects.create(
            tenant=self.tenant,
            name="Main Warehouse",
            location="Kathmandu"
        )
        
        self.stock = Stock.objects.create(
            tenant=self.tenant,
            product=self.product,
            warehouse=self.warehouse,
            quantity=Decimal('50.00')  # Below reorder level
        )
        
        # Construction Site
        self.site = Site.objects.create(
            tenant=self.tenant,
            name="Test Site",
            location="Kathmandu",
            allocated_budget=Decimal('1000000.00'),
            status='active'
        )
        
        # Daily Log
        self.daily_log = DailyLog.objects.create(
            tenant=self.tenant,
            site=self.site,
            date=date.today(),
            weather='sunny',
            other_expenses=Decimal('10000.00')
        )
        
        # Material Consumption
        self.material_consumption = MaterialConsumption.objects.create(
            tenant=self.tenant,
            site=self.site,
            daily_log=self.daily_log,
            material_name="Cement",
            quantity=Decimal('100.00'),
            unit='bag',
            unit_cost=Decimal('600.00')
        )
        
        # Worker and Attendance
        self.worker = Worker.objects.create(
            tenant=self.tenant,
            name="Test Worker",
            phone="9861234567",
            role='labor',
            daily_wage=Decimal('1000.00')
        )
        
        self.attendance = Attendance.objects.create(
            tenant=self.tenant,
            site=self.site,
            worker=self.worker,
            date=date.today(),
            status='present',
            wage_amount=Decimal('1000.00')
        )
    
    def test_dashboard_summary_structure(self):
        """Test dashboard summary API returns correct structure"""
        response = self.client.get('/api/reports/dashboard-summary/')
        
        self.assertEqual(response.status_code, 200)
        data = response.json()
        
        # Check main sections exist
        self.assertIn('financials', data)
        self.assertIn('inventory', data)
        self.assertIn('construction', data)
        self.assertIn('generated_at', data)
    
    def test_dashboard_financials(self):
        """Test dashboard financials section"""
        response = self.client.get('/api/reports/dashboard-summary/')
        data = response.json()
        
        financials = data['financials']
        
        # Check all financial fields exist
        self.assertIn('total_receivables', financials)
        self.assertIn('total_payables', financials)
        self.assertIn('total_revenue', financials)
        self.assertIn('total_expenses', financials)
        self.assertIn('net_profit', financials)
        self.assertIn('profit_margin_percentage', financials)
        
        # Verify calculations
        self.assertEqual(financials['total_receivables'], 50000.00)
        self.assertEqual(financials['total_payables'], 30000.00)
        
        # Revenue should include sales order
        self.assertGreaterEqual(financials['total_revenue'], 100000.00)
        
        # Expenses should include purchase
        self.assertGreaterEqual(financials['total_expenses'], 60000.00)
        
        # Net profit = revenue - expenses
        expected_profit = financials['total_revenue'] - financials['total_expenses']
        self.assertEqual(financials['net_profit'], expected_profit)
    
    def test_dashboard_inventory(self):
        """Test dashboard inventory section"""
        response = self.client.get('/api/reports/dashboard-summary/')
        data = response.json()
        
        inventory = data['inventory']
        
        # Check structure
        self.assertIn('low_stock_items', inventory)
        self.assertIn('total_low_stock_items', inventory)
        self.assertIn('critical_items', inventory)
        
        # Should have at least one low stock item (our test product)
        self.assertGreater(len(inventory['low_stock_items']), 0)
        
        # Check low stock item structure
        if inventory['low_stock_items']:
            item = inventory['low_stock_items'][0]
            self.assertIn('product_id', item)
            self.assertIn('product_name', item)
            self.assertIn('sku', item)
            self.assertIn('current_stock', item)
            self.assertIn('reorder_level', item)
            self.assertIn('stock_deficit', item)
            self.assertIn('urgency', item)
    
    def test_dashboard_construction(self):
        """Test dashboard construction section"""
        response = self.client.get('/api/reports/dashboard-summary/')
        data = response.json()
        
        construction = data['construction']
        
        # Check structure
        self.assertIn('budget_alert_sites', construction)
        self.assertIn('total_alert_sites', construction)
        self.assertIn('critical_sites', construction)
        self.assertIn('total_active_sites', construction)
        
        # Our test site has 7.1% budget utilization (71000/1000000)
        # So it shouldn't appear in alerts (< 80%)
        # But let's verify the structure is correct
        self.assertIsInstance(construction['budget_alert_sites'], list)
    
    def test_profit_and_loss_requires_dates(self):
        """Test P&L API requires date parameters"""
        response = self.client.get('/api/reports/profit-and-loss/')
        
        self.assertEqual(response.status_code, 400)
        data = response.json()
        self.assertIn('error', data)
    
    def test_profit_and_loss_with_dates(self):
        """Test P&L API with valid date range"""
        start_date = (date.today() - timedelta(days=30)).isoformat()
        end_date = date.today().isoformat()
        
        response = self.client.get(
            f'/api/reports/profit-and-loss/?start_date={start_date}&end_date={end_date}'
        )
        
        self.assertEqual(response.status_code, 200)
        data = response.json()
        
        # Check main sections
        self.assertIn('period', data)
        self.assertIn('revenue', data)
        self.assertIn('expenses', data)
        self.assertIn('profit', data)
        self.assertIn('metrics', data)
    
    def test_profit_and_loss_period(self):
        """Test P&L period information"""
        start_date = '2024-01-01'
        end_date = '2024-03-31'
        
        response = self.client.get(
            f'/api/reports/profit-and-loss/?start_date={start_date}&end_date={end_date}'
        )
        
        data = response.json()
        period = data['period']
        
        self.assertEqual(period['start_date'], start_date)
        self.assertEqual(period['end_date'], end_date)
        self.assertEqual(period['days'], 90)
    
    def test_profit_and_loss_revenue(self):
        """Test P&L revenue section"""
        start_date = (date.today() - timedelta(days=30)).isoformat()
        end_date = date.today().isoformat()
        
        response = self.client.get(
            f'/api/reports/profit-and-loss/?start_date={start_date}&end_date={end_date}'
        )
        
        data = response.json()
        revenue = data['revenue']
        
        # Check structure
        self.assertIn('sales_revenue', revenue)
        self.assertIn('invoice_revenue', revenue)
        self.assertIn('payments_received', revenue)
        self.assertIn('total_revenue', revenue)
        
        # Each should have amount and count
        self.assertIn('amount', revenue['sales_revenue'])
        self.assertIn('count', revenue['sales_revenue'])
    
    def test_profit_and_loss_expenses(self):
        """Test P&L expenses section"""
        start_date = (date.today() - timedelta(days=30)).isoformat()
        end_date = date.today().isoformat()
        
        response = self.client.get(
            f'/api/reports/profit-and-loss/?start_date={start_date}&end_date={end_date}'
        )
        
        data = response.json()
        expenses = data['expenses']
        
        # Check structure
        self.assertIn('purchase_expenses', expenses)
        self.assertIn('material_expenses', expenses)
        self.assertIn('labor_expenses', expenses)
        self.assertIn('other_expenses', expenses)
        self.assertIn('total_expenses', expenses)
    
    def test_profit_and_loss_profit(self):
        """Test P&L profit section"""
        start_date = (date.today() - timedelta(days=30)).isoformat()
        end_date = date.today().isoformat()
        
        response = self.client.get(
            f'/api/reports/profit-and-loss/?start_date={start_date}&end_date={end_date}'
        )
        
        data = response.json()
        profit = data['profit']
        
        # Check structure
        self.assertIn('gross_profit', profit)
        self.assertIn('gross_profit_margin_percentage', profit)
        self.assertIn('ebitda', profit)
        self.assertIn('net_profit', profit)
        
        # Verify calculation
        revenue = data['revenue']['total_revenue']
        expenses = data['expenses']['total_expenses']
        expected_profit = revenue - expenses
        
        self.assertEqual(profit['gross_profit'], expected_profit)
    
    def test_profit_and_loss_metrics(self):
        """Test P&L metrics section"""
        start_date = (date.today() - timedelta(days=30)).isoformat()
        end_date = date.today().isoformat()
        
        response = self.client.get(
            f'/api/reports/profit-and-loss/?start_date={start_date}&end_date={end_date}'
        )
        
        data = response.json()
        metrics = data['metrics']
        
        # Check structure
        self.assertIn('days_in_period', metrics)
        self.assertIn('average_daily_revenue', metrics)
        self.assertIn('average_daily_expenses', metrics)
        self.assertIn('expense_ratio', metrics)
    
    def test_profit_and_loss_invalid_date_range(self):
        """Test P&L with invalid date range"""
        start_date = '2024-03-31'
        end_date = '2024-01-01'  # End before start
        
        response = self.client.get(
            f'/api/reports/profit-and-loss/?start_date={start_date}&end_date={end_date}'
        )
        
        self.assertEqual(response.status_code, 400)
        data = response.json()
        self.assertIn('error', data)
    
    def test_list_available_reports(self):
        """Test listing available reports"""
        response = self.client.get('/api/reports/')
        
        self.assertEqual(response.status_code, 200)
        data = response.json()
        
        # Should be a list of reports
        self.assertIsInstance(data, list)
        self.assertGreater(len(data), 0)
        
        # Check structure of first report
        if data:
            report = data[0]
            self.assertIn('name', report)
            self.assertIn('description', report)
    
    def test_construction_profitability(self):
        """Test construction profitability report"""
        response = self.client.get('/api/reports/construction-profitability/')
        
        self.assertEqual(response.status_code, 200)
        data = response.json()
        
        self.assertIn('sites', data)
        self.assertIn('total_sites', data)
        self.assertIn('total_budget', data)
        self.assertIn('total_spent', data)
    
    def test_inventory_valuation(self):
        """Test inventory valuation report"""
        response = self.client.get('/api/reports/inventory-valuation/')
        
        self.assertEqual(response.status_code, 200)
        data = response.json()
        
        self.assertIn('total_inventory_value', data)
        self.assertIn('products', data)
        self.assertIn('total_products', data)
    
    def test_credit_summary(self):
        """Test credit summary report"""
        response = self.client.get('/api/reports/credit-summary/')
        
        self.assertEqual(response.status_code, 200)
        data = response.json()
        
        self.assertIn('total_outstanding', data)
        self.assertIn('total_customers_with_credit', data)
        self.assertIn('top_debtors', data)
        
        # Should have our test customer
        self.assertGreater(data['total_outstanding'], 0)
    
    def test_revenue_expense_trend(self):
        """Test revenue vs expense trend report"""
        response = self.client.get('/api/reports/revenue-expense-trend/')
        
        self.assertEqual(response.status_code, 200)
        data = response.json()
        
        self.assertIn('monthly_data', data)
        self.assertIsInstance(data['monthly_data'], list)
    
    def test_sales_performance(self):
        """Test sales performance report"""
        response = self.client.get('/api/reports/sales-performance/')
        
        self.assertEqual(response.status_code, 200)
        data = response.json()
        
        self.assertIn('total_sales', data)
        self.assertIn('total_orders', data)
        self.assertIn('average_order_value', data)
        self.assertIn('top_customers', data)


class ReportsPerformanceTestCase(TestCase):
    """Test performance of reports using aggregations"""
    
    def setUp(self):
        """Set up test data"""
        self.tenant = Tenant.objects.create(
            name="Performance Test",
            business_type='hardware'
        )
        
        self.user = User.objects.create_user(
            username='perfuser',
            email='perf@example.com',
            password='testpass123',
            tenant=self.tenant
        )
        
        self.client = APIClient()
        self.client.force_authenticate(user=self.user)
    
    def test_dashboard_query_count(self):
        """Test that dashboard uses minimal queries"""
        from django.test.utils import override_settings
        from django.db import connection
        from django.test.utils import CaptureQueriesContext
        
        with CaptureQueriesContext(connection) as context:
            response = self.client.get('/api/reports/dashboard-summary/')
            self.assertEqual(response.status_code, 200)
        
        # Should use reasonable number of queries (not N+1)
        # Exact number depends on data, but should be < 50
        query_count = len(context.captured_queries)
        self.assertLess(query_count, 50, 
            f"Dashboard used {query_count} queries - possible N+1 problem")
    
    def test_pl_query_count(self):
        """Test that P&L uses minimal queries"""
        from django.db import connection
        from django.test.utils import CaptureQueriesContext
        
        start_date = '2024-01-01'
        end_date = '2024-03-31'
        
        with CaptureQueriesContext(connection) as context:
            response = self.client.get(
                f'/api/reports/profit-and-loss/?start_date={start_date}&end_date={end_date}'
            )
            self.assertEqual(response.status_code, 200)
        
        # Should use reasonable number of queries
        query_count = len(context.captured_queries)
        self.assertLess(query_count, 30,
            f"P&L used {query_count} queries - possible N+1 problem")
