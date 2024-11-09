import datetime

from django.contrib.auth.models import Group
from django.db.utils import IntegrityError
from django.test import TestCase
from django.utils import timezone

from footprints.main.models import Language, DigitalFormat, \
    ExtendedDate, StandardizedIdentification, \
    Actor, Imprint, FOOTPRINT_LEVEL, IMPRINT_LEVEL, WRITTENWORK_LEVEL, Role, \
    Place, Footprint, WrittenWork, BookCopy, StandardizedIdentificationType, \
    CanonicalPlace
from footprints.main.templatetags.moderation import \
    flag_empty_narrative, flag_percent_complete, flag_empty_call_number, \
    flag_empty_bhb_number, moderation_flags, moderation_footprints, \
    flag_creator
from footprints.main.tests.factories import RoleFactory, \
    ActorFactory, PlaceFactory, CollectionFactory, \
    WrittenWorkFactory, ImprintFactory, BookCopyFactory, FootprintFactory, \
    PersonFactory, DigitalObjectFactory, ExtendedDateFactory, \
    EmptyFootprintFactory, StandardizedIdentificationFactory, UserFactory, \
    ImprintAlternateTitleFactory
from footprints.main.utils import string_to_point


class LanguageTest(TestCase):

    def test_language(self):
        language = Language.objects.create(name='English')
        self.assertEqual(str(language), 'English')

        with self.assertRaises(IntegrityError):
            Language.objects.create(name='English')


class RoleTest(TestCase):

    def test_role(self):
        owner = RoleFactory(name="Owner", level=FOOTPRINT_LEVEL)
        publisher = RoleFactory(name="Publisher", level=IMPRINT_LEVEL)
        author = RoleFactory(name="Author", level=WRITTENWORK_LEVEL)
        printer = RoleFactory(name="Printer", level=IMPRINT_LEVEL)

        qs = Role.objects.for_footprint()
        self.assertEqual(qs.count(), 1)
        self.assertEqual(qs.first(), owner)

        qs = Role.objects.for_imprint().order_by('name')
        self.assertEqual(qs.count(), 2)
        self.assertEqual(qs[0], printer)
        self.assertEqual(qs[1], publisher)

        qs = Role.objects.for_work()
        self.assertEqual(qs.count(), 1)
        self.assertEqual(qs.first(), author)


class DigitalFormatTest(TestCase):

    def test_digital_format(self):
        digital_format = DigitalFormat.objects.create(name='png')
        self.assertEqual(str(digital_format), 'png')

        with self.assertRaises(IntegrityError):
            DigitalFormat.objects.create(name='png')


class StandardizedIdentificationTest(TestCase):

    def test_standardized_identification(self):
        stt = StandardizedIdentificationType.objects.create(
            name="Sample", slug="SSS", level=IMPRINT_LEVEL)
        si = StandardizedIdentification.objects.create(identifier='foo',
                                                       identifier_type=stt)

        self.assertEqual(str(si), 'foo')
        self.assertEqual(si.authority(), 'Sample')

        si = StandardizedIdentification.objects.create(identifier='foo',
                                                       identifier_type=None)
        self.assertEqual(str(si), 'foo')
        self.assertIsNone(si.authority())


class PersonTest(TestCase):

    def test_person(self):
        person = PersonFactory(name='Cicero')
        self.assertEqual(str(person), "Cicero")

        person.digital_object.add(DigitalObjectFactory())
        self.assertEqual(person.percent_complete(), 100)


class PlaceTest(TestCase):

    def test_titles(self):
        p = PlaceFactory()
        self.assertEqual(p.display_title(), 'Cracow, Poland')

        p = Place(alternate_name='Poland')
        self.assertEqual(p.display_title(), 'Poland')
        self.assertEqual(str(p), 'Poland')

    def test_string_to_point(self):
        latlng = '50.06465,19.944979'
        pt = string_to_point(latlng)
        place = CanonicalPlace.objects.create(latlng=pt, canonical_name='Foo')

        self.assertEqual(str(place), 'Foo')
        self.assertTrue(place.match_string(latlng))
        self.assertFalse(place.match_string('12.34,56.789'))


