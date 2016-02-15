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
