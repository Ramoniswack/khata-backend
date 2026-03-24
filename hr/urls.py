from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    DepartmentViewSet, EmployeeViewSet, AttendanceViewSet, 
    LeaveTypeViewSet, LeaveRequestViewSet, PayrollViewSet, hr_reports
)

router = DefaultRouter()
router.register(r'departments', DepartmentViewSet, basename='department')
router.register(r'employees', EmployeeViewSet, basename='employee')
router.register(r'attendance', AttendanceViewSet, basename='attendance')
router.register(r'leave-types', LeaveTypeViewSet, basename='leavetype')
router.register(r'leave-requests', LeaveRequestViewSet, basename='leaverequest')
router.register(r'payroll', PayrollViewSet, basename='payroll')

urlpatterns = [
    path('reports/', hr_reports, name='hr-reports'),
    path('', include(router.urls)),
]