class CollectionTest(TestCase):
    def test_collection(self):
        collection = CollectionFactory(name='The Morgan Collection')
        self.assertEqual(str(collection), 'The Morgan Collection')


class WrittenWorkTest(TestCase):

    def test_written_work(self):
        work = WrittenWorkFactory()
        self.assertEqual(str(work), work.title)
        self.assertEqual(work.percent_complete(), 100)

        author_role, created = Role.objects.get_or_create(name=Role.AUTHOR)
        work.actor.add(ActorFactory(role=author_role))
        self.assertEqual(work.authors().count(), 1)

        self.assertTrue(work.title in work.description())

    def test_references(self):
        work = WrittenWorkFactory()
        self.assertEqual(work.references(), 0)
        copy = BookCopyFactory(imprint=ImprintFactory(work=work))
        FootprintFactory(book_copy=copy)
        FootprintFactory(book_copy=copy)
        FootprintFactory()  # noise
        self.assertEqual(work.references(), 2)

    def test_identifiers(self):
        work = WrittenWorkFactory()
        loc_type = StandardizedIdentificationType.objects.loc()
        idf = StandardizedIdentificationFactory(identifier_type=loc_type)
        work.standardized_identifier.add(idf)
        self.assertEqual(work.get_library_of_congress_identifier(), idf)


