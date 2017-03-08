from json import loads
import json

from django.conf import settings
from django.core import mail
from django.core.files.uploadedfile import SimpleUploadedFile
from django.core.urlresolvers import reverse
from django.test.client import Client, RequestFactory, encode_multipart

from django.contrib.auth.models import AnonymousUser
from django.test import TestCase
from footprints.main.forms import ContactUsForm
from footprints.main.models import Footprint, Actor, Imprint, \
    StandardizedIdentificationType, ExtendedDate, Language, \
    WrittenWork, BookCopy
from footprints.main.search_indexes import format_sort_by
from footprints.main.serializers import \
    StandardizedIdentificationTypeSerializer, \
    StandardizedIdentificationSerializer, LanguageSerializer, \
    ExtendedDateSerializer, ActorSerializer
from footprints.main.tests.factories import (
    UserFactory, WrittenWorkFactory, ImprintFactory, FootprintFactory,
    PersonFactory, RoleFactory, PlaceFactory, ActorFactory, BookCopyFactory,
    ExtendedDateFactory, LanguageFactory, StandardizedIdentificationFactory)
from footprints.main.views import (
    CreateFootprintView, AddActorView, ContactUsView)
from footprints.main.viewsets import ImprintViewSet, BookCopyViewSet, \
    WrittenWorkViewSet


class BasicTest(TestCase):
    def test_root(self):
        response = self.client.get("/")
        self.assertEquals(response.status_code, 200)

    def test_smoketest(self):
        response = self.client.get("/smoketest/")
        self.assertEquals(response.status_code, 200)
        assert "PASS" in response.content

    def test_sign_s3_view(self):
        user = UserFactory()
        self.client.login(username=user.username, password="test")
        with self.settings(
                AWS_ACCESS_KEY='',
                AWS_SECRET_KEY='',
                AWS_S3_UPLOAD_BUCKET=''):
            r = self.client.get(
                "/sign_s3/?s3_object_name=default_name&s3_object_type=foo")
            self.assertEqual(r.status_code, 200)
            j = json.loads(r.content)
            self.assertTrue('signed_request' in j)


class PasswordTest(TestCase):

    def setUp(self):
        super(TestCase, self).setUp()

        self.user = UserFactory(is_staff=True)

    def test_logged_out(self):
        response = self.client.get('/accounts/password_change/')
        self.assertEquals(response.status_code, 302)

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

        self.work_detail = reverse('writtenwork-detail-view',
                                   kwargs={'pk': WrittenWorkFactory().id})

        self.footprint_detail = reverse('footprint-detail-view',
                                        kwargs={'pk': FootprintFactory().id})

    def test_get_logged_out(self):
        self.assertEquals(self.client.get(self.work_detail).status_code, 200)
        self.assertEquals(self.client.get(self.footprint_detail).status_code,
                          200)

    def test_get_logged_in(self):
        self.client.login(username=self.user.username, password="test")

        self.assertEquals(self.client.get(self.work_detail).status_code, 200)
        self.assertEquals(self.client.get(self.footprint_detail).status_code,
                          200)


