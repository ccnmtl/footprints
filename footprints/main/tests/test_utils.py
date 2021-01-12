from unittest import mock

from django.test.testcases import TestCase

from footprints.main.models import Actor, Role
from footprints.main.utils import (
    interpolate_role_actors, snake_to_camel, camel_to_snake, GeonameUtil)


class CustomUtilsTest(TestCase):

    def test_interpolate_role_actors(self):
        roles = []
        actors = []

        role1, created = Role.objects.get_or_create(name='Author')
        role2, created = Role.objects.get_or_create(name='Printer')
        role3, created = Role.objects.get_or_create(name='Censor')
        roles = [role1, role2, role3]

        actor1, created = Actor.objects.get_or_create_by_attributes(
            'Nick', 1234, role1, '11/09/84', '11/09/17')
        actor2, created = Actor.objects.get_or_create_by_attributes(
            'Nick', 1234, role2, '11/09/84', '11/09/17')
        actor3, created = Actor.objects.get_or_create_by_attributes(
            'Nick', 1234, role3, '11/09/84', '11/09/17')
        actors = [actor1, actor2, actor3]
        # no roles or actors
        self.assertTrue([] == interpolate_role_actors([], []))

        # roles but no actors should return 2 times the number roles as cols
        array = interpolate_role_actors(roles, [])
        self.assertTrue(len(array) == 6)

        # roles and actors should return the string you expect
        array = interpolate_role_actors(roles, actors)
        self.assertTrue(array[0].count(b'Nick (Author)') == 1)
        self.assertTrue(array[2].count(b'Nick (Printer)') == 1)
        self.assertTrue(array[4].count(b'Nick (Censor)') == 1)

        # roles and multiple actors should put all the actors of a given role
        # into the same col
        actor4, created = Actor.objects.get_or_create_by_attributes(
            'Nick', 1234, role1, '11/09/84', '11/09/17')
        actors.append(actor4)
        array = interpolate_role_actors(roles, actors)
        self.assertTrue(array[0].count(b'Nick (Author)') == 2)
        self.assertTrue(array[2].count(b'Nick (Printer)') == 1)
        self.assertTrue(array[4].count(b'Nick (Censor)') == 1)

    def test_snake_to_camel(self):
        self.assertEqual(snake_to_camel(''), '')
        self.assertEqual(snake_to_camel('footprint'), 'footprint')
        self.assertEqual(snake_to_camel('footprint_start'), 'footprintStart')

    def test_camel_to_snake(self):
        self.assertEqual(camel_to_snake(''), '')
        self.assertEqual(camel_to_snake('footprint'), 'footprint')
        self.assertEqual(camel_to_snake('footprintStart'), 'footprint_start')


class GeonameUtilTest(TestCase):

    def test_format_name(self):
        data = {'name': 'Albany', 'adminName1': '', 'countryName': 'US'}
        self.assertEqual('Albany, US', GeonameUtil().format_name(data))

        data['adminName1'] = 'NY'
        self.assertEqual('Albany, NY, US', GeonameUtil().format_name(data))

    def test_get_place_by_id(self):
        content = {
            'name': 'Osgiliath',
            'adminName1': 'Gondor', 'countryName': 'Middle Earth',
            'lat': '-44.2599', 'lng': '170.1043'
        }

        with self.settings(GEONAMES_KEY='abcd'):
            with mock.patch('footprints.main.utils.requests.get') as mock_get:
                mock_get.return_value.json.return_value = content

                place = GeonameUtil().get_or_create_place('123')
                self.assertEqual(
                    place.canonical_place.canonical_name,
                    'Osgiliath, Gondor, Middle Earth')
                self.assertEqual(
                    place.alternate_name,
                    'Osgiliath, Gondor, Middle Earth')

                self.assertEqual(place.id,
                                 GeonameUtil().get_or_create_place('123').id)
