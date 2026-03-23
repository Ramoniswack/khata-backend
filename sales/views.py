from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from drf_spectacular.utils import extend_schema, extend_schema_view, OpenApiParameter
from drf_spectacular.types import OpenApiTypes
from django.db.models import Sum, Q
from django.utils import timezone
from datetime import timedelta
from decimal import Decimal

from .models import (
    Customer, SalesOrder, SalesOrderLine, Quotation, Invoice, CreditNote,
    CustomerLedger, PaymentReceived
)
from .serializers import (
    CustomerSerializer, CustomerDetailSerializer, SalesOrderSerializer, SalesOrderCreateSerializer,
    QuotationSerializer, QuotationCreateSerializer, InvoiceSerializer, CreditNoteSerializer,
    CustomerLedgerSerializer, PaymentReceivedSerializer
)


@extend_schema_view(
    list=extend_schema(description="List all customers for the current tenant", tags=["Sales - Customers"]),
    retrieve=extend_schema(description="Get customer details", tags=["Sales - Customers"]),
    create=extend_schema(description="Create a new customer", tags=["Sales - Customers"]),
    update=extend_schema(description="Update customer details", tags=["Sales - Customers"]),
    partial_update=extend_schema(description="Partially update customer", tags=["Sales - Customers"]),
    destroy=extend_schema(description="Delete a customer", tags=["Sales - Customers"]),
)
class CustomerViewSet(viewsets.ModelViewSet):
    """ViewSet for Customer CRUD operations with credit management"""
    permission_classes = [IsAuthenticated]
    filterset_fields = ['status', 'type', 'payment_terms']
    search_fields = ['name', 'phone', 'email', 'pan']
    ordering_fields = ['name', 'created_at', 'current_balance']
    ordering = ['-created_at']
    
    def get_queryset(self):
        """Filter by current tenant"""
        return Customer.objects.all()
    
    def get_serializer_class(self):
        if self.action == 'retrieve':
            return CustomerDetailSerializer
        return CustomerSerializer
    
    def perform_create(self, serializer):
        """Set tenant when creating customer"""
        serializer.save(tenant=self.request.user.tenant)
    
    @extend_schema(
        tags=['Sales - Customers'],
        summary='Get customer ledger',
        description='Returns complete ledger history for a customer'
    )
    @action(detail=True, methods=['get'])
    def ledger(self, request, pk=None):
        """Get customer ledger entries"""
        customer = self.get_object()
        ledger_entries = customer.ledger_entries.all()
        serializer = CustomerLedgerSerializer(ledger_entries, many=True)
        return Response(serializer.data)
    
    @extend_schema(
        tags=['Sales - Customers'],
        summary='Get aging report',
        description='Returns outstanding balance by age buckets (30, 60, 90+ days)',
        responses={200: {
            'type': 'object',
            'properties': {
                'customer_id': {'type': 'string'},
                'customer_name': {'type': 'string'},
                'total_outstanding': {'type': 'number'},
                'current': {'type': 'number', 'description': '0-30 days'},
                'days_30_60': {'type': 'number', 'description': '30-60 days'},
                'days_60_90': {'type': 'number', 'description': '60-90 days'},
                'days_90_plus': {'type': 'number', 'description': '90+ days'},
                'overdue_invoices': {'type': 'array'},
            }
        }}
    )
    @action(detail=True, methods=['get'])
    def aging_report(self, request, pk=None):
        """
        Generate aging report for customer
        Shows outstanding balance by age buckets
        """
        customer = self.get_object()
        today = timezone.now().date()
        
        # Get all unpaid/partially paid invoices
        unpaid_invoices = customer.invoices.filter(
            Q(status='Sent') | Q(status='Partially Paid') | Q(status='Overdue')
        ).exclude(status='Paid')
        
        # Initialize buckets
        current = Decimal('0.00')  # 0-30 days
        days_30_60 = Decimal('0.00')
        days_60_90 = Decimal('0.00')
        days_90_plus = Decimal('0.00')
        
        overdue_invoices = []
        
        for invoice in unpaid_invoices:
            balance = invoice.balance
            days_overdue = (today - invoice.due_date).days
            
            # Categorize by age
            if days_overdue < 0:
                # Not yet due
                current += balance
            elif days_overdue <= 30:
                current += balance
            elif days_overdue <= 60:
                days_30_60 += balance
            elif days_overdue <= 90:
                days_60_90 += balance
            else:
                days_90_plus += balance
            
            # Add to overdue list if past due date
            if days_overdue > 0:
                overdue_invoices.append({
                    'invoice_number': invoice.invoice_number,
                    'date': invoice.date.isoformat(),
                    'due_date': invoice.due_date.isoformat(),
                    'amount': float(invoice.amount),
                    'paid_amount': float(invoice.paid_amount),
                    'balance': float(balance),
                    'days_overdue': days_overdue
                })
        
        report = {
            'customer_id': str(customer.id),
            'customer_name': customer.name,
            'total_outstanding': float(customer.current_balance),
            'current': float(current),
            'days_30_60': float(days_30_60),
            'days_60_90': float(days_60_90),
            'days_90_plus': float(days_90_plus),
            'overdue_invoices': overdue_invoices,
            'credit_limit': float(customer.credit_limit),
            'available_credit': float(customer.available_credit),
            'is_over_limit': customer.is_over_limit,
        }
        
        return Response(report)


