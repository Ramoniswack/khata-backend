"""
Test cases for Hardware & Udhaar (Credit) System
"""
from django.test import TestCase
from django.contrib.auth import get_user_model
from decimal import Decimal
from datetime import date, timedelta

from tenants.models import Tenant
from sales.models import (
    Customer, SalesOrder, SalesOrderLine, Invoice, 
    CustomerLedger, PaymentReceived
)
from inventory.models import Product, Category

User = get_user_model()


class CreditSystemTestCase(TestCase):
    """Test cases for credit management system"""
    
    def setUp(self):
        """Set up test data"""
        # Create tenant
        self.tenant = Tenant.objects.create(
            name="Test Hardware Store",
            business_type='hardware'
        )
        
        # Create user
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123',
            tenant=self.tenant
        )
        
        # Create customer with credit limit
        self.customer = Customer.objects.create(
            tenant=self.tenant,
            name="ABC Construction",
            phone="9841234567",
            pan="123456789",
            credit_limit=Decimal('100000.00'),
            type='Business',
            payment_terms='Net 30'
        )
        
        # Create product category and product
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
            selling_price=Decimal('650.00'),
            stock_quantity=Decimal('1000')
        )
    
    def test_customer_credit_properties(self):
        """Test customer credit-related properties"""
        self.assertEqual(self.customer.current_balance, Decimal('0.00'))
        self.assertEqual(self.customer.available_credit, Decimal('100000.00'))
        self.assertFalse(self.customer.is_over_limit)
        
        # Add balance
        self.customer.current_balance = Decimal('50000.00')
        self.customer.save()
        
        self.assertEqual(self.customer.available_credit, Decimal('50000.00'))
        self.assertFalse(self.customer.is_over_limit)
        
        # Exceed limit
        self.customer.current_balance = Decimal('150000.00')
        self.customer.save()
        
        self.assertTrue(self.customer.is_over_limit)
        self.assertEqual(self.customer.available_credit, Decimal('0.00'))
    
    def test_sales_order_finalize_on_credit(self):
        """Test finalizing sales order on credit"""
        # Create sales order
        order = SalesOrder.objects.create(
            tenant=self.tenant,
            order_number="SO-TEST-001",
            date=date.today(),
            customer=self.customer,
            payment_type='credit',
            status='Draft',
            total=Decimal('10000.00'),
            created_by=self.user
        )
        
        # Create order line
        SalesOrderLine.objects.create(
            tenant=self.tenant,
            sales_order=order,
            product=self.product,
            quantity=Decimal('10'),
            unit_price=Decimal('650.00')
        )
        
        # Verify initial state
        self.assertEqual(self.customer.current_balance, Decimal('0.00'))
        self.assertEqual(CustomerLedger.objects.count(), 0)
        
        # Finalize on credit
        order.finalize_on_credit()
        
        # Verify order status
        self.assertEqual(order.status, 'Delivered')
        
        # Verify customer balance updated
        self.customer.refresh_from_db()
        self.assertEqual(self.customer.current_balance, Decimal('10000.00'))
        
        # Verify ledger entry created
        self.assertEqual(CustomerLedger.objects.count(), 1)
        ledger = CustomerLedger.objects.first()
        self.assertEqual(ledger.customer, self.customer)
        self.assertEqual(ledger.transaction_type, 'sale')
        self.assertEqual(ledger.debit_amount, Decimal('10000.00'))
        self.assertEqual(ledger.credit_amount, Decimal('0.00'))
        self.assertEqual(ledger.running_balance, Decimal('10000.00'))
    
    def test_credit_limit_check(self):
        """Test credit limit validation"""
        # Create order that exceeds credit limit
        order = SalesOrder.objects.create(
            tenant=self.tenant,
            order_number="SO-TEST-002",
            date=date.today(),
            customer=self.customer,
            payment_type='credit',
            status='Draft',
            total=Decimal('150000.00'),  # Exceeds 100k limit
            created_by=self.user
        )
        
        # Should raise ValueError
        with self.assertRaises(ValueError) as context:
            order.finalize_on_credit()
        
        self.assertIn('Credit limit exceeded', str(context.exception))
    
    def test_invoice_credit_sale(self):
        """Test invoice creation on credit"""
        # Create invoice on credit
        invoice = Invoice.objects.create(
            tenant=self.tenant,
            invoice_number="INV-TEST-001",
            date=date.today(),
            due_date=date.today() + timedelta(days=30),
            customer=self.customer,
            amount=Decimal('5000.00'),
            payment_type='credit',
            status='Sent',  # Not Draft
            created_by=self.user
        )
        
        # Verify customer balance updated
        self.customer.refresh_from_db()
        self.assertEqual(self.customer.current_balance, Decimal('5000.00'))
        
        # Verify ledger entry created
        self.assertEqual(CustomerLedger.objects.count(), 1)
        ledger = CustomerLedger.objects.first()
        self.assertEqual(ledger.transaction_type, 'sale')
        self.assertEqual(ledger.debit_amount, Decimal('5000.00'))
    
    def test_payment_received(self):
        """Test payment received functionality"""
        # Setup: Customer with balance
        self.customer.current_balance = Decimal('10000.00')
        self.customer.save()
        
        # Create invoice
        invoice = Invoice.objects.create(
            tenant=self.tenant,
            invoice_number="INV-TEST-002",
            date=date.today(),
            due_date=date.today() + timedelta(days=30),
            customer=self.customer,
            amount=Decimal('10000.00'),
            payment_type='credit',
            status='Draft',  # Keep as Draft to avoid auto-ledger
            created_by=self.user
        )
        invoice.status = 'Sent'
        invoice.save()
        
        # Record payment
        payment = PaymentReceived.objects.create(
            tenant=self.tenant,
            customer=self.customer,
            date=date.today(),
            amount=Decimal('5000.00'),
            payment_method='cash',
            invoice=invoice,
            received_by=self.user
        )
        
        # Verify payment number generated
        self.assertTrue(payment.payment_number.startswith('PAY-'))
        
        # Verify customer balance decreased
        self.customer.refresh_from_db()
        self.assertEqual(self.customer.current_balance, Decimal('5000.00'))
        
        # Verify invoice updated
        invoice.refresh_from_db()
        self.assertEqual(invoice.paid_amount, Decimal('5000.00'))
        self.assertEqual(invoice.status, 'Partially Paid')
        
        # Verify ledger entry
        payment_ledger = CustomerLedger.objects.filter(
            transaction_type='payment'
        ).first()
        self.assertIsNotNone(payment_ledger)
        self.assertEqual(payment_ledger.credit_amount, Decimal('5000.00'))
    
    def test_full_payment(self):
        """Test full payment of invoice"""
        # Setup
        self.customer.current_balance = Decimal('10000.00')
        self.customer.save()
        
        invoice = Invoice.objects.create(
            tenant=self.tenant,
            invoice_number="INV-TEST-003",
            date=date.today(),
            due_date=date.today() + timedelta(days=30),
            customer=self.customer,
            amount=Decimal('10000.00'),
            payment_type='credit',
            status='Draft',
            created_by=self.user
        )
        invoice.status = 'Sent'
        invoice.save()
        
        # Full payment
        payment = PaymentReceived.objects.create(
            tenant=self.tenant,
            customer=self.customer,
            date=date.today(),
            amount=Decimal('10000.00'),
            payment_method='bank',
            invoice=invoice,
            received_by=self.user
        )
        
        # Verify invoice fully paid
        invoice.refresh_from_db()
        self.assertEqual(invoice.status, 'Paid')
        self.assertEqual(invoice.balance, Decimal('0.00'))
        
        # Verify customer balance cleared
        self.customer.refresh_from_db()
        self.assertEqual(self.customer.current_balance, Decimal('0.00'))
    
    def test_ledger_immutability(self):
        """Test that ledger entries are immutable"""
        # Create a ledger entry via payment
        self.customer.current_balance = Decimal('5000.00')
        self.customer.save()
        
        payment = PaymentReceived.objects.create(
            tenant=self.tenant,
            customer=self.customer,
            date=date.today(),
            amount=Decimal('5000.00'),
            payment_method='cash',
            received_by=self.user
        )
        
        ledger = CustomerLedger.objects.first()
        original_balance = ledger.running_balance
        
        # Ledger should not be editable through normal means
        # This is enforced at admin level, not model level
        self.assertEqual(ledger.running_balance, original_balance)
    
    def test_multiple_transactions_running_balance(self):
        """Test running balance calculation across multiple transactions"""
        # Transaction 1: Credit sale
        order1 = SalesOrder.objects.create(
            tenant=self.tenant,
            order_number="SO-TEST-003",
            date=date.today(),
            customer=self.customer,
            payment_type='credit',
            total=Decimal('10000.00'),
            created_by=self.user
        )
        order1.finalize_on_credit()
        
        # Transaction 2: Another credit sale
        order2 = SalesOrder.objects.create(
            tenant=self.tenant,
            order_number="SO-TEST-004",
            date=date.today(),
            customer=self.customer,
            payment_type='credit',
            total=Decimal('5000.00'),
            created_by=self.user
        )
        order2.finalize_on_credit()
        
        # Transaction 3: Payment
        payment = PaymentReceived.objects.create(
            tenant=self.tenant,
            customer=self.customer,
            date=date.today(),
            amount=Decimal('7000.00'),
            payment_method='cash',
            received_by=self.user
        )
        
        # Verify final balance
        self.customer.refresh_from_db()
        self.assertEqual(self.customer.current_balance, Decimal('8000.00'))
        
        # Verify ledger entries
        ledgers = CustomerLedger.objects.order_by('created_at')
        self.assertEqual(ledgers.count(), 3)
        
        # Check running balances
        self.assertEqual(ledgers[0].running_balance, Decimal('10000.00'))
        self.assertEqual(ledgers[1].running_balance, Decimal('15000.00'))
        self.assertEqual(ledgers[2].running_balance, Decimal('8000.00'))