class FootprintListViewTest(TestCase):
    def setUp(self):
        self.user = UserFactory()

        place1 = PlaceFactory(city='Teit')
        place2 = PlaceFactory(city='Cheit')
        place3 = PlaceFactory(city='Zavin')

        date1 = ExtendedDateFactory(edtf_format='1492')
        date2 = ExtendedDateFactory(edtf_format='1493')
        date3 = ExtendedDateFactory(edtf_format='1494')

        role = RoleFactory(name='Owner')
        owner1 = ActorFactory(role=role, person=PersonFactory(name='Hank'))
        owner2 = ActorFactory(role=role, person=PersonFactory(name='Banana'))
        owner3 = ActorFactory(role=role, person=PersonFactory(name='Zed'))

        self.footprint1 = FootprintFactory(title='Alpha', provenance='one',
                                           place=place1, associated_date=date1)
        self.footprint1.actor.add(owner1)

        self.footprint2 = FootprintFactory(title='Beta', provenance='two',
                                           place=place2, associated_date=date2)
        self.footprint2.actor.add(owner2)

        self.footprint3 = FootprintFactory(title='Delta', provenance='three',
                                           place=place3, associated_date=date3)

        self.footprint4 = FootprintFactory(title='Epsilon', provenance='four',
                                           place=None, associated_date=None)
        self.footprint4.actor.add(owner3)

    def test_bogus_sort(self):
        url = reverse('browse-footprint-list-default')
        url += '101/'
        response = self.client.get(url)
        self.assertEquals(response.status_code, 200)

        ctx = response.context_data
        self.assertTrue('paginator' in ctx)
        self.assertTrue('sort_options' in ctx)
        self.assertEquals(ctx['selected_sort'], 'ftitle')
        self.assertEquals(ctx['selected_sort_label'], 'Footprint')

        self.assertEquals(ctx['object_list'][0], self.footprint1)
        self.assertEquals(ctx['object_list'][1], self.footprint2)
        self.assertEquals(ctx['object_list'][2], self.footprint3)
        self.assertEquals(ctx['object_list'][3], self.footprint4)

    def test_default_sort(self):
        url = reverse('browse-footprint-list-default')
        response = self.client.get(url)
        self.assertEquals(response.status_code, 200)

        ctx = response.context_data
        self.assertTrue('paginator' in ctx)
        self.assertTrue('sort_options' in ctx)
        self.assertEquals(ctx['selected_sort'], 'ftitle')
        self.assertEquals(ctx['selected_sort_label'], 'Footprint')

        self.assertEquals(ctx['object_list'][0], self.footprint1)
        self.assertEquals(ctx['object_list'][1], self.footprint2)
        self.assertEquals(ctx['object_list'][2], self.footprint3)
        self.assertEquals(ctx['object_list'][3], self.footprint4)

        # reverse the sort
        url += '?direction=desc'
        response = self.client.get(url)
        self.assertEquals(response.status_code, 200)

        ctx = response.context_data
        self.assertEquals(ctx['object_list'][0], self.footprint4)
        self.assertEquals(ctx['object_list'][1], self.footprint3)
        self.assertEquals(ctx['object_list'][2], self.footprint2)
        self.assertEquals(ctx['object_list'][3], self.footprint1)

    def test_footprint_location_sort(self):
        url = reverse('browse-footprint-list', args=['flocation'])
        response = self.client.get(url)
        self.assertEquals(response.status_code, 200)

        ctx = response.context_data
        self.assertTrue('paginator' in ctx)
        self.assertTrue('sort_options' in ctx)
        self.assertEquals(ctx['selected_sort'], 'flocation')
        self.assertEquals(ctx['selected_sort_label'], 'Footprint Location')

        self.assertEquals(ctx['object_list'][0], self.footprint4)
        self.assertEquals(ctx['object_list'][1], self.footprint2)
        self.assertEquals(ctx['object_list'][2], self.footprint1)
        self.assertEquals(ctx['object_list'][3], self.footprint3)

        # reverse the sort
        url += '?direction=desc'
        response = self.client.get(url)
        self.assertEquals(response.status_code, 200)

        ctx = response.context_data

        self.assertEquals(ctx['object_list'][0], self.footprint3)
        self.assertEquals(ctx['object_list'][1], self.footprint1)
        self.assertEquals(ctx['object_list'][2], self.footprint2)
        self.assertEquals(ctx['object_list'][3], self.footprint4)

    def test_footprint_date_sort(self):
        url = reverse('browse-footprint-list', args=['fdate'])
        response = self.client.get(url)
        self.assertEquals(response.status_code, 200)

        ctx = response.context_data
        self.assertTrue('paginator' in ctx)
        self.assertTrue('sort_options' in ctx)
        self.assertEquals(ctx['selected_sort'], 'fdate')
        self.assertEquals(ctx['selected_sort_label'], 'Footprint Date')

        self.assertEquals(ctx['object_list'][0], self.footprint4)
        self.assertEquals(ctx['object_list'][1], self.footprint1)
        self.assertEquals(ctx['object_list'][2], self.footprint2)
        self.assertEquals(ctx['object_list'][3], self.footprint3)

        # reverse the sort
        url += '?direction=desc'
        response = self.client.get(url)
        self.assertEquals(response.status_code, 200)

        ctx = response.context_data

        self.assertEquals(ctx['object_list'][0], self.footprint3)
        self.assertEquals(ctx['object_list'][1], self.footprint2)
        self.assertEquals(ctx['object_list'][2], self.footprint1)
        self.assertEquals(ctx['object_list'][3], self.footprint4)

    def test_footprint_owner_sort(self):
        url = reverse('browse-footprint-list', args=['owners'])
        response = self.client.get(url)
        self.assertEquals(response.status_code, 200)

        ctx = response.context_data
        self.assertTrue('paginator' in ctx)
        self.assertTrue('sort_options' in ctx)
        self.assertEquals(ctx['selected_sort'], 'owners')
        self.assertEquals(ctx['selected_sort_label'], 'Owners')

        self.assertEquals(ctx['object_list'][0], self.footprint3)
        self.assertEquals(ctx['object_list'][1], self.footprint2)
        self.assertEquals(ctx['object_list'][2], self.footprint1)
        self.assertEquals(ctx['object_list'][3], self.footprint4)

        # reverse the sort
        url += '?direction=desc'
        response = self.client.get(url)
        self.assertEquals(response.status_code, 200)

        ctx = response.context_data

        self.assertEquals(ctx['object_list'][0], self.footprint4)
        self.assertEquals(ctx['object_list'][1], self.footprint1)
        self.assertEquals(ctx['object_list'][2], self.footprint2)
        self.assertEquals(ctx['object_list'][3], self.footprint3)

    def test_filter(self):
        url = reverse('browse-footprint-list', args=['owners'])
        url += '?direction=asc&q=zed'
        response = self.client.get(url)
        self.assertEquals(response.status_code, 200)

        ctx = response.context_data
        self.assertEquals(ctx['query'], 'zed')

        self.assertEquals(ctx['object_list'][0], self.footprint4)


