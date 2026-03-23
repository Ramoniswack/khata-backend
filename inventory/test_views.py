from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from .models import Product, Category, UnitOfMeasure
import traceback


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def test_create_product(request):
    """
    Test endpoint to create a product with detailed error logging
    """
    try:
        data = request.data
        print(f"\n=== TEST CREATE PRODUCT ===")
        print(f"User: {request.user.username}")
        print(f"Tenant: {request.user.tenant.name}")
        print(f"Data received: {data}")
        
        # Get category and unit
        category_id = data.get('category')
        unit_id = data.get('unit')
        
        category = None
        if category_id:
            category = Category.objects.get(id=category_id, tenant=request.user.tenant)
            print(f"Category: {category.name}")
        
        unit = UnitOfMeasure.objects.get(id=unit_id, tenant=request.user.tenant)
        print(f"Unit: {unit.name}")
        
        # Create product
        product = Product.objects.create(
            tenant=request.user.tenant,
            name=data['name'],
            sku=data['sku'],
            description=data.get('description', ''),
            category=category,
            unit=unit,
            cost_price=data['cost_price'],
            selling_price=data['selling_price'],
            reorder_level=data.get('reorder_level', 0),
            status=data.get('status', 'active')
        )
        
        print(f"Product created: {product.id}")
        
        return Response({
            'id': product.id,
            'name': product.name,
            'sku': product.sku,
            'message': 'Product created successfully'
        }, status=status.HTTP_201_CREATED)
        
    except Exception as e:
        error_trace = traceback.format_exc()
        print(f"\n=== ERROR ===")
        print(f"Error: {str(e)}")
        print(f"Traceback:\n{error_trace}")
        
        return Response({
            'error': str(e),
            'traceback': error_trace,
            'data_received': request.data
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
