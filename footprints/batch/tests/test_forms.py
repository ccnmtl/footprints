from django.core.files.uploadedfile import SimpleUploadedFile
from django.test.testcases import TestCase

from footprints.batch.forms import CreateBatchJobForm
from footprints.batch.models import BatchRow


class CreateBatchJobFormTest(TestCase):

    def test_form_clean(self):
        form = CreateBatchJobForm()
        form._errors = {}
        form.cleaned_data = {}

        form.clean()
        self.assertTrue('csvfile' in form._errors.keys())

    def test_form_clean_invalid_file_format(self):
        content = ','.join(CreateBatchJobForm.VALID_HEADERS) + '\r\n'
        content += '1,2,3,'
        csvfile = SimpleUploadedFile('file.csv', content)

        form = CreateBatchJobForm()
        form._errors = {}
        form.cleaned_data = {'csvfile': csvfile}

        form.clean()
        self.assertTrue('csvfile' in form._errors.keys())
        self.assertEquals(form._errors['csvfile'], [form.INVALID_FILE_FORMAT])

    def test_form_validate_headers(self):
        content = 'bad content'
        csvfile = SimpleUploadedFile('file.csv', content)

        form = CreateBatchJobForm()
        form._errors = {}
        form.cleaned_data = {'csvfile': csvfile}

        form.clean()
        self.assertTrue('csvfile' in form._errors.keys())
        self.assertEquals(form._errors['csvfile'], [form.INVALID_HEADER_ROW])

    def test_form_validate_headers_success(self):
        form = CreateBatchJobForm()
        self.assertTrue(form.validate_header(CreateBatchJobForm.VALID_HEADERS))

    def test_form_clean_valid_file_format(self):
        content = ','.join(CreateBatchJobForm.VALID_HEADERS) + '\r\n'
        content += ',' * (len(BatchRow.FIELD_MAPPING) - 1)
        csvfile = SimpleUploadedFile('file.csv', content)

        form = CreateBatchJobForm()
        form._errors = {}
        form.cleaned_data = {'csvfile': csvfile}

        form.clean()
        self.assertFalse('csvfile' in form._errors.keys())