class FootprintListExportTest(TestCase):
    def setUp(self):
        work = WrittenWork.objects.create()
        imprint = Imprint.objects.create(work=work)
        book_copy = BookCopy.objects.create(imprint=imprint)

        self.footprint1 = Footprint.objects.create(
            title='Empty Footprint', book_copy=book_copy)
        self.footprint2 = FootprintFactory()

        role = RoleFactory(name='Printer')
        self.printer = ActorFactory(role=role,
                                    person=PersonFactory(name='Hank2'))
        self.footprint2.book_copy.imprint.actor.add(self.printer)

        role = RoleFactory(name='Owner')
        self.owner = ActorFactory(role=role, person=PersonFactory(name='Tim'))
        self.footprint2.actor.add(self.owner)

    def test_export_list(self):
        url = reverse('export-footprint-list', args=['ftitle'])
        response = self.client.get(url)

        self.assertEquals(response.status_code, 200)
        self.assertEquals(Footprint.objects.all().count(), 2)

        # owners
        o = [owner.display_name().encode('utf-8')
             for owner in self.footprint2.owners()]
        o = '; '.join(o)

        # Imprint Printers
        p = [p.display_name().encode('utf-8')
             for p in self.footprint2.book_copy.imprint.printers()]
        p = '; '.join(p)

        headers = ('Footprint Title,Footprint Date,Footprint Location,'
                   'Footprint Owners,Written Work Title,'
                   'Imprint Display Title,Imprint Printers,'
                   'Imprint Publicaton Date,Imprint Creation Date,'
                   'Footprint Percent Complete\r\n')
        row1 = ('Empty Footprint,None,None,,None,None,'
                ',None,{},0\r\n').format(
            self.footprint1.created_at.strftime('%m/%d/%Y'))
        row2 = ('Odyssey,c. 1984,"Cracow, Poland",{},'
                'The Odyssey,"The Odyssey, Edition 1",{},'
                'c. 1984,{},90\r\n').format(
            o, p, self.footprint2.created_at.strftime('%m/%d/%Y'))
        self.assertEquals(response.streaming_content.next(), headers)
        self.assertEquals(response.streaming_content.next(), row1)
        self.assertEquals(response.streaming_content.next(), row2)

        with self.assertRaises(StopIteration):
            response.streaming_content.next()


class ApiViewTests(TestCase):

    def setUp(self):
        self.user = UserFactory()

    def test_anonymous(self):
        response = self.client.get('/api/title/', {'q': 'Foo'},
                                   HTTP_X_REQUESTED_WITH='XMLHttpRequest')
        self.assertEquals(response.status_code, 302)

        response = self.client.get('/api/name/', {'q': 'Foo'},
                                   HTTP_X_REQUESTED_WITH='XMLHttpRequest')
        self.assertEquals(response.status_code, 302)

    def test_title_listview(self):
        self.client.login(username=self.user.username, password="test")

        WrittenWorkFactory(title='Alpha')
        ImprintFactory(title='Beta')
        FootprintFactory(title='Gamma')

        response = self.client.get('/api/title/', {'q': 'Foo'},
                                   HTTP_X_REQUESTED_WITH='XMLHttpRequest')
        self.assertEquals(response.status_code, 200)
        the_json = loads(response.content)
        self.assertEquals(len(the_json), 0)

        response = self.client.get('/api/title/', {'q': 'Alp'},
                                   HTTP_X_REQUESTED_WITH='XMLHttpRequest')
        self.assertEquals(response.status_code, 200)
        the_json = loads(response.content)
        self.assertEquals(len(the_json), 1)
        self.assertEquals(the_json[0], 'Alpha')

    def test_name_listview(self):
        self.client.login(username=self.user.username, password="test")

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


class ConnectFootprintViewTest(TestCase):

    def setUp(self):
        self.book = BookCopyFactory()
        self.imprint = ImprintFactory()
        self.work = WrittenWorkFactory()
        self.footprint = FootprintFactory()

        self.staff = UserFactory(is_staff=True)

        self.url = reverse('connect-footprint-view',
                           kwargs={'pk': self.footprint.pk})

    def test_post_expected_errors(self):
        # not logged in
        self.assertEquals(self.client.post(self.url).status_code, 302)

    def test_post_update_book(self):
        self.client.login(username=self.staff.username, password="test")

        data = {'work': self.work.id,
                'imprint': self.imprint.id,
                'copy': self.book.id}
        response = self.client.post(self.url, data)
        self.assertEquals(response.status_code, 302)

        fp = Footprint.objects.get(id=self.footprint.id)
        self.assertEquals(fp.book_copy, self.book)

    def test_post_update_imprint(self):
        self.client.login(username=self.staff.username, password="test")

        data = {'work': self.work.id,
                'imprint': self.imprint.id}
        response = self.client.post(self.url, data)
        self.assertEquals(response.status_code, 302)

        fp = Footprint.objects.get(id=self.footprint.id)
        self.assertEquals(fp.book_copy.imprint, self.imprint)

    def test_post_update_work(self):
        self.client.login(username=self.staff.username, password="test")

        data = {'work': self.work.id}
        response = self.client.post(self.url, data)
        self.assertEquals(response.status_code, 302)

        fp = Footprint.objects.get(id=self.footprint.id)
        self.assertEquals(fp.book_copy.imprint.work, self.work)


