from decimal import Decimal

from django.db.utils import IntegrityError
from django.test import TestCase

from footprints.main.models import Language, DigitalFormat, \
    ExtendedDate, StandardizedIdentification, \
    Actor, Imprint, FOOTPRINT_LEVEL, IMPRINT_LEVEL, WRITTENWORK_LEVEL, Role, \
    Place, Footprint, WrittenWork, BookCopy, StandardizedIdentificationType, \
    SLUG_BHB
from footprints.main.tests.factories import RoleFactory, \
    ActorFactory, PlaceFactory, CollectionFactory, \
    WrittenWorkFactory, ImprintFactory, BookCopyFactory, FootprintFactory, \
    PersonFactory, DigitalObjectFactory, ExtendedDateFactory


class BasicModelTest(TestCase):

    def test_language(self):
        language = Language.objects.create(name='English')
        self.assertEquals(language.__unicode__(), 'English')

        with self.assertRaises(IntegrityError):
            Language.objects.create(name='English')

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

        with self.assertRaises(IntegrityError):
            DigitalFormat.objects.create(name='png')

    def test_standardized_identification(self):
        stt = StandardizedIdentificationType.objects.create(
            name="Sample", slug="SSS", level=IMPRINT_LEVEL)
        si = StandardizedIdentification.objects.create(identifier='foo',
                                                       identifier_type=stt)

        self.assertEquals(si.__unicode__(), 'foo')
        self.assertEquals(si.authority(), 'Sample')

        si = StandardizedIdentification.objects.create(identifier='foo',
                                                       identifier_type=None)
        self.assertEquals(si.__unicode__(), 'foo')
        self.assertIsNone(si.authority())

    def test_person(self):
        person = PersonFactory(name='Cicero')
        self.assertEquals(person.__unicode__(), "Cicero")

        person.digital_object.add(DigitalObjectFactory())
        self.assertEquals(person.percent_complete(), 100)

    def test_place(self):
        latlng = '50.064650,19.944979'
        place = Place.objects.create(position=latlng)
        self.assertEquals(place.__unicode__(), '')
        self.assertTrue(place.match_string(latlng))
        self.assertFalse(place.match_string('12.34,56.789'))

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

        # references
        self.assertEquals(work.references(), 0)
        copy = BookCopyFactory(imprint=ImprintFactory(work=work))
        FootprintFactory(book_copy=copy)
        FootprintFactory(book_copy=copy)
        FootprintFactory()  # noise
        self.assertEquals(work.references(), 2)

    def test_book_copy(self):
        copy = BookCopyFactory()
        self.assertTrue(
            copy.__unicode__().endswith('The Odyssey, Edition 1 (c. 1984)'))
        # copy.digital_object.add(DigitalObjectFactory())
        # self.assertEquals(copy.percent_complete(), 100)

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
        self.assertFalse(footprint.is_bare())

        footprint.digital_object.add(DigitalObjectFactory())
        self.assertEquals(footprint.calculate_percent_complete(), 100)

        self.assertEquals(footprint.display_title(), "The Odyssey")

        owner_role = Role.objects.get_owner_role()
        footprint.actor.add(ActorFactory(role=owner_role))
        self.assertEquals(footprint.owners().count(), 1)

        work = WrittenWork.objects.create()
        imprint = Imprint.objects.create(work=work)
        book_copy = BookCopy.objects.create(imprint=imprint)
        footprint = Footprint.objects.create(medium="Medium",
                                             provenance="Provenance",
                                             book_copy=book_copy)
        self.assertTrue(footprint.is_bare())


class ExtendedDateTest(TestCase):

    use_cases = {
        '999': 'invalid',
        '1xxx': '2nd millenium',
        '2xxx': '3rd millenium',
        '14xx': '15th century',  # PRECISION_CENTURY
        '192x': '1920s',  # PRECISION_DECADE
        '1613': '1613',  # PRECISION_YEAR
        '1944-11': 'November 1944',  # PRECISION_MONTH
        '1659-06-30': 'June 30, 1659',  # PRECISION_DAY
        '1659~': 'c. 1659',  # uncertain
        '1659?': '1659?',  # approximate
        '1659?~': 'c. 1659?',  # approximate & uncertain
        '16xx/1871': '1600s - 1871',
        '1557-09/1952-01-31': 'September 1557 - January 31, 1952',
        '1829/open': '1829 - present',
        'unknown/1736': '? - 1736',
    }

    def test_use_cases(self):
        for key, val in self.use_cases.items():
            e = ExtendedDate(edtf_format=key)
            self.assertEquals(e.__unicode__(), val)

    def test_create_from_dict(self):
        values = {
            'is_range': True,
            'millenium1': 2, 'century1': 0, 'decade1': 0, 'year1': 1,
            'month1': 1, 'day1': 1,
            'approximate1': True, 'uncertain1': True,
            'millenium2': 2, 'century2': 0, 'decade2': None, 'year2': None,
            'month2': None, 'day2': None,
            'approximate2': False, 'uncertain2': False}

        dt = ExtendedDate.objects.from_dict(values)
        self.assertEquals(dt.edtf_format, '2001-01-01?~/20xx')

    def test_to_edtf(self):
        mgr = ExtendedDate.objects
        dt = mgr.to_edtf(2, None, None, None, None, None, True, True)
        self.assertEquals(dt, '2xxx?~')

        dt = mgr.to_edtf(2, 0, None, None, None, None, True, True)
        self.assertEquals(dt, '20xx?~')

        dt = mgr.to_edtf(2, 0, 1, 5, None, None, False, False)
        self.assertEquals(dt, '2015')

        dt = mgr.to_edtf(2, 0, 1, 5, 2, None, False, False)
        self.assertEquals(dt, '2015-02')

        dt = mgr.to_edtf(2, 0, 1, 5, 12, 31, False, False)
        self.assertEquals(dt, '2015-12-31')

    def test_match_string(self):
        edtf = ExtendedDateFactory()
        self.assertTrue(edtf.match_string('approximately 1984'))
        self.assertFalse(edtf.match_string('1984'))

    def test_create_from_string(self):
        dt = ExtendedDate.objects.create_from_string('approximately 1983')
        self.assertEquals(dt.edtf_format, '1983~')

        dt = ExtendedDate.objects.create_from_string('before 1984')
        self.assertEquals(dt.edtf_format, 'unknown/1984')


