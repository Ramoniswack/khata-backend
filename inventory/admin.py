from django.contrib import admin
from .models import Category, UnitOfMeasure, Warehouse, Product, Stock, StockMovement


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'parent', 'tenant', 'created_at']
    list_filter = ['tenant', 'parent']
    search_fields = ['name', 'description']


@admin.register(UnitOfMeasure)
class UnitOfMeasureAdmin(admin.ModelAdmin):
    list_display = ['name', 'abbreviation', 'type', 'tenant']
    list_filter = ['type', 'tenant']
    search_fields = ['name', 'abbreviation']


@admin.register(Warehouse)
class WarehouseAdmin(admin.ModelAdmin):
    list_display = ['name', 'location', 'manager', 'is_active', 'tenant']
    list_filter = ['is_active', 'tenant']
    search_fields = ['name', 'location']


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ['name', 'sku', 'category', 'cost_price', 'selling_price', 'status', 'tenant']
    list_filter = ['status', 'category', 'tenant']
    search_fields = ['name', 'sku', 'description']


@admin.register(Stock)
class StockAdmin(admin.ModelAdmin):
    list_display = ['product', 'warehouse', 'quantity', 'tenant']
    list_filter = ['warehouse', 'tenant']
    search_fields = ['product__name', 'product__sku']


@admin.register(StockMovement)
class StockMovementAdmin(admin.ModelAdmin):
    list_display = ['product', 'warehouse', 'movement_type', 'quantity', 'performed_by', 'created_at']
    list_filter = ['movement_type', 'warehouse', 'created_at']
    search_fields = ['product__name', 'reason']
    readonly_fields = ['created_at']
