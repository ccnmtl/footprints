import csv

from django import forms
from django.utils.encoding import DjangoUnicodeDecodeError, force_text

from footprints.batch.models import BatchRow


class CreateBatchJobForm(forms.Form):
    INVALID_FILE_FORMAT = ("The selected file is not formatted properly. "
                           "Please select a valid data file.")
    INVALID_ENCODING = (
        "The selected file is not encoded properly. Batch files must be "
        "encoded using the UTF-8 standard to ensure special characters are "
        "translated correctly.<br /><br /> The full error is:<br />{}.")

    csvfile = forms.FileField(required=True)

    def validate_column_count(self, row):
        return len(row) == len(BatchRow.FIELD_MAPPING)

    def validate_encoding(self, row):
        for col in row:
            try:
                force_text(col)
            except DjangoUnicodeDecodeError, e:
                return False, e

        return True, ''

    def clean(self):
        cleaned_data = super(CreateBatchJobForm, self).clean()

        if 'csvfile' not in cleaned_data:
            self._errors['csvfile'] = self.error_class([
                'Please select a data file'])
            return cleaned_data

        # do some rudimentary validation on the file
        try:
            for row in csv.reader(cleaned_data['csvfile']):
                if not self.validate_column_count(row):
                    self._errors['csvfile'] = self.error_class([
                        self.INVALID_FILE_FORMAT])
                    break

                valid, e = self.validate_encoding(row)
                if not valid:
                    self._errors['csvfile'] = self.error_class([
                        self.INVALID_ENCODING.format(unicode(e))])
                    break

        except csv.Error:
            self._errors['csvfile'] = self.error_class([
                self.INVALID_FILE_FORMAT])

        return cleaned_data
