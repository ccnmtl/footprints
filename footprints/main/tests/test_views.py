from json import loads

from django.conf import settings
from django.contrib.auth.models import AnonymousUser, Group, Permission
from django.core import mail
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase
from django.test.client import RequestFactory
from django.urls.base import reverse
from django.utils.encoding import smart_text

from footprints.main.forms import ContactUsForm
from footprints.main.models import Footprint, Actor, Imprint, \
    StandardizedIdentificationType, ExtendedDate, Language, \
    WrittenWork, BookCopy, Role
from footprints.main.search_indexes import format_sort_by
from footprints.main.tests.factories import (
    UserFactory, WrittenWorkFactory, ImprintFactory, FootprintFactory,
    PersonFactory, RoleFactory, PlaceFactory, ActorFactory, BookCopyFactory,
    ExtendedDateFactory, LanguageFactory,
    GroupFactory, MODERATION_PERMISSIONS, ADD_CHANGE_PERMISSIONS,
    CanonicalPlaceFactory)
from footprints.main.utils import interpolate_role_actors
from footprints.main.views import (
    CreateFootprintView, AddActorView, ContactUsView, FootprintDetailView,
    ExportFootprintSearch, VerifiedFootprintFeed, AddPlaceView)


class BasicTest(TestCase):
    def test_root(self):
        response = self.client.get("/")
        self.assertEqual(response.status_code, 200)

    def test_smoketest(self):
        # just looking for an exception here
        self.client.get("/smoketest/")

    def test_sign_s3_view(self):
        user = UserFactory()
        self.client.login(username=user.username, password="test")
        with self.settings(
                AWS_ACCESS_KEY='',
                AWS_SECRET_KEY='',
                AWS_S3_UPLOAD_BUCKET=''):
            r = self.client.get(
                '/sign_s3/?s3_object_name=default_name&s3_object_type=foo')
            self.assertEqual(r.status_code, 200)
            j = loads(r.content.decode('utf-8'))
            self.assertTrue('signed_request' in j)


class PasswordTest(TestCase):

    def setUp(self):
        super(TestCase, self).setUp()
        self.user = UserFactory()

    def test_logged_out(self):
        response = self.client.get('/accounts/password_change/')
        self.assertEqual(response.status_code, 302)

        response = self.client.get('/accounts/password_reset/')
        self.assertEqual(response.status_code, 200)

    def test_logged_in(self):
        self.assertTrue(self.client.login(
            username=self.user.username, password="test"))
        response = self.client.get('/accounts/password_change/')
        self.assertEqual(response.status_code, 200)

        response = self.client.get('/accounts/password_reset/')
        self.assertEqual(response.status_code, 200)


class IndexViewTest(TestCase):

    def setUp(self):
        super(TestCase, self).setUp()

        self.user = UserFactory()

    def test_anonymous_user(self):
        response = self.client.get('/')
        self.assertEqual(response.status_code, 200)
        self.assertTrue(b'Log In' in response.content)
        self.assertFalse(b'Log Out' in response.content)

    def test_logged_in_user(self):
        self.assertTrue(self.client.login(
            username=self.user.username, password="test"))
        response = self.client.get('/')
        self.assertEqual(response.status_code, 200)
        self.assertFalse(b'Log In' in response.content)
        self.assertTrue(b'Log Out' in response.content)


class DetailViewTest(TestCase):

    def setUp(self):
        self.user = UserFactory()

        self.work_detail = reverse('writtenwork-detail-view',
                                   kwargs={'pk': WrittenWorkFactory().id})

        self.footprint_detail = reverse('footprint-detail-view',
                                        kwargs={'pk': FootprintFactory().id})

    def get_group(self):
        grp = Group.objects.get(name='Creator')
        lst = list(Permission.objects.filter(
            codename__in=ADD_CHANGE_PERMISSIONS))
        grp.permissions.add(*lst)

        return grp

    def test_get_logged_out(self):
        self.assertEqual(self.client.get(self.work_detail).status_code, 200)
        self.assertEqual(self.client.get(self.footprint_detail).status_code,
                         200)

    def test_get_logged_in(self):
        self.client.login(username=self.user.username, password="test")

        self.assertEqual(self.client.get(self.work_detail).status_code, 200)
        self.assertEqual(self.client.get(self.footprint_detail).status_code,
                         200)

    def test_can_edit(self):
        view = FootprintDetailView()

        user = UserFactory()
        self.assertFalse(view.can_edit(user))

        contributor = UserFactory(group=self.get_group())
        self.assertTrue(view.can_edit(contributor))

    def test_is_creator(self):
        view = FootprintDetailView()

        user = UserFactory()
        self.assertFalse(view.is_creator(user))

        creator = UserFactory(group=self.get_group())

        self.assertTrue(view.is_creator(creator))

    def test_has_perm(self):
        view = FootprintDetailView()

        fp1 = FootprintFactory()
        self.assertFalse(view.has_perm(self.user, False, False, fp1))
        self.assertTrue(view.has_perm(self.user, True, False, fp1))
        self.assertFalse(view.has_perm(self.user, True, True, fp1))

    def test_has_perm_two(self):
        view = FootprintDetailView()
        creator = UserFactory(group=self.get_group())
        fp2 = FootprintFactory(created_by=creator)
        self.assertTrue(view.has_perm(creator, True, True, fp2))

    def test_permissions(self):
        view = FootprintDetailView()

        creator = UserFactory(group=self.get_group())
        fp2 = FootprintFactory(created_by=creator)
        self.assertEqual(
            view.permissions(creator, fp2),
            {'can_edit_footprint': True,
             'can_edit_copy': False,
             'can_edit_imprint': False,
             'can_edit_work': False})


