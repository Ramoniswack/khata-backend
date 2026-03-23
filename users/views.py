from rest_framework import generics, permissions, viewsets, status
from rest_framework.response import Response
from rest_framework_simplejwt.views import TokenObtainPairView
from drf_spectacular.utils import extend_schema, extend_schema_view
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import SearchFilter, OrderingFilter
from .models import User
from .serializers import UserSerializer, RegisterSerializer, CustomTokenObtainPairSerializer
from .permissions import IsAdminOrManager


@extend_schema(
    tags=['Authentication'],
    summary='Login',
    description='''
    Obtain JWT access and refresh tokens by providing username and password.
    
    The response includes:
    - access: JWT access token (expires in 1 hour by default)
    - refresh: JWT refresh token (expires in 7 days by default)
    - user: User information including role
    - tenant: Tenant information including slug and active_modules
    
    The access token also contains custom claims:
    - role: User's role (admin, manager, supervisor, accountant)
    - tenant_id: Tenant ID
    - tenant_slug: Tenant slug for URL routing
    - tenant_name: Tenant name
    ''',
)
class CustomTokenObtainPairView(TokenObtainPairView):
    serializer_class = CustomTokenObtainPairSerializer


@extend_schema(
    tags=['Authentication'],
    summary='Register a new user',
    description='Create a new user account. The user will be assigned to a tenant by an admin.',
)
class RegisterView(generics.CreateAPIView):
    queryset = User.objects.all()
    permission_classes = [permissions.AllowAny]
    serializer_class = RegisterSerializer


@extend_schema_view(
    get=extend_schema(
        tags=['Authentication'],
        summary='Get user profile',
        description='Get the authenticated user\'s profile information.',
    ),
    put=extend_schema(
        tags=['Authentication'],
        summary='Update user profile',
        description='Update the authenticated user\'s profile information.',
    ),
    patch=extend_schema(
        tags=['Authentication'],
        summary='Partially update user profile',
        description='Partially update the authenticated user\'s profile information.',
    ),
)
class UserProfileView(generics.RetrieveUpdateAPIView):
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_object(self):
        return self.request.user


@extend_schema_view(
    list=extend_schema(tags=['Users'], summary='List users'),
    retrieve=extend_schema(tags=['Users'], summary='Get user details'),
    create=extend_schema(tags=['Users'], summary='Create user'),
    update=extend_schema(tags=['Users'], summary='Update user'),
    partial_update=extend_schema(tags=['Users'], summary='Partially update user'),
    destroy=extend_schema(tags=['Users'], summary='Delete user'),
)
class UserViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing users (full CRUD)
    Filtered by current tenant
    Only admins and managers can create/update/delete users
    """
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ['role', 'is_active']
    search_fields = ['username', 'email', 'first_name', 'last_name']
    ordering_fields = ['username', 'created_at', 'last_login']
    ordering = ['-created_at']
    
    def get_queryset(self):
        """Filter by current tenant"""
        return User.objects.filter(tenant=self.request.user.tenant)
    
    def perform_create(self, serializer):
        """Assign user to current tenant when creating"""
        serializer.save(tenant=self.request.user.tenant)
    
    def get_permissions(self):
        """Only admins and managers can create/update/delete users"""
        if self.action in ['create', 'update', 'partial_update', 'destroy']:
            return [permissions.IsAuthenticated(), IsAdminOrManager()]
        return super().get_permissions()
