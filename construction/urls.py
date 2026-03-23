from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    SiteViewSet, WorkerViewSet, AttendanceViewSet, DailyLogViewSet,
    MaterialConsumptionViewSet, EquipmentViewSet, EquipmentUsageLogViewSet
)

router = DefaultRouter()
router.register(r'sites', SiteViewSet, basename='site')
router.register(r'workers', WorkerViewSet, basename='worker')
router.register(r'attendance', AttendanceViewSet, basename='attendance')
router.register(r'daily-logs', DailyLogViewSet, basename='daily-log')
router.register(r'material-consumption', MaterialConsumptionViewSet, basename='material-consumption')
router.register(r'equipment', EquipmentViewSet, basename='equipment')
router.register(r'equipment-usage', EquipmentUsageLogViewSet, basename='equipment-usage')

urlpatterns = [
    path('', include(router.urls)),
]