class ExportFootprintSearchTest(TestCase):

    def setUp(self):
        work = WrittenWork.objects.create()
        imprint = Imprint.objects.create(work=work)
        book_copy = BookCopy.objects.create(imprint=imprint)

        self.footprint1 = Footprint.objects.create(
            title='Empty Footprint', book_copy=book_copy)
        self.footprint2 = FootprintFactory(title='Footprint 2')

        role = RoleFactory(name='Printer')
        self.printer = ActorFactory(role=role,
                                    person=PersonFactory(name='Hank2'))
        self.footprint2.book_copy.imprint.actor.add(self.printer)

        role = RoleFactory(name='Owner')
        self.owner = ActorFactory(role=role, person=PersonFactory(name='Tim'))
        self.footprint2.actor.add(self.owner)

    def get_headers(self):
        headers = ('FootprintID,Footprint Title,Footprint Date,',
                   'Footprint Location,Footprint Owners,Written Work Title,'
                   'Imprint Display Title,Imprint Printers,'
                   'Imprint Publication Date,Imprint Creation Date,'
                   'Footprint Percent Complete,Literary Work LOC,'
                   'Imprint Actor and Role,Imprint BHB Number,'
                   'Imprint OCLC Number,Evidence Type,Evidence Location,'
                   'Evidence Call Number,Evidence Details,')

        for r in Role.objects.for_footprint():
            role = 'Footprint Role ' + smart_text(r.name) + ' Actor'
            headers += role + ','
            headers += (role + ' VIAF Number,')

        for r in Role.objects.for_imprint():
            role = 'Imprint Role: ' + smart_text(r.name) + ' Actor'
            headers += role + ','
            headers += (role + ' VIAF Number,')

        headers = headers[:-1]
        headers += '\r\n'
        return headers

    def test_export_list(self):
        # owners
        o = [owner.display_name() for owner in self.footprint2.owners()]
        o = '; '.join(o)

        # Imprint Printers
        p = [p.display_name()
             for p in self.footprint2.book_copy.imprint.printers()]
        p = '; '.join(p)

        # Imprint Actors
        actors = [smart_text(a)
                  for a in self.footprint2.book_copy.imprint.actor.all()]
        actors = '; '.join(actors)

        row1 = [self.footprint1.identifier(),
                'Empty Footprint', 'None', 'None', '', 'None', 'None',
                '', 'None', self.footprint1.created_at.strftime('%m/%d/%Y'),
                0, 'None', '', '', '', '', '', 'None', 'None']

        row1 += interpolate_role_actors(Role.objects.all().for_footprint(),
                                        self.footprint1.actors())

        row1 += interpolate_role_actors(
            Role.objects.all().for_imprint(),
            self.footprint1.book_copy.imprint.actor.all())

        work = self.footprint2.book_copy.imprint.work
        row2 = [self.footprint2.identifier(),
                'Footprint 2',  # Footprint Title
                'c. 1984',  # Footprint Date
                'Cracow, Poland',  # Footprint Location
                o,  # Footprint Owners
                work.title,  # Written Work Title
                'The Odyssey, Edition 1',  # Imprint Display Title
                p,  # Imprint Printers
                'c. 1984',  # Imprint Creation Date
                self.footprint2.created_at.strftime('%m/%d/%Y'),
                90,  # Footprint Percent Complete
                'None',
                actors,  # Imprint Actor and Role
                '',  # Imprint BHB
                '',  # Imprint OCLC Number
                'Medium',  # Evidence Type
                'Provenance',  # Evidence Location
                'call number',  # Evidence Call Number
                'lorem ipsum']

        # Footprint Actors
        row2 += interpolate_role_actors(Role.objects.all().for_footprint(),
                                        self.footprint2.actors())

        # Imprint Actors
        row2 += interpolate_role_actors(
            Role.objects.all().for_imprint(),
            self.footprint2.book_copy.imprint.actor.all())

        # Mock a SearchQuerySet
        qs = Footprint.objects.all()
        for o in qs:
            o.object = o

        rows = ExportFootprintSearch().get_rows(qs)
        next(rows)  # skip header row

        self.assertEqual(next(rows), row1)
        self.assertEqual(next(rows), row2)

        with self.assertRaises(StopIteration):
            next(rows)

    def test_get(self):
        url = reverse('export-footprint-list')

        kwargs = {
            'precision': 'contains',
            'direction': 'asc',
            'q': 'Footprint',
            'sort_by': 'ftitle',
            'page': 1
        }

        response = self.client.get(url, kwargs)
        self.assertEqual(response.status_code, 200)

        rows = response.streaming_content
        next(rows)  # headers
        next(rows)  # footprint1
        next(rows)  # footprint2

        with self.assertRaises(StopIteration):
            next(response.streaming_content)


