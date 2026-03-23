from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.db import transaction
from django.db.models import Q, Sum, F
from drf_spectacular.utils import extend_schema, extend_schema_view, OpenApiParameter, OpenApiExample
from drf_spectacular.types import OpenApiTypes
from .models import Category, UnitOfMeasure, Warehouse, Product, Stock, StockMovement
from .serializers import (
    CategorySerializer, UnitOfMeasureSerializer, WarehouseSerializer,
    ProductListSerializer, ProductDetailSerializer, StockSerializer,
    StockMovementSerializer, StockAdjustmentSerializer, StockTransferSerializer
)
from .permissions import IsAdminOrReadOnly, IsSupervisorOrAdmin


@extend_schema_view(
    list=extend_schema(
        tags=['Inventory - Categories'],
        summary='List all categories',
        description='Get a paginated list of all product categories for the current tenant.',
    ),
    retrieve=extend_schema(
        tags=['Inventory - Categories'],
        summary='Get category details',
        description='Retrieve detailed information about a specific category.',
    ),
    create=extend_schema(
        tags=['Inventory - Categories'],
        summary='Create a new category',
        description='Create a new product category. Categories can be hierarchical.',
    ),
    update=extend_schema(
        tags=['Inventory - Categories'],
        summary='Update category',
        description='Update an existing category.',
    ),
    partial_update=extend_schema(
        tags=['Inventory - Categories'],
        summary='Partially update category',
        description='Partially update an existing category.',
    ),
    destroy=extend_schema(
        tags=['Inventory - Categories'],
        summary='Delete category',
        description='Delete a category. Cannot delete if it has child categories or products.',
    ),
)
class CategoryViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing product categories.
    Supports hierarchical categories.
    """
    serializer_class = CategorySerializer
    permission_classes = [IsAuthenticated]
    filterset_fields = ['parent']
    search_fields = ['name', 'description']
    ordering_fields = ['name', 'created_at']
    
    def get_queryset(self):
        """Filter categories by current tenant"""
        return Category.objects.all()
    
    def perform_create(self, serializer):
        """Ensure tenant is set when creating category"""
        serializer.save(tenant=self.request.user.tenant)
    
    @extend_schema(
        tags=['Inventory - Categories'],
        summary='Get category tree',
        description='Get all root categories with their hierarchical structure.',
    )
    @action(detail=False, methods=['get'])
    def tree(self, request):
        """Get categories in tree structure"""
        root_categories = self.get_queryset().filter(parent__isnull=True)
        serializer = self.get_serializer(root_categories, many=True)
        return Response(serializer.data)


@extend_schema_view(
    list=extend_schema(
        tags=['Inventory - Units'],
        summary='List all units of measure',
    ),
    retrieve=extend_schema(
        tags=['Inventory - Units'],
        summary='Get unit details',
    ),
    create=extend_schema(
        tags=['Inventory - Units'],
        summary='Create a new unit',
    ),
    update=extend_schema(
        tags=['Inventory - Units'],
        summary='Update unit',
    ),
    destroy=extend_schema(
        tags=['Inventory - Units'],
        summary='Delete unit',
    ),
)
class UnitOfMeasureViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing units of measure.
    """
    serializer_class = UnitOfMeasureSerializer
    permission_classes = [IsAuthenticated]
    filterset_fields = ['type']
    search_fields = ['name', 'abbreviation']
    ordering_fields = ['name', 'type']
    
    def get_queryset(self):
        """Filter units by current tenant"""
        return UnitOfMeasure.objects.all()
    
    def perform_create(self, serializer):
        """Ensure tenant is set when creating unit"""
        serializer.save(tenant=self.request.user.tenant)


