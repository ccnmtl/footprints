from django.test.testcases import TestCase

from footprints.batch.tests.factories import BatchRowFactory
from footprints.batch.validators import validate_date, \
    validate_numeric
from footprints.main.tests.factories import RoleFactory


class ValidatorsTest(TestCase):

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

    def test_validate_catalog_url(self):
        row = BatchRowFactory(catalog_url=None)
        self.assertTrue(row.validate_catalog_url())

        row = BatchRowFactory(catalog_url='http://www.google.com')
        self.assertTrue(row.validate_catalog_url())

        row = BatchRowFactory(catalog_url='')
        self.assertTrue(row.validate_catalog_url())

        row = BatchRowFactory(catalog_url='foobarbaz')
        self.assertFalse(row.validate_catalog_url())

    def test_validate_footprint_actor_role(self):
        # valid actor name & role
        RoleFactory(name='Expurgator')
        row = BatchRowFactory()
        self.assertTrue(row.validate_footprint_actor_role())

        # empty name/role
        row = BatchRowFactory(footprint_actor=None, footprint_actor_role=None)
        self.assertTrue(row.validate_footprint_actor_role())

        # name specified, role not specified
        row = BatchRowFactory(footprint_actor_role=None)
        self.assertFalse(row.validate_footprint_actor_role())

        # invalid role
        row = BatchRowFactory(footprint_actor_role='foo')
        self.assertFalse(row.validate_footprint_actor_role())

    def test_validate_footprint_actor(self):
        # valid actor name & role
        RoleFactory(name='Expurgator')
        row = BatchRowFactory()
        self.assertTrue(row.validate_footprint_actor())

        # empty name/role
        row = BatchRowFactory(footprint_actor=None, footprint_actor_role=None)
        self.assertTrue(row.validate_footprint_actor())

        # valid role, no actor name
        row = BatchRowFactory(footprint_actor=None)
        self.assertFalse(row.validate_footprint_actor())

    def test_validate_medium(self):
        row = BatchRowFactory(medium='')
        self.assertTrue(row.validate_medium())

        row = BatchRowFactory(medium='Dedication in imprint')
        self.assertTrue(row.validate_medium())

        row = BatchRowFactory(medium='foo')
        self.assertFalse(row.validate_medium())
