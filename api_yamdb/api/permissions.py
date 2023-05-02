from rest_framework.permissions import BasePermission, SAFE_METHODS


class IsAdmin(BasePermission):
    """Права доступа администратора."""
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.is_admin


class IsAuthorOrModeratorOrAdminOrReadOnly(BasePermission):
    def has_object_permission(self, request, view, obj):
        """Права доступа автора или модератора."""
        return (
            True if request.method in SAFE_METHODS else
            obj.author == request.user or request.user.is_moderator
            or request.user.is_admin if request.user.is_authenticated else
            False)


class IsAdminOrReadOnly(BasePermission):
    """Права доступа админу или только на чтение."""
    def has_permission(self, request, view):
        return (
            True if request.method in SAFE_METHODS else
            request.user.is_admin if request.user.is_authenticated else
            False
        )