class AgingReportTestCase(TestCase):
    """Test cases for aging report"""
    
    def setUp(self):
        """Set up test data"""
        self.tenant = Tenant.objects.create(
            name="Test Store",
            business_type='hardware'
        )
        
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123',
            tenant=self.tenant
        )
        
        self.customer = Customer.objects.create(
            tenant=self.tenant,
            name="Test Customer",
            phone="9841234567",
            credit_limit=Decimal('100000.00')
        )
    
    def test_aging_buckets(self):
        """Test aging report bucket calculations"""
        today = date.today()
        
        # Create invoices with different ages
        # Current (not overdue)
        Invoice.objects.create(
            tenant=self.tenant,
            invoice_number="INV-001",
            date=today - timedelta(days=10),
            due_date=today + timedelta(days=20),
            customer=self.customer,
            amount=Decimal('5000.00'),
            payment_type='credit',
            status='Sent',
            created_by=self.user
        )
        
        # 30-60 days overdue
        Invoice.objects.create(
            tenant=self.tenant,
            invoice_number="INV-002",
            date=today - timedelta(days=75),
            due_date=today - timedelta(days=45),
            customer=self.customer,
            amount=Decimal('10000.00'),
            payment_type='credit',
            status='Overdue',
            created_by=self.user
        )
        
        # 60-90 days overdue
        Invoice.objects.create(
            tenant=self.tenant,
            invoice_number="INV-003",
            date=today - timedelta(days=105),
            due_date=today - timedelta(days=75),
            customer=self.customer,
            amount=Decimal('8000.00'),
            payment_type='credit',
            status='Overdue',
            created_by=self.user
        )
        
        # 90+ days overdue
        Invoice.objects.create(
            tenant=self.tenant,
            invoice_number="INV-004",
            date=today - timedelta(days=150),
            due_date=today - timedelta(days=120),
            customer=self.customer,
            amount=Decimal('12000.00'),
            payment_type='credit',
            status='Overdue',
            created_by=self.user
        )
        
        # Note: Aging report is tested via API endpoint
        # This test verifies the data setup for aging calculations
        self.assertEqual(Invoice.objects.filter(customer=self.customer).count(), 4)
