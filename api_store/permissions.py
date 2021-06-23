from rest_framework.permissions import BasePermission


class IsAdminOrOwner(BasePermission):
    """
    Permissions для админов или создателей заказов.
    """

    def has_object_permission(self, request, view, obj):
        return obj.user == request.user or request.user.is_staff