class CopyFootprintViewTest(TestCase):
    def setUp(self):
        self.footprint = FootprintFactory()
        self.staff = UserFactory(is_staff=True)
        self.url = reverse('copy-footprint-view',
                           kwargs={'pk': self.footprint.pk})

    def test_post_expected_errors(self):
        # not logged in
        self.assertEquals(self.client.post(self.url).status_code, 302)

    def test_post_new_evidence(self):
        self.client.login(username=self.staff.username, password="test")

        data = {
            'footprint-medium': 'New Medium',
            'footprint-provenance': 'New Provenance',
            'footprint-title': 'Iliad',
            'footprint-medium-description': 'Medium Description',
            'footprint-call-number': 'Call Number',
            'imprint': 0,
            'copy': 0
        }

        response = self.client.post(self.url, data)
        self.assertEquals(response.status_code, 302)
        qs = Footprint.objects.exclude(id=self.footprint.id)
        self.assertEquals(qs.count(), 1)

        new_fp = qs.first()
        self.assertEquals(new_fp.medium, 'New Medium')
        self.assertEquals(new_fp.provenance, 'New Provenance')
        self.assertEquals(new_fp.title, 'Iliad')
        self.assertEquals(new_fp.medium_description, 'Medium Description')
        self.assertEquals(new_fp.call_number, 'Call Number')


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

        self.assertIsNotNone(fp.book_copy)
        self.assertIsNotNone(fp.book_copy.imprint)
        self.assertIsNotNone(fp.book_copy.imprint.work)


class AddActorViewTest(TestCase):
    def setUp(self):
        self.user = UserFactory()
        self.staff = UserFactory(is_staff=True)
        self.footprint = FootprintFactory()

        self.add_url = reverse('add-actor-view')
        self.role = RoleFactory()

    def test_create_actor_new_person(self):
        view = AddActorView()
        view.create_actor('', 'Alpha Centauri', self.role, 'Alf')

        Actor.objects.get(person__name='Alpha Centauri',
                          role=self.role, alias='Alf')

    def test_create_actor_existing_person(self):
        alpha = PersonFactory(name='Alpha')
        view = AddActorView()
        view.create_actor(alpha.id, alpha.name, self.role, 'Alf')

        Actor.objects.get(person__id=alpha.id,
                          person__name=alpha.name,
                          role=self.role, alias='Alf')

    def test_create_actor_existing_person_new_name(self):
        alpha = PersonFactory(name='Alpha')

        view = AddActorView()
        view.create_actor(alpha.id, 'Alpha Beta', self.role, 'Alf')

        try:
            Actor.objects.get(person__id=alpha.id)
        except:
            pass  # expected

        Actor.objects.get(person__name='Alpha Beta',
                          role=self.role, alias='Alf')

    def test_post_expected_errors(self):
        # not logged in
        self.assertEquals(self.client.post(self.add_url).status_code, 302)

        # no ajax
        self.client.login(username=self.user.username, password="test")
        self.assertEquals(self.client.post(self.add_url).status_code, 405)

    def test_post_invalid_role(self):
        # invalid role id
        self.client.login(username=self.staff.username, password="test")
        response = self.client.post(self.add_url,
                                    {'parent_id': self.footprint.id,
                                     'parent_model': 'footprint',
                                     'person_name': 'Albert Einstein',
                                     'role': 3000},
                                    HTTP_X_REQUESTED_WITH='XMLHttpRequest')
        self.assertEquals(response.status_code, 404)

    def test_post_success(self):
        self.assertEquals(self.footprint.actor.count(), 1)

        self.client.login(username=self.staff.username, password="test")
        response = self.client.post(self.add_url,
                                    {'parent_id': self.footprint.id,
                                     'parent_model': 'footprint',
                                     'person_name': 'Albert Einstein',
                                     'role': self.role.id},
                                    HTTP_X_REQUESTED_WITH='XMLHttpRequest')
        self.assertEquals(response.status_code, 200)
        the_json = loads(response.content)
        self.assertTrue(the_json['success'])

        # refresh footprint from database
        footprint = Footprint.objects.get(id=self.footprint.id)
        self.assertEquals(footprint.actor.count(), 2)
        footprint.actor.get(person__name='Albert Einstein')


