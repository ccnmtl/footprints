from django.contrib.auth.models import AnonymousUser
from django.test.client import RequestFactory
from django.test.testcases import TestCase

from footprints.main.tests.factories import UserFactory
from footprints.mixins import EditableMixin


class EditableMixinTest(TestCase):
    def setUp(self):
        self.mixin = EditableMixin()

    def test_editable_anonymous_user(self):
        request = RequestFactory().get('/')
        request.user = AnonymousUser()

        self.assertFalse(self.mixin.has_edit_permission(request.user))

    def test_editable_authenticated_user(self):
        request = RequestFactory().get('/')
        request.user = UserFactory()

        self.assertTrue(self.mixin.has_edit_permission(request.user))
