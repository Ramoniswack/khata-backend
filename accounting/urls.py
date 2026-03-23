from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    AccountViewSet, JournalEntryViewSet, BankAccountViewSet,
    BankTransactionViewSet, TaxRuleViewSet, VATReturnViewSet
)

router = DefaultRouter()
router.register(r'accounts', AccountViewSet, basename='account')
router.register(r'journal-entries', JournalEntryViewSet, basename='journal-entry')
router.register(r'bank-accounts', BankAccountViewSet, basename='bank-account')
router.register(r'bank-transactions', BankTransactionViewSet, basename='bank-transaction')
router.register(r'tax-rules', TaxRuleViewSet, basename='tax-rule')
router.register(r'vat-returns', VATReturnViewSet, basename='vat-return')

urlpatterns = [
    path('', include(router.urls)),
]