@extend_schema_view(
    list=extend_schema(
        tags=['Inventory - Warehouses'],
        summary='List all warehouses',
    ),
    retrieve=extend_schema(
        tags=['Inventory - Warehouses'],
        summary='Get warehouse details',
    ),
    create=extend_schema(
        tags=['Inventory - Warehouses'],
        summary='Create a new warehouse',
    ),
    update=extend_schema(
        tags=['Inventory - Warehouses'],
        summary='Update warehouse',
    ),
    destroy=extend_schema(
        tags=['Inventory - Warehouses'],
        summary='Delete warehouse',
    ),
)
class WarehouseViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing warehouses/storage locations.
    """
    serializer_class = WarehouseSerializer
    permission_classes = [IsAuthenticated]
    filterset_fields = ['is_active', 'manager']
    search_fields = ['name', 'location']
    ordering_fields = ['name', 'created_at']
    
    def get_queryset(self):
        """Filter warehouses by current tenant"""
        return Warehouse.objects.all()
    
    def perform_create(self, serializer):
        """Ensure tenant is set when creating warehouse"""
        serializer.save(tenant=self.request.user.tenant)

    @extend_schema(
        tags=['Inventory - Warehouses'],
        summary='Get warehouse stock summary',
        description='Get all products with stock in this warehouse.',
    )
    @action(detail=True, methods=['get'])
    def stock_summary(self, request, pk=None):
        """Get stock summary for a warehouse"""
        warehouse = self.get_object()
        stocks = warehouse.stocks.select_related('product', 'product__unit').filter(quantity__gt=0)
        serializer = StockSerializer(stocks, many=True)
        return Response(serializer.data)


@extend_schema_view(
    list=extend_schema(
        tags=['Inventory - Products'],
        summary='List all products',
        description='Get a paginated list of all products with basic information.',
    ),
    retrieve=extend_schema(
        tags=['Inventory - Products'],
        summary='Get product details',
        description='Get detailed information about a product including stock levels by warehouse.',
    ),
    create=extend_schema(
        tags=['Inventory - Products'],
        summary='Create a new product',
    ),
    update=extend_schema(
        tags=['Inventory - Products'],
        summary='Update product',
    ),
    destroy=extend_schema(
        tags=['Inventory - Products'],
        summary='Delete product',
    ),
)
class ProductViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing products.
    RBAC: Only ADMIN users can delete products.
    """
    permission_classes = [IsAdminOrReadOnly]
    filterset_fields = ['category', 'status']
    search_fields = ['name', 'sku', 'description']
    ordering_fields = ['name', 'sku', 'created_at']
    
    def get_queryset(self):
        """Filter products by current tenant"""
        return Product.objects.select_related('category', 'unit').all()
    
    def get_serializer_class(self):
        if self.action == 'list':
            return ProductListSerializer
        return ProductDetailSerializer
    
    def create(self, request, *args, **kwargs):
        """Override create with tenant-aware validation"""
        import logging
        logger = logging.getLogger(__name__)
        
        try:
            logger.info(f"Creating product - User: {request.user.username}, Tenant: {request.user.tenant.name if request.user.tenant else 'None'}")
            logger.info(f"Request data: {request.data}")
            
            # The TenantManager automatically filters by current tenant,
            # so we just need to check if the category/unit exists
            category_id = request.data.get('category')
            unit_id = request.data.get('unit')
            
            if category_id:
                try:
                    from .models import Category
                    # This will raise DoesNotExist if category doesn't belong to current tenant
                    category = Category.objects.get(id=category_id)
                    logger.info(f"Category validated: {category.name} (ID: {category.id})")
                except Category.DoesNotExist:
                    logger.error(f"Category ID {category_id} not found for current tenant")
                    return Response(
                        {'category': ['Category not found. Please select a valid category.']},
                        status=status.HTTP_400_BAD_REQUEST
                    )
            
            if unit_id:
                try:
                    from .models import UnitOfMeasure
                    # This will raise DoesNotExist if unit doesn't belong to current tenant
                    unit = UnitOfMeasure.objects.get(id=unit_id)
                    logger.info(f"Unit validated: {unit.name} (ID: {unit.id})")
                except UnitOfMeasure.DoesNotExist:
                    logger.error(f"Unit ID {unit_id} not found for current tenant")
                    return Response(
                        {'unit': ['Unit not found. Please select a valid unit.']},
                        status=status.HTTP_400_BAD_REQUEST
                    )
            
            return super().create(request, *args, **kwargs)
            
        except Exception as e:
            logger.error(f"Error creating product: {str(e)}", exc_info=True)
            return Response(
                {
                    'detail': str(e),
                    'error_type': type(e).__name__
                },
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    def perform_create(self, serializer):
        """Ensure tenant is set when creating product"""
        serializer.save(tenant=self.request.user.tenant)
    
    @extend_schema(
        tags=['Inventory - Products'],
        summary='Get low stock products',
        description='Get all products where total stock is below the reorder level.',
    )
    @action(detail=False, methods=['get'])
    def low_stock(self, request):
        """Get products with stock below reorder level"""
        products = self.get_queryset().annotate(
            total_stock=Sum('stocks__quantity')
        ).filter(
            Q(total_stock__lt=F('reorder_level')) | Q(total_stock__isnull=True)
        )
        serializer = ProductListSerializer(products, many=True)
        return Response(serializer.data)
    
    @extend_schema(
        tags=['Inventory - Products'],
        summary='Get product stock history',
        description='Get the last 50 stock movements for this product.',
    )
    @action(detail=True, methods=['get'])
    def stock_history(self, request, pk=None):
        """Get stock movement history for a product"""
        product = self.get_object()
        movements = product.movements.select_related(
            'warehouse', 'from_warehouse', 'to_warehouse', 'performed_by'
        ).all()[:50]
        serializer = StockMovementSerializer(movements, many=True)
        return Response(serializer.data)


@extend_schema_view(
    list=extend_schema(
        tags=['Inventory - Stocks'],
        summary='List all stock levels',
        description='View current stock levels across all warehouses. Stock cannot be edited directly - use stock operations.',
    ),
    retrieve=extend_schema(
        tags=['Inventory - Stocks'],
        summary='Get stock details',
    ),
)
class StockViewSet(viewsets.ModelViewSet):
    """
    ViewSet for viewing stock levels.
    Stock is updated through stock operations, not direct editing.
    """
    serializer_class = StockSerializer
    permission_classes = [IsAuthenticated]
    filterset_fields = ['product', 'warehouse']
    search_fields = ['product__name', 'product__sku', 'warehouse__name']
    ordering_fields = ['quantity', 'created_at']
    
    def get_queryset(self):
        """Filter stocks by current tenant"""
        return Stock.objects.select_related('product', 'warehouse', 'product__unit').all()
    
    # Disable create, update, delete - stock is managed through operations
    http_method_names = ['get', 'head', 'options']


@extend_schema_view(
    list=extend_schema(
        tags=['Inventory - Movements'],
        summary='List all stock movements',
        description='View immutable audit trail of all stock movements.',
    ),
    retrieve=extend_schema(
        tags=['Inventory - Movements'],
        summary='Get movement details',
    ),
)
class StockMovementViewSet(viewsets.ReadOnlyModelViewSet):
    """
    ViewSet for viewing stock movement history.
    Movements are immutable - created through stock operations only.
    """
    serializer_class = StockMovementSerializer
    permission_classes = [IsAuthenticated]
    filterset_fields = ['product', 'warehouse', 'movement_type']
    search_fields = ['product__name', 'product__sku', 'reason']
    ordering_fields = ['created_at']
    
    def get_queryset(self):
        """Filter movements by current tenant"""
        return StockMovement.objects.select_related(
            'product', 'warehouse', 'from_warehouse', 'to_warehouse', 'performed_by'
        ).all()


@extend_schema(tags=['Inventory - Operations'])
class StockOperationsViewSet(viewsets.ViewSet):
    """
    ViewSet for stock operations: in, out, transfer, adjustment.
    RBAC: Only SUPERVISOR or ADMIN users can create stock movements.
    """
    permission_classes = [IsSupervisorOrAdmin]
    
    @extend_schema(
        summary='Add stock to warehouse',
        description='Increase stock quantity in a warehouse. Creates a stock movement record.',
        request=StockAdjustmentSerializer,
        responses={201: {'description': 'Stock added successfully'}},
    )
    @action(detail=False, methods=['post'])
    def stock_in(self, request):
        """Add stock to warehouse"""
        serializer = StockAdjustmentSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        with transaction.atomic():
            product = Product.objects.get(id=serializer.validated_data['product'])
            warehouse = Warehouse.objects.get(id=serializer.validated_data['warehouse'])
            quantity = serializer.validated_data['quantity']
            
            # Update or create stock
            stock, created = Stock.objects.get_or_create(
                product=product,
                warehouse=warehouse,
                defaults={'quantity': 0}
            )
            stock.quantity += quantity
            stock.save()
            
            # Create movement record
            StockMovement.objects.create(
                product=product,
                warehouse=warehouse,
                movement_type='in',
                quantity=quantity,
                reason=serializer.validated_data['reason'],
                notes=serializer.validated_data.get('notes', ''),
                performed_by=request.user
            )
        
        return Response({'message': 'Stock added successfully'}, status=status.HTTP_201_CREATED)
    
    @extend_schema(
        summary='Remove stock from warehouse',
        description='Decrease stock quantity in a warehouse. Validates sufficient stock is available.',
        request=StockAdjustmentSerializer,
        responses={
            200: {'description': 'Stock removed successfully'},
            400: {'description': 'Insufficient stock or validation error'}
        },
    )
    @action(detail=False, methods=['post'])
    def stock_out(self, request):
        """Remove stock from warehouse"""
        serializer = StockAdjustmentSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        with transaction.atomic():
            product = Product.objects.get(id=serializer.validated_data['product'])
            warehouse = Warehouse.objects.get(id=serializer.validated_data['warehouse'])
            quantity = serializer.validated_data['quantity']
            
            # Get stock
            try:
                stock = Stock.objects.get(product=product, warehouse=warehouse)
            except Stock.DoesNotExist:
                return Response(
                    {'error': 'No stock available for this product in this warehouse'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            if stock.quantity < quantity:
                return Response(
                    {'error': f'Insufficient stock. Available: {stock.quantity}'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            stock.quantity -= quantity
            stock.save()
            
            # Create movement record
            StockMovement.objects.create(
                product=product,
                warehouse=warehouse,
                movement_type='out',
                quantity=quantity,
                reason=serializer.validated_data['reason'],
                notes=serializer.validated_data.get('notes', ''),
                performed_by=request.user
            )
        
        return Response({'message': 'Stock removed successfully'})

    @extend_schema(
        summary='Transfer stock between warehouses',
        description='Move stock from one warehouse to another. Validates sufficient stock in source warehouse.',
        request=StockTransferSerializer,
        responses={
            200: {'description': 'Stock transferred successfully'},
            400: {'description': 'Insufficient stock or validation error'}
        },
    )
    @action(detail=False, methods=['post'])
    def transfer(self, request):
        """Transfer stock between warehouses"""
        serializer = StockTransferSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        with transaction.atomic():
            product = Product.objects.get(id=serializer.validated_data['product'])
            from_warehouse = Warehouse.objects.get(id=serializer.validated_data['from_warehouse'])
            to_warehouse = Warehouse.objects.get(id=serializer.validated_data['to_warehouse'])
            quantity = serializer.validated_data['quantity']
            
            # Check source stock
            try:
                from_stock = Stock.objects.get(product=product, warehouse=from_warehouse)
            except Stock.DoesNotExist:
                return Response(
                    {'error': 'No stock available in source warehouse'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            if from_stock.quantity < quantity:
                return Response(
                    {'error': f'Insufficient stock. Available: {from_stock.quantity}'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            # Deduct from source
            from_stock.quantity -= quantity
            from_stock.save()
            
            # Add to destination
            to_stock, created = Stock.objects.get_or_create(
                product=product,
                warehouse=to_warehouse,
                defaults={'quantity': 0}
            )
            to_stock.quantity += quantity
            to_stock.save()
            
            # Create movement record
            StockMovement.objects.create(
                product=product,
                warehouse=from_warehouse,
                movement_type='transfer',
                quantity=quantity,
                from_warehouse=from_warehouse,
                to_warehouse=to_warehouse,
                notes=serializer.validated_data.get('notes', ''),
                performed_by=request.user
            )
        
        return Response({'message': 'Stock transferred successfully'})
    
    @extend_schema(
        summary='Adjust stock (correction)',
        description='Make a correction to stock levels. Can be positive or negative. Requires a reason.',
        request=StockAdjustmentSerializer,
        responses={
            200: {'description': 'Stock adjusted successfully'},
            400: {'description': 'Adjustment would result in negative stock'}
        },
    )
    @action(detail=False, methods=['post'])
    def adjustment(self, request):
        """Adjust stock (correction entry)"""
        serializer = StockAdjustmentSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        with transaction.atomic():
            product = Product.objects.get(id=serializer.validated_data['product'])
            warehouse = Warehouse.objects.get(id=serializer.validated_data['warehouse'])
            quantity = serializer.validated_data['quantity']
            
            # Get or create stock
            stock, created = Stock.objects.get_or_create(
                product=product,
                warehouse=warehouse,
                defaults={'quantity': 0}
            )
            
            # Adjustment can be positive or negative
            stock.quantity += quantity
            if stock.quantity < 0:
                return Response(
                    {'error': 'Adjustment would result in negative stock'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            stock.save()
            
            # Create movement record
            StockMovement.objects.create(
                product=product,
                warehouse=warehouse,
                movement_type='adjustment',
                quantity=quantity,
                reason=serializer.validated_data['reason'],
                notes=serializer.validated_data.get('notes', ''),
                performed_by=request.user
            )
        
        return Response({'message': 'Stock adjusted successfully'})
