from django.test.testcases import TestCase
from footprints.batch.tests.factories import BatchRowFactory
from footprints.main.models import StandardizedIdentificationType, \
    StandardizedIdentification
from footprints.main.tests.factories import ImprintFactory, BookCopyFactory, \
    FootprintFactory, WrittenWorkFactory, StandardizedIdentificationFactory, \
    ActorFactory, CanonicalPlaceFactory, PlaceFactory


class BatchRowTest(TestCase):

    def test_aggregate_notes(self):
        row = BatchRowFactory()
        self.assertEqual(
            row.aggregate_notes(),
            'http://clio.columbia.edu/catalog/11262981<br />Levita, Elijah.')

        row = BatchRowFactory(catalog_url='')
        self.assertEqual(row.aggregate_notes(), 'Levita, Elijah.')

    def test_strip_trailing_period(self):
        row = BatchRowFactory(writtenwork_title='abcd')
        self.assertEqual(row.writtenwork_title, 'abcd')

        row = BatchRowFactory(writtenwork_title='efg.')
        self.assertEqual(row.writtenwork_title, 'efg')

    def test_similar_footprints(self):
        bhb_number = '1234'
        actor = ActorFactory()
        work = WrittenWorkFactory()

        cp = CanonicalPlaceFactory(position='50.064650,20.944979')
        place = PlaceFactory(canonical_place=cp)

        imprint = ImprintFactory(work=work, place=place)
        si = StandardizedIdentificationFactory(identifier=bhb_number)
        imprint.standardized_identifier.add(si)

        copy = BookCopyFactory(imprint=imprint)

        row = BatchRowFactory(
            imprint_title=imprint.title,
            publisher=imprint.actor.first().person.name,
            publication_location='50.064650,20.944979',
            bhb_number=bhb_number,
            writtenwork_title=work.title,
            writtenwork_author=work.actor.first().person.name,
            footprint_actor=actor.person.name,
            footprint_location='50.064650,19.944979')

        self.assertFalse(row.similar_footprints().exists())

        cp = CanonicalPlaceFactory(position='50.064650,19.944979')
        place = PlaceFactory(canonical_place=cp)
        fp = FootprintFactory(
            medium=row.medium, provenance=row.provenance,
            call_number=row.call_number, notes=row.aggregate_notes(),
            book_copy=copy,
            place=place)
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

        # book copy exists and the bhb numbers do not match
        copy = BookCopyFactory()
        row = BatchRowFactory()
        self.assertFalse(row.validate_book_copy_call_number())

        # book copy exists, and the bhb numbers match
        bhb_type = StandardizedIdentificationType.objects.bhb()
        si = StandardizedIdentification.objects.create(
            identifier=row.bhb_number, identifier_type=bhb_type)
        copy.imprint.standardized_identifier.add(si)
        copy.imprint.save()
        self.assertTrue(row.validate_book_copy_call_number())
