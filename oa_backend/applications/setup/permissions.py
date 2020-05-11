# __author__ = itsneo1990
from rest_framework.permissions import BasePermission


class SiteReceptionGroupPermission(BasePermission):
    def has_permission(self, request, view):
        if request.user.is_superuser:
            return True
        if request.method == 'GET':
            return request.user.has_perm("setup.view_sitereceptiongroup")
        elif request.method == 'POST':
            return request.user.has_perm("setup.add_sitereceptiongroup")
        elif request.method == 'PUT':
            return request.user.has_perm("setup.change_sitereceptiongroup")
        return False
