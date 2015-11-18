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
        self.assertEquals(person_name(actor), 'Albert Einstein')

    def test_imprint_display_name(self):
        book_copy = BookCopyFactory()
        self.assertEquals(imprint_display(book_copy),
                          'The Odyssey, Edition 1 (c. 1984)')

    def test_work_title(self):
        imprint = ImprintFactory()
        self.assertEquals(work_title(imprint), 'The Odyssey')

    def test_languages(self):
        footprint = FootprintFactory()
        self.assertEquals(language(footprint),
                          footprint.language.first().name)

    def test_imprint_title(self):
        footprint = FootprintFactory()
        self.assertEquals(imprint_title(footprint),
                          'The Odyssey, Edition 1')

    def test_imprint_date(self):
        footprint = FootprintFactory()
        self.assertEquals(imprint_date(footprint).__unicode__(),
                          'c. 1984')

    def test_owner(self):
        footprint = FootprintFactory()
        self.assertEquals(owner(footprint), '')

        role, created = Role.objects.get_or_create(name="Owner")
        actor = ActorFactory(role=role)
        footprint.actor.add(actor)

        self.assertEquals(owner(footprint), actor.person.name)
