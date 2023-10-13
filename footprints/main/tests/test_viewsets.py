from json import loads

from django.test import TestCase
from django.test.client import Client, encode_multipart
from django.urls.base import reverse

from footprints.main.serializers import (
    StandardizedIdentificationTypeSerializer,
    StandardizedIdentificationSerializer, LanguageSerializer,
    ExtendedDateSerializer, ActorSerializer)
from footprints.main.tests.factories import (
    StandardizedIdentificationFactory,
    LanguageFactory, ExtendedDateFactory, ActorFactory,
    GroupFactory, ADD_CHANGE_PERMISSIONS,
    UserFactory, FootprintFactory, CanonicalPlaceFactory, PlaceFactory)


class SerializerTest(TestCase):

    def test_standardized_identification_type_serializer(self):
        serializer = StandardizedIdentificationTypeSerializer()

        qs = serializer.get_queryset()
        self.assertEqual(qs.count(), 5)  # preloaded in migrations

    def test_standardized_identification_serializer(self):
        si = StandardizedIdentificationFactory()
        serializer = StandardizedIdentificationSerializer()

        qs = serializer.get_queryset()
        self.assertEqual(qs.count(), 1)
        self.assertEqual(qs.first(), si)

    def test_language_serializer(self):
        lang = LanguageFactory()
        serializer = LanguageSerializer()

        qs = serializer.get_queryset()
        self.assertEqual(qs.count(), 1)
        self.assertEqual(qs.first(), lang)

        self.assertEqual(serializer.to_internal_value(lang.id), lang)

    def test_extended_date_serializer(self):
        dt = ExtendedDateFactory()
        serializer = ExtendedDateSerializer()

        qs = serializer.get_queryset()
        self.assertEqual(qs.count(), 1)
        self.assertEqual(qs.first(), dt)

    def test_actor_serializer(self):
        a = ActorFactory()
        serializer = ActorSerializer()

        qs = serializer.get_queryset()
        self.assertEqual(qs.count(), 1)
        self.assertEqual(qs.first(), a)

        self.assertEqual(serializer.to_internal_value(a.id), a)


class FootprintViewsetTest(TestCase):

    def test_footprint_viewset(self):
        csrf_client = Client(enforce_csrf_checks=True)

        grp = GroupFactory(permissions=ADD_CHANGE_PERMISSIONS)
        contributor = UserFactory(group=grp)

        csrf_client.login(username=contributor.username, password='test')

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
        self.assertEqual(response.status_code, 200)

        footprint.refresh_from_db()
        self.assertEqual(footprint.title, 'abcdefg')


class AlternatePlaceNameViewsetTest(TestCase):

    def test_viewset(self):
        cp = CanonicalPlaceFactory(
            canonical_name='New York, New York, United States',
            geoname_id=1234)
        PlaceFactory(canonical_place=cp, alternate_name='New York')
        PlaceFactory(canonical_place=cp, alternate_name='Neuva York')
        p1 = PlaceFactory(canonical_place=cp, alternate_name='NYC')

        grp = GroupFactory(permissions=ADD_CHANGE_PERMISSIONS)
        contributor = UserFactory(group=grp)
        self.client.login(username=contributor.username, password='test')

        url = '/api/altname/?q=&geonameId=1234'
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        the_json = loads(response.content.decode('utf-8'))
        self.assertEqual(len(the_json['results']), 3)

        url = '/api/altname/?q=NYC&geonameId=1234'
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        the_json = loads(response.content.decode('utf-8'))
        self.assertEqual(len(the_json['results']), 1)
        self.assertEqual(
            the_json['results'][0]['id'], p1.id)