class BookCopyTest(TestCase):

    def test_book_copy(self):
        copy = BookCopyFactory()
        self.assertTrue(
            str(copy).endswith('The Odyssey, Edition 1 (c. 1984)'))

        self.assertTrue(copy.identifier() in copy.description())

    def test_has_expurgator(self):
        copy = BookCopyFactory()
        self.assertFalse(copy.has_expurgator())

        role = RoleFactory(name=Role.EXPURGATOR, level=FOOTPRINT_LEVEL)
        expurgator = ActorFactory(role=role)

        fp = FootprintFactory(book_copy=copy)
        fp.actor.add(expurgator)
        self.assertTrue(copy.has_expurgator())

    def test_has_censor(self):
        copy = BookCopyFactory()
        self.assertFalse(copy.has_censor())

        role = RoleFactory(name=Role.CENSOR, level=IMPRINT_LEVEL)
        censor = ActorFactory(role=role)

        copy.imprint.actor.add(censor)
        self.assertTrue(copy.has_censor())

    def test_book_copy_owners(self):
        copy = BookCopyFactory()
        owner = RoleFactory(name="Owner", level=FOOTPRINT_LEVEL)
        owner1 = ActorFactory(role=owner)
        owner2 = ActorFactory(role=owner)
        owner3 = ActorFactory(role=owner)

        footprint1 = FootprintFactory(
            book_copy=copy,
            associated_date=ExtendedDateFactory(edtf_format='1981'))
        footprint1.actor.add(owner1)
        footprint2 = FootprintFactory(
            book_copy=copy,
            associated_date=ExtendedDateFactory(edtf_format='1982'))
        footprint2.actor.add(owner2)
        footprint3 = FootprintFactory(
            associated_date=ExtendedDateFactory(edtf_format='1983'))
        footprint3.actor.add(owner3)

        owners = copy.owners()
        self.assertEqual(owners.count(), 2)
        self.assertIsNotNone(owners.get(id=owner1.id))
        self.assertIsNotNone(owners.get(id=owner2.id))

        current_owners = copy.current_owners()
        self.assertEqual(current_owners.count(), 1)
        self.assertIsNotNone(current_owners.get(id=owner2.id))

    def test_book_copy_dates(self):
        copy = BookCopyFactory()

        EmptyFootprintFactory(book_copy=copy)
        FootprintFactory(
            book_copy=copy,
            associated_date=ExtendedDateFactory(edtf_format=''))
        FootprintFactory(
            book_copy=copy,
            associated_date=ExtendedDateFactory(edtf_format='1981/2000'))
        FootprintFactory(
            book_copy=copy,
            associated_date=ExtendedDateFactory(edtf_format='1982'))
        FootprintFactory(
            book_copy=copy,
            associated_date=ExtendedDateFactory(edtf_format='1983'))

        self.assertEqual(
            copy.footprints_start_date(), datetime.date(1981, 1, 1))
        self.assertEqual(
            copy.footprints_end_date(), datetime.date(2000, 12, 31))


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
            self.assertEqual(str(e), val)

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
        self.assertEqual(dt.edtf_format, '2001-01-01?~/20xx')

    def test_create_from_dict_missing_elements(self):
        values = {
            'is_range': True,
            'millenium1': 2, 'century1': 0, 'decade1': 0, 'year1': 1,
            'month1': 1,
            'approximate1': True, 'uncertain1': True,
            'millenium2': 2, 'century2': 0, 'decade2': None, 'year2': None,
            'month2': None, 'day2': None,
            'approximate2': False, 'uncertain2': False}

        dt = ExtendedDate.objects.from_dict(values)
        self.assertEqual(dt.edtf_format, '2001-01?~/20xx')

    def test_to_edtf(self):
        mgr = ExtendedDate.objects
        dt = mgr.to_edtf(2, None, None, None, None, None, True, True)
        self.assertEqual(dt, '2xxx?~')

        dt = mgr.to_edtf(2, 0, None, None, None, None, True, True)
        self.assertEqual(dt, '20xx?~')

        dt = mgr.to_edtf(2, 0, 1, 5, None, None, False, False)
        self.assertEqual(dt, '2015')

        dt = mgr.to_edtf(2, 0, 1, 5, 2, None, False, False)
        self.assertEqual(dt, '2015-02')

        dt = mgr.to_edtf(2, 0, 1, 5, 12, 31, False, False)
        self.assertEqual(dt, '2015-12-31')

    def test_match_string(self):
        edtf = ExtendedDateFactory()
        self.assertTrue(edtf.match_string('approximately 1984'))
        self.assertFalse(edtf.match_string('1984'))

    def test_create_from_string(self):
        dt = ExtendedDate.objects.create_from_string('approximately 1983')
        self.assertEqual(dt.edtf_format, '1983~')

        dt = ExtendedDate.objects.create_from_string('before 1984')
        self.assertEqual(dt.edtf_format, 'unknown/1984')

    def test_invalid_month(self):
        dt = ExtendedDate.objects.create(edtf_format='uuuu-uu-17/uuuu-uu-18')
        self.assertEqual(str(dt), ' 17, uuuu -  18, uuuu')

    def test_end_date(self):
        dt = ExtendedDate.objects.create(edtf_format='1700')
        self.assertEqual(dt.end(), datetime.date(1700, 12, 31))

        dt = ExtendedDate.objects.create(edtf_format='1700/open')
        self.assertIsNone(dt.end())

        dt = ExtendedDate.objects.create(edtf_format='1700/unknown')
        self.assertEqual(dt.end(), datetime.date(1705, 12, 31))

        dt = ExtendedDate.objects.create(edtf_format='1700/18xx')
        self.assertEqual(dt.end(), datetime.date(1899, 12, 31))


