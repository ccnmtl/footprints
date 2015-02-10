from django.test.client import RequestFactory
from django.test.testcases import TestCase

from footprints.main.permissions import IsOwnerOrReadOnly, IsStaffOrReadOnly
from footprints.main.tests.factories import FootprintFactory, UserFactory


class IsOwnerOrReadOnlyTest(TestCase):

    def setUp(self):
        self.permission = IsOwnerOrReadOnly()
        self.get = RequestFactory().get('/', {})
        self.post = RequestFactory().post('/', {})

    def test_has_object_permission(self):
        user = UserFactory()
        user2 = UserFactory()
        staff = UserFactory(is_staff=True)
        obj = FootprintFactory(created_by=user)

        self.get.user = user2
        auth = self.permission.has_object_permission(self.get, None, obj)
        self.assertTrue(auth)

        self.post.user = user2
        auth = self.permission.has_object_permission(self.post, None, obj)
        self.assertFalse(auth)

        self.post.user = user
        auth = self.permission.has_object_permission(self.post, None, obj)
        self.assertTrue(auth)

        self.post.user = staff
        auth = self.permission.has_object_permission(self.post, None, obj)
        self.assertTrue(auth)


class IsStaffOrReadOnlyTest(TestCase):

    def setUp(self):
        self.permission = IsStaffOrReadOnly()
        self.get = RequestFactory().get('/', {})
        self.post = RequestFactory().post('/', {})

    def test_has_object_permission(self):
        user = UserFactory()
        staff = UserFactory(is_staff=True)
        obj = FootprintFactory(created_by=user)

        self.get.user = user
        auth = self.permission.has_object_permission(self.get, None, obj)
        self.assertTrue(auth)

        self.post.user = user
        auth = self.permission.has_object_permission(self.post, None, obj)
        self.assertFalse(auth)

        self.post.user = staff
        auth = self.permission.has_object_permission(self.post, None, obj)
        self.assertTrue(auth)
