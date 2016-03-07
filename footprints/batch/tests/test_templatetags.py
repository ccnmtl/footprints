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
        row = BatchRowFactory(imprint_title='')
        self.assertEquals(validate_field_value(row, fld, ''),
                          'missing has-error')

        row = BatchRowFactory()
        self.assertEquals(validate_field_value(row, fld, 'Sample'), 'valid')

        # non-required field
        row = BatchRowFactory(footprint_date=None)
        fld = BatchRow._meta.get_field('footprint_date')
        self.assertEquals(validate_field_value(row, fld, None), 'empty')

        row = BatchRowFactory(footprint_date='')
        self.assertEquals(validate_field_value(row, fld, ''), 'empty')

        row = BatchRowFactory(footprint_date='foobar')
        self.assertEquals(validate_field_value(row, fld, 'foobar'),
                          'invalid has-error')

        row = BatchRowFactory(footprint_date=1902)
        self.assertEquals(validate_field_value(row, fld, '1902'), 'valid')
