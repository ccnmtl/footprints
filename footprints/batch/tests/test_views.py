from django.core.files.uploadedfile import SimpleUploadedFile
from django.core.urlresolvers import reverse
from django.test.client import RequestFactory
from django.test.testcases import TestCase

from footprints.batch.forms import CreateBatchJobForm
from footprints.batch.models import BatchRow, BatchJob
from footprints.batch.tests.factories import BatchJobFactory
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