class ApiViewTests(TestCase):

    def setUp(self):
        self.user = UserFactory()

    def test_anonymous(self):
        response = self.client.get('/api/title/', {'q': 'Foo'},
                                   HTTP_X_REQUESTED_WITH='XMLHttpRequest')
        self.assertEqual(response.status_code, 302)

        response = self.client.get('/api/name/', {'q': 'Foo'},
                                   HTTP_X_REQUESTED_WITH='XMLHttpRequest')
        self.assertEqual(response.status_code, 302)

    def test_title_listview(self):
        self.client.login(username=self.user.username, password="test")

        WrittenWorkFactory(title='Alpha')
        ImprintFactory(title='Beta')
        FootprintFactory(title='Gamma')

        response = self.client.get('/api/title/', {'q': 'Foo'},
                                   HTTP_X_REQUESTED_WITH='XMLHttpRequest')
        self.assertEqual(response.status_code, 200)
        the_json = loads(response.content.decode('utf-8'))
        self.assertEqual(len(the_json), 0)

        response = self.client.get('/api/title/', {'q': 'Alp'},
                                   HTTP_X_REQUESTED_WITH='XMLHttpRequest')
        self.assertEqual(response.status_code, 200)
        the_json = loads(response.content.decode('utf-8'))
        self.assertEqual(len(the_json), 1)
        self.assertEqual(the_json[0], 'Alpha')

    def test_name_listview(self):
        self.client.login(username=self.user.username, password="test")

        PersonFactory(name='Alpha')

        response = self.client.get('/api/name/', {'q': 'Foo'},
                                   HTTP_X_REQUESTED_WITH='XMLHttpRequest')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data), 0)

        response = self.client.get('/api/name/', {'q': 'Alp'},
                                   HTTP_X_REQUESTED_WITH='XMLHttpRequest')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['name'], 'Alpha')


class ConnectFootprintViewTest(TestCase):

    def setUp(self):
        self.book = BookCopyFactory()
        self.imprint = ImprintFactory()
        self.work = WrittenWorkFactory()
        self.footprint = FootprintFactory()

        grp = GroupFactory(permissions=ADD_CHANGE_PERMISSIONS)
        self.contributor = UserFactory(group=grp)

        self.url = reverse('connect-footprint-view',
                           kwargs={'pk': self.footprint.pk})

    def test_post(self):
        # not logged in
        self.assertEqual(self.client.post(self.url).status_code, 302)

        # update book
        self.client.login(username=self.contributor.username, password="test")

        data = {'work': self.work.id,
                'imprint': self.imprint.id,
                'copy': self.book.id}
        response = self.client.post(self.url, data)
        self.assertEqual(response.status_code, 302)

        fp = Footprint.objects.get(id=self.footprint.id)
        self.assertEqual(fp.book_copy, self.book)

        # update imprint
        self.client.login(username=self.contributor.username, password="test")

        data = {'work': self.work.id,
                'imprint': self.imprint.id}
        response = self.client.post(self.url, data)
        self.assertEqual(response.status_code, 302)

        fp = Footprint.objects.get(id=self.footprint.id)
        self.assertEqual(fp.book_copy.imprint, self.imprint)

        # update work
        self.client.login(username=self.contributor.username, password="test")

        data = {'work': self.work.id}
        response = self.client.post(self.url, data)
        self.assertEqual(response.status_code, 302)

        fp = Footprint.objects.get(id=self.footprint.id)
        self.assertEqual(fp.book_copy.imprint.work, self.work)


