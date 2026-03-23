from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from drf_spectacular.utils import extend_schema, OpenApiParameter
from .models import Tenant
from .serializers import TenantSerializer, TenantProfileSerializer, TenantCreateSerializer


class TenantViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing tenants
    """
    def get_queryset(self):
        """Filter tenants - authenticated users see all tenants they created"""
        if self.request.user.is_authenticated:
            # Return all tenants created by this user
            return Tenant.objects.filter(created_by=self.request.user)
        # For unauthenticated users (for create action), return none
        return Tenant.objects.none()
    serializer_class = TenantSerializer
    permission_classes = [IsAuthenticated]
    lookup_field = 'slug'
    
    def get_permissions(self):
        """Allow unauthenticated access to create action only"""
        if self.action == 'create':
            return [AllowAny()]
        return super().get_permissions()
    
    def get_serializer_class(self):
        """Use different serializer for create action"""
        if self.action == 'create':
            return TenantCreateSerializer
        return super().get_serializer_class()
    
    def perform_create(self, serializer):
        """Associate the created tenant with the current user if authenticated"""
        # Save tenant with created_by field
        tenant = serializer.save(created_by=self.request.user if self.request.user.is_authenticated else None)
        
        # If user is authenticated, assign this tenant as their active tenant
        if self.request.user.is_authenticated:
            self.request.user.tenant = tenant
            # Make them admin of their organization if they don't have a role yet
            if not self.request.user.role or self.request.user.role == 'viewer':
                self.request.user.role = 'admin'
            self.request.user.save()
        
        return tenant
    
    @extend_schema(
        summary='Get tenant profile by slug',
        description='Retrieve tenant profile information using the tenant slug. This endpoint is used for workspace routing.',
        parameters=[
            OpenApiParameter(
                name='slug',
                description='Tenant slug',
                required=True,
                type=str,
                location=OpenApiParameter.QUERY
            )
        ],
        responses={200: TenantProfileSerializer}
    )
    @action(detail=False, methods=['get'], permission_classes=[IsAuthenticated])
    def profile(self, request):
        """Get tenant profile by slug"""
        slug = request.query_params.get('slug')
        
        if not slug:
            return Response(
                {'error': 'Slug parameter is required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            tenant = Tenant.objects.get(slug=slug, is_active=True)
        except Tenant.DoesNotExist:
            return Response(
                {'error': 'Tenant not found'},
                status=status.HTTP_404_NOT_FOUND
            )
        
        # Verify user has access to this tenant
        if request.user.tenant != tenant:
            return Response(
                {'error': 'You do not have access to this workspace'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        serializer = TenantProfileSerializer(tenant)
        return Response(serializer.data)
    
    @extend_schema(
        summary='Activate a module for tenant',
        description='Activate a specific module for the tenant',
    )
    @action(detail=True, methods=['post'])
    def activate_module(self, request, slug=None):
        """Activate a module for this tenant"""
        tenant = self.get_object()
        module_name = request.data.get('module_name')
        
        if not module_name:
            return Response(
                {'error': 'module_name is required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        tenant.activate_module(module_name)
        serializer = self.get_serializer(tenant)
        return Response(serializer.data)
    
    @extend_schema(
        summary='Deactivate a module for tenant',
        description='Deactivate a specific module for the tenant',
    )
    @action(detail=True, methods=['post'])
    def deactivate_module(self, request, slug=None):
        """Deactivate a module for this tenant"""
        tenant = self.get_object()
        module_name = request.data.get('module_name')
        
        if not module_name:
            return Response(
                {'error': 'module_name is required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        tenant.deactivate_module(module_name)
        serializer = self.get_serializer(tenant)
        return Response(serializer.data)
