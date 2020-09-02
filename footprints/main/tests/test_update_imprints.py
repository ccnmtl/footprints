from django.test import TestCase

from footprints.main.management.commands.update_imprints import Command, \
    FIELD_TITLE
from footprints.main.models import ImprintAlternateTitle, SLUG_BHB
from footprints.main.tests.factories import ImprintFactory, LanguageFactory


TEST_ROW = [
    '105180',
    'heb',
    'author',
    'alternate title',
    'written work title',
    'subtitle',
    'place murky',
    'publication place',
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