class RemoveRelatedViewTest(TestCase):
    def setUp(self):
        self.user = UserFactory()
        self.staff = UserFactory(is_staff=True)
        self.footprint = FootprintFactory()

        self.actor = ActorFactory()
        self.footprint.actor.add(self.actor)

        self.remove_url = reverse('remove-related')

    def test_post_expected_errors(self):
        # not logged in
        self.assertEquals(self.client.post(self.remove_url).status_code, 302)

        # no ajax
        self.client.login(username=self.user.username, password="test")
        self.assertEquals(self.client.post(self.remove_url).status_code, 405)

    def test_post_missing_params(self):
        self.client.login(username=self.staff.username, password="test")

        response = self.client.post(self.remove_url,
                                    {'parent_id': self.footprint.id,
                                     'parent_model': 'footprint'},
                                    HTTP_X_REQUESTED_WITH='XMLHttpRequest')
        self.assertEquals(response.status_code, 200)
        self.assertFalse(loads(response.content)['success'])

    def test_post_remove_invalid_child_id(self):
        dt = ExtendedDateFactory()

        self.client.login(username=self.staff.username, password="test")

        response = self.client.post(self.remove_url, {
            'parent_id': self.footprint.id,
            'parent_model': 'footprint',
            'child_id': dt.id,
            'attr': 'associated_date'},
            HTTP_X_REQUESTED_WITH='XMLHttpRequest')

        self.assertEquals(response.status_code, 200)
        self.assertFalse(loads(response.content)['success'])

        footprint = Footprint.objects.get(id=self.footprint.id)  # refresh
        self.assertIsNotNone(footprint.associated_date)

    def test_post_remove_success(self):
        dt = self.footprint.associated_date

        self.client.login(username=self.staff.username, password="test")

        response = self.client.post(self.remove_url, {
            'parent_id': self.footprint.id,
            'parent_model': 'footprint',
            'child_id': self.footprint.associated_date.id,
            'attr': 'associated_date'},
            HTTP_X_REQUESTED_WITH='XMLHttpRequest')

        self.assertEquals(response.status_code, 200)
        self.assertTrue(loads(response.content)['success'])

        footprint = Footprint.objects.get(id=self.footprint.id)  # refresh
        self.assertIsNone(footprint.associated_date)

        with self.assertRaises(ExtendedDate.DoesNotExist):
            ExtendedDate.objects.get(id=dt.id)

    def test_post_remove_actor(self):
        self.assertEquals(self.footprint.actor.count(), 2)

        self.client.login(username=self.staff.username, password="test")
        response = self.client.post(self.remove_url,
                                    {'parent_id': self.footprint.id,
                                     'parent_model': 'footprint',
                                     'child_id': self.actor.id,
                                     'attr': 'actor'},
                                    HTTP_X_REQUESTED_WITH='XMLHttpRequest')
        self.assertEquals(response.status_code, 200)
        self.assertTrue(loads(response.content)['success'])
        self.assertEquals(self.footprint.actor.count(), 1)

    def test_post_remove_identifier(self):
        imprint = self.footprint.book_copy.imprint
        identifier = imprint.standardized_identifier.first()

        self.client.login(username=self.staff.username, password="test")
        response = self.client.post(self.remove_url,
                                    {'parent_id': imprint.id,
                                     'parent_model': 'imprint',
                                     'child_id': identifier.id,
                                     'attr': 'standardized_identifier'},
                                    HTTP_X_REQUESTED_WITH='XMLHttpRequest')
        self.assertEquals(response.status_code, 200)
        self.assertTrue(loads(response.content)['success'])

        imprint = Imprint.objects.get(id=imprint.id)  # refresh
        self.assertEquals(imprint.standardized_identifier.count(), 0)


class AddDateViewTest(TestCase):

    def setUp(self):
        self.user = UserFactory()
        self.staff = UserFactory(is_staff=True)
        self.footprint = FootprintFactory(title="Custom", associated_date=None)

        self.url = reverse('add-date-view')

    def test_post_expected_errors(self):
        # not logged in
        self.assertEquals(self.client.post(self.url).status_code, 302)

        # no ajax
        self.client.login(username=self.user.username, password="test")
        self.assertEquals(self.client.post(self.url).status_code, 405)

    def test_post_no_data(self):
        self.client.login(username=self.staff.username, password="test")
        response = self.client.post(self.url,
                                    {'parent_id': self.footprint.id,
                                     'parent_model': 'footprint'},
                                    HTTP_X_REQUESTED_WITH='XMLHttpRequest')
        self.assertEquals(response.status_code, 200)
        the_json = loads(response.content)
        self.assertFalse(the_json['success'])

    def test_post_success(self):
        self.client.login(username=self.staff.username, password="test")
        response = self.client.post(self.url,
                                    {'parent_id': self.footprint.id,
                                     'parent_model': 'footprint',
                                     'attr': 'associated_date',
                                     'millenium1': '1', 'century1': '6',
                                     'decade1': '7', 'year1': '3',
                                     'month1': '', 'day1': '',
                                     'millenium2': '', 'century2': '',
                                     'decade': '', 'year2': '',
                                     'month2': '', 'day2': ''},
                                    HTTP_X_REQUESTED_WITH='XMLHttpRequest')
        self.assertEquals(response.status_code, 200)
        the_json = loads(response.content)

        self.footprint.refresh_from_db()
        self.assertTrue(the_json['success'])
        self.assertEquals(self.footprint.associated_date.edtf_format, '1673')


class DisplayDateViewTest(TestCase):

    def setUp(self):
        self.user = UserFactory()
        self.staff = UserFactory(is_staff=True)
        self.footprint = FootprintFactory(title="Custom", associated_date=None)

        self.url = reverse('display-date-view')

    def test_post_expected_errors(self):
        # no ajax
        self.client.login(username=self.user.username, password="test")
        self.assertEquals(self.client.post(self.url).status_code, 405)

    def test_post_no_data(self):
        self.client.login(username=self.staff.username, password="test")
        response = self.client.post(self.url,
                                    {'parent_id': self.footprint.id,
                                     'parent_model': 'footprint'},
                                    HTTP_X_REQUESTED_WITH='XMLHttpRequest')
        self.assertEquals(response.status_code, 200)
        the_json = loads(response.content)
        self.assertFalse(the_json['success'])

    def test_post_success(self):
        self.client.login(username=self.staff.username, password="test")
        response = self.client.post(self.url,
                                    {'parent_id': self.footprint.id,
                                     'parent_model': 'footprint',
                                     'attr': 'associated_date',
                                     'millenium1': '1', 'century1': '6',
                                     'decade1': '7', 'year1': '3',
                                     'month1': '', 'day1': '',
                                     'millenium2': '', 'century2': '',
                                     'decade': '', 'year2': '',
                                     'month2': '', 'day2': ''},
                                    HTTP_X_REQUESTED_WITH='XMLHttpRequest')
        self.assertEquals(response.status_code, 200)
        the_json = loads(response.content)
        self.assertTrue(the_json['success'])
        self.assertEquals(the_json['display'], '1673')


