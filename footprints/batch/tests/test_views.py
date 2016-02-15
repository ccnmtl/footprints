from json import loads

from django.core.files.uploadedfile import SimpleUploadedFile
from django.core.urlresolvers import reverse
from django.test.client import RequestFactory
from django.test.testcases import TestCase

from footprints.batch.forms import CreateBatchJobForm
from footprints.batch.models import BatchRow, BatchJob
from footprints.batch.tests.factories import BatchJobFactory, BatchRowFactory
from footprints.batch.views import BatchJobListView
from footprints.main.tests.factories import UserFactory


class BatchJobListViewTest(TestCase):

    def setUp(self):
        super(TestCase, self).setUp()

        url = reverse('batchjob-list-view')
        request = RequestFactory().get(url, {})
        request.user = UserFactory(is_staff=True)

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
        self.assertEquals(self.view.get_success_url(),
                          '/batch/job/{}/'.format(self.view.job.id))

    def test_form_valid(self):
        row = ','.join(BatchRow.FIELD_MAPPING)
        content = '{}\n{}'.format(row, row)
        csvfile = SimpleUploadedFile('test.csv', content)

        form = CreateBatchJobForm()
        form.cleaned_data = {'csvfile': csvfile}
        form.clean()

        self.view.form_valid(form)

        jobs = BatchJob.objects.all()
        self.assertEquals(jobs.count(), 1)

        job = jobs.first()
        self.assertEquals(job.created_by, self.view.request.user)
        self.assertEquals(job.batchrow_set.count(), 1)


class BatchJobDetailView(TestCase):

    def test_get(self):
        job = BatchJobFactory()
        url = reverse('batchjob-detail-view', kwargs={'pk': job.id})

        response = self.client.get(url)
        self.assertEquals(response.status_code, 405)

        staff = UserFactory(is_staff=True)
        self.client.login(username=staff.username, password='test')
        response = self.client.get(url)
        self.assertEquals(response.status_code, 200)
        self.assertTrue('fields' in response.context_data)


class BatchJobDeleteViewTest(TestCase):
    def setUp(self):
        self.staff = UserFactory(is_staff=True)
        self.job = BatchJobFactory()

        self.url = reverse('batchjob-delete-view', kwargs={'pk': self.job.id})

    def test_post(self):
        self.client.login(username=self.staff.username, password='test')
        response = self.client.post(self.url, {})
        self.assertEquals(response.status_code, 302)

        self.assertFalse(BatchJob.objects.filter(id=self.job.id).exists())


class BatchRowUpdateViewTest(TestCase):

    def setUp(self):
        self.staff = UserFactory(is_staff=True)
        self.row = BatchRowFactory()

        self.url = reverse('batchrow-update-view',
                           kwargs={'pk': self.row.job.id})

    def test_get(self):
        response = self.client.get(self.url)
        self.assertEquals(response.status_code, 405)

    def test_post_noajax(self):
        self.client.login(username=self.staff.username, password='test')
        response = self.client.post(self.url, {})
        self.assertEquals(response.status_code, 405)

    def test_post(self):
        self.client.login(username=self.staff.username, password='test')
        data = {
            'imprint_title': 'Something different',
            'bhb_number': 'abcdefg'
        }

        response = self.client.post(self.url, data,
                                    HTTP_X_REQUESTED_WITH='XMLHttpRequest')

        self.assertEquals(response.status_code, 200)
        the_json = loads(response.content)

        self.row.refresh_from_db()
        self.assertEquals(self.row.imprint_title, 'Something different')
        self.assertEquals(the_json['errors']['imprint_title'], 'valid')

        self.assertEquals(self.row.bhb_number, 'abcdefg')
        self.assertEquals(the_json['errors']['bhb_number'],
                          'invalid has-error')


class BatchRowDeleteViewTest(TestCase):
    def setUp(self):
        self.staff = UserFactory(is_staff=True)
        self.row = BatchRowFactory()

        self.url = reverse('batchrow-delete-view',
                           kwargs={'pk': self.row.job.id})

    def test_post(self):
        self.client.login(username=self.staff.username, password='test')
        response = self.client.post(self.url, {})
        self.assertEquals(response.status_code, 302)

        self.assertFalse(BatchRow.objects.filter(id=self.row.id).exists())
