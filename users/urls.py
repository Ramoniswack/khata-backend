from django.urls import path
from rest_framework_simplejwt.views import TokenRefreshView
from drf_spectacular.utils import extend_schema
from .views import (
    RegisterView, UserProfileView, UserViewSet, CustomTokenObtainPairView, 
    AuditLogViewSet, get_permissions, update_permissions
)

# Add schema documentation to JWT refresh view
TokenRefreshView = extend_schema(
    tags=['Authentication'],
    summary='Refresh access token',
    description='Get a new access token using a valid refresh token.',
)(TokenRefreshView)

urlpatterns = [
    # Authentication
    path('register/', RegisterView.as_view(), name='register'),
    path('login/', CustomTokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('profile/', UserProfileView.as_view(), name='user_profile'),
    
    # Permissions
    path('permissions/', get_permissions, name='get_permissions'),
    path('permissions/update/', update_permissions, name='update_permissions'),
    
    # Users
    path('users/', UserViewSet.as_view({'get': 'list', 'post': 'create'}), name='user-list'),
    path('users/<int:pk>/', UserViewSet.as_view({'get': 'retrieve', 'put': 'update', 'patch': 'partial_update', 'delete': 'destroy'}), name='user-detail'),
    
    # Audit Logs
    path('audit-logs/', AuditLogViewSet.as_view({'get': 'list'}), name='audit-log-list'),
    path('audit-logs/<int:pk>/', AuditLogViewSet.as_view({'get': 'retrieve'}), name='audit-log-detail'),
]