class AddPlaceViewTest(TestCase):

    def setUp(self):
        self.user = UserFactory()
        self.staff = UserFactory(is_staff=True)
        self.footprint = FootprintFactory(title="Custom", place=None)

        self.url = reverse('add-place-view')

    def test_post_expected_errors(self):
        # not logged in
        self.assertEquals(self.client.post(self.url).status_code, 302)

        # no ajax
        self.client.login(username=self.user.username, password="test")
        self.assertEquals(self.client.post(self.url).status_code, 405)

    def test_post_no_data(self):
        self.client.login(username=self.staff.username, password="test")
        response = self.client.post(self.url,
                                    {'parent_id': self.footprint.id,
                                     'parent_model': 'footprint'},
                                    HTTP_X_REQUESTED_WITH='XMLHttpRequest')
        self.assertEquals(response.status_code, 200)
        the_json = loads(response.content)
        self.assertFalse(the_json['success'])

    def test_post_success(self):
        self.client.login(username=self.staff.username, password="test")
        response = self.client.post(self.url,
                                    {'parent_id': self.footprint.id,
                                     'parent_model': 'footprint',
                                     'city': 'New York',
                                     'country': 'United States',
                                     'position': '40.752946,-73.983435'},
                                    HTTP_X_REQUESTED_WITH='XMLHttpRequest')
        self.assertEquals(response.status_code, 200)
        the_json = loads(response.content)

        footprint = Footprint.objects.get(title='Custom')  # refresh from db
        self.assertTrue(the_json['success'])
        self.assertEquals(footprint.place.city, 'New York')
        self.assertEquals(footprint.place.country, 'United States')
        self.assertEquals(str(footprint.place.position.latitude), '40.752946')
        self.assertEquals(str(footprint.place.position.longitude),
                          '-73.983435')


class AddIdentifierViewTest(TestCase):

    def setUp(self):
        self.user = UserFactory()
        self.staff = UserFactory(is_staff=True)
        self.imprint = ImprintFactory()

        self.url = reverse('add-identifier-view')

    def test_post_expected_errors(self):
        # not logged in
        self.assertEquals(self.client.post(self.url).status_code, 302)

        # no ajax
        self.client.login(username=self.user.username, password="test")
        self.assertEquals(self.client.post(self.url).status_code, 405)

    def test_post_no_data(self):
        self.client.login(username=self.staff.username, password="test")
        response = self.client.post(self.url,
                                    {'parent_id': self.imprint.id,
                                     'parent_model': 'imprint'},
                                    HTTP_X_REQUESTED_WITH='XMLHttpRequest')
        self.assertEquals(response.status_code, 404)

    def test_post_success(self):
        self.assertEquals(self.imprint.standardized_identifier.count(), 1)
        self.client.login(username=self.staff.username, password="test")
        response = self.client.post(self.url,
                                    {'parent_id': self.imprint.id,
                                     'parent_model': 'imprint',
                                     'identifier': 'abcdefg',
                                     'identifier_type': 'LOC'},
                                    HTTP_X_REQUESTED_WITH='XMLHttpRequest')
        self.assertEquals(response.status_code, 200)
        the_json = loads(response.content)
        self.assertTrue(the_json['success'])

        imprint = Imprint.objects.get(id=self.imprint.id)  # refresh from db
        identifier = imprint.standardized_identifier.get(identifier='abcdefg')
        self.assertEquals(
            identifier.identifier_type,
            StandardizedIdentificationType.objects.get(slug='LOC'))


class AddDigitalObjectViewTest(TestCase):

    def setUp(self):
        self.user = UserFactory()
        self.staff = UserFactory(is_staff=True)
        self.footprint = FootprintFactory()

        self.url = reverse('add-digital-object-view')

    def test_post_expected_errors(self):
        # not logged in
        self.assertEquals(self.client.post(self.url).status_code, 302)

        # no ajax
        self.client.login(username=self.user.username, password="test")
        self.assertEquals(self.client.post(self.url).status_code, 405)

    def test_post_no_data(self):
        self.client.login(username=self.staff.username, password="test")
        response = self.client.post(self.url,
                                    {'parent_id': self.footprint.id,
                                     'parent_model': 'footprint'},
                                    HTTP_X_REQUESTED_WITH='XMLHttpRequest')
        self.assertEquals(response.status_code, 200)
        the_json = loads(response.content)
        self.assertFalse(the_json['success'])

    def test_post_success(self):
        f = SimpleUploadedFile("file.txt", "file_content")

        self.client.login(username=self.staff.username, password="test")
        response = self.client.post(self.url,
                                    {'parent_id': self.footprint.id,
                                     'parent_model': 'footprint',
                                     'name': 'foo.jpg',
                                     'description': 'Foo Bar',
                                     'file': f},
                                    HTTP_X_REQUESTED_WITH='XMLHttpRequest')
        self.assertEquals(response.status_code, 200)
        the_json = loads(response.content)

        footprint = Footprint.objects.get(id=self.footprint.id)  # refresh
        self.assertTrue(the_json['success'])
        self.assertEquals(footprint.digital_object.count(), 1)


