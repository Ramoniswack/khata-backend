from django.contrib import admin
from .models import (
    Customer, SalesOrder, SalesOrderLine, Quotation, QuotationLine, Invoice, CreditNote,
    CustomerLedger, PaymentReceived
)


@admin.register(Customer)
class CustomerAdmin(admin.ModelAdmin):
    list_display = ['name', 'phone', 'email', 'type', 'status', 'credit_limit', 'current_balance', 'created_at']
    list_filter = ['status', 'type', 'payment_terms']
    search_fields = ['name', 'phone', 'email', 'pan']
    ordering = ['-created_at']
    readonly_fields = ['current_balance']


class SalesOrderLineInline(admin.TabularInline):
    model = SalesOrderLine
    extra = 1
    fields = ['product', 'description', 'quantity', 'unit_price', 'discount_percent', 'tax_percent', 'amount']
    readonly_fields = ['amount']


@admin.register(SalesOrder)
class SalesOrderAdmin(admin.ModelAdmin):
    list_display = ['order_number', 'date', 'customer', 'payment_type', 'status', 'total', 'created_at']
    list_filter = ['status', 'payment_type', 'date']
    search_fields = ['order_number', 'customer__name', 'reference']
    ordering = ['-date', '-created_at']
    inlines = [SalesOrderLineInline]


class QuotationLineInline(admin.TabularInline):
    model = QuotationLine
    extra = 1
    fields = ['product', 'description', 'quantity', 'unit_price', 'discount_percent', 'tax_percent', 'amount']
    readonly_fields = ['amount']


@admin.register(Quotation)
class QuotationAdmin(admin.ModelAdmin):
    list_display = ['quotation_number', 'date', 'customer', 'valid_until', 'total', 'status', 'created_at']
    list_filter = ['status', 'date']
    search_fields = ['quotation_number', 'customer__name']
    ordering = ['-date', '-created_at']
    inlines = [QuotationLineInline]


@admin.register(Invoice)
class InvoiceAdmin(admin.ModelAdmin):
    list_display = ['invoice_number', 'date', 'due_date', 'customer', 'amount', 'paid_amount', 'status', 'created_at']
    list_filter = ['status', 'date']
    search_fields = ['invoice_number', 'customer__name']
    ordering = ['-date', '-created_at']


@admin.register(CreditNote)
class CreditNoteAdmin(admin.ModelAdmin):
    list_display = ['credit_note_number', 'date', 'customer', 'invoice', 'amount', 'status', 'created_at']
    list_filter = ['status', 'date']
    search_fields = ['credit_note_number', 'customer__name']
    ordering = ['-date', '-created_at']



@admin.register(CustomerLedger)
class CustomerLedgerAdmin(admin.ModelAdmin):
    list_display = ['customer', 'date', 'transaction_type', 'reference_number', 'debit_amount', 'credit_amount', 'running_balance', 'tenant']
    list_filter = ['transaction_type', 'date', 'tenant']
    search_fields = ['customer__name', 'reference_number', 'description']
    ordering = ['-date', '-created_at']
    readonly_fields = ['running_balance', 'created_at']
    
    def has_add_permission(self, request):
        # Ledger entries are created automatically
        return False
    
    def has_delete_permission(self, request, obj=None):
        # Ledger entries are immutable
        return False


@admin.register(PaymentReceived)
class PaymentReceivedAdmin(admin.ModelAdmin):
    list_display = ['payment_number', 'customer', 'date', 'amount', 'payment_method', 'received_by', 'tenant']
    list_filter = ['payment_method', 'date', 'tenant']
    search_fields = ['payment_number', 'customer__name', 'reference_number']
    ordering = ['-date', '-created_at']
    readonly_fields = ['payment_number', 'received_by', 'created_at', 'updated_at']
