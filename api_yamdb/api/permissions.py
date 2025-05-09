from rest_framework import permissions


class IsSuperUserOrAdminOnly(permissions.BasePermission):
    """Права для администратора и супер юзера
    на добавление и удаление произведений, категорий и жанров.
    """
    message = 'Изменять этот контент может только админ или супер юзер'

    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.is_admin


class IsSuperUserOrAdminOrReadOnly(IsSuperUserOrAdminOnly):

    def has_permission(self, request, view):
        return (
            request.method in permissions.SAFE_METHODS
            or super().has_permission(request, view)
        )


class IsModerOrAdminOrAuthorOrReadOnly(permissions.BasePermission):

    def has_permission(self, request, view):
        return (request.user.is_authenticated
                or request.method in permissions.SAFE_METHODS
                )

    def has_object_permission(self, request, view, obj):
        return (request.method in permissions.SAFE_METHODS
                or request.user.is_admin
                or request.user.is_moderator
                or obj.author == request.user
                )