class ViewsetsTest(TestCase):

    def test_writtenwork_viewset(self):
        viewset = WrittenWorkViewSet()
        ww1 = WrittenWorkFactory(title='Alpha')
        ww2 = WrittenWorkFactory(title='Beta')

        viewset.request = RequestFactory().get('/', {})
        qs = viewset.get_queryset()
        self.assertEquals(qs.count(), 2)
        self.assertEquals(qs[0], ww1)
        self.assertEquals(qs[1], ww2)

        data = {'q': 'bet'}
        viewset.request = RequestFactory().get('/', data)
        qs = viewset.get_queryset()
        self.assertEquals(qs.count(), 1)
        self.assertEquals(qs.first(), ww2)

    def test_imprint_viewset(self):
        viewset = ImprintViewSet()
        imprint1 = ImprintFactory(title='Alpha')
        imprint2 = ImprintFactory(title='Beta')

        viewset.request = RequestFactory().get('/', {})
        qs = viewset.get_queryset()
        self.assertEquals(qs.count(), 2)
        self.assertEquals(qs[0], imprint1)
        self.assertEquals(qs[1], imprint2)

        data = {'work': imprint1.work.id}
        viewset.request = RequestFactory().get('/', data)
        qs = viewset.get_queryset()
        self.assertEquals(qs.count(), 1)
        self.assertEquals(qs.first(), imprint1)

        data = {'q': 'bet'}
        viewset.request = RequestFactory().get('/', data)
        qs = viewset.get_queryset()
        self.assertEquals(qs.count(), 1)
        self.assertEquals(qs.first(), imprint2)

    def test_bookcopy_viewset(self):
        viewset = BookCopyViewSet()
        book1 = BookCopyFactory()
        book2 = BookCopyFactory()

        viewset.request = RequestFactory().get('/', {})
        qs = viewset.get_queryset()
        self.assertEquals(qs.count(), 2)
        self.assertEquals(qs[0], book1)
        self.assertEquals(qs[1], book2)

        data = {'imprint': book1.imprint.id}
        viewset.request = RequestFactory().get('/', data)
        qs = viewset.get_queryset()
        self.assertEquals(qs.count(), 1)
        self.assertEquals(qs.first(), book1)

    def test_footprint_viewset(self):
        csrf_client = Client(enforce_csrf_checks=True)

        self.user = UserFactory()
        csrf_client.login(username=self.user.username, password="test")

        # get a csrf token
        url = reverse('create-footprint-view')
        response = csrf_client.get(url)

        footprint = FootprintFactory()
        data = {'pk': footprint.id, 'title': 'abcdefg'}
        content = encode_multipart('BoUnDaRyStRiNg', data)
        content_type = 'multipart/form-data; boundary=BoUnDaRyStRiNg'

        url = '/api/footprint/%s/' % footprint.id

        csrf_header = response.cookies['csrftoken'].value
        response = csrf_client.patch(url, content,
                                     content_type=content_type,
                                     HTTP_X_CSRFTOKEN=csrf_header)
        self.assertEquals(response.status_code, 200)

        footprint.refresh_from_db()
        self.assertEquals(footprint.title, 'abcdefg')


class ContactUsViewTest(TestCase):

    def test_get_initial_anonymous(self):
        view = ContactUsView()
        view.request = RequestFactory().get('/contact/')
        view.request.session = {}
        view.request.user = AnonymousUser()
        initial = view.get_initial()

        self.assertFalse('name' in initial)
        self.assertFalse('email' in initial)

    def test_get_initial_not_anonymous(self):
        view = ContactUsView()
        view.request = RequestFactory().get('/contact/')
        view.request.session = {}
        view.request.user = UserFactory(first_name='Foo',
                                        last_name='Bar',
                                        email='foo@bar.com')

        initial = view.get_initial()
        self.assertEquals(initial['name'], 'Foo Bar')
        self.assertEquals(initial['email'], 'foo@bar.com')

        # a subsequent call using an anonymous session returns a clean initial
        view.request.session = {}
        view.request.user = AnonymousUser()
        initial = view.get_initial()
        self.assertFalse('name' in initial)
        self.assertFalse('email' in initial)

    def test_form_valid(self):
        view = ContactUsView()
        view.request = RequestFactory().get('/contact/')
        view.request.user = AnonymousUser()

        form = ContactUsForm()
        form.cleaned_data = {
            'name': 'Foo Bar',
            'email': 'footprints@ccnmtl.columbia.edu',
            'subject': 'other',
            'description': 'There is a problem'
        }

        view.form_valid(form)
        self.assertEqual(len(mail.outbox), 1)

        self.assertEqual(mail.outbox[0].subject,
                         'Footprints Contact Us Request')
        self.assertEquals(mail.outbox[0].from_email,
                          'footprints@ccnmtl.columbia.edu')
        self.assertEquals(mail.outbox[0].to,
                          [settings.CONTACT_US_EMAIL])