class CopyFootprintViewTest(TestCase):
    def setUp(self):
        self.footprint = FootprintFactory()

        grp = GroupFactory(permissions=ADD_CHANGE_PERMISSIONS)
        self.contributor = UserFactory(group=grp)

        self.url = reverse('copy-footprint-view',
                           kwargs={'pk': self.footprint.pk})

    def test_post(self):
        # not logged in
        self.assertEqual(self.client.post(self.url).status_code, 302)

        # post new evidence
        self.client.login(username=self.contributor.username, password="test")

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
        self.assertEqual(response.status_code, 302)
        qs = Footprint.objects.exclude(id=self.footprint.id)
        self.assertEqual(qs.count(), 1)

        new_fp = qs.first()
        self.assertEqual(new_fp.medium, 'New Medium')
        self.assertEqual(new_fp.provenance, 'New Provenance')
        self.assertEqual(new_fp.title, 'Iliad')
        self.assertEqual(new_fp.medium_description, 'Medium Description')
        self.assertEqual(new_fp.call_number, 'Call Number')


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
        self.assertEqual(response.status_code, 302)

        # there's only one in the system
        fp = Footprint.objects.all()[0]
        self.assertEqual(fp.title, 'New Title')
        self.assertEqual(fp.medium, 'New Medium')
        self.assertEqual(fp.provenance, 'New Provenance')
        self.assertEqual(fp.notes, 'Some notes')

        self.assertIsNotNone(fp.book_copy)
        self.assertIsNotNone(fp.book_copy.imprint)
        self.assertIsNotNone(fp.book_copy.imprint.work)


class AddActorViewTest(TestCase):
    def setUp(self):
        self.user = UserFactory()

        grp = GroupFactory(permissions=ADD_CHANGE_PERMISSIONS)
        self.contributor = UserFactory(group=grp)

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
        except Actor.DoesNotExist:
            pass  # expected

        Actor.objects.get(person__name='Alpha Beta',
                          role=self.role, alias='Alf')

    def test_post_expected_errors(self):
        # not logged in
        self.assertEqual(self.client.post(self.add_url).status_code, 302)

        # no ajax
        self.client.login(username=self.user.username, password="test")
        self.assertEqual(self.client.post(self.add_url).status_code, 403)

    def test_post_invalid_role(self):
        # invalid role id
        self.client.login(username=self.contributor.username, password="test")
        response = self.client.post(self.add_url,
                                    {'parent_id': self.footprint.id,
                                     'parent_model': 'footprint',
                                     'person_name': 'Albert Einstein',
                                     'role': 3000},
                                    HTTP_X_REQUESTED_WITH='XMLHttpRequest')
        self.assertEqual(response.status_code, 404)

    def test_post_success(self):
        self.assertEqual(self.footprint.actor.count(), 1)

        self.client.login(username=self.contributor.username, password="test")
        response = self.client.post(self.add_url,
                                    {'parent_id': self.footprint.id,
                                     'parent_model': 'footprint',
                                     'person_name': 'Albert Einstein',
                                     'role': self.role.id},
                                    HTTP_X_REQUESTED_WITH='XMLHttpRequest')
        self.assertEqual(response.status_code, 200)
        the_json = loads(response.content.decode('utf-8'))
        self.assertTrue(the_json['success'])

        # refresh footprint from database
        footprint = Footprint.objects.get(id=self.footprint.id)
        self.assertEqual(footprint.actor.count(), 2)
        footprint.actor.get(person__name='Albert Einstein')


class RemoveRelatedViewTest(TestCase):

    def setUp(self):
        self.user = UserFactory()

        grp = GroupFactory(permissions=ADD_CHANGE_PERMISSIONS)
        self.contributor = UserFactory(group=grp)

        self.footprint = FootprintFactory()
        self.remove_url = reverse('remove-related')

    def test_post(self):
        # not logged in
        self.assertEqual(self.client.post(self.remove_url).status_code, 302)

        # no ajax
        self.client.login(username=self.user.username, password="test")
        self.assertEqual(self.client.post(self.remove_url).status_code, 403)

        # missing params
        self.client.login(username=self.contributor.username, password="test")

        response = self.client.post(self.remove_url,
                                    {'parent_id': self.footprint.id,
                                     'parent_model': 'footprint'},
                                    HTTP_X_REQUESTED_WITH='XMLHttpRequest')
        self.assertEqual(response.status_code, 200)
        self.assertFalse(loads(response.content.decode('utf-8'))['success'])

        # success
        dt = self.footprint.associated_date

        self.client.login(username=self.contributor.username, password="test")

        response = self.client.post(self.remove_url, {
            'parent_id': self.footprint.id,
            'parent_model': 'footprint',
            'child_id': self.footprint.associated_date.id,
            'attr': 'associated_date'},
            HTTP_X_REQUESTED_WITH='XMLHttpRequest')

        self.assertEqual(response.status_code, 200)
        self.assertTrue(loads(response.content.decode('utf-8'))['success'])

        footprint = Footprint.objects.get(id=self.footprint.id)  # refresh
        self.assertIsNone(footprint.associated_date)

        with self.assertRaises(ExtendedDate.DoesNotExist):
            ExtendedDate.objects.get(id=dt.id)

    def test_post_remove_invalid_child_id(self):
        dt = ExtendedDateFactory()

        self.client.login(username=self.contributor.username, password="test")

        response = self.client.post(self.remove_url, {
            'parent_id': self.footprint.id,
            'parent_model': 'footprint',
            'child_id': dt.id,
            'attr': 'associated_date'},
            HTTP_X_REQUESTED_WITH='XMLHttpRequest')

        self.assertEqual(response.status_code, 200)
        self.assertFalse(loads(response.content.decode('utf-8'))['success'])

        footprint = Footprint.objects.get(id=self.footprint.id)  # refresh
        self.assertIsNotNone(footprint.associated_date)


