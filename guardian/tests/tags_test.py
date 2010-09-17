from django.test import TestCase
from django.template import Template, Context, TemplateSyntaxError
from django.contrib.auth.models import User, Group, AnonymousUser

from guardian.exceptions import NotUserNorGroup
from guardian.models import UserObjectPermission, GroupObjectPermission
from guardian.tests.models import Keycard

def render(template, context):
    """
    Returns rendered ``template`` with ``context``, which are given as string
    and dict respectively.
    """
    t = Template(template)
    return t.render(Context(context))

class GetObjPermsTagTest(TestCase):
    fixtures = ['tests.json']

    def setUp(self):
        self.keycard = Keycard.objects.create()
        self.user = User.objects.get(username='jack')
        self.group = Group.objects.get(name='jackGroup')
        UserObjectPermission.objects.all().delete()
        GroupObjectPermission.objects.all().delete()

    def test_wrong_formats(self):
        wrong_formats = (
            #'{% get_obj_perms user for keycard as obj_perms %}', # no quotes
            '{% get_obj_perms user for keycard as \'obj_perms" %}', # wrong quotes
            '{% get_obj_perms user for keycard as \'obj_perms" %}', # wrong quotes
            '{% get_obj_perms user for keycard as obj_perms" %}', # wrong quotes
            '{% get_obj_perms user for keycard as obj_perms\' %}', # wrong quotes
            '{% get_obj_perms user for keycard as %}', # no context_var
            '{% get_obj_perms for keycard as "obj_perms" %}', # no user/group
            '{% get_obj_perms user keycard as "obj_perms" %}', # no "for" bit
            '{% get_obj_perms user for keycard "obj_perms" %}', # no "as" bit
            '{% get_obj_perms user for as "obj_perms" %}', # no object
        )

        context = {'user': User.get_anonymous(), 'keycard': self.keycard}
        for wrong in wrong_formats:
            fullwrong = '{% load guardian_tags %}' + wrong
            try:
                render(fullwrong, context)
                self.fail("Used wrong get_obj_perms tag format: \n\n\t%s\n\n "
                    "but TemplateSyntaxError have not been raised" % wrong)
            except TemplateSyntaxError:
                pass

    def test_anonymous_user(self):
        template = ''.join((
            '{% load guardian_tags %}',
            '{% get_obj_perms user for keycard as "obj_perms" %}{{ perms }}',
        ))
        context = {'user': AnonymousUser(), 'keycard': self.keycard}
        anon_output = render(template, context)
        context = {'user': User.get_anonymous(), 'keycard': self.keycard}
        real_anon_user_output = render(template, context)
        self.assertEqual(anon_output, real_anon_user_output)

    def test_wrong_user_or_group(self):
        template = ''.join((
            '{% load guardian_tags %}',
            '{% get_obj_perms some_obj for keycard as "obj_perms" %}',
        ))
        context = {'some_obj': Keycard(), 'keycard': self.keycard}
        self.assertRaises(NotUserNorGroup, render, template, context)

    def test_superuser(self):
        user = User.objects.create(username='superuser', is_superuser=True)
        template = ''.join((
            '{% load guardian_tags %}',
            '{% get_obj_perms user for keycard as "obj_perms" %}',
            '{{ obj_perms|join:" " }}',
        ))
        context = {'user': user, 'keycard': self.keycard}
        output = render(template, context)

        for perm in ('add_keycard', 'change_keycard', 'delete_keycard'):
            self.assertTrue(perm in output)

    def test_user(self):
        UserObjectPermission.objects.assign("change_keycard", self.user,
            self.keycard)
        GroupObjectPermission.objects.assign("delete_keycard", self.group,
            self.keycard)

        template = ''.join((
            '{% load guardian_tags %}',
            '{% get_obj_perms user for keycard as "obj_perms" %}',
            '{{ obj_perms|join:" " }}',
        ))
        context = {'user': self.user, 'keycard': self.keycard}
        output = render(template, context)

        self.assertEqual(output, 'change_keycard delete_keycard')

    def test_group(self):
        GroupObjectPermission.objects.assign("delete_keycard", self.group,
            self.keycard)

        template = ''.join((
            '{% load guardian_tags %}',
            '{% get_obj_perms group for keycard as "obj_perms" %}',
            '{{ obj_perms|join:" " }}',
        ))
        context = {'group': self.group, 'keycard': self.keycard}
        output = render(template, context)

        self.assertEqual(output, 'delete_keycard')