class AddLanguageViewTest(TestCase):

    def testAddRemove(self):
        staff = UserFactory(is_staff=True)
        self.client.login(username=staff.username, password='test')
        url = reverse('add-language-view')

        footprint = FootprintFactory(title='Alpha')
        generic = footprint.language.first()

        # add english & generic
        english = LanguageFactory(name='English')

        data = {'parent_id': footprint.id,
                'parent_model': 'footprint',
                'language': [english.id, generic.id]}

        response = self.client.post(url, data,
                                    HTTP_X_REQUESTED_WITH='XMLHttpRequest')
        self.assertEquals(response.status_code, 200)

        footprint.refresh_from_db()
        self.assertEquals(footprint.language.count(), 2)
        self.assertTrue(english in footprint.language.all())
        self.assertTrue(generic in footprint.language.all())

        # remove generic
        data = {'parent_id': footprint.id,
                'parent_model': 'footprint',
                'language': [english.id]}

        response = self.client.post(url, data,
                                    HTTP_X_REQUESTED_WITH='XMLHttpRequest')
        self.assertEquals(response.status_code, 200)

        footprint.refresh_from_db()
        self.assertEquals(footprint.language.count(), 1)
        self.assertTrue(english in footprint.language.all())

        # generic was not deleted
        Language.objects.get(id=generic.id)

        # remove english too
        data = {'parent_id': footprint.id,
                'parent_model': 'footprint',
                'language': []}

        response = self.client.post(url, data,
                                    HTTP_X_REQUESTED_WITH='XMLHttpRequest')
        self.assertEquals(response.status_code, 200)

        footprint.refresh_from_db()
        self.assertEquals(footprint.language.count(), 0)

        # english was not deleted
        Language.objects.get(id=english.id)


class SearchViewTest(TestCase):

    def test_search(self):
        url = "{}/?q=foo&models=main.footprint".format(reverse('search'))

        response = self.client.get(url)
        self.assertEquals(response.status_code, 200)
        self.assertEquals(len(response.context['page'].object_list), 0)


class SearchIndexTest(TestCase):

    def test_format_sort_by(self):
        self.assertEquals(format_sort_by('ABCD'), 'abcd')
        self.assertEquals(format_sort_by('The A', True), 'a')


class SerializerTest(TestCase):

    def test_standardized_identification_type_serializer(self):
        serializer = StandardizedIdentificationTypeSerializer()

        qs = serializer.get_queryset()
        self.assertEquals(qs.count(), 5)  # preloaded in migrations

    def test_standardized_identification_serializer(self):
        si = StandardizedIdentificationFactory()
        serializer = StandardizedIdentificationSerializer()

        qs = serializer.get_queryset()
        self.assertEquals(qs.count(), 1)
        self.assertEquals(qs.first(), si)

    def test_language_serializer(self):
        l = LanguageFactory()
        serializer = LanguageSerializer()

        qs = serializer.get_queryset()
        self.assertEquals(qs.count(), 1)
        self.assertEquals(qs.first(), l)

        self.assertEquals(serializer.to_internal_value(l.id), l)

    def test_extended_date_serializer(self):
        dt = ExtendedDateFactory()
        serializer = ExtendedDateSerializer()

        qs = serializer.get_queryset()
        self.assertEquals(qs.count(), 1)
        self.assertEquals(qs.first(), dt)

    def test_actor_serializer(self):
        a = ActorFactory()
        serializer = ActorSerializer()

        qs = serializer.get_queryset()
        self.assertEquals(qs.count(), 1)
        self.assertEquals(qs.first(), a)

        self.assertEquals(serializer.to_internal_value(a.id), a)


class ModerationViewTest(TestCase):

    def test_get(self):
        user = UserFactory()
        staff = UserFactory(is_staff=True)

        url = reverse('moderation-view')
        self.assertEquals(self.client.get(url).status_code, 405)

        self.client.login(username=user.username, password='test')
        self.assertEquals(self.client.get(url).status_code, 405)

        self.client.login(username=staff.username, password='test')
        self.assertEquals(self.client.get(url).status_code, 200)


class VerifyFootprintViewTest(TestCase):

    def test_post(self):
        fp = FootprintFactory()
        user = UserFactory()
        staff = UserFactory(is_staff=True)

        url = reverse('verify-footprint-view', kwargs={'pk': fp.id})
        self.assertEquals(self.client.get(url).status_code, 405)

        self.client.login(username=user.username, password='test')
        self.assertEquals(self.client.get(url).status_code, 405)

        self.client.login(username=staff.username, password='test')

        data = {'verified': 1}
        self.assertEquals(self.client.post(url, data).status_code, 302)
        fp.refresh_from_db()
        self.assertTrue(fp.verified)

        data = {'verified': 0}
        self.assertEquals(self.client.post(url, data).status_code, 302)
        fp.refresh_from_db()
        self.assertFalse(fp.verified)
