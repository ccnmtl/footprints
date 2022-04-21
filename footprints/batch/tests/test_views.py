from django.core.files.uploadedfile import SimpleUploadedFile
from django.test.client import RequestFactory
from django.test.testcases import TestCase
from django.urls.base import reverse
from django.contrib.messages import get_messages

from footprints.batch.forms import CreateBatchJobForm
from footprints.batch.models import BatchRow, BatchJob
from footprints.batch.tests.factories import BatchJobFactory, BatchRowFactory
from footprints.batch.views import BatchJobListView, BatchJobUpdateView
from footprints.main.models import Footprint
from footprints.main.tests.factories import UserFactory, WrittenWorkFactory, \
    ImprintFactory, FootprintFactory, RoleFactory, BookCopyFactory, \
    PlaceFactory, GroupFactory, BATCH_PERMISSIONS, CanonicalPlaceFactory


try:
    from unittest import mock
except ImportError:
    import mock


class BatchJobListViewTest(TestCase):

    def setUp(self):
        super(TestCase, self).setUp()

        url = reverse('batchjob-list-view')
        request = RequestFactory().get(url, {})
        request.user = UserFactory()

        self.view = BatchJobListView()
        self.view.request = request

    def test_get_context_data(self):
        BatchJobFactory()
        BatchJobFactory()

        ctx = self.view.get_context_data()
        self.assertTrue('jobs' in ctx)
        self.assertTrue(ctx['jobs'].count(), 2)

    def test_get_success_url(self):
        self.view.job = BatchJobFactory()
        self.assertEqual(self.view.get_success_url(),
                         '/batch/job/{}/'.format(self.view.job.id))

    def test_form_valid(self):
        row = ','.join(BatchRow.FIELD_MAPPING)
        content = '{}\n{}'.format(row, row)
        csvfile = SimpleUploadedFile('test.csv', str.encode(content))

        form = CreateBatchJobForm()
        form.cleaned_data = {'csvfile': csvfile}
        form._errors = {}
        form.clean()

        self.view.form_valid(form)

        jobs = BatchJob.objects.all()
        self.assertEqual(jobs.count(), 1)

        job = jobs.first()
        self.assertEqual(job.created_by, self.view.request.user)
        self.assertEqual(job.batchrow_set.count(), 1)


class BatchJobDetailView(TestCase):

    def test_get(self):
        job = BatchJobFactory()
        url = reverse('batchjob-detail-view', kwargs={'pk': job.id})

        response = self.client.get(url)
        self.assertEqual(response.status_code, 302)

        grp = GroupFactory(permissions=BATCH_PERMISSIONS)
        staff = UserFactory(group=grp)
        self.client.login(username=staff.username, password='test')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertTrue('fields' in response.context_data)


class BatchJobDeleteViewTest(TestCase):
    def setUp(self):
        grp = GroupFactory(permissions=BATCH_PERMISSIONS)
        self.staff = UserFactory(group=grp)

        self.job = BatchJobFactory()

        self.url = reverse('batchjob-delete-view', kwargs={'pk': self.job.id})

    def test_post(self):
        self.client.login(username=self.staff.username, password='test')
        response = self.client.post(self.url, {})
        self.assertEqual(response.status_code, 302)

        self.assertFalse(BatchJob.objects.filter(id=self.job.id).exists())


