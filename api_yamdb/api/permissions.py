from rest_framework import permissions


class IsAdmin(permissions.BasePermission):
    """Права доступа администратора"""
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.is_admin


class ReadOnly(permissions.BasePermission):
    """Права доступа только на чтение"""
    def has_permission(self, request, view):
        return request.method in permissions.SAFE_METHODS


class IsAuthorOrModeratorOrReadOnly(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        """Права доступа автора или модератора"""
        if request.method in permissions.SAFE_METHODS:
            return True
        if request.user.is_authenticated:
            return (
                obj.author == request.user
                or request.user.is_moderator
            )
        return False


class SelfEditUserOnlyPermission(permissions.BasePermission):
    """Обеспечивает доступ к users/me только текущему."""

    def has_permission(self, request, view):
        return (request.user.is_authenticated)

    def has_object_permission(self, request, view, obj):
        return (obj.id == request.user)


class IsAdminOrReadOnlyPermission(permissions.BasePermission):
    """
    Обеспечивает доступ администратору.
    Для остальных только безопасные методы.
    """
    def has_permission(self, request, view):
        if request.user.is_authenticated:
            return (request.user.is_admin or request.user.is_superuser)
        return request.method in permissions.SAFE_METHODS


class IsAdminOnlyPermission(permissions.BasePermission):
    """Обеспечивает доступ только администратору."""
    def has_permission(self, request, view):
        if request.user.is_authenticated:
            return (request.user.is_admin or request.user.is_superuser)
        return False


class IsAuthorModeratorAdminOrReadOnlyPermission(permissions.BasePermission):
    """
    Обеспечивает доступ автору, модератору и администратору.
    Для остальных только безопасные методы.
    """
    def has_permission(self, request, view):
        return (
            request.method in permissions.SAFE_METHODS
            or request.user.is_authenticated
        )

    def has_object_permission(self, request, view, obj):
        return (
            request.method in permissions.SAFE_METHODS
            or obj.author == request.user or request.user.is_moderator
            or request.user.is_admin or request.user.is_superuser
        )
