from json import loads

from django.core.urlresolvers import reverse
from django.test import TestCase
from django.test.client import Client, RequestFactory

from footprints.main.models import Footprint, Actor
from footprints.main.tests.factories import (UserFactory, WrittenWorkFactory,
                                             ImprintFactory, FootprintFactory,
                                             PersonFactory, RoleFactory,
                                             PlaceFactory, ActorFactory)
from footprints.main.views import CreateFootprintView, FootprintAddActorView


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
        the_json = loads(response.content)
        self.assertTrue(the_json['error'], True)

        response = self.client.post('/accounts/login/',
                                    {'username': self.user.username,
                                     'password': 'test'},
                                    HTTP_X_REQUESTED_WITH='XMLHttpRequest')
        self.assertEquals(response.status_code, 200)
        the_json = loads(response.content)
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


class DetailViewTest(TestCase):
    def setUp(self):
        self.user = UserFactory()

        self.person_detail = reverse('person-detail-view',
                                     kwargs={'pk': PersonFactory().id})

        self.place_detail = reverse('place-detail-view',
                                    kwargs={'pk': PlaceFactory().id})

        self.work_detail = reverse('writtenwork-detail-view',
                                   kwargs={'pk': WrittenWorkFactory().id})

        self.footprint_detail = reverse('footprint-detail-view',
                                        kwargs={'pk': FootprintFactory().id})

    def test_get_logged_out(self):
        self.assertEquals(self.client.get(self.person_detail).status_code, 302)
        self.assertEquals(self.client.get(self.place_detail).status_code, 302)
        self.assertEquals(self.client.get(self.work_detail).status_code, 302)
        self.assertEquals(self.client.get(self.footprint_detail).status_code,
                          302)

    def test_get_logged_in(self):
        self.client.login(username=self.user.username, password="test")

        self.assertEquals(self.client.get(self.person_detail).status_code, 200)
        self.assertEquals(self.client.get(self.place_detail).status_code, 200)
        self.assertEquals(self.client.get(self.work_detail).status_code, 200)
        self.assertEquals(self.client.get(self.footprint_detail).status_code,
                          200)


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
        PersonFactory(name='Alpha')

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

    def test_post(self):
        data = {'footprint-title': 'New Title',
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
        self.assertEquals(fp.title, 'New Title')
        self.assertEquals(fp.medium, 'New Medium')
        self.assertEquals(fp.provenance, 'New Provenance')
        self.assertEquals(fp.notes, 'Some notes')


class FootprintAddActorViewTest(TestCase):

    def test_create_actor_new_person(self):
        role = RoleFactory()

        view = FootprintAddActorView()
        view.create_actor('', 'Alpha Centauri', role, 'Alf')

        Actor.objects.get(person__name='Alpha Centauri',
                          role=role, alias='Alf')

    def test_create_actor_existing_person(self):
        alpha = PersonFactory(name='Alpha')
        role = RoleFactory()

        view = FootprintAddActorView()
        view.create_actor(alpha.id, alpha.name, role, 'Alf')

        Actor.objects.get(person__id=alpha.id,
                          person__name=alpha.name,
                          role=role, alias='Alf')

    def test_create_actor_existing_person_new_name(self):
        alpha = PersonFactory(name='Alpha')
        role = RoleFactory()

        view = FootprintAddActorView()
        view.create_actor(alpha.id, 'Alpha Beta', role, 'Alf')

        try:
            Actor.objects.get(person__id=alpha.id)
        except:
            pass  # expected

        Actor.objects.get(person__name='Alpha Beta',
                          role=role, alias='Alf')


class FootprintRemoveActorViewTest(TestCase):
    def setUp(self):
        self.user = UserFactory()
        self.staff = UserFactory(is_staff=True)
        self.footprint = FootprintFactory()

        self.actor = ActorFactory()
        self.footprint.actor.add(self.actor)

        self.remove_url = reverse('footprint-remove-actor-view',
                                  kwargs={'footprint_id': self.footprint.id,
                                          'actor_id': self.actor.id})

    def test_post_expected_errors(self):
        # not logged in
        self.assertEquals(self.client.post(self.remove_url).status_code, 302)

        self.client.login(username=self.user.username, password="test")

        # no ajax
        self.assertEquals(self.client.post(self.remove_url).status_code, 405)

        # no permissions
        response = self.client.post(self.remove_url, {},
                                    HTTP_X_REQUESTED_WITH='XMLHttpRequest')
        self.assertEquals(response.status_code, 403)

        # invalid actor id
        bad_remove_url = reverse('footprint-remove-actor-view',
                                 kwargs={'footprint_id': self.footprint.id,
                                         'actor_id': 500})
        self.client.login(username=self.staff.username, password="test")
        response = self.client.post(bad_remove_url, {},
                                    HTTP_X_REQUESTED_WITH='XMLHttpRequest')
        self.assertEquals(response.status_code, 404)

    def test_post_success(self):
        self.assertEquals(self.footprint.actor.count(), 1)

        self.client.login(username=self.staff.username, password="test")
        response = self.client.post(self.remove_url,
                                    {},
                                    HTTP_X_REQUESTED_WITH='XMLHttpRequest')
        self.assertEquals(response.status_code, 200)
        self.assertTrue(loads(response.content)['success'])
        self.assertEquals(self.footprint.actor.count(), 0)


class FootprintAddDateView(TestCase):

    def setUp(self):
        self.user = UserFactory()
        self.staff = UserFactory(is_staff=True)
        self.footprint = FootprintFactory(title="Custom", associated_date=None)

        self.url = reverse('footprint-add-date-view',
                           kwargs={'footprint_id': self.footprint.id})

    def test_post_expected_errors(self):
        # not logged in
        self.assertEquals(self.client.post(self.url).status_code, 302)

        self.client.login(username=self.user.username, password="test")

        # no ajax
        self.assertEquals(self.client.post(self.url).status_code, 405)

        # no permissions
        response = self.client.post(self.url, {},
                                    HTTP_X_REQUESTED_WITH='XMLHttpRequest')
        self.assertEquals(response.status_code, 403)

    def test_post_no_data(self):
        self.client.login(username=self.staff.username, password="test")
        response = self.client.post(self.url,
                                    {},
                                    HTTP_X_REQUESTED_WITH='XMLHttpRequest')
        self.assertEquals(response.status_code, 200)
        the_json = loads(response.content)
        self.assertFalse(the_json['success'])

    def test_post_success(self):
        self.client.login(username=self.staff.username, password="test")
        response = self.client.post(self.url,
                                    {'associated_date': '1673'},
                                    HTTP_X_REQUESTED_WITH='XMLHttpRequest')
        self.assertEquals(response.status_code, 200)
        the_json = loads(response.content)

        footprint = Footprint.objects.get(title='Custom')  # refresh from db
        self.assertTrue(the_json['success'])
        self.assertEquals(the_json['footprint_id'], footprint.id)
        self.assertEquals(footprint.associated_date.id,
                          the_json['associated_date'])
