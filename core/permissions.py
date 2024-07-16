from rest_framework.permissions import BasePermission


class IsAdmin(BasePermission):
    def has_permission(self, request, view):
        return request.user and request.user.role == 'admin'


class IsDeveloper(BasePermission):
    def has_permission(self, request, view):
        return request.user and request.user.role in ['admin', 'developer']


class IsViewer(BasePermission):
    def has_permission(self, request, view):
        return request.user and request.user.role in ['admin', 'developer', 'viewer']