class RemoveRelatedActorViewTest(TestCase):

    def setUp(self):
        self.user = UserFactory()

        grp = GroupFactory(permissions=ADD_CHANGE_PERMISSIONS)
        self.contributor = UserFactory(group=grp)

        self.footprint = FootprintFactory()

        self.actor = ActorFactory()
        self.footprint.actor.add(self.actor)

        self.remove_url = reverse('remove-related')

    def test_post_remove_actor(self):
        self.assertEqual(self.footprint.actor.count(), 2)

        self.client.login(username=self.contributor.username, password="test")
        response = self.client.post(self.remove_url,
                                    {'parent_id': self.footprint.id,
                                     'parent_model': 'footprint',
                                     'child_id': self.actor.id,
                                     'attr': 'actor'},
                                    HTTP_X_REQUESTED_WITH='XMLHttpRequest')
        self.assertEqual(response.status_code, 200)
        self.assertTrue(loads(response.content.decode('utf-8'))['success'])
        self.assertEqual(self.footprint.actor.count(), 1)


class RemoveRelatedIdentifierViewTest(TestCase):

    def setUp(self):
        self.user = UserFactory()

        grp = GroupFactory(permissions=ADD_CHANGE_PERMISSIONS)
        self.contributor = UserFactory(group=grp)

        self.footprint = FootprintFactory()

        self.remove_url = reverse('remove-related')

    def test_post_remove_identifier(self):
        imprint = self.footprint.book_copy.imprint
        identifier = imprint.standardized_identifier.first()

        self.client.login(username=self.contributor.username, password="test")
        response = self.client.post(self.remove_url,
                                    {'parent_id': imprint.id,
                                     'parent_model': 'imprint',
                                     'child_id': identifier.id,
                                     'attr': 'standardized_identifier'},
                                    HTTP_X_REQUESTED_WITH='XMLHttpRequest')
        self.assertEqual(response.status_code, 200)
        self.assertTrue(loads(response.content.decode('utf-8'))['success'])

        imprint = Imprint.objects.get(id=imprint.id)  # refresh
        self.assertEqual(imprint.standardized_identifier.count(), 0)


class AddDateViewTest(TestCase):

    def setUp(self):
        self.user = UserFactory()
        self.url = reverse('add-date-view')

    def test_post(self):
        # not logged in
        self.assertEqual(self.client.post(self.url).status_code, 302)

        # no ajax
        self.client.login(username=self.user.username, password="test")
        self.assertEqual(self.client.post(self.url).status_code, 403)

        # success
        grp = GroupFactory(permissions=ADD_CHANGE_PERMISSIONS)
        self.contributor = UserFactory(group=grp)

        self.footprint = FootprintFactory(title="Custom", associated_date=None)

        # no data
        self.client.login(username=self.contributor.username, password="test")
        response = self.client.post(self.url,
                                    {'parent_id': self.footprint.id,
                                     'parent_model': 'footprint'},
                                    HTTP_X_REQUESTED_WITH='XMLHttpRequest')
        self.assertEqual(response.status_code, 200)
        the_json = loads(response.content.decode('utf-8'))
        self.assertFalse(the_json['success'])

        self.client.login(username=self.contributor.username, password="test")
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
        self.assertEqual(response.status_code, 200)
        the_json = loads(response.content.decode('utf-8'))

        self.footprint.refresh_from_db()
        self.assertTrue(the_json['success'])
        self.assertEqual(self.footprint.associated_date.edtf_format, '1673')