class ImprintTest(TestCase):

    def test_percent_complete(self):
        i = ImprintFactory()
        # default 'factory settings'
        self.assertEqual(i.percent_complete(), 88)
        # eliminate one of them
        i.notes = None
        self.assertEqual(i.percent_complete(), 77)

    def test_basics(self):
        imprint = Imprint.objects.create(work=WrittenWorkFactory())
        self.assertEqual(str(imprint), imprint.work.title)

        imprint = ImprintFactory()
        self.assertEqual(str(imprint), 'The Odyssey, Edition 1 (c. 1984)')

        # imprint.digital_object.add(DigitalObjectFactory())
        # self.assertEqual(imprint.percent_complete(), 100)

        publisher = RoleFactory(name="Publisher", level=IMPRINT_LEVEL)
        printer = RoleFactory(name="Printer", level=IMPRINT_LEVEL)

        imprint.actor.add(ActorFactory(alias="Publisher", role=publisher))
        imprint.actor.add(ActorFactory(alias="Printer", role=printer))
        printers = imprint.printers()
        self.assertEqual(len(printers), 1)
        self.assertEqual(printers[0].alias, "Printer")

        publishers = imprint.publishers()
        self.assertEqual(len(publishers), 1)
        self.assertEqual(publishers[0].alias, "Publisher")

        # references
        self.assertEqual(imprint.references(), 0)
        copy = BookCopyFactory(imprint=imprint)
        FootprintFactory(book_copy=copy)
        FootprintFactory(book_copy=copy)
        FootprintFactory()  # noise
        self.assertEqual(imprint.references(), 2)

        self.assertTrue(imprint.title in imprint.description())

    def test_get_or_create_by_attributes(self):
        bhb_number = '94677047'

        imprint, created = Imprint.objects.get_or_create_by_attributes(
            bhb_number, 'The Odyssey', 'The Odyssey, Edition 1',
            'approximately 1984')

        self.assertEqual(imprint.title, 'The Odyssey, Edition 1')
        self.assertEqual(imprint.work.title, 'The Odyssey')
        self.assertEqual(imprint.publication_date.edtf_format, '1984~')

        bhb_type = StandardizedIdentificationType.objects.bhb()
        q = imprint.standardized_identifier.filter(
            identifier=bhb_number, identifier_type=bhb_type)
        self.assertTrue(q.exists())

    def test_has_bhb_number(self):
        imprint, created = Imprint.objects.get_or_create_by_attributes(
            '94677047', 'The Odyssey', 'The Odyssey, Edition 1',
            'approximately 1984')
        imprint2 = ImprintFactory()

        self.assertTrue(imprint.has_bhb_number())
        self.assertFalse(imprint2.has_bhb_number())

    def test_get_bhb_number(self):
        imprint, created = Imprint.objects.get_or_create_by_attributes(
            '94677047', 'The Odyssey', 'The Odyssey, Edition 1',
            'approximately 1984')
        bhb_type = StandardizedIdentificationType.objects.bhb()
        si = StandardizedIdentification.objects.create(
            identifier='94677047', identifier_type=bhb_type)
        imprint2 = ImprintFactory()

        self.assertEqual(imprint.get_bhb_number().identifier, si.identifier)
        self.assertEqual(imprint2.get_bhb_number(), None)

    def test_has_oclc_number(self):
        imprint, created = Imprint.objects.get_or_create_by_attributes(
            '94677047', 'The Odyssey', 'The Odyssey, Edition 1',
            'approximately 1984')
        imprint2 = ImprintFactory()

        oclc_type = StandardizedIdentificationType.objects.oclc()
        idf = StandardizedIdentificationFactory(identifier_type=oclc_type)
        imprint.standardized_identifier.add(idf)

        self.assertTrue(imprint.has_oclc_number())
        self.assertFalse(imprint2.has_oclc_number())

    def test_get_oclc_number(self):
        imprint, created = Imprint.objects.get_or_create_by_attributes(
            '94677047', 'The Odyssey', 'The Odyssey, Edition 1',
            'approximately 1984')
        imprint2 = ImprintFactory()

        oclc_type = StandardizedIdentificationType.objects.oclc()
        idf = StandardizedIdentificationFactory(identifier_type=oclc_type)
        imprint.standardized_identifier.add(idf)

        self.assertEqual(imprint.get_oclc_number(), idf)
        self.assertEqual(imprint2.get_oclc_number(), None)

    def test_has_censor(self):
        imprint = ImprintFactory()
        self.assertFalse(imprint.has_censor())

        role = RoleFactory(name=Role.CENSOR, level=IMPRINT_LEVEL)
        censor = ActorFactory(role=role)

        imprint.actor.add(censor)
        self.assertTrue(imprint.has_censor())

    def test_get_alternate_titles(self):
        imprint = ImprintFactory()
        self.assertEqual(imprint.get_alternate_titles(), [])

        bhb_number = '094677047'
        imprint, created = Imprint.objects.get_or_create_by_attributes(
            bhb_number, 'The Odyssey', 'The Odyssey, Edition 1',
            'approximately 1984')
        self.assertEqual(imprint.get_alternate_titles().count(), 0)

        title = ImprintAlternateTitleFactory(bhb_number=bhb_number)
        self.assertEqual(imprint.get_alternate_titles().count(), 1)
        self.assertEqual(
            imprint.get_alternate_titles().first(),
            title.alternate_title)


