"""Granular RBAC and Tenant-Isolation permissions."""
from rest_framework import permissions

class IsContractingAuthority(permissions.BasePermission):
    """Allows access only to Contracting Authority users."""
    def has_permission(self, request, view):
        return bool(request.user and request.user.is_authenticated and request.user.is_contracting_authority)

class IsEconomicOperator(permissions.BasePermission):
    """Allows access only to Economic Operator users."""
    def has_permission(self, request, view):
        return bool(request.user and request.user.is_authenticated and request.user.is_economic_operator)

class IsCentralAdmin(permissions.BasePermission):
    """Allows access only to Central Administration users."""
    def has_permission(self, request, view):
        return bool(request.user and request.user.is_authenticated and (request.user.is_central_admin or request.user.is_superuser))

class IsTenantMember(permissions.BasePermission):
    """
    Object-level permission to ensure the user belongs to the object's organization.
    Central Administration and Superusers have oversight read-only permissions if explicitly authorized.
    """
    def has_object_permission(self, request, view, obj):
        if not request.user or not request.user.is_authenticated:
            return False

        # Superusers and Central Admins for safe read methods
        if (request.user.is_superuser or request.user.is_central_admin) and request.method in permissions.SAFE_METHODS:
            return True

        target_org = getattr(obj, 'organization', None)
        if target_org is None and hasattr(obj, 'procurement'):
            target_org = getattr(obj.procurement, 'organization', None)

        if target_org and request.user.organization:
            return target_org.id == request.user.organization.id

        return False