class DisplayDateViewTest(TestCase):

    def setUp(self):
        self.user = UserFactory()

        grp = GroupFactory(permissions=ADD_CHANGE_PERMISSIONS)
        self.contributor = UserFactory(group=grp)

        self.footprint = FootprintFactory(title="Custom", associated_date=None)

        self.url = reverse('display-date-view')

    def test_post(self):
        # no ajax
        self.client.login(username=self.user.username, password="test")
        self.assertEqual(self.client.post(self.url).status_code, 405)

        # no_data(self):
        self.client.login(username=self.contributor.username, password="test")
        response = self.client.post(self.url,
                                    {'parent_id': self.footprint.id,
                                     'parent_model': 'footprint'},
                                    HTTP_X_REQUESTED_WITH='XMLHttpRequest')
        self.assertEqual(response.status_code, 200)
        the_json = loads(response.content.decode('utf-8'))
        self.assertFalse(the_json['success'])

        # success
        self.client.login(username=self.contributor.username, password="test")
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
        self.assertEqual(response.status_code, 200)
        the_json = loads(response.content.decode('utf-8'))
        self.assertTrue(the_json['success'])
        self.assertEqual(the_json['display'], '1673')


class AddPlaceViewTest(TestCase):

    def setUp(self):
        self.user = UserFactory()

        grp = GroupFactory(permissions=ADD_CHANGE_PERMISSIONS)
        self.contributor = UserFactory(group=grp)

        self.url = reverse('add-place-view')

    def test_post_anon(self):
        # not logged in
        self.assertEqual(self.client.post(self.url).status_code, 302)

    def test_post_ajax(self):
        # no ajax
        self.client.login(username=self.user.username, password="test")
        self.assertEqual(self.client.post(self.url).status_code, 403)

    def test_post_invalid_data(self):
        fp = FootprintFactory()

        # no data
        self.client.login(username=self.contributor.username, password="test")
        response = self.client.post(self.url,
                                    {'parent_id': fp.id,
                                     'parent_model': 'footprint'},
                                    HTTP_X_REQUESTED_WITH='XMLHttpRequest')
        self.assertEqual(response.status_code, 200)
        the_json = loads(response.content.decode('utf-8'))
        self.assertFalse(the_json['success'])

    def test_post_success(self):
        footprint = FootprintFactory(title='Custom', place=None)

        # success
        self.client.login(username=self.contributor.username, password="test")
        response = self.client.post(
            self.url,
            {'parent_id': footprint.id,
             'parent_model': 'footprint',
             'placeName': 'NYC',
             'placeId': 'NYC',
             'canonicalName': 'New York, United States',
             'geonameId': 1234,
             'position': '40.752946,-73.983435'},
            HTTP_X_REQUESTED_WITH='XMLHttpRequest')
        self.assertEqual(response.status_code, 200)
        the_json = loads(response.content.decode('utf-8'))

        # place is created
        footprint.refresh_from_db()
        self.assertTrue(the_json['success'])
        self.assertEqual(footprint.place.alternate_name, 'NYC')
        self.assertEqual(
            footprint.place.canonical_place.geoname_id, '1234')
        self.assertEqual(
            footprint.place.canonical_place.canonical_name,
            'New York, United States')
        self.assertEqual(
            footprint.place.canonical_place.latlng_string(),
            '40.752946,-73.983435')

    def test_post_existing_canonical_place(self):
        fp = FootprintFactory()
        old_place = fp.place

        # existing canonical place is used, new place created
        self.client.login(username=self.contributor.username, password="test")
        response = self.client.post(
            self.url,
            {'parent_id': fp.id,
             'parent_model': 'footprint',
             'placeName': 'Nueva York',
             'placeId': 'Nueva York',
             'geonameId': fp.place.canonical_place.geoname_id,
             'canonicalName': fp.place.canonical_place.canonical_name,
             'position': fp.place.canonical_place.latlng_string()},
            HTTP_X_REQUESTED_WITH='XMLHttpRequest')
        self.assertEqual(response.status_code, 200)
        fp.refresh_from_db()
        self.assertEqual(
            old_place.canonical_place.id, fp.place.canonical_place.id)
        self.assertNotEqual(old_place.id, fp.place.id)
        self.assertEqual(fp.place.alternate_name, 'Nueva York')

    def test_post_existing_place_id(self):
        place = PlaceFactory()
        fp = FootprintFactory()

        # existing canonical place is used, new place created
        self.client.login(username=self.contributor.username, password="test")
        response = self.client.post(
            self.url,
            {'parent_id': fp.id,
             'parent_model': 'footprint',
             'placeName': place.alternate_name,
             'placeId': place.id,
             'geonameId': place.canonical_place.geoname_id,
             'canonicalName': place.canonical_place.canonical_name,
             'position': place.canonical_place.latlng_string()},
            HTTP_X_REQUESTED_WITH='XMLHttpRequest')
        self.assertEqual(response.status_code, 200)
        fp.refresh_from_db()
        self.assertEqual(fp.place.id, place.id)

    def test_post_existing_place(self):
        fp = FootprintFactory()
        old_place = fp.place

        # existing canonical place is used, new place created
        self.client.login(username=self.contributor.username, password="test")
        response = self.client.post(
            self.url,
            {'parent_id': fp.id,
             'parent_model': 'footprint',
             'placeName': fp.place.alternate_name,
             'placeId': fp.place.alternate_name,
             'geonameId': fp.place.canonical_place.geoname_id,
             'canonicalName': fp.place.canonical_place.canonical_name,
             'position': fp.place.canonical_place.latlng_string()},
            HTTP_X_REQUESTED_WITH='XMLHttpRequest')
        self.assertEqual(response.status_code, 200)
        fp.refresh_from_db()
        self.assertEqual(
            old_place.canonical_place.id, fp.place.canonical_place.id)
        self.assertEqual(old_place.id, fp.place.id)

    def test_get_canonical_place(self):
        # gets an existing place by geonameid
        cp = CanonicalPlaceFactory()
        view = AddPlaceView()
        self.assertEqual(
            cp,
            view.get_canonical_place(
                cp.geoname_id, cp.latlng_string(), cp.canonical_name))

        # creates a new place
        view = AddPlaceView()
        self.assertNotEqual(
            cp,
            view.get_canonical_place('5', '40.71427,-74.00597', 'New York'))

        # get an existing place that doesn't have a geoname id yet,
        cp2 = CanonicalPlaceFactory(geoname_id=None)
        AddPlaceView().get_canonical_place(
            '15', cp2.latlng_string(), cp2.canonical_name)
        cp2.refresh_from_db()
        self.assertEqual(cp2.geoname_id, '15')


