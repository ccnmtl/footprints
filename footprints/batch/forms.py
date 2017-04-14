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

    INVALID_HEADER_ROW = (
            "The selected file has an invalid header row.")

    VALID_HEADERS = [
        'Catalog Link', 'BHB number', 'Imprint Title', 'Literary Work Title',
        'Literary Work Author', 'Literary Work Author VIAF ID',
        'Literary Work Author Birth Date', 'Literary Work Author Death Date',
        'Publisher', 'Publisher VIAF ID', 'Publication Location',
        'Publication Date', 'Book Copy Call Number', 'Evidence Type',
        'Evidence Location Description', 'Evidence Call Number',
        'Footprint Actor', 'Footprint Actor VIAF ID', 'Footprint Actor Role',
        'Footprint Actor Begin Date', 'Footprint Actor End Date',
        'Footprint Notes', 'Footprint Location', 'Footprint Date']

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

    def validate_header(self, row):
        for idx, a in enumerate(row):
            if a.lower() != self.VALID_HEADERS[idx].lower():
                return False
        return True

    def clean(self):
        cleaned_data = super(CreateBatchJobForm, self).clean()
        if 'csvfile' not in cleaned_data:
            self._errors['csvfile'] = self.error_class([
                'Please select a data file'])
            return cleaned_data

        # do some rudimentary validation on the file
        try:
            for idx, row in enumerate(csv.reader(cleaned_data['csvfile'])):
                if (idx == 0 and not self.validate_header(row)):
                    self._errors['csvfile'] = self.error_class([
                        self.INVALID_HEADER_ROW])
                    break

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
