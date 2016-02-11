from django.test.testcases import TestCase

from footprints.batch.validators import validate_catalog_url, validate_date, \
    validate_numeric, validate_footprint_actor_role, validate_medium, \
    validate_latlng
from footprints.main.tests.factories import RoleFactory


class ValidatorsTest(TestCase):

    def test_validate_catalog_url(self):
        self.assertTrue(validate_catalog_url(None))
        self.assertTrue(validate_catalog_url(''))
        self.assertFalse(validate_catalog_url('foobarbaz'))
        self.assertFalse(validate_catalog_url('1982'))

    def test_validate_date(self):
        self.assertTrue(validate_date(None))
        self.assertTrue(validate_date(''))
        self.assertTrue(validate_date('1987'))
        self.assertFalse(validate_date('abcdefg'))

    def test_validate_numeric(self):
        self.assertTrue(validate_numeric(None))
        self.assertTrue(validate_numeric(''))
        self.assertTrue(validate_numeric('1987'))
        self.assertFalse(validate_numeric('a12b'))
        self.assertFalse(validate_numeric('abcd'))

    def test_validate_footprint_actor_role(self):
        RoleFactory(name='seller')

        self.assertTrue(validate_footprint_actor_role(None))
        self.assertTrue(validate_footprint_actor_role(''))
        self.assertTrue(validate_footprint_actor_role('seller'))
        self.assertFalse(validate_footprint_actor_role('buyer'))

    def test_validate_medium(self):
        self.assertTrue(validate_medium(None))
        self.assertTrue(validate_medium(''))
        self.assertTrue(validate_medium('Dedication in imprint'))
        self.assertFalse(validate_medium('foo'))

    def test_validate_latlong(self):
        self.assertTrue(validate_latlng(None))
        self.assertTrue(validate_latlng(''))
        self.assertTrue(validate_latlng('41.0136,28.9550'))
        self.assertTrue(validate_latlng('41.0136, 28.9550'))
        self.assertFalse(validate_latlng('12312312312'))
