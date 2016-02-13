from django.test.testcases import TestCase

from footprints.batch.tests.factories import BatchRowFactory
from footprints.main.tests.factories import ImprintFactory, BookCopyFactory, \
    FootprintFactory, WrittenWorkFactory


class BatchRowTest(TestCase):

    def test_aggregate_notes(self):
        row = BatchRowFactory()
        self.assertEquals(
            row.aggregate_notes(),
            'http://clio.columbia.edu/catalog/11262981<br />Levita, Elijah.')

        row = BatchRowFactory(catalog_url='')
        self.assertEquals(row.aggregate_notes(), 'Levita, Elijah.')

    def test_similar_footprints(self):
        row = BatchRowFactory()
        self.assertFalse(row.similar_footprints().exists())

        work = WrittenWorkFactory(title=row.writtenwork_title)
        imprint = ImprintFactory(title=row.imprint_title, work=work)
        copy = BookCopyFactory(imprint=imprint)
        FootprintFactory(
            medium=row.medium, provenance=row.provenance,
            call_number=row.call_number, notes=row.aggregate_notes(),
            book_copy=copy)

        self.assertTrue(row.similar_footprints().exists())
