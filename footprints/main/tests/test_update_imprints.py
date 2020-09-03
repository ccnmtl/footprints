from django.test import TestCase

from footprints.main.management.commands.update_imprints import Command, \
    FIELD_TITLE, FIELD_PLACE_MURKY, FIELD_PUBLICATION_PLACE
from footprints.main.models import ImprintAlternateTitle, SLUG_BHB
from footprints.main.tests.factories import ImprintFactory, LanguageFactory


TEST_ROW = [
    '105180',
    'heb',
    'author',
    'alternate title',
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
        self.assertEqual(iat.alternate_title, 'alternate title')
        self.assertEqual(iat.standardized_identifier.identifier, bhb_number)
        self.assertEqual(iat.standardized_identifier.identifier_type.slug,
                         SLUG_BHB)
        self.assertEqual(iat.language, language)

        # but don't create duplicates
        cmd.handle_title(imprint, TEST_ROW, bhb_number)
        self.assertEqual(ImprintAlternateTitle.objects.count(), 1)

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
            'Notes from the BHB: note<br />')

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
