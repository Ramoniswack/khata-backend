from django.urls import path
from .views import (
    DepartmentViewSet, EmployeeViewSet, AttendanceViewSet, 
    LeaveTypeViewSet, LeaveRequestViewSet, PayrollViewSet, hr_reports
)

urlpatterns = [
    # Departments
    path('departments/', DepartmentViewSet.as_view({'get': 'list', 'post': 'create'}), name='department-list'),
    path('departments/<int:pk>/', DepartmentViewSet.as_view({'get': 'retrieve', 'put': 'update', 'patch': 'partial_update', 'delete': 'destroy'}), name='department-detail'),
    path('departments/<int:pk>/employees/', DepartmentViewSet.as_view({'get': 'employees'}), name='department-employees'),
    
    # Employees
    path('employees/', EmployeeViewSet.as_view({'get': 'list', 'post': 'create'}), name='employee-list'),
    path('employees/<int:pk>/', EmployeeViewSet.as_view({'get': 'retrieve', 'put': 'update', 'patch': 'partial_update', 'delete': 'destroy'}), name='employee-detail'),
    path('employees/dashboard/', EmployeeViewSet.as_view({'get': 'hr_dashboard'}), name='employee-dashboard'),
    path('employees/<int:pk>/attendance_summary/', EmployeeViewSet.as_view({'get': 'attendance_summary'}), name='employee-attendance-summary'),
    
    # Attendance
    path('attendance/', AttendanceViewSet.as_view({'get': 'list', 'post': 'create'}), name='attendance-list'),
    path('attendance/<int:pk>/', AttendanceViewSet.as_view({'get': 'retrieve', 'put': 'update', 'patch': 'partial_update', 'delete': 'destroy'}), name='attendance-detail'),
    path('attendance/bulk-mark/', AttendanceViewSet.as_view({'post': 'bulk_mark'}), name='attendance-bulk-mark'),
    path('attendance/stats/', AttendanceViewSet.as_view({'get': 'stats'}), name='attendance-stats'),
    
    # Leave Types
    path('leave-types/', LeaveTypeViewSet.as_view({'get': 'list', 'post': 'create'}), name='leavetype-list'),
    path('leave-types/<int:pk>/', LeaveTypeViewSet.as_view({'get': 'retrieve', 'put': 'update', 'patch': 'partial_update', 'delete': 'destroy'}), name='leavetype-detail'),
    
    # Leave Requests
    path('leave-requests/', LeaveRequestViewSet.as_view({'get': 'list', 'post': 'create'}), name='leaverequest-list'),
    path('leave-requests/<int:pk>/', LeaveRequestViewSet.as_view({'get': 'retrieve', 'put': 'update', 'patch': 'partial_update', 'delete': 'destroy'}), name='leaverequest-detail'),
    path('leave-requests/<int:pk>/approve/', LeaveRequestViewSet.as_view({'post': 'approve'}), name='leaverequest-approve'),
    path('leave-requests/<int:pk>/reject/', LeaveRequestViewSet.as_view({'post': 'reject'}), name='leaverequest-reject'),
    
    # Payroll
    path('payroll/', PayrollViewSet.as_view({'get': 'list', 'post': 'create'}), name='payroll-list'),
    path('payroll/<int:pk>/', PayrollViewSet.as_view({'get': 'retrieve', 'put': 'update', 'patch': 'partial_update', 'delete': 'destroy'}), name='payroll-detail'),
    path('payroll/calculate/', PayrollViewSet.as_view({'post': 'calculate'}), name='payroll-calculate'),
    path('payroll/process/', PayrollViewSet.as_view({'post': 'process'}), name='payroll-process'),
    path('payroll/<int:pk>/approve/', PayrollViewSet.as_view({'post': 'approve'}), name='payroll-approve'),
    
    # Reports
    path('reports/', hr_reports, name='hr-reports'),
]
