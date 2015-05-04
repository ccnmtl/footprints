from django.contrib.auth.models import AnonymousUser
from django.test.client import RequestFactory
from django.test.testcases import TestCase

from footprints.main.permissions import IsLoggedInOrReadOnly
from footprints.main.tests.factories import FootprintFactory, UserFactory


class IsLoggedInOrReadOnlyTest(TestCase):

    def setUp(self):
        self.permission = IsLoggedInOrReadOnly()
        self.get = RequestFactory().get('/', {})
        self.post = RequestFactory().post('/', {})

    def test_not_logged_in(self):
        user = AnonymousUser()
        obj = FootprintFactory()

        self.get.user = user
        auth = self.permission.has_object_permission(self.get, None, obj)
        self.assertTrue(auth)

        self.post.user = user
        auth = self.permission.has_object_permission(self.post, None, obj)
        self.assertFalse(auth)

    def test_logged_in(self):
        user = UserFactory()
        obj = FootprintFactory()

        self.get.user = user
        auth = self.permission.has_object_permission(self.get, None, obj)
        self.assertTrue(auth)

        self.post.user = user
        auth = self.permission.has_object_permission(self.post, None, obj)
        self.assertTrue(auth)
