from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import TenantViewSet, OrganizationInvitationViewSet

# Create separate routers to avoid conflicts
tenant_router = DefaultRouter()
tenant_router.register(r'', TenantViewSet, basename='tenant')

invitation_router = DefaultRouter()
invitation_router.register(r'', OrganizationInvitationViewSet, basename='invitation')

urlpatterns = [
    path('invitations/', include(invitation_router.urls)),
    path('', include(tenant_router.urls)),
]