class ActorTest(TestCase):

    def test_basics(self):
        person = PersonFactory()
        role = RoleFactory()
        actor = Actor.objects.create(person=person, role=role)

        # No Alternate Name
        self.assertEqual(
            str(actor),
            '%s (%s)' % (actor.person.name, role.name))

        # With Alternate Name
        actor = ActorFactory(role=role)
        self.assertEqual(
            str(actor),
            '%s as %s (%s)' % (actor.person.name, actor.alias, role.name))

    def test_get_or_create_by_attributes(self):
        role = RoleFactory()
        viaf = '94677047'

        actor, created = Actor.objects.get_or_create_by_attributes(
            'Grace Hopper', None, role, None, None)
        self.assertEqual(actor.person.name, 'Grace Hopper')
        self.assertEqual(actor.role, role)
        self.assertIsNone(actor.alias)
        self.assertIsNone(actor.person.birth_date)
        self.assertIsNone(actor.person.death_date)
        self.assertIsNone(actor.person.standardized_identifier)

        # name match results in the same object
        # attributes are updated if no viaf match, yes name match
        Actor.objects.get_or_create_by_attributes(
            'Grace Hopper', viaf, role, 'December 9, 1906', 'January 1, 1992')
        actor.person.refresh_from_db()
        self.assertEqual(actor.person.birth_date.edtf_format, '1906-12-09')
        self.assertEqual(actor.person.death_date.edtf_format, '1992-01-01')
        self.assertEqual(
            actor.person.standardized_identifier.identifier, viaf)

        # same viaf and role results in the same object
        actor2, created = Actor.objects.get_or_create_by_attributes(
            'Grace Hopper', viaf, role, None, None)
        self.assertEqual(actor, actor2)

        # same name and role results in the same object
        # attributes are not updated if they already exist
        actor2, created = Actor.objects.get_or_create_by_attributes(
            'Grace Hopper', None, role, None, None)
        self.assertEqual(actor, actor2)
        actor.person.refresh_from_db()
        self.assertEqual(actor.person.birth_date.edtf_format, '1906-12-09')
        self.assertEqual(actor.person.death_date.edtf_format, '1992-01-01')
        self.assertEqual(
            actor.person.standardized_identifier.identifier, viaf)

        # same name/viaf and different role results in same person, diff actor
        role2 = RoleFactory()
        actor2, created = Actor.objects.get_or_create_by_attributes(
            'Grace Hopper', None, role2, None, None)
        self.assertNotEqual(actor, actor2)
        self.assertEqual(actor.person, actor2.person)

        # same viaf diff name results in same person, diff actor w/alias
        role2 = RoleFactory()
        actor2, created = Actor.objects.get_or_create_by_attributes(
            'Amazing Grace', viaf, role2, None, None)
        self.assertNotEqual(actor, actor2)
        self.assertEqual(actor2.alias, 'Amazing Grace')
        self.assertEqual(actor.person, actor2.person)


