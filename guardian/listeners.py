from django.contrib.auth.models import Permission, User, Group
from django.core.cache import cache
from django.db.models.signals import post_save

from guardian.models import UserObjectPermission, GroupObjectPermission

def clear_perm_cache(sender, instance, **kwargs):
    key_list = cache.get('guardian.keys', [])
    cache.delete_many(key_list)
    cache.delete('guardian.keys')

post_save.connect(clear_perm_cache, sender=UserObjectPermission, dispatch_uid='guardian.listeners')
post_save.connect(clear_perm_cache, sender=GroupObjectPermission, dispatch_uid='guardian.listeners')
post_save.connect(clear_perm_cache, sender=Group, dispatch_uid='guardian.listeners')
post_save.connect(clear_perm_cache, sender=User, dispatch_uid='guardian.listeners')
post_save.connect(clear_perm_cache, sender=Group, dispatch_uid='guardian.listeners')