@extend_schema_view(
    list=extend_schema(description="List all sales orders for the current tenant", tags=["Sales - Orders"]),
    retrieve=extend_schema(description="Get sales order details with line items", tags=["Sales - Orders"]),
    create=extend_schema(
        description="Create a new sales order with line items",
        tags=["Sales - Orders"],
        request=SalesOrderCreateSerializer
    ),
    update=extend_schema(
        description="Update sales order",
        tags=["Sales - Orders"],
        request=SalesOrderCreateSerializer
    ),
    partial_update=extend_schema(description="Partially update sales order", tags=["Sales - Orders"]),
    destroy=extend_schema(description="Delete a sales order", tags=["Sales - Orders"]),
)
class SalesOrderViewSet(viewsets.ModelViewSet):
    """ViewSet for Sales Order CRUD operations"""
    permission_classes = [IsAuthenticated]
    filterset_fields = ['status', 'customer']
    search_fields = ['order_number', 'reference', 'customer__name']
    ordering_fields = ['date', 'created_at', 'total']
    ordering = ['-date', '-created_at']
    
    def get_queryset(self):
        """Filter by current tenant"""
        return SalesOrder.objects.select_related('customer', 'created_by').prefetch_related('lines__product')
    
    def get_serializer_class(self):
        if self.action in ['create', 'update', 'partial_update']:
            return SalesOrderCreateSerializer
        return SalesOrderSerializer
    
    def perform_create(self, serializer):
        # Auto-generate order number (globally unique across all tenants due to DB constraint)
        # Use _base_manager to bypass tenant filtering and get true last order number
        last_order = SalesOrder._base_manager.all().order_by('-id').first()
        if last_order and last_order.order_number.startswith('SO-'):
            try:
                last_num = int(last_order.order_number.split('-')[1])
                order_number = f"SO-{str(last_num + 1).zfill(4)}"
            except:
                order_number = "SO-0001"
        else:
            order_number = "SO-0001"
        
        serializer.save(
            tenant=self.request.user.tenant,
            created_by=self.request.user, 
            order_number=order_number
        )
    
    @extend_schema(
        description="Update sales order status",
        tags=["Sales - Orders"],
        request={'application/json': {'type': 'object', 'properties': {'status': {'type': 'string'}}}},
        responses={200: SalesOrderSerializer}
    )
    @action(detail=True, methods=['patch'])
    def update_status(self, request, pk=None):
        """Update the status of a sales order"""
        sales_order = self.get_object()
        new_status = request.data.get('status')
        
        if new_status not in dict(SalesOrder.STATUS_CHOICES):
            return Response(
                {'error': 'Invalid status'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        sales_order.status = new_status
        sales_order.save()
        
        serializer = self.get_serializer(sales_order)
        return Response(serializer.data)
    
    @extend_schema(
        description="Finalize sales order on credit - creates ledger entry and updates customer balance",
        tags=["Sales - Orders"],
        request=None,
        responses={200: SalesOrderSerializer}
    )
    @action(detail=True, methods=['post'])
    def finalize_on_credit(self, request, pk=None):
        """
        Finalize a sales order on credit
        Automatically creates ledger entry and updates customer balance
        """
        sales_order = self.get_object()
        
        try:
            sales_order.finalize_on_credit()
            serializer = self.get_serializer(sales_order)
            return Response({
                'message': 'Sales order finalized on credit successfully',
                'order': serializer.data
            })
        except ValueError as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )
        except Exception as e:
            return Response(
                {'error': f'Failed to finalize order: {str(e)}'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    @extend_schema(
        tags=['Sales - Dashboard'],
        summary='Get sales dashboard data',
        description='Returns comprehensive sales dashboard data including stats, charts, recent orders, top products, and customers',
        parameters=[
            OpenApiParameter(
                name='period',
                description='Time period for revenue chart (today, week, month, year)',
                required=False,
                type=OpenApiTypes.STR,
                default='month'
            )
        ]
    )
    @action(detail=False, methods=['get'], url_path='dashboard')
    def sales_dashboard(self, request):
        """Sales Dashboard API endpoint - Returns dashboard data"""
        # TODO: Fix indentation issues and restore full implementation
        return Response({
            'stats': {
                'revenue': "Rs. 0",
                'revenueChange': 0,
                'orders': 0,
                'ordersChange': 0,
                'customers': 0,
                'customersChange': 0,
                'products': 0,
                'productsChange': 0,
            },
            'revenueData': [],
            'recentOrders': [],
            'topProducts': [],
            'recentCustomers': [],
            'inventorySummary': {
                'inStock': 0,
                'lowStock': 0,
                'outOfStock': 0,
                'totalSKUs': 0
            }
        })


@extend_schema_view(
    list=extend_schema(description="List all quotations for the current tenant", tags=["Sales - Quotations"]),
    retrieve=extend_schema(description="Get quotation details", tags=["Sales - Quotations"]),
    create=extend_schema(description="Create a new quotation", tags=["Sales - Quotations"]),
    update=extend_schema(description="Update quotation", tags=["Sales - Quotations"]),
    partial_update=extend_schema(description="Partially update quotation", tags=["Sales - Quotations"]),
    destroy=extend_schema(description="Delete a quotation", tags=["Sales - Quotations"]),
)
class QuotationViewSet(viewsets.ModelViewSet):
    """ViewSet for Quotation CRUD operations"""
    permission_classes = [IsAuthenticated]
    filterset_fields = ['status', 'customer']
    search_fields = ['quotation_number', 'customer__name']
    ordering_fields = ['date', 'created_at', 'valid_until']
    ordering = ['-date', '-created_at']
    
    def get_serializer_class(self):
        if self.action in ['create', 'update', 'partial_update']:
            return QuotationCreateSerializer
        return QuotationSerializer
    
    def get_queryset(self):
        """Filter by current tenant"""
        return Quotation.objects.select_related('customer', 'created_by').prefetch_related('lines__product')
    
    def perform_create(self, serializer):
        # Generate quotation number
        last_quotation = Quotation.objects.filter(tenant=self.request.user.tenant).order_by('-id').first()
        if last_quotation:
            last_num = int(last_quotation.quotation_number.split('-')[1])
            quotation_number = f"QT-{str(last_num + 1).zfill(4)}"
        else:
            quotation_number = "QT-0001"
        
        serializer.save(
            created_by=self.request.user,
            tenant=self.request.user.tenant,
            quotation_number=quotation_number
        )

    
    @extend_schema(
        description="Convert quotation to sales order",
        tags=["Sales - Quotations"],
        request=None,
        responses={201: SalesOrderSerializer}
    )
    @action(detail=True, methods=['post'])
    def convert_to_order(self, request, pk=None):
        """Convert a quotation to a sales order"""
        quotation = self.get_object()
        
        if quotation.status == 'Expired':
            return Response(
                {'error': 'Cannot convert expired quotation'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Generate order number
        last_order = SalesOrder.objects.filter(tenant=request.user.tenant).order_by('-id').first()
        if last_order:
            last_num = int(last_order.order_number.split('-')[1])
            order_number = f"SO-{str(last_num + 1).zfill(4)}"
        else:
            order_number = "SO-0001"
        
        # Create sales order with line items
        sales_order = SalesOrder.objects.create(
            tenant=request.user.tenant,
            order_number=order_number,
            date=quotation.date,
            customer=quotation.customer,
            reference=f"From {quotation.quotation_number}",
            status='Draft',
            subtotal=quotation.subtotal,
            discount=quotation.discount,
            tax=quotation.tax,
            total=quotation.total,
            notes=quotation.notes,
            created_by=request.user
        )
        
        # Copy line items from quotation to sales order
        for quote_line in quotation.lines.all():
            SalesOrderLine.objects.create(
                tenant=request.user.tenant,
                sales_order=sales_order,
                product=quote_line.product,
                description=quote_line.description,
                quantity=quote_line.quantity,
                unit_price=quote_line.unit_price,
                discount_percent=quote_line.discount_percent,
                tax_percent=quote_line.tax_percent,
                amount=quote_line.amount
            )
        
        quotation.status = 'Accepted'
        quotation.save()
        
        serializer = SalesOrderSerializer(sales_order)
        return Response(serializer.data, status=status.HTTP_201_CREATED)


@extend_schema_view(
    list=extend_schema(description="List all invoices for the current tenant", tags=["Sales - Invoices"]),
    retrieve=extend_schema(description="Get invoice details", tags=["Sales - Invoices"]),
    create=extend_schema(description="Create a new invoice", tags=["Sales - Invoices"]),
    update=extend_schema(description="Update invoice", tags=["Sales - Invoices"]),
    partial_update=extend_schema(description="Partially update invoice", tags=["Sales - Invoices"]),
    destroy=extend_schema(description="Delete an invoice", tags=["Sales - Invoices"]),
)
class InvoiceViewSet(viewsets.ModelViewSet):
    """ViewSet for Invoice CRUD operations"""
    def get_queryset(self):
        """Filter by current tenant"""
        return Invoice.objects.select_related('customer', 'sales_order', 'created_by')
    serializer_class = InvoiceSerializer
    permission_classes = [IsAuthenticated]
    filterset_fields = ['status', 'customer']
    search_fields = ['invoice_number', 'customer__name']
    ordering_fields = ['date', 'due_date', 'created_at', 'amount']
    ordering = ['-date', '-created_at']
    
    def perform_create(self, serializer):
        # Auto-generate invoice number if not provided
        if 'invoice_number' not in serializer.validated_data or not serializer.validated_data.get('invoice_number'):
            last_invoice = Invoice.objects.filter(tenant=self.request.user.tenant).order_by('-id').first()
            if last_invoice and last_invoice.invoice_number.startswith('INV-'):
                try:
                    last_num = int(last_invoice.invoice_number.split('-')[1])
                    invoice_number = f"INV-{str(last_num + 1).zfill(4)}"
                except:
                    invoice_number = "INV-0001"
            else:
                invoice_number = "INV-0001"
            serializer.save(
                tenant=self.request.user.tenant,
                created_by=self.request.user,
                invoice_number=invoice_number
            )
        else:
            serializer.save(tenant=self.request.user.tenant, created_by=self.request.user)

    
    @extend_schema(
        description="Record payment for an invoice",
        tags=["Sales - Invoices"],
        request={'application/json': {'type': 'object', 'properties': {'amount': {'type': 'number'}}}},
        responses={200: InvoiceSerializer}
    )
    @action(detail=True, methods=['post'])
    def record_payment(self, request, pk=None):
        """Record a payment for an invoice"""
        invoice = self.get_object()
        payment_amount = request.data.get('amount')
        
        if not payment_amount:
            return Response(
                {'error': 'Payment amount is required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            payment_amount = float(payment_amount)
        except ValueError:
            return Response(
                {'error': 'Invalid payment amount'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        if payment_amount <= 0:
            return Response(
                {'error': 'Payment amount must be positive'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        if invoice.paid_amount + payment_amount > invoice.amount:
            return Response(
                {'error': 'Payment amount exceeds invoice balance'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        invoice.paid_amount += payment_amount
        
        # Update status based on payment
        if invoice.paid_amount >= invoice.amount:
            invoice.status = 'Paid'
        elif invoice.paid_amount > 0:
            invoice.status = 'Partially Paid'
        
        invoice.save()
        
        serializer = self.get_serializer(invoice)
        return Response(serializer.data)


@extend_schema_view(
    list=extend_schema(description="List all credit notes for the current tenant", tags=["Sales - Credit Notes"]),
    retrieve=extend_schema(description="Get credit note details", tags=["Sales - Credit Notes"]),
    create=extend_schema(description="Create a new credit note", tags=["Sales - Credit Notes"]),
    update=extend_schema(description="Update credit note", tags=["Sales - Credit Notes"]),
    partial_update=extend_schema(description="Partially update credit note", tags=["Sales - Credit Notes"]),
    destroy=extend_schema(description="Delete a credit note", tags=["Sales - Credit Notes"]),
)
class CreditNoteViewSet(viewsets.ModelViewSet):
    """ViewSet for Credit Note CRUD operations"""
    def get_queryset(self):
        """Filter by current tenant"""
        return CreditNote.objects.select_related('customer', 'invoice', 'created_by')
    serializer_class = CreditNoteSerializer
    permission_classes = [IsAuthenticated]
    filterset_fields = ['status', 'customer', 'invoice']
    search_fields = ['credit_note_number', 'customer__name']
    ordering_fields = ['date', 'created_at', 'amount']
    ordering = ['-date', '-created_at']
    
    def perform_create(self, serializer):
        # Auto-generate credit note number if not provided
        if 'credit_note_number' not in serializer.validated_data or not serializer.validated_data.get('credit_note_number'):
            last_credit_note = CreditNote.objects.filter(tenant=self.request.user.tenant).order_by('-id').first()
            if last_credit_note and last_credit_note.credit_note_number.startswith('CN-'):
                try:
                    last_num = int(last_credit_note.credit_note_number.split('-')[1])
                    credit_note_number = f"CN-{str(last_num + 1).zfill(4)}"
                except:
                    credit_note_number = "CN-0001"
            else:
                credit_note_number = "CN-0001"
            serializer.save(
                tenant=self.request.user.tenant,
                created_by=self.request.user,
                credit_note_number=credit_note_number
            )
        else:
            serializer.save(tenant=self.request.user.tenant, created_by=self.request.user)



@extend_schema_view(
    list=extend_schema(tags=['Sales - Ledger'], summary='List customer ledger entries'),
    retrieve=extend_schema(tags=['Sales - Ledger'], summary='Get ledger entry details'),
)
class CustomerLedgerViewSet(viewsets.ReadOnlyModelViewSet):
    """
    ViewSet for Customer Ledger (Read-only)
    Ledger entries are immutable - created automatically by system
    """
    serializer_class = CustomerLedgerSerializer
    permission_classes = [IsAuthenticated]
    filterset_fields = ['customer', 'transaction_type', 'date']
    search_fields = ['customer__name', 'reference_number', 'description']
    ordering_fields = ['date', 'created_at']
    ordering = ['-date', '-created_at']
    
    def get_queryset(self):
        return CustomerLedger.objects.filter(tenant=self.request.user.tenant).select_related('customer')


@extend_schema_view(
    list=extend_schema(tags=['Sales - Payments'], summary='List all payments received'),
    retrieve=extend_schema(tags=['Sales - Payments'], summary='Get payment details'),
    create=extend_schema(tags=['Sales - Payments'], summary='Record payment received'),
    update=extend_schema(tags=['Sales - Payments'], summary='Update payment'),
    partial_update=extend_schema(tags=['Sales - Payments'], summary='Partially update payment'),
    destroy=extend_schema(tags=['Sales - Payments'], summary='Delete payment'),
)
class PaymentReceivedViewSet(viewsets.ModelViewSet):
    """
    ViewSet for Payment Received
    Automatically creates ledger entry and updates customer balance
    """
    serializer_class = PaymentReceivedSerializer
    permission_classes = [IsAuthenticated]
    filterset_fields = ['customer', 'payment_method', 'date', 'invoice']
    search_fields = ['payment_number', 'customer__name', 'reference_number']
    ordering_fields = ['date', 'amount', 'created_at']
    ordering = ['-date', '-created_at']
    
    def get_queryset(self):
        return PaymentReceived.objects.filter(tenant=self.request.user.tenant).select_related(
            'customer', 'invoice', 'received_by'
        )
    
    def perform_create(self, serializer):
        serializer.save(tenant=self.request.user.tenant)



