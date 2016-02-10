from django.test.testcases import TestCase

from footprints.batch.validators import validate_catalog_url, validate_date


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
