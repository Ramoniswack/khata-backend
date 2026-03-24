from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    CategoryViewSet, UnitOfMeasureViewSet, WarehouseViewSet,
    ProductViewSet, StockViewSet, StockMovementViewSet, StockOperationsViewSet
)

router = DefaultRouter()
router.register(r'categories', CategoryViewSet, basename='category')
router.register(r'units', UnitOfMeasureViewSet, basename='unit')
router.register(r'warehouses', WarehouseViewSet, basename='warehouse')
router.register(r'products', ProductViewSet, basename='product')
router.register(r'stocks', StockViewSet, basename='stock')
router.register(r'movements', StockMovementViewSet, basename='movement')
router.register(r'operations', StockOperationsViewSet, basename='operations')

urlpatterns = [
    path('', include(router.urls)),
]
