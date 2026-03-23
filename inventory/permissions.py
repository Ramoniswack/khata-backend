"""
Custom permissions for Inventory module RBAC.
"""
from rest_framework import permissions


class IsAdminOrReadOnly(permissions.BasePermission):
    """
    Only ADMIN users can delete products.
    Other authenticated users can read and create/update.
    """
    
    def has_permission(self, request, view):
        # Allow read operations for all authenticated users
        if request.method in permissions.SAFE_METHODS:
            return request.user and request.user.is_authenticated
        
        # Allow create/update for authenticated users
        if request.method in ['POST', 'PUT', 'PATCH']:
            return request.user and request.user.is_authenticated
        
        # Only ADMIN can delete
        if request.method == 'DELETE':
            return request.user and request.user.is_authenticated and request.user.role == 'admin'
        
        return False


class IsSupervisorOrAdmin(permissions.BasePermission):
    """
    Only SUPERVISOR or ADMIN users can create stock movements.
    All authenticated users can read.
    """
    
    def has_permission(self, request, view):
        # Allow read operations for all authenticated users
        if request.method in permissions.SAFE_METHODS:
            return request.user and request.user.is_authenticated
        
        # Only SUPERVISOR or ADMIN can create stock movements
        if request.method == 'POST':
            return (
                request.user and 
                request.user.is_authenticated and 
                request.user.role in ['supervisor', 'admin']
            )
        
        return False
