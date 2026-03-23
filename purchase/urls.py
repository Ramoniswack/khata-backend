from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    SupplierViewSet, PurchaseRequestViewSet, PurchaseOrderViewSet,
    PurchaseInvoiceViewSet, DebitNoteViewSet
)

router = DefaultRouter()
router.register(r'suppliers', SupplierViewSet, basename='supplier')
router.register(r'requests', PurchaseRequestViewSet, basename='purchaserequest')
router.register(r'orders', PurchaseOrderViewSet, basename='purchaseorder')
router.register(r'invoices', PurchaseInvoiceViewSet, basename='purchaseinvoice')
router.register(r'debit-notes', DebitNoteViewSet, basename='debitnote')

urlpatterns = [
    path('', include(router.urls)),
]
