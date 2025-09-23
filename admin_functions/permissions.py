from rest_framework.permissions import BasePermission


class IsAuthenticatedAndStaff(BasePermission):
    """
    Custom permission: only authenticated staff users can access.
    """

    def has_permission(self, request, view):
        return bool(request.user and request.user.is_authenticated and request.user.is_staff)
