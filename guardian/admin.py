from django.contrib import admin
from django.contrib.contenttypes.generic import GenericTabularInline

from guardian.models import UserObjectPermission, GroupObjectPermission

class GroupObjectPermissionInline(GenericTabularInline):
    model = GroupObjectPermission
    raw_id_fields = ['group']

class UserObjectPermissionInline(GenericTabularInline):
    model = UserObjectPermission
    raw_id_fields = ['user']

class ObjectPermissionMixin(object):
    def has_change_permission(self, request, obj=None):
        opts = self.opts
        return request.user.has_perm(opts.app_label + '.' + opts.get_change_permission(), obj)

    def has_delete_permission(self, request, obj=None):
        opts = self.opts
        return request.user.has_perm(opts.app_label + '.' + opts.get_delete_permission(), obj)