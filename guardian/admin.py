from django.contrib import admin
from django.contrib.auth.models import Permission
from django.contrib.contenttypes.generic import GenericTabularInline
from django.contrib.admin.sites import NotRegistered

from guardian.models import UserObjectPermission, GroupObjectPermission

class GroupObjectPermissionInline(GenericTabularInline):
    model = GroupObjectPermission
    raw_id_fields = ['group', 'permission']

class UserObjectPermissionInline(GenericTabularInline):
    model = UserObjectPermission
    raw_id_fields = ['user', 'permission']

class ObjectPermissionMixin(object):
    def has_change_permission(self, request, obj=None):
        opts = self.opts
        return request.user.has_perm(opts.app_label + '.' + opts.get_change_permission(), obj)

    def has_delete_permission(self, request, obj=None):
        opts = self.opts
        return request.user.has_perm(opts.app_label + '.' + opts.get_delete_permission(), obj)

class PermissionAdmin(admin.ModelAdmin):
    search_fields = ('name',)

try:
    admin.site.unregister(Permission)
except NotRegistered:
    pass
admin.site.register(Permission, PermissionAdmin)