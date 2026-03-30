"""
POS URL Configuration
"""

from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    POSDiscountViewSet,
    POSTransactionViewSet,
    POSDailySalesReportViewSet,
    POSProductSearchViewSet
)

router = DefaultRouter()
router.register(r'discounts', POSDiscountViewSet, basename='pos-discount')
router.register(r'transactions', POSTransactionViewSet, basename='pos-transaction')
router.register(r'reports', POSDailySalesReportViewSet, basename='pos-report')
router.register(r'products', POSProductSearchViewSet, basename='pos-product')

urlpatterns = [
    path('', include(router.urls)),
]
