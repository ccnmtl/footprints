from django.test.testcases import TestCase

from footprints.batch.tests.factories import BatchRowFactory
from footprints.main.tests.factories import ImprintFactory, BookCopyFactory, \
    FootprintFactory, WrittenWorkFactory, StandardizedIdentificationFactory, \
    ActorFactory


class BatchRowTest(TestCase):

    def test_aggregate_notes(self):
        row = BatchRowFactory()
        self.assertEquals(
            row.aggregate_notes(),
            'http://clio.columbia.edu/catalog/11262981<br />Levita, Elijah.')

        row = BatchRowFactory(catalog_url='')
        self.assertEquals(row.aggregate_notes(), 'Levita, Elijah.')

    def test_strip_trailing_period(self):
        row = BatchRowFactory(writtenwork_title='abcd')
        self.assertEquals(row.writtenwork_title, 'abcd')

        row = BatchRowFactory(writtenwork_title='efg.')
        self.assertEquals(row.writtenwork_title, 'efg')

    def test_similar_footprints(self):
        bhb_number = '1234'
        actor = ActorFactory()
        work = WrittenWorkFactory()
        imprint = ImprintFactory(work=work)
        si = StandardizedIdentificationFactory(identifier=bhb_number)
        imprint.standardized_identifier.add(si)

        copy = BookCopyFactory(imprint=imprint)

        row = BatchRowFactory(
            imprint_title=imprint.title,
            publisher=imprint.actor.first().person.name,
            publication_location='50.064650,19.944979',
            bhb_number=bhb_number,
            writtenwork_title=work.title,
            writtenwork_author=work.actor.first().person.name,
            footprint_actor=actor.person.name,
            footprint_location='50.064650,19.944979')

        self.assertFalse(row.similar_footprints().exists())

        fp = FootprintFactory(
            medium=row.medium, provenance=row.provenance,
            call_number=row.call_number, notes=row.aggregate_notes(),
            book_copy=copy)
        fp.actor.add(actor)

        self.assertTrue(row.similar_footprints().exists())

    def test_check_imprint_integrity(self):
        coord = '-61.999,-53.859'
        row = BatchRowFactory(publication_location=coord)

        # no match
        self.assertIsNone(row.check_imprint_integrity())

        # found imprint, fields are mismatched
        imprint = ImprintFactory()
        sid = StandardizedIdentificationFactory(identifier=row.bhb_number)
        imprint.standardized_identifier.add(sid)

        flds = ['literary work title']
        self.assertTrue(', '.join(flds) in row.check_imprint_integrity())

        # found imprint, fields match
        work = WrittenWorkFactory(title=row.writtenwork_title)
        imprint = ImprintFactory(title=row.imprint_title, work=work)

        sid = StandardizedIdentificationFactory(identifier=row.bhb_number)
        imprint.standardized_identifier.add(sid)

        self.assertIsNone(row.check_imprint_integrity())

    def test_validate_book_copy_call_number(self):
        # no book_copy_call_number
        row = BatchRowFactory(book_copy_call_number=None)
        self.assertTrue(row.validate_book_copy_call_number())

        row = BatchRowFactory(book_copy_call_number='abcde')
        self.assertTrue(row.validate_book_copy_call_number())

        # book copy exists, but the imprint title doesn't match batch row title
        copy = BookCopyFactory()
        row = BatchRowFactory()
        self.assertFalse(row.validate_book_copy_call_number())

        # book copy exists, and the imprint title matches batch row title
        copy.imprint.title = row.imprint_title
        copy.imprint.save()
        self.assertTrue(row.validate_book_copy_call_number())