class AddIdentifierViewTest(TestCase):

    def setUp(self):
        self.user = UserFactory()

        grp = GroupFactory(permissions=ADD_CHANGE_PERMISSIONS)
        self.contributor = UserFactory(group=grp)

        self.imprint = ImprintFactory()

        self.url = reverse('add-identifier-view')

    def test_post(self):
        # not logged in
        self.assertEqual(self.client.post(self.url).status_code, 302)

        # no ajax
        self.client.login(username=self.user.username, password="test")
        self.assertEqual(self.client.post(self.url).status_code, 403)

        # no data
        self.client.login(username=self.contributor.username, password="test")
        response = self.client.post(self.url,
                                    {'parent_id': self.imprint.id,
                                     'parent_model': 'imprint'},
                                    HTTP_X_REQUESTED_WITH='XMLHttpRequest')
        self.assertEqual(response.status_code, 404)

        # success
        self.assertEqual(self.imprint.standardized_identifier.count(), 1)
        self.client.login(username=self.contributor.username, password="test")
        response = self.client.post(self.url,
                                    {'parent_id': self.imprint.id,
                                     'parent_model': 'imprint',
                                     'identifier': 'abcdefg',
                                     'identifier_type': 'LOC'},
                                    HTTP_X_REQUESTED_WITH='XMLHttpRequest')
        self.assertEqual(response.status_code, 200)
        the_json = loads(response.content.decode('utf-8'))
        self.assertTrue(the_json['success'])

        imprint = Imprint.objects.get(id=self.imprint.id)  # refresh from db
        identifier = imprint.standardized_identifier.get(identifier='abcdefg')
        self.assertEqual(
            identifier.identifier_type,
            StandardizedIdentificationType.objects.get(slug='LOC'))