class ImprintTest(TestCase):

    def test_percent_complete(self):
        i = ImprintFactory()
        # default 'factory settings'
        self.assertEquals(i.percent_complete(), 88)
        # eliminate one of them
        i.notes = None
        self.assertEquals(i.percent_complete(), 77)

    def test_basics(self):
        imprint = Imprint.objects.create(work=WrittenWorkFactory())
        self.assertEquals(imprint.__unicode__(), 'The Odyssey')

        imprint = ImprintFactory()
        self.assertEquals(imprint.__unicode__(),
                          'The Odyssey, Edition 1 (c. 1984)')

        # imprint.digital_object.add(DigitalObjectFactory())
        # self.assertEquals(imprint.percent_complete(), 100)

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

        # references
        self.assertEquals(imprint.references(), 0)
        copy = BookCopyFactory(imprint=imprint)
        FootprintFactory(book_copy=copy)
        FootprintFactory(book_copy=copy)
        FootprintFactory()  # noise
        self.assertEquals(imprint.references(), 2)

    def test_get_or_create_by_attributes(self):
        bhb_number = '94677047'

        imprint, created = Imprint.objects.get_or_create_by_attributes(
            bhb_number, 'The Odyssey', 'The Odyssey, Edition 1',
            'approximately 1984')

        self.assertEquals(imprint.title, 'The Odyssey, Edition 1')
        self.assertEquals(imprint.work.title, 'The Odyssey')
        self.assertEquals(imprint.date_of_publication.edtf_format, '1984~')

        q = imprint.standardized_identifier.filter(
            identifier=bhb_number, identifier_type__slug=SLUG_BHB)
        self.assertTrue(q.exists())


class ActorTest(TestCase):

    def test_basics(self):
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

    def test_get_or_create_by_attributes(self):
        role = RoleFactory()
        viaf = '94677047'

        actor, created = Actor.objects.get_or_create_by_attributes(
            'Grace Hopper', None, role, None, None)
        self.assertEquals(actor.person.name, 'Grace Hopper')
        self.assertEquals(actor.role, role)
        self.assertIsNone(actor.alias)
        self.assertIsNone(actor.person.birth_date)
        self.assertIsNone(actor.person.death_date)
        self.assertIsNone(actor.person.standardized_identifier)

        # name match results in the same object
        # attributes are updated if no viaf match, yes name match
        Actor.objects.get_or_create_by_attributes(
            'Grace Hopper', viaf, role, 'December 9, 1906', 'January 1, 1992')
        actor.person.refresh_from_db()
        self.assertEquals(actor.person.birth_date.edtf_format, '1906-12-09')
        self.assertEquals(actor.person.death_date.edtf_format, '1992-01-01')
        self.assertEquals(
            actor.person.standardized_identifier.identifier, viaf)

        # same viaf and role results in the same object
        actor2, created = Actor.objects.get_or_create_by_attributes(
            'Grace Hopper', viaf, role, None, None)
        self.assertEquals(actor, actor2)

        # same name and role results in the same object
        # attributes are not updated if they already exist
        actor2, created = Actor.objects.get_or_create_by_attributes(
            'Grace Hopper', None, role, None, None)
        self.assertEquals(actor, actor2)
        actor.person.refresh_from_db()
        self.assertEquals(actor.person.birth_date.edtf_format, '1906-12-09')
        self.assertEquals(actor.person.death_date.edtf_format, '1992-01-01')
        self.assertEquals(
            actor.person.standardized_identifier.identifier, viaf)

        # same name/viaf and different role results in same person, diff actor
        role2 = RoleFactory()
        actor2, created = Actor.objects.get_or_create_by_attributes(
            'Grace Hopper', None, role2, None, None)
        self.assertNotEquals(actor, actor2)
        self.assertEquals(actor.person, actor2.person)

        # same viaf diff name results in same person, diff actor w/alias
        role2 = RoleFactory()
        actor2, created = Actor.objects.get_or_create_by_attributes(
            'Amazing Grace', viaf, role2, None, None)
        self.assertNotEquals(actor, actor2)
        self.assertEquals(actor2.alias, 'Amazing Grace')
        self.assertEquals(actor.person, actor2.person)
