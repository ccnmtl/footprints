import json

from django.test import TestCase
from django.test.client import Client, RequestFactory

from footprints.main.models import Role, Footprint
from footprints.main.tests.factories import (UserFactory, RoleFactory,
                                             PersonFactory, ActorFactory,
                                             NameFactory, WrittenWorkFactory,
                                             ImprintFactory, FootprintFactory)
from footprints.main.views import CreateFootprintView


class BasicTest(TestCase):
    def setUp(self):
        self.c = Client()

    def test_root(self):
        response = self.c.get("/")
        self.assertEquals(response.status_code, 200)

    def test_smoketest(self):
        response = self.c.get("/smoketest/")
        self.assertEquals(response.status_code, 200)
        assert "PASS" in response.content


class PasswordTest(TestCase):

    def setUp(self):
        super(TestCase, self).setUp()

        self.user = UserFactory(is_staff=True)

    def test_logged_out(self):
        response = self.client.get('/accounts/password_change/')
        self.assertEquals(response.status_code, 405)

        response = self.client.get('/accounts/password_reset/')
        self.assertEquals(response.status_code, 200)

    def test_logged_in(self):
        self.assertTrue(self.client.login(
            username=self.user.username, password="test"))
        response = self.client.get('/accounts/password_change/')
        self.assertEquals(response.status_code, 200)

        response = self.client.get('/accounts/password_reset/')
        self.assertEquals(response.status_code, 200)


class IndexViewTest(TestCase):

    def setUp(self):
        super(TestCase, self).setUp()

        self.user = UserFactory()

    def test_anonymous_user(self):
        response = self.client.get('/')
        self.assertEquals(response.status_code, 200)
        self.assertTrue('Log In' in response.content)
        self.assertFalse('Log Out' in response.content)

    def test_logged_in_user(self):
        self.assertTrue(self.client.login(
            username=self.user.username, password="test"))
        response = self.client.get('/')
        self.assertEquals(response.status_code, 200)
        self.assertFalse('Log In' in response.content)
        self.assertTrue('Log Out' in response.content)


class LoginTest(TestCase):

    def setUp(self):
        super(TestCase, self).setUp()

        self.user = UserFactory()

    def test_login_get(self):
        response = self.client.get('/accounts/login/')
        self.assertEquals(response.status_code, 405)

    def test_login_post_noajax(self):
        response = self.client.post('/accounts/login/',
                                    {'username': self.user.username,
                                     'password': 'test'})
        self.assertEquals(response.status_code, 405)

    def test_login_post_ajax(self):
        response = self.client.post('/accounts/login/',
                                    {'username': '',
                                     'password': ''},
                                    HTTP_X_REQUESTED_WITH='XMLHttpRequest')
        self.assertEquals(response.status_code, 200)
        the_json = json.loads(response.content)
        self.assertTrue(the_json['error'], True)

        response = self.client.post('/accounts/login/',
                                    {'username': self.user.username,
                                     'password': 'test'},
                                    HTTP_X_REQUESTED_WITH='XMLHttpRequest')
        self.assertEquals(response.status_code, 200)
        the_json = json.loads(response.content)
        self.assertTrue(the_json['next'], "/")
        self.assertTrue('error' not in the_json)


class LogoutTest(TestCase):

    def setUp(self):
        super(TestCase, self).setUp()

        self.user = UserFactory()

    def test_logout_user(self):
        self.client.login(username=self.user.username, password="test")

        response = self.client.get('/accounts/logout/?next=/', follow=True)
        self.assertEquals(response.status_code, 200)
        self.assertTrue('Log In' in response.content)
        self.assertFalse('Log Out' in response.content)


class ListViewTests(TestCase):
    def test_title_listview(self):
        WrittenWorkFactory(title='Alpha')
        ImprintFactory(title='Beta')
        FootprintFactory(title='Gamma')

        response = self.client.get('/api/title/', {'q': 'Foo'},
                                   HTTP_X_REQUESTED_WITH='XMLHttpRequest')
        self.assertEquals(response.status_code, 200)
        self.assertEquals(len(response.data), 0)

        response = self.client.get('/api/title/', {'q': 'Alp'},
                                   HTTP_X_REQUESTED_WITH='XMLHttpRequest')
        self.assertEquals(response.status_code, 200)
        self.assertEquals(len(response.data), 1)
        self.assertEquals(response.data[0]['title'], 'Alpha')

    def test_name_listview(self):
        NameFactory(name="Alpha")

        response = self.client.get('/api/name/', {'q': 'Foo'},
                                   HTTP_X_REQUESTED_WITH='XMLHttpRequest')
        self.assertEquals(response.status_code, 200)
        self.assertEquals(len(response.data), 0)

        response = self.client.get('/api/name/', {'q': 'Alp'},
                                   HTTP_X_REQUESTED_WITH='XMLHttpRequest')
        self.assertEquals(response.status_code, 200)
        self.assertEquals(len(response.data), 1)
        self.assertEquals(response.data[0]['name'], 'Alpha')


class CreateFootprintViewTest(TestCase):

    def test_get_or_create_author_new_actor(self):
        # No associated id indicates a new actor
        actor = CreateFootprintView().get_or_create_author('', 'New Actor')
        self.assertEquals(actor.person.name.name, 'New Actor')

    def test_get_or_create_author_existing_actor(self):
        # a person with multiple roles
        author_role = Role.objects.get_author_role()
        publisher_role = RoleFactory(name='Publisher')
        person = PersonFactory()

        author = ActorFactory(role=author_role, person=person)
        ActorFactory(role=publisher_role, person=person)

        actor = CreateFootprintView().get_or_create_author(
            str(author.actor_name.id), author.actor_name.name)
        self.assertEquals(author, actor)

        actor = CreateFootprintView().get_or_create_author(
            str(author.person.name.id), author.person.name.name)
        self.assertEquals(author, actor)

    def test_get_or_create_author_existing_person(self):
        # a Person with no roles
        person = PersonFactory()
        author_role = Role.objects.get_author_role()

        # Existing Actor with role author
        actor = CreateFootprintView().get_or_create_author(str(person.name.id),
                                                           person.name.name)
        self.assertEquals(actor.person, person)
        self.assertEquals(actor.role, author_role)

    def test_get_names(self):
        person = PersonFactory()
        data = {'author_': 'Alpha',
                'author_%s' % person.name.id: person.name}

        request = RequestFactory().post('/footprint/create/', data)
        view = CreateFootprintView()
        view.request = request

        names = view.get_names()
        self.assertEquals(names[0], ('', 'Alpha'))
        self.assertEquals(names[1], (str(person.name.id), person.name.name))

    def test_post(self):
        data = {'author_': 'New Name',
                'footprint-title': 'New Title',
                'footprint-medium': 'New Medium',
                'footprint-provenance': 'New Provenance',
                'footprint-notes': 'Some notes'}

        request = RequestFactory().post('/footprint/create/', data)
        view = CreateFootprintView()
        view.request = request

        response = view.post()
        self.assertEquals(response.status_code, 302)

        # there's only one in the system
        fp = Footprint.objects.all()[0]
        self.assertEquals(fp.book_copy.imprint.actor.count(), 1)
        self.assertEquals(fp.title, 'New Title')
        self.assertEquals(fp.medium, 'New Medium')
        self.assertEquals(fp.provenance, 'New Provenance')
        self.assertEquals(fp.notes, 'Some notes')
