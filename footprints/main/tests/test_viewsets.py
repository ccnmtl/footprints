from django.test import TestCase
from django.test.client import RequestFactory, Client, encode_multipart
from django.urls.base import reverse

from footprints.main.serializers import (
    StandardizedIdentificationTypeSerializer,
    StandardizedIdentificationSerializer, LanguageSerializer,
    ExtendedDateSerializer, ActorSerializer)
from footprints.main.tests.factories import (
    StandardizedIdentificationFactory,
    LanguageFactory, ExtendedDateFactory, ActorFactory, WrittenWorkFactory,
    ImprintFactory, BookCopyFactory, GroupFactory, ADD_CHANGE_PERMISSIONS,
    UserFactory, FootprintFactory)
from footprints.main.viewsets import (
    WrittenWorkViewSet, ImprintViewSet, BookCopyViewSet)


class SerializerTest(TestCase):

    def test_standardized_identification_type_serializer(self):
        serializer = StandardizedIdentificationTypeSerializer()

        qs = serializer.get_queryset()
        self.assertEquals(qs.count(), 5)  # preloaded in migrations

    def test_standardized_identification_serializer(self):
        si = StandardizedIdentificationFactory()
        serializer = StandardizedIdentificationSerializer()

        qs = serializer.get_queryset()
        self.assertEquals(qs.count(), 1)
        self.assertEquals(qs.first(), si)

    def test_language_serializer(self):
        lang = LanguageFactory()
        serializer = LanguageSerializer()

        qs = serializer.get_queryset()
        self.assertEquals(qs.count(), 1)
        self.assertEquals(qs.first(), lang)

        self.assertEquals(serializer.to_internal_value(lang.id), lang)

    def test_extended_date_serializer(self):
        dt = ExtendedDateFactory()
        serializer = ExtendedDateSerializer()

        qs = serializer.get_queryset()
        self.assertEquals(qs.count(), 1)
        self.assertEquals(qs.first(), dt)

    def test_actor_serializer(self):
        a = ActorFactory()
        serializer = ActorSerializer()

        qs = serializer.get_queryset()
        self.assertEquals(qs.count(), 1)
        self.assertEquals(qs.first(), a)

        self.assertEquals(serializer.to_internal_value(a.id), a)


class WrittenWorkViewsetTest(TestCase):

    def test_filter_by_title(self):
        viewset = WrittenWorkViewSet()
        ww1 = WrittenWorkFactory(title='Alpha')
        ww2 = WrittenWorkFactory(title='Beta')

        viewset.request = RequestFactory().get('/', {})
        qs = viewset.get_queryset()
        self.assertEquals(qs.count(), 2)
        self.assertEquals(qs[0], ww1)
        self.assertEquals(qs[1], ww2)

        data = {'q': 'bet'}
        viewset.request = RequestFactory().get('/', data)
        qs = viewset.get_queryset()
        self.assertEquals(qs.count(), 1)
        self.assertEquals(qs.first(), ww2)

    def test_filter_by_imprint_location(self):
        fp1 = FootprintFactory()
        FootprintFactory()

        data = {'imprintLocation': fp1.book_copy.imprint.place.id}

        viewset = WrittenWorkViewSet()
        viewset.request = RequestFactory().get('/', data)
        qs = viewset.get_queryset()
        self.assertEquals(qs.count(), 1)
        self.assertEquals(qs.first(), fp1.book_copy.imprint.work)

    def test_filter_by_footprint_location(self):
        fp = FootprintFactory()
        FootprintFactory()

        data = {'footprintLocation': fp.place.id}

        viewset = WrittenWorkViewSet()
        viewset.request = RequestFactory().get('/', data)
        qs = viewset.get_queryset()
        self.assertEquals(qs.count(), 1)
        self.assertEquals(qs.first(), fp.book_copy.imprint.work)


class ImprintViewsetTest(TestCase):

    def setUp(self):
        self.viewset = ImprintViewSet()
        self.imprint1 = ImprintFactory(title='Alpha')
        self.imprint2 = ImprintFactory(title='Beta')

    def test_filter_no_criteria(self):
        self.viewset.request = RequestFactory().get('/', {})
        qs = self.viewset.get_queryset()
        self.assertEquals(qs.count(), 2)
        self.assertEquals(qs[0], self.imprint1)
        self.assertEquals(qs[1], self.imprint2)

    def test_filter_by_work_id(self):
        data = {'work': self.imprint1.work.id}
        self.viewset.request = RequestFactory().get('/', data)
        qs = self.viewset.get_queryset()
        self.assertEquals(qs.count(), 1)
        self.assertEquals(qs.first(), self.imprint1)

    def test_filter_by_title(self):
        data = {'q': 'bet'}
        self.viewset.request = RequestFactory().get('/', data)
        qs = self.viewset.get_queryset()
        self.assertEquals(qs.count(), 1)
        self.assertEquals(qs.first(), self.imprint2)

    def test_filter_by_imprint_location(self):
        data = {'imprintLocation': self.imprint1.place.id}
        self.viewset.request = RequestFactory().get('/', data)

        qs = self.viewset.get_queryset()
        self.assertEquals(qs.count(), 1)
        self.assertEquals(qs.first(), self.imprint1)

    def test_filter_by_footprint_location(self):
        fp = FootprintFactory()
        FootprintFactory()

        data = {'footprintLocation': fp.place.id}
        self.viewset.request = RequestFactory().get('/', data)

        qs = self.viewset.get_queryset()
        self.assertEquals(qs.count(), 1)
        self.assertEquals(qs.first(), fp.book_copy.imprint)


class BookCopyViewsetTest(TestCase):

    def test_bookcopy_viewset(self):
        viewset = BookCopyViewSet()
        book1 = BookCopyFactory()
        book2 = BookCopyFactory()

        viewset.request = RequestFactory().get('/', {})
        qs = viewset.get_queryset()
        self.assertEquals(qs.count(), 2)
        self.assertEquals(qs[0], book1)
        self.assertEquals(qs[1], book2)

        data = {'imprint': book1.imprint.id}
        viewset.request = RequestFactory().get('/', data)
        qs = viewset.get_queryset()
        self.assertEquals(qs.count(), 1)
        self.assertEquals(qs.first(), book1)


class FootprintViewsetTest(TestCase):

    def test_footprint_viewset(self):
        csrf_client = Client(enforce_csrf_checks=True)

        grp = GroupFactory(permissions=ADD_CHANGE_PERMISSIONS)
        contributor = UserFactory(group=grp)

        csrf_client.login(username=contributor.username, password="test")

        # get a csrf token
        url = reverse('create-footprint-view')
        response = csrf_client.get(url)

        footprint = FootprintFactory()
        data = {'pk': footprint.id, 'title': 'abcdefg'}
        content = encode_multipart('BoUnDaRyStRiNg', data)
        content_type = 'multipart/form-data; boundary=BoUnDaRyStRiNg'

        url = '/api/footprint/%s/' % footprint.id

        csrf_header = response.cookies['csrftoken'].value
        response = csrf_client.patch(url, content,
                                     content_type=content_type,
                                     HTTP_X_CSRFTOKEN=csrf_header)
        self.assertEquals(response.status_code, 200)

        footprint.refresh_from_db()
        self.assertEquals(footprint.title, 'abcdefg')
