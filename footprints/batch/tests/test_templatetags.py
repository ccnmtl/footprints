from django.test.testcases import TestCase

from footprints.batch.models import BatchRow
from footprints.batch.templatetags.batchrowtags import field_value, \
    validate_field_value
from footprints.batch.tests.factories import BatchRowFactory


class BatchRowTest(TestCase):

    def test_field_value(self):
        fld = BatchRow._meta.get_field('publisher')
        value = field_value(BatchRowFactory(), fld)
        self.assertEquals(value, 'Eliezer Soncino')

    def test_validate_field_value(self):
        # required field
        fld = BatchRow._meta.get_field('imprint_title')
        self.assertEquals(validate_field_value(fld, None),
                          'missing has-error')
        self.assertEquals(validate_field_value(fld, ''),
                          'missing has-error')
        self.assertEquals(validate_field_value(fld, 'Sample'), 'valid')

        # non-required field
        fld = BatchRow._meta.get_field('footprint_date')
        self.assertEquals(validate_field_value(fld, None), 'empty')
        self.assertEquals(validate_field_value(fld, ''), 'empty')
        self.assertEquals(validate_field_value(fld, 'foobar'),
                          'invalid has-error')
        self.assertEquals(validate_field_value(fld, '1902'), 'valid')
