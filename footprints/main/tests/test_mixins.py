from django.contrib.auth.models import AnonymousUser
from django.test.client import RequestFactory
from django.test.testcases import TestCase

from footprints.main.tests.factories import FootprintFactory, UserFactory, \
    RoleFactory
from footprints.mixins import EditableMixin


class EditableMixinTest(TestCase):
    def setUp(self):
        self.mixin = EditableMixin()

    def test_editable_anonymous_user(self):
        the_object = FootprintFactory()
        request = RequestFactory().get('/')
        request.user = AnonymousUser()

        self.assertFalse(self.mixin.has_edit_permission(request.user,
                                                        the_object))

    def test_editable_authenticated_user(self):
        request = RequestFactory().get('/')
        request.user = UserFactory()
        the_object = FootprintFactory()

        self.assertFalse(self.mixin.has_edit_permission(request.user,
                                                        the_object))

    def test_editable_authenticated_owner(self):
        request = RequestFactory().get('/')
        request.user = UserFactory()
        the_object = FootprintFactory(created_by=request.user)

        self.assertTrue(self.mixin.has_edit_permission(request.user,
                                                       the_object))

    def test_editable_authenticated_staff(self):
        request = RequestFactory().get('/')
        request.user = UserFactory(is_staff=True)
        the_object = FootprintFactory()

        self.assertTrue(self.mixin.has_edit_permission(request.user,
                                                       the_object))

    def test_editable_no_creator(self):
        request = RequestFactory().get('/')
        request.user = UserFactory()
        the_object = RoleFactory()

        self.assertFalse(self.mixin.has_edit_permission(request.user,
                                                        the_object))
