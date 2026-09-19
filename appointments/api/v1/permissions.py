from rest_framework.permissions import BasePermission


class RolePermission(BasePermission):
    """
    Custom permission to allow access based on user role.
    Only authenticated users with a role in the allowed list can proceed.
    """

    def has_permission(self, request, view):
        if not request.user.is_authenticated:
            return False

        allowed_roles = getattr(view, "allowed_roles", [])
        if not allowed_roles:
            return True

        return request.user.role in allowed_roles