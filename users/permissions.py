from rest_framework.permissions import BasePermission


class IsModerator(BasePermission):
    """Проверяет, что пользователь в группе 'Модераторы'"""

    def has_permission(self, request, view):
        return request.user.groups.filter(name="Модераторы").exists()


class IsNotModerator(BasePermission):
    """Проверяет, что пользователь НЕ в группе 'Модераторы'"""

    def has_permission(self, request, view):
        return not request.user.groups.filter(name="Модераторы").exists()


class IsOwner(BasePermission):
    """Проверяет, что пользователь — владелец объекта"""

    def has_object_permission(self, request, view, obj):
        return obj.owner == request.user
