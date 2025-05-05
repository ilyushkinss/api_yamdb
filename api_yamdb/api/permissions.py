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
        return request.user.is_authenticated and (request.user.is_admin or request.user.is_superuser)


class IsSuperUserOrAdminOrReadOnly(IsSuperUserOrAdmin):

    def has_permission(self, request, view):
        return request.method in permissions.SAFE_METHODS or super().has_permission(request, view)
