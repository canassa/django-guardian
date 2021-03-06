from itertools import chain

from django.test import TestCase
from django.contrib.auth.models import User, Group, Permission, AnonymousUser
from django.contrib.contenttypes.models import ContentType

from guardian.core import ObjectPermissionChecker
from guardian.models import UserObjectPermission, GroupObjectPermission
from guardian.exceptions import NotUserNorGroup
from guardian.shortcuts import assign
from guardian.tests.models import Keycard

class ObjectPermissionTestCase(TestCase):
    fixtures = ['tests.json']

    def setUp(self):
        self.user = User.objects.get(username='jack')
        self.group = Group.objects.get(name='jackGroup')
        UserObjectPermission.objects.all().delete()
        GroupObjectPermission.objects.all().delete()
        self.keycard = Keycard.objects.create()

class ObjectPermissionCheckerTest(ObjectPermissionTestCase):

    '''
    # Commented out as during tests connection.queries attribute is not being
    # updated
    def test_cache(self):
        from django.db import connection
        UserObjectPermission.objects.all().delete()
        GroupObjectPermission.objects.all().delete()
        check = ObjectPermissionChecker(user=self.user)
        query_count_pre = len(connection.queries)
        res = check.has_perm("change_group", self.group)
        query_count = len(connection.queries)
        res_new = check.has_perm("change_group", self.group)
        query_count_new = len(connection.queries)

        # TODO
        # has_perm on Checker should spawn only one query
        self.assertEqual( query_count - query_count_pre, 1)

        self.assertEqual(res, res_new)
        self.assertEqual(query_count, query_count_new)
    '''

    def test_init(self):
        self.assertRaises(NotUserNorGroup, ObjectPermissionChecker,
            user_or_group=Keycard())
        self.assertRaises(NotUserNorGroup, ObjectPermissionChecker)

    def test_anonymous_user(self):
        user = AnonymousUser()
        check = ObjectPermissionChecker(user)
        # assert anonymous user has no object permissions at all for keycard
        self.assertTrue( [] == list(check.get_perms(self.keycard)) )

    def test_superuser(self):
        user = User.objects.create(username='superuser', is_superuser=True)
        check = ObjectPermissionChecker(user)
        ctype = ContentType.objects.get_for_model(self.keycard)
        perms = sorted(chain(*Permission.objects
            .filter(content_type=ctype)
            .values_list('codename')))
        self.assertEqual(perms, check.get_perms(self.keycard))
        for perm in perms:
            self.assertTrue(check.has_perm(perm, self.keycard))

    def test_not_active_superuser(self):
        user = User.objects.create(username='not_active_superuser',
            is_superuser=True, is_active=False)
        check = ObjectPermissionChecker(user)
        ctype = ContentType.objects.get_for_model(self.keycard)
        perms = sorted(chain(*Permission.objects
            .filter(content_type=ctype)
            .values_list('codename')))
        self.assertEqual(check.get_perms(self.keycard), [])
        for perm in perms:
            self.assertFalse(check.has_perm(perm, self.keycard))

    def test_not_active_user(self):
        user = User.objects.create(username='notactive')
        assign("change_keycard", user, self.keycard)

        # new ObjectPermissionChecker is created for each User.has_perm call
        self.assertTrue(user.has_perm("change_keycard", self.keycard))
        user.is_active = False
        self.assertFalse(user.has_perm("change_keycard", self.keycard))

        # use on one checker only (as user's is_active attr should be checked
        # before try to use cache
        user = User.objects.create(username='notactive-cache')
        assign("change_keycard", user, self.keycard)

        check = ObjectPermissionChecker(user)
        self.assertTrue(check.has_perm("change_keycard", self.keycard))
        user.is_active = False
        self.assertFalse(check.has_perm("change_keycard", self.keycard))

    def test_get_perms(self):
        group = Group.objects.create(name='group')
        key1 = Keycard.objects.create(key='key1')
        key2 = Keycard.objects.create(key='key2')

        assign_perms = {
            group: ('change_group', 'delete_group'),
            key1: ('change_keycard', 'can_use_keycard', 'can_suspend_keycard'),
            key2: ('delete_keycard', 'can_suspend_keycard'),
        }

        check = ObjectPermissionChecker(self.user)

        for obj, perms in assign_perms.items():
            for perm in perms:
                UserObjectPermission.objects.assign(perm, self.user, obj)
            self.assertEqual(sorted(perms), sorted(check.get_perms(obj)))

        check = ObjectPermissionChecker(self.group)

        for obj, perms in assign_perms.items():
            for perm in perms:
                GroupObjectPermission.objects.assign(perm, self.group, obj)
            self.assertEqual(sorted(perms), sorted(check.get_perms(obj)))

