from django.test.testcases import TestCase

from footprints.main.admin import person_name, imprint_display, work_title, \
    language, imprint_title, imprint_date, owner
from footprints.main.models import Role
from footprints.main.tests.factories import PersonFactory, ActorFactory, \
    BookCopyFactory, ImprintFactory, FootprintFactory


class CustomAdminViewTest(TestCase):

    def test_person_name(self):
        person = PersonFactory(name='Albert Einstein')
        actor = ActorFactory(person=person)
        self.assertEqual(person_name(actor), 'Albert Einstein')

    def test_imprint_display_name(self):
        book_copy = BookCopyFactory()
        self.assertEqual(imprint_display(book_copy),
                         'The Odyssey, Edition 1 (c. 1984)')

    def test_work_title(self):
        imprint = ImprintFactory()
        self.assertEqual(work_title(imprint), imprint.work.title)

    def test_languages(self):
        footprint = FootprintFactory()
        self.assertEqual(language(footprint),
                         footprint.language.first().name)

    def test_imprint_title(self):
        footprint = FootprintFactory()
        self.assertEqual(imprint_title(footprint),
                         'The Odyssey, Edition 1')

    def test_imprint_date(self):
        footprint = FootprintFactory()
        self.assertEqual(str(imprint_date(footprint)), 'c. 1984')

    def test_owner(self):
        footprint = FootprintFactory()
        self.assertEqual(owner(footprint), '')

        role, created = Role.objects.get_or_create(name="Owner")
        actor = ActorFactory(role=role)
        footprint.actor.add(actor)

        self.assertEqual(owner(footprint), actor.person.name)