class AddDigitalObjectViewTest(TestCase):

    def setUp(self):
        self.user = UserFactory()

        grp = GroupFactory(permissions=ADD_CHANGE_PERMISSIONS)
        self.contributor = UserFactory(group=grp)

        self.footprint = FootprintFactory()

        self.url = reverse('add-digital-object-view')

    def test_post(self):
        # not logged in
        self.assertEqual(self.client.post(self.url).status_code, 302)

        # no ajax
        self.client.login(username=self.user.username, password="test")
        self.assertEqual(self.client.post(self.url).status_code, 403)

        # no data
        self.client.login(username=self.contributor.username, password="test")
        response = self.client.post(self.url,
                                    {'parent_id': self.footprint.id,
                                     'parent_model': 'footprint'},
                                    HTTP_X_REQUESTED_WITH='XMLHttpRequest')
        self.assertEqual(response.status_code, 200)
        the_json = loads(response.content.decode('utf-8'))
        self.assertFalse(the_json['success'])

        # success
        f = SimpleUploadedFile('file.txt', b'file_content')

        self.client.login(username=self.contributor.username, password="test")
        response = self.client.post(self.url,
                                    {'parent_id': self.footprint.id,
                                     'parent_model': 'footprint',
                                     'name': 'foo.jpg',
                                     'description': 'Foo Bar',
                                     'file': f},
                                    HTTP_X_REQUESTED_WITH='XMLHttpRequest')
        self.assertEqual(response.status_code, 200)
        the_json = loads(response.content.decode('utf-8'))

        footprint = Footprint.objects.get(id=self.footprint.id)  # refresh
        self.assertTrue(the_json['success'])
        self.assertEqual(footprint.digital_object.count(), 1)


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
        self.assertEqual(initial['name'], 'Foo Bar')
        self.assertEqual(initial['email'], 'foo@bar.com')

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
        self.assertEqual(mail.outbox[0].from_email,
                         'footprints@mail.ctl.columbia.edu')
        self.assertEqual(mail.outbox[0].to,
                         [settings.CONTACT_US_EMAIL])


class AddLanguageViewTest(TestCase):

    def testAddRemove(self):
        grp = GroupFactory(permissions=ADD_CHANGE_PERMISSIONS)
        contributor = UserFactory(group=grp)

        self.client.login(username=contributor.username, password='test')
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
        self.assertEqual(response.status_code, 200)

        footprint.refresh_from_db()
        self.assertEqual(footprint.language.count(), 2)
        self.assertTrue(english in footprint.language.all())
        self.assertTrue(generic in footprint.language.all())

        # remove generic
        data = {'parent_id': footprint.id,
                'parent_model': 'footprint',
                'language': [english.id]}

        response = self.client.post(url, data,
                                    HTTP_X_REQUESTED_WITH='XMLHttpRequest')
        self.assertEqual(response.status_code, 200)

        footprint.refresh_from_db()
        self.assertEqual(footprint.language.count(), 1)
        self.assertTrue(english in footprint.language.all())

        # generic was not deleted
        Language.objects.get(id=generic.id)

        # remove english too
        data = {'parent_id': footprint.id,
                'parent_model': 'footprint',
                'language': []}

        response = self.client.post(url, data,
                                    HTTP_X_REQUESTED_WITH='XMLHttpRequest')
        self.assertEqual(response.status_code, 200)

        footprint.refresh_from_db()
        self.assertEqual(footprint.language.count(), 0)

        # english was not deleted
        Language.objects.get(id=english.id)


class SearchViewTest(TestCase):

    def test_search(self):
        url = "{}/?q=foo&models=main.footprint".format(reverse('search'))

        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.context['page_obj'].object_list), 0)

        self.assertTrue(response.context['search_criteria'])

    def test_empty_search(self):
        url = reverse('search')

        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.context['page_obj'].object_list), 0)

        self.assertFalse(response.context['search_criteria'])


class SearchIndexTest(TestCase):

    def test_format_sort_by(self):
        self.assertEqual(format_sort_by(u'ABCD'), 'abcd')
        self.assertEqual(format_sort_by(u'The A', True), 'a')


class ModerationViewTest(TestCase):

    def test_get(self):
        user = UserFactory()

        grp = GroupFactory(permissions=MODERATION_PERMISSIONS)
        moderator = UserFactory(group=grp)

        url = reverse('moderation-view')
        self.assertEqual(self.client.get(url).status_code, 302)

        self.client.login(username=user.username, password='test')
        self.assertEqual(self.client.get(url).status_code, 403)

        self.client.login(username=moderator.username, password='test')
        self.assertEqual(self.client.get(url).status_code, 200)


class VerifyFootprintViewTest(TestCase):

    def test_post(self):
        feed = VerifiedFootprintFeed()
        fp = FootprintFactory()
        user = UserFactory()

        grp = GroupFactory(permissions=MODERATION_PERMISSIONS)
        moderator = UserFactory(group=grp)

        url = reverse('verify-footprint-view', kwargs={'pk': fp.id})
        self.assertEqual(self.client.get(url).status_code, 302)

        self.client.login(username=user.username, password='test')
        self.assertEqual(self.client.get(url).status_code, 403)

        self.client.login(username=moderator.username, password='test')

        data = {'verified': 1}
        self.assertEqual(self.client.post(url, data).status_code, 302)
        fp.refresh_from_db()
        self.assertTrue(fp.verified)
        self.assertEqual(feed.items().count(), 1)

        data = {'verified': 0}
        self.assertEqual(self.client.post(url, data).status_code, 302)
        fp.refresh_from_db()
        self.assertFalse(fp.verified)
        self.assertEqual(feed.items().count(), 0)
