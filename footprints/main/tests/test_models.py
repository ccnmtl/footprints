from django.db.utils import IntegrityError
from django.test import TestCase

from footprints.main.models import Language, DigitalFormat, \
    ExtendedDateFormat, Name, StandardizedIdentification, \
    Actor, Place, Imprint
from footprints.main.tests.factories import RoleFactory, \
    ActorFactory, PlaceFactory, CollectionFactory, \
    WrittenWorkFactory, ImprintFactory, BookCopyFactory, FootprintFactory, \
    PersonFactory


class BasicModelTest(TestCase):

    def test_fuzzy_date(self):
        a_date = ExtendedDateFormat.objects.create(edtf_format='2004?-06-11')
        self.assertEquals(a_date.__unicode__(), '2004?-06-11')

    def test_language(self):
        language = Language.objects.create(name='English')
        self.assertEquals(language.__unicode__(), 'English')

        try:
            Language.objects.create(name='English')
            self.fail('expected an already exists error')
        except IntegrityError:
            pass  # expected

    def test_digital_format(self):
        digital_format = DigitalFormat.objects.create(name='png')
        self.assertEquals(digital_format.__unicode__(), 'png')

        try:
            DigitalFormat.objects.create(name='png')
            self.fail('expected an already exists error')
        except IntegrityError:
            pass  # expected

    def test_name(self):
        name = Name.objects.create(name='Prince')
        self.assertEquals(name.__unicode__(), 'Prince')

    def test_standardized_identification(self):
        si = StandardizedIdentification.objects.create(identifier='foo',
                                                       identifier_type='LOC')

        self.assertEquals(si.__unicode__(), 'foo [Library of Congress] ')

        si = StandardizedIdentification.objects.create(
            identifier='bar', identifier_type='BHB',
            identifier_text='Barish')

        self.assertEquals(si.__unicode__(),
                          'bar [Bibliography of the Hebrew Book] Barish')

    def test_person(self):
        person = PersonFactory()
        self.assertEquals(person.__unicode__(), 'Last, First Middle Esq')

    def test_actor(self):
        person = PersonFactory()
        role = RoleFactory()
        actor = Actor.objects.create(person=person, role=role)

        # No Alternate Name
        self.assertEquals(actor.__unicode__(),
                          'Last, First Middle Esq (%s)' % role.name)

        # With Alternate Name
        actor = ActorFactory()
        self.assertEquals(actor.__unicode__(),
                          'Homer, First Middle Esq (%s)' % actor.role.name)

    def test_place(self):
        place = Place.objects.create(continent='EU')
        self.assertEquals(place.__unicode__(), 'Europe')

        place = PlaceFactory()
        self.assertEquals(place.__unicode__(),
                          'Smyrna, Greece, Balkan Peninsula, Europe')

    def test_collection(self):
        collection = CollectionFactory(name='The Morgan Collection')
        self.assertEquals(collection.__unicode__(), 'The Morgan Collection')

    def test_written_work(self):
        work = WrittenWorkFactory()
        self.assertEquals(work.__unicode__(), 'The Odyssey')

    def test_imprint(self):
        imprint = Imprint.objects.create(work=WrittenWorkFactory())
        self.assertEquals(imprint.__unicode__(), 'The Odyssey')

        imprint = ImprintFactory()
        self.assertEquals(imprint.__unicode__(),
                          'The Odyssey, Edition 1 (1984~)')

    def test_book_copy(self):
        copy = BookCopyFactory()
        self.assertEquals(copy.__unicode__(), 'The Odyssey, Edition 1 (1984~)')

    def test_footprint(self):
        footprint = FootprintFactory()
        self.assertEquals(footprint.__unicode__(), 'Provenance')
