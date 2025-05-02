from rest_framework import permissions


class IsAuthorOrReadOnly(permissions.BasePermission):
    message = 'Нельзя изменять чужой контент!'

    def has_permission(self, request, view):
        return (request.method in permissions.SAFE_METHODS
                or request.user.is_authenticated)

    def has_object_permission(self, request, view, obj):
        return (request.method in permissions.SAFE_METHODS
                or obj.author == request.user)


class IsSuperUserOrAdmin(permissions.BasePermission):
    """Права для администратора и супер юзера
    на добавление и удаление произведений, категорий и жанров.
    """
    message = 'Изменять этот контент может только админ или супер юзер'

    def has_permission(self, request, view):
        if request.method in permissions.SAFE_METHODS:
            return True
        if not request.user.is_authenticated:
            return False
        if request.user.is_admin or request.user.is_superuser:
            return True
        return False
