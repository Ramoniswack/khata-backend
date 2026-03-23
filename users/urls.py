from django.urls import path, include
from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt.views import TokenRefreshView
from drf_spectacular.utils import extend_schema
from .views import RegisterView, UserProfileView, UserViewSet, CustomTokenObtainPairView

# Router for ViewSets
router = DefaultRouter()
router.register(r'users', UserViewSet, basename='user')

# Add schema documentation to JWT refresh view
TokenRefreshView = extend_schema(
    tags=['Authentication'],
    summary='Refresh access token',
    description='Get a new access token using a valid refresh token.',
)(TokenRefreshView)

urlpatterns = [
    path('register/', RegisterView.as_view(), name='register'),
    path('login/', CustomTokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('profile/', UserProfileView.as_view(), name='user_profile'),
    path('', include(router.urls)),
]
