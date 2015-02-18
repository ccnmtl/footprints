from decimal import Decimal

from django.db.utils import IntegrityError
from django.test import TestCase

from footprints.main.models import Language, DigitalFormat, \
    ExtendedDateFormat, StandardizedIdentification, \
    Actor, Imprint, FOOTPRINT_LEVEL, IMPRINT_LEVEL, WRITTENWORK_LEVEL, Role, \
    Place
from footprints.main.tests.factories import RoleFactory, \
    ActorFactory, PlaceFactory, CollectionFactory, \
    WrittenWorkFactory, ImprintFactory, BookCopyFactory, FootprintFactory, \
    PersonFactory, DigitalObjectFactory


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

    def test_role(self):
        owner = RoleFactory(name="Owner", level=FOOTPRINT_LEVEL)
        publisher = RoleFactory(name="Publisher", level=IMPRINT_LEVEL)
        author = RoleFactory(name="Author", level=WRITTENWORK_LEVEL)
        printer = RoleFactory(name="Printer", level=IMPRINT_LEVEL)

        self.assertEquals(author, Role.objects.get_author_role())
        self.assertEquals(owner, Role.objects.get_owner_role())
        self.assertEquals(publisher, Role.objects.get_publisher_role())
        self.assertEquals(printer, Role.objects.get_printer_role())

        qs = Role.objects.for_footprint()
        self.assertEquals(qs.count(), 1)
        self.assertEquals(qs.first(), owner)

        qs = Role.objects.for_imprint().order_by('name')
        self.assertEquals(qs.count(), 2)
        self.assertEquals(qs[0], printer)
        self.assertEquals(qs[1], publisher)

        qs = Role.objects.for_work()
        self.assertEquals(qs.count(), 1)
        self.assertEquals(qs.first(), author)

    def for_footprint(self):
        return self.filter(level=FOOTPRINT_LEVEL)

    def for_imprint(self):
        return self.filter(level=IMPRINT_LEVEL)

    def for_work(self):
        return self.filter(level=WRITTENWORK_LEVEL)

    def test_digital_format(self):
        digital_format = DigitalFormat.objects.create(name='png')
        self.assertEquals(digital_format.__unicode__(), 'png')

        try:
            DigitalFormat.objects.create(name='png')
            self.fail('expected an already exists error')
        except IntegrityError:
            pass  # expected

    def test_standardized_identification(self):
        si = StandardizedIdentification.objects.create(identifier='foo',
                                                       identifier_type='LOC')

        self.assertEquals(si.__unicode__(), 'foo')

        si = StandardizedIdentification.objects.create(
            identifier='bar', identifier_type='BHB')

        self.assertEquals(si.__unicode__(),
                          'bar')

    def test_person(self):
        person = PersonFactory(name='Cicero')
        self.assertEquals(person.__unicode__(), "Cicero")

        person.digital_object.add(DigitalObjectFactory())

        self.assertEquals(person.percent_complete(), 100)

    def test_actor(self):
        person = PersonFactory()
        role = RoleFactory()
        actor = Actor.objects.create(person=person, role=role)

        # No Alternate Name
        self.assertEquals(
            actor.__unicode__(),
            '%s (%s)' % (actor.person.name, role.name))

        # With Alternate Name
        actor = ActorFactory(role=role)
        self.assertEquals(
            actor.__unicode__(),
            '%s as %s (%s)' % (actor.person.name, actor.alias, role.name))

    def test_place(self):
        place = Place.objects.create(position='50.064650,19.944979')
        self.assertEquals(place.__unicode__(), '')

        place = PlaceFactory()
        self.assertEquals(place.__unicode__(), 'Cracow, Poland')
        self.assertEquals(place.latitude(), Decimal('50.064650'))
        self.assertEquals(place.longitude(), Decimal('19.944979'))

    def test_collection(self):
        collection = CollectionFactory(name='The Morgan Collection')
        self.assertEquals(collection.__unicode__(), 'The Morgan Collection')

    def test_written_work(self):
        work = WrittenWorkFactory()
        self.assertEquals(work.__unicode__(), 'The Odyssey')

        self.assertEquals(work.percent_complete(), 100)

        author_role = Role.objects.get_author_role()
        work.actor.add(ActorFactory(role=author_role))
        self.assertEquals(work.authors().count(), 1)

    def test_imprint(self):
        imprint = Imprint.objects.create(work=WrittenWorkFactory())
        self.assertEquals(imprint.__unicode__(), 'The Odyssey')

        imprint = ImprintFactory()
        self.assertEquals(imprint.__unicode__(),
                          'The Odyssey, Edition 1 (1984~)')

        imprint.digital_object.add(DigitalObjectFactory())
        self.assertEquals(imprint.percent_complete(), 100)

        publisher = RoleFactory(name="Publisher", level=IMPRINT_LEVEL)
        printer = RoleFactory(name="Printer", level=IMPRINT_LEVEL)

        imprint.actor.add(ActorFactory(alias="Publisher", role=publisher))
        imprint.actor.add(ActorFactory(alias="Printer", role=printer))
        printers = imprint.printers()
        self.assertEquals(len(printers), 1)
        self.assertEquals(printers[0].alias, "Printer")

        publishers = imprint.publishers()
        self.assertEquals(len(publishers), 1)
        self.assertEquals(publishers[0].alias, "Publisher")

    def test_book_copy(self):
        copy = BookCopyFactory()
        self.assertTrue(
            copy.__unicode__().endswith('The Odyssey, Edition 1 (1984~)'))
        copy.digital_object.add(DigitalObjectFactory())
        self.assertEquals(copy.percent_complete(), 100)

    def test_book_copy_owners(self):
        copy = BookCopyFactory()
        owner = RoleFactory(name="Owner", level=FOOTPRINT_LEVEL)
        owner1 = ActorFactory(role=owner)
        owner2 = ActorFactory(role=owner)
        owner3 = ActorFactory(role=owner)

        footprint1 = FootprintFactory(book_copy=copy)
        footprint1.actor.add(owner1)
        footprint2 = FootprintFactory(book_copy=copy)
        footprint2.actor.add(owner2)
        footprint3 = FootprintFactory()
        footprint3.actor.add(owner3)

        owners = copy.owners()
        self.assertEquals(owners.count(), 2)
        self.assertIsNotNone(owners.get(id=owner1.id))
        self.assertIsNotNone(owners.get(id=owner2.id))

    def test_footprint(self):
        footprint = FootprintFactory()
        self.assertEquals(footprint.__unicode__(), 'Provenance')

        footprint.digital_object.add(DigitalObjectFactory())
        self.assertEquals(footprint.percent_complete(), 100)

        self.assertEquals(footprint.display_title(), "The Odyssey")

        owner_role = Role.objects.get_owner_role()
        footprint.actor.add(ActorFactory(role=owner_role))
        self.assertEquals(footprint.owners().count(), 1)
