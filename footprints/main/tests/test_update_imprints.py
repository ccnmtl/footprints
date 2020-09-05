from django.test import TestCase

from footprints.main.management.commands.update_imprints import Command, \
    FIELD_TITLE, FIELD_PLACE_MURKY, FIELD_PUBLICATION_PLACE
from footprints.main.models import ImprintAlternateTitle, SLUG_BHB, Role
from footprints.main.tests.factories import ImprintFactory, LanguageFactory, \
    PlaceFactory, RoleFactory


TEST_ROW = [
    '105180',
    'heb',
    'author',
    'alternate imprint title',
    'written work title',
    'subtitle',
    'Cracóvia',  # FIELD_PLACE_MURKY
    'Cracow',  # FIELD_PUBLICATION_PLACE
    'locstatus',
    'print murky',
    'publisher',
    'year murky',
    '1653',
    'date status',
    'range from',
    'range to',
    'decade',
    'haskama',
    'note'
]


class UpdateImprintsTest(TestCase):

    def test_format_bhb_number(self):
        cmd = Command()
        self.assertEqual(cmd.format_bhb_number('12345'), '000012345')
        self.assertEqual(cmd.format_bhb_number('000012345'), '000012345')

    def test_handle_title(self):
        cmd = Command()
        bhb_number = '000105180'

        imprint = ImprintFactory(title=TEST_ROW[FIELD_TITLE])

        # don't create an alternate title if we have a match
        cmd.handle_title(imprint, TEST_ROW, bhb_number)
        self.assertEqual(ImprintAlternateTitle.objects.count(), 0)

        # create an alternate title record for this bhb number
        imprint = ImprintFactory()
        language = LanguageFactory(name='Hebrew', marc_code='heb')
        cmd.handle_title(imprint, TEST_ROW, bhb_number)

        self.assertEqual(ImprintAlternateTitle.objects.count(), 1)
        iat = ImprintAlternateTitle.objects.first()
        self.assertEqual(iat.alternate_title, 'alternate imprint title')
        self.assertEqual(iat.standardized_identifier.identifier, bhb_number)
        self.assertEqual(iat.standardized_identifier.identifier_type.slug,
                         SLUG_BHB)
        self.assertEqual(iat.language, language)

        # but don't create duplicates
        cmd.handle_title(imprint, TEST_ROW, bhb_number)
        self.assertEqual(ImprintAlternateTitle.objects.count(), 1)

    def test_handle_language(self):
        language = LanguageFactory(marc_code='heb')
        cmd = Command()

        imprint = ImprintFactory()
        cmd.handle_language(imprint, TEST_ROW)
        self.assertTrue(language in imprint.language.all())

    def test_handle_publication_date(self):
        cmd = Command()

        imprint = ImprintFactory()
        cmd.handle_publication_date(imprint, TEST_ROW)
        self.assertEqual(imprint.publication_date.__str__(), 'c. 1984')

        imprint = ImprintFactory(publication_date=None)
        cmd.handle_publication_date(imprint, TEST_ROW)
        self.assertEqual(imprint.publication_date.__str__(), '1653')

    def test_handle_notes(self):
        cmd = Command()

        imprint = ImprintFactory()
        cmd.handle_notes(imprint, TEST_ROW)
        self.assertEqual(
            imprint.notes,
            'lorem ipsum<br />Subtitle: subtitle<br />'
            'BHB note: note')

    def test_handle_place(self):
        cmd = Command()

        # An imprint with an existing place
        # Same Canonical Place, Updated Place alternate_name
        imprint = ImprintFactory()
        existing_place = imprint.place
        cmd.handle_place(imprint, TEST_ROW)
        self.assertEqual(existing_place.id, imprint.place.id)
        self.assertEqual(
            existing_place.canonical_place, imprint.place.canonical_place)
        self.assertEqual(existing_place.alternate_name, 'Cracóvia')

        # An imprint with no place should first try to match an
        # existing CanonicalPlace and existing Place
        imprint = ImprintFactory(place=None)
        cmd.handle_place(imprint, TEST_ROW)
        self.assertEqual(existing_place.id, imprint.place.id)
        self.assertEqual(
            existing_place.canonical_place, imprint.place.canonical_place)
        self.assertEqual(existing_place.alternate_name, 'Cracóvia')

        # An imprint with no place should first get an
        # existing CanonicalPlace and existing Place
        row = TEST_ROW.copy()
        row[FIELD_PLACE_MURKY] = 'Krakkó'
        row[FIELD_PUBLICATION_PLACE] = 'Kraków'
        imprint = ImprintFactory(place=None)
        cmd.handle_place(imprint, row)
        self.assertNotEqual(existing_place.id, imprint.place.id)
        self.assertEqual(imprint.place.alternate_name, 'Krakkó')
        self.assertEqual(
            existing_place.canonical_place, imprint.place.canonical_place)

    def test_create_imprint(self):
        cmd = Command()
        bhb_number = '000105180'
        language = LanguageFactory(marc_code='heb')
        PlaceFactory(alternate_name='Cracow')
        RoleFactory(name=Role.AUTHOR)
        RoleFactory(name=Role.PUBLISHER)

        imprint = cmd.create_imprint(TEST_ROW, bhb_number)

        self.assertEqual(imprint.title, 'alternate imprint title')
        self.assertEqual(imprint.work.title, 'written work title')
        self.assertEqual(imprint.get_bhb_number().identifier, bhb_number)
        self.assertTrue(language in imprint.language.all())
        self.assertEqual(imprint.publication_date.__str__(), '1653')
        self.assertEqual(imprint.place.alternate_name, 'Cracóvia')
        self.assertEqual(imprint.place.canonical_place.canonical_name,
                         'Kraków, Poland')
        self.assertEqual(imprint.notes,
                         'Subtitle: subtitle<br />'
                         'BHB note: note')

    def test_get_or_create_actor(self):
        cmd = Command()

        role = RoleFactory(name=Role.AUTHOR)

        # Create person & actor
        actor = cmd.get_or_create_actor(role, 'Jacob Weil')
        self.assertEqual(actor.role.name, Role.AUTHOR)
        self.assertEqual(actor.alias, 'Jacob Weil')
        self.assertEqual(actor.person.name, 'Jacob Weil')

        # Pickup existing person & actor
        actor2 = cmd.get_or_create_actor(role, 'Jacob Weil')
        self.assertEqual(actor.id, actor2.id)

    def test_handle_actors(self):
        cmd = Command()

        RoleFactory(name=Role.AUTHOR)
        RoleFactory(name=Role.PUBLISHER)
        imprint = ImprintFactory()

        cmd.handle_actors(imprint, TEST_ROW)

        self.assertEqual(imprint.actor.count(), 2)
        actor = imprint.actor.filter(alias='publisher').first()
        self.assertIsNotNone(actor)
        self.assertEqual(actor.role.name, Role.PUBLISHER)
        self.assertEqual(actor.person.name, 'publisher')

        self.assertEqual(imprint.work.actor.count(), 2)
        actor = imprint.work.actor.filter(alias='author').first()
        self.assertIsNotNone(actor)
        self.assertEqual(actor.role.name, Role.AUTHOR)
        self.assertEqual(actor.person.name, 'author')

    def test_log_entry(self):
        bhb_number = '000105180'
        LanguageFactory(marc_code='heb')
        PlaceFactory(alternate_name='Cracow')
        RoleFactory(name=Role.AUTHOR)
        RoleFactory(name=Role.PUBLISHER)

        cmd = Command()
        imprint = cmd.create_imprint(TEST_ROW, bhb_number)

        entry = cmd.log_entry(1, imprint, 'created')
        self.assertTrue(entry.startswith('"2","created"'))