class BatchJobUpdateViewTest(TestCase):

    def setUp(self):
        self.user = UserFactory()

        grp = GroupFactory(permissions=BATCH_PERMISSIONS)
        self.staff = UserFactory(group=grp)

        self.job = BatchJobFactory()
        self.record1 = BatchRowFactory(job=self.job)
        self.record2 = BatchRowFactory(job=self.job,
                                       footprint_date='1996',
                                       medium='Approbation in imprint')
        self.url = reverse('batchjob-update-view', kwargs={'pk': self.job.pk})

        RoleFactory(name=self.record1.footprint_actor_role)

    def test_view_basics(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 302)

        response = self.client.post(self.url)
        self.assertEqual(response.status_code, 302)

        self.client.login(username=self.user.username, password='test')
        response = self.client.post(self.url)
        self.assertEqual(response.status_code, 403)

    def test_add_author(self):
        work = WrittenWorkFactory()
        row = BatchRowFactory()
        RoleFactory(name='Author')

        view = BatchJobUpdateView()
        view.add_author(row, work)

        q = {
            'person__standardized_identifier__identifier':
                row.writtenwork_author_viaf,
            'person__name': row.writtenwork_author,
            'person__birth_date__edtf_format': '1702',
            'person__death_date__edtf_format': '1789',
            'role__name': 'Author'
        }
        self.assertTrue(work.actor.filter(**q).exists())

    def test_add_publisher(self):
        imprint = ImprintFactory()
        row = BatchRowFactory()

        view = BatchJobUpdateView()
        view.add_publisher(row, imprint)

        q = {
            'person__standardized_identifier__identifier':
                row.publisher_viaf,
            'person__name': row.publisher,
            'role__name': 'Publisher'
        }
        self.assertTrue(imprint.actor.filter(**q).exists())

    def test_add_actor(self):
        footprint = FootprintFactory()

        view = BatchJobUpdateView()
        view.add_actor(self.record1, footprint)

        q = {
            'person__name': self.record1.footprint_actor,
            'role__name': self.record1.footprint_actor_role
        }
        self.assertTrue(footprint.actor.filter(**q).exists())

    def test_add_place_new(self):
        content = {
            'name': 'Osgiliath',
            'adminName1': 'Gondor', 'countryName': 'Middle Earth',
            'lat': '-44.2599', 'lng': '170.1043'
        }

        with self.settings(GEONAMES_KEY='abcd'):
            with mock.patch('footprints.main.utils.requests.get') as mock_get:
                mock_get.return_value.json.return_value = content

                footprint = FootprintFactory()
                view = BatchJobUpdateView()
                view.add_place(footprint, '1')

                footprint.refresh_from_db()
                self.assertEqual(-44.2599, footprint.place.latitude())
                self.assertEqual(170.1043, footprint.place.longitude())
                self.assertEqual(
                    'Osgiliath, Gondor, Middle Earth',
                    footprint.place.alternate_name)
                self.assertEqual(
                    'Osgiliath, Gondor, Middle Earth',
                    footprint.place.canonical_place.canonical_name)

    def test_add_place_existing(self):
        position = '51.064650,20.944979'
        cp = CanonicalPlaceFactory(position=position)
        place = PlaceFactory(
            canonical_place=cp, alternate_name=cp.canonical_name)
        footprint = FootprintFactory()

        view = BatchJobUpdateView()
        view.add_place(footprint, cp.geoname_id)

        footprint.refresh_from_db()
        self.assertEqual(place.latitude(), footprint.place.latitude())
        self.assertEqual(place.longitude(), footprint.place.longitude())
        self.assertEqual(place.alternate_name, footprint.place.alternate_name)
        self.assertEqual(place.canonical_place.canonical_name,
                         footprint.place.canonical_place.canonical_name)

    def test_get_or_create_imprint(self):
        view = BatchJobUpdateView()
        imprint = view.get_or_create_imprint(self.record1)

        self.assertIsNone(imprint.place)

        self.assertTrue(imprint.work.actor.filter(
            person__name=self.record1.writtenwork_author).exists())

        self.assertTrue(imprint.actor.filter(
            person__name=self.record1.publisher).exists())

    def test_get_or_create_copy(self):
        view = BatchJobUpdateView()

        # match copy via book call number
        existing_copy = BookCopyFactory(call_number='123456')
        copy = view.get_or_create_copy(existing_copy.imprint,
                                       existing_copy.call_number)
        self.assertEqual(existing_copy, copy)

        # get a new copy. no footprint found to match
        imprint = ImprintFactory()
        copy = view.get_or_create_copy(imprint, 'abcd')
        self.assertEqual(copy.call_number, 'abcd')

    def test_create_footprint(self):
        copy = BookCopyFactory()

        view = BatchJobUpdateView()
        fp = view.create_footprint(self.record1, copy)

        self.assertEqual(fp.book_copy, copy)
        self.assertEqual(fp.medium, self.record1.medium)
        self.assertEqual(fp.medium_description,
                         self.record1.medium_description)
        self.assertEqual(fp.provenance, self.record1.provenance)
        self.assertEqual(fp.call_number, self.record1.call_number)
        self.assertEqual(fp.notes, self.record1.aggregate_notes())

        self.assertEqual(str(fp.associated_date),
                         self.record1.footprint_date)
        self.assertEqual(fp.place, None)
        self.assertEqual(fp.narrative, 'Sample Narrative')

    def test_post(self):
        self.client.login(username=self.staff.username, password='test')
        response = self.client.post(self.url)
        self.assertEqual(response.status_code, 302)

        fp1 = Footprint.objects.get(medium='Library Catalog/Union Catalog')
        a = self.record1.similar_footprints()
        self.assertEqual(a.count(), 1)
        self.assertEqual(a.first(), fp1.id)
        self.record1.refresh_from_db()
        self.assertEqual(self.record1.footprint, fp1)

        fp2 = Footprint.objects.get(medium='Approbation in imprint')
        a = self.record2.similar_footprints()
        self.assertEqual(a.count(), 1)
        self.assertEqual(a.first(), fp2.id)
        self.record2.refresh_from_db()
        self.assertEqual(self.record2.footprint, fp2)

        self.assertTrue(fp1.book_copy, fp2.book_copy)
        messages = [m.message for m in get_messages(response.wsgi_request)]
        self.assertIn('2 footprints created', messages[0])

        self.job.refresh_from_db()
        self.assertTrue(self.job.processed)


class BatchRowUpdateViewTest(TestCase):

    def setUp(self):
        grp = GroupFactory(permissions=BATCH_PERMISSIONS)
        self.staff = UserFactory(group=grp)

        self.row = BatchRowFactory()

        self.url = reverse('batchrow-update-view',
                           kwargs={'pk': self.row.id})

    def test_get(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 302)

    def test_post(self):
        self.client.login(username=self.staff.username, password='test')
        data = {
            'imprint_title': 'Something different',
            'bhb_number': 'abcdefg'
        }

        response = self.client.post(self.url, data)
        self.assertEqual(response.status_code, 302)

        self.row.refresh_from_db()
        self.assertEqual(self.row.imprint_title, 'Something different')
        self.assertEqual(self.row.bhb_number, 'abcdefg')


class BatchRowDeleteViewTest(TestCase):
    def setUp(self):
        grp = GroupFactory(permissions=BATCH_PERMISSIONS)
        self.staff = UserFactory(group=grp)
        self.row = BatchRowFactory()

        self.url = reverse('batchrow-delete-view',
                           kwargs={'pk': self.row.id})

    def test_post(self):
        self.client.login(username=self.staff.username, password='test')
        response = self.client.post(self.url, {})
        self.assertEqual(response.status_code, 302)

        self.assertFalse(BatchRow.objects.filter(id=self.row.id).exists())