class FootprintTest(TestCase):

    def test_footprint(self):
        footprint = FootprintFactory()
        self.assertEqual(str(footprint), 'Provenance')
        self.assertFalse(footprint.is_bare())

        footprint.digital_object.add(DigitalObjectFactory())
        self.assertEqual(footprint.calculate_percent_complete(), 100)

        self.assertTrue(footprint.display_title().startswith('The Odyssey'))

        owner_role, created = Role.objects.get_or_create(name=Role.OWNER)
        footprint.actor.add(ActorFactory(role=owner_role))
        self.assertEqual(footprint.owners().count(), 1)

        work = WrittenWork.objects.create()
        imprint = Imprint.objects.create(work=work)
        book_copy = BookCopy.objects.create(imprint=imprint)
        footprint = Footprint.objects.create(medium="Medium",
                                             provenance="Provenance",
                                             book_copy=book_copy)
        self.assertTrue(footprint.is_bare())

        self.assertTrue('Footprint Place' in footprint.description())

    def test_individual_flags(self):
        f1 = EmptyFootprintFactory()
        self.assertTrue(flag_percent_complete(f1))
        self.assertTrue(flag_empty_narrative(f1))
        self.assertTrue(flag_empty_call_number(f1))
        self.assertTrue(flag_empty_bhb_number(f1))

        a = moderation_flags(f1)
        self.assertEqual(len(a), 4)

    def test_has_expurgator(self):
        role = RoleFactory(name=Role.EXPURGATOR, level=FOOTPRINT_LEVEL)
        expurgator = ActorFactory(role=role)

        fp = FootprintFactory()
        self.assertFalse(fp.has_expurgator())
        fp.actor.add(expurgator)
        self.assertTrue(fp.has_expurgator())

    def test_is_terminal(self):
        copy = BookCopyFactory()
        footprint1 = FootprintFactory(
            book_copy=copy,
            associated_date=ExtendedDateFactory(edtf_format='1452'))
        footprint2 = FootprintFactory(
            book_copy=copy,
            associated_date=ExtendedDateFactory(edtf_format='1300'))
        footprint3 = FootprintFactory(
            book_copy=copy,
            associated_date=ExtendedDateFactory(edtf_format='1500'))

        self.assertFalse(footprint1.is_terminal())
        self.assertFalse(footprint2.is_terminal())
        self.assertTrue(footprint3.is_terminal())


class FootprintModerationTest(TestCase):

    def test_moderation_footprints(self):
        f1 = EmptyFootprintFactory()  # < 50% complete
        self.assertTrue(moderation_flags(f1))

        f2 = FootprintFactory(narrative=None)  # empty narrative
        self.assertTrue(moderation_flags(f2))

        f3 = FootprintFactory(
            medium='Bookseller/auction catalog (1850-present)',
            call_number=None)
        self.assertTrue(moderation_flags(f3))

        # excluded footprints
        today = timezone.now()
        f4 = FootprintFactory()
        f4.save_verified(True)
        self.assertTrue(moderation_flags(f4))
        self.assertTrue((f4.verified_modified_at - today).seconds < 1)

        # has a bhb identifier
        bhb_type = StandardizedIdentificationType.objects.bhb()
        idf = StandardizedIdentificationFactory(identifier_type=bhb_type)
        f5 = FootprintFactory()
        f5.book_copy.imprint.standardized_identifier.add(idf)
        self.assertFalse(moderation_flags(f5))

        # created by a new contributor
        grp = Group.objects.get(name='Creator')
        self.assertIsNotNone(grp)
        creator = UserFactory(group=grp)
        f6 = FootprintFactory(created_by=creator)
        self.assertTrue(f6.created_by.groups.filter(name='Creator').exists())

        qs = moderation_footprints()
        self.assertEqual(qs.count(), 4)

        self.assertTrue(f1 in qs)
        self.assertTrue(f2 in qs)
        self.assertTrue(f3 in qs)
        self.assertFalse(f4 in qs)
        self.assertFalse(f5 in qs)
        self.assertTrue(f6 in qs)

        # retrieve by id to resolve qs annotation
        # verify new_contributor value
        f1 = qs.get(id=f1.id)
        self.assertFalse(flag_creator(f1))

        f6 = qs.get(id=f6.id)
        self.assertTrue(flag_creator(f6))
