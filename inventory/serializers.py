from rest_framework import serializers
from .models import Category, UnitOfMeasure, Warehouse, Product, Stock, StockMovement


class CategorySerializer(serializers.ModelSerializer):
    parent_name = serializers.CharField(source='parent.name', read_only=True)
    children_count = serializers.SerializerMethodField()
    
    class Meta:
        model = Category
        fields = [
            'id', 'name', 'parent', 'parent_name', 'description',
            'children_count', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']
    
    def get_children_count(self, obj):
        return obj.children.count()


class UnitOfMeasureSerializer(serializers.ModelSerializer):
    class Meta:
        model = UnitOfMeasure
        fields = [
            'id', 'name', 'abbreviation', 'type',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']


class WarehouseSerializer(serializers.ModelSerializer):
    manager_name = serializers.CharField(source='manager.get_full_name', read_only=True)
    total_products = serializers.SerializerMethodField()
    
    class Meta:
        model = Warehouse
        fields = [
            'id', 'name', 'location', 'manager', 'manager_name',
            'is_active', 'total_products', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']
    
    def get_total_products(self, obj):
        return obj.stocks.filter(quantity__gt=0).count()


class ProductListSerializer(serializers.ModelSerializer):
    """Lightweight serializer for product lists"""
    category_name = serializers.CharField(source='category.name', read_only=True)
    unit_name = serializers.CharField(source='unit.abbreviation', read_only=True)
    total_stock = serializers.SerializerMethodField()
    
    class Meta:
        model = Product
        fields = [
            'id', 'name', 'sku', 'category_name', 'unit_name',
            'cost_price', 'selling_price', 'total_stock',
            'reorder_level', 'status'
        ]
    
    def get_total_stock(self, obj):
        return obj.get_total_stock()


class ProductDetailSerializer(serializers.ModelSerializer):
    """Detailed serializer for single product view"""
    category_name = serializers.CharField(source='category.name', read_only=True)
    unit_name = serializers.CharField(source='unit.name', read_only=True)
    total_stock = serializers.SerializerMethodField()
    stock_by_warehouse = serializers.SerializerMethodField()
    
    class Meta:
        model = Product
        fields = [
            'id', 'name', 'sku', 'description', 'category', 'category_name',
            'unit', 'unit_name', 'cost_price', 'selling_price',
            'reorder_level', 'status', 'total_stock', 'stock_by_warehouse',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']
    
    def create(self, validated_data):
        """Override create to add logging"""
        import logging
        logger = logging.getLogger(__name__)
        
        try:
            logger.info(f"Creating product with data: {validated_data}")
            product = super().create(validated_data)
            logger.info(f"Product created successfully: {product.id}")
            return product
        except Exception as e:
            logger.error(f"Error creating product: {str(e)}")
            logger.error(f"Validated data: {validated_data}")
            raise
    
    def get_total_stock(self, obj):
        return obj.get_total_stock()
    
    def get_stock_by_warehouse(self, obj):
        stocks = obj.stocks.select_related('warehouse').all()
        return [
            {
                'warehouse_id': stock.warehouse.id,
                'warehouse_name': stock.warehouse.name,
                'quantity': stock.quantity
            }
            for stock in stocks
        ]


class StockSerializer(serializers.ModelSerializer):
    product_name = serializers.CharField(source='product.name', read_only=True)
    product_sku = serializers.CharField(source='product.sku', read_only=True)
    warehouse_name = serializers.CharField(source='warehouse.name', read_only=True)
    unit = serializers.CharField(source='product.unit.abbreviation', read_only=True)
    
    class Meta:
        model = Stock
        fields = [
            'id', 'product', 'product_name', 'product_sku',
            'warehouse', 'warehouse_name', 'quantity', 'unit',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']


class StockMovementSerializer(serializers.ModelSerializer):
    product_name = serializers.CharField(source='product.name', read_only=True)
    warehouse_name = serializers.CharField(source='warehouse.name', read_only=True)
    from_warehouse_name = serializers.CharField(source='from_warehouse.name', read_only=True)
    to_warehouse_name = serializers.CharField(source='to_warehouse.name', read_only=True)
    performed_by_name = serializers.CharField(source='performed_by.get_full_name', read_only=True)
    
    class Meta:
        model = StockMovement
        fields = [
            'id', 'product', 'product_name', 'warehouse', 'warehouse_name',
            'movement_type', 'quantity', 'from_warehouse', 'from_warehouse_name',
            'to_warehouse', 'to_warehouse_name', 'reference_type', 'reference_id',
            'reason', 'notes', 'performed_by', 'performed_by_name', 'created_at'
        ]
        read_only_fields = ['id', 'created_at']


class StockAdjustmentSerializer(serializers.Serializer):
    """Serializer for stock adjustment operations"""
    product = serializers.IntegerField()
    warehouse = serializers.IntegerField()
    quantity = serializers.DecimalField(max_digits=12, decimal_places=2)
    reason = serializers.CharField()
    notes = serializers.CharField(required=False, allow_blank=True)


class StockTransferSerializer(serializers.Serializer):
    """Serializer for stock transfer operations"""
    product = serializers.IntegerField()
    from_warehouse = serializers.IntegerField()
    to_warehouse = serializers.IntegerField()
    quantity = serializers.DecimalField(max_digits=12, decimal_places=2)
    notes = serializers.CharField(required=False, allow_blank=True)
