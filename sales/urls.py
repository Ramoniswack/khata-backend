from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    CustomerViewSet, SalesOrderViewSet, QuotationViewSet,
    InvoiceViewSet, CreditNoteViewSet, CustomerLedgerViewSet, PaymentReceivedViewSet
)

router = DefaultRouter()
router.register(r'customers', CustomerViewSet, basename='customer')
router.register(r'orders', SalesOrderViewSet, basename='salesorder')
router.register(r'quotations', QuotationViewSet, basename='quotation')
router.register(r'invoices', InvoiceViewSet, basename='invoice')
router.register(r'credit-notes', CreditNoteViewSet, basename='creditnote')
router.register(r'ledger', CustomerLedgerViewSet, basename='customer-ledger')
router.register(r'payments', PaymentReceivedViewSet, basename='payment-received')

urlpatterns = [
    path('', include(router.urls)),
]
