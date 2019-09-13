import csv
from django import forms
from django.utils.encoding import (
    DjangoUnicodeDecodeError, force_text, smart_text)

from footprints.batch.models import BatchRow


class CreateBatchJobForm(forms.Form):
    INVALID_FILE_FORMAT = ("The selected file is not formatted properly. "
                           "Please select a valid data file.")
    INVALID_ENCODING = (
        "The selected file is not encoded properly. Batch files must be "
        "encoded using the UTF-8 standard to ensure special characters are "
        "translated correctly.<br /><br /> The full error is:<br />{}.")

    INVALID_HEADER_ROW = (
            "The selected file has an invalid header element. "
            "Column {} is \"{}\", rather than \"{}\".")

    VALID_HEADERS = [
        'Catalog Link', 'BHB number', 'Imprint Title', 'Literary Work Title',
        'Literary Work Author', 'Literary Work Author VIAF ID',
        'Literary Work Author Birth Date', 'Literary Work Author Death Date',
        'Publisher', 'Publisher VIAF ID', 'Publication Location',
        'Publication Date', 'Book Copy Call Number', 'Evidence Type',
        'Evidence Location Description', 'Evidence Citation',
        'Footprint Actor (Former Owner/Seller/Other)',
        'Footprint Actor VIAF ID', 'Footprint Actor Role',
        'Footprint Actor Begin Date', 'Footprint Actor End Date',
        'Footprint Notes', 'Footprint Location', 'Footprint Date',
        'Footprint Narrative']

    csvfile = forms.FileField(required=True)

    def csvfile_reader(self):
        csv_file = self.cleaned_data['csvfile']
        return csv.reader(csv_file)

    def validate_column_count(self, row):
        return len(row) == len(BatchRow.FIELD_MAPPING)

    def validate_encoding(self, row):
        for col in row:
            try:
                force_text(col)
            except DjangoUnicodeDecodeError as e:
                return False, e

        return True, ''

    def validate_header(self, row):
        for idx, a in enumerate(row):
            if a.lower() != self.VALID_HEADERS[idx].lower():
                msg = self.INVALID_HEADER_ROW.format(
                    idx, a,  self.VALID_HEADERS[idx])
                self._errors['csvfile'] = self.error_class([msg])
                return False
        return True

    def clean(self):
        cleaned_data = super(CreateBatchJobForm, self).clean()
        if 'csvfile' not in cleaned_data:
            self._errors['csvfile'] = self.error_class([
                'Please select a data file'])
            return cleaned_data

        self.validate_clean_data(cleaned_data)
        return cleaned_data

    def validate_clean_data(self, cleaned_data):
        # do some rudimentary validation on the file
        try:
            csvreader = self.csvfile_reader()
            for idx, row in enumerate(csvreader):
                if idx == 0 and not self.validate_header(row):
                    break

                if not self.validate_column_count(row):
                    self._errors['csvfile'] = self.error_class([
                        self.INVALID_FILE_FORMAT])
                    break

                valid, e = self.validate_encoding(row)
                if not valid:
                    self._errors['csvfile'] = self.error_class([
                        self.INVALID_ENCODING.format(
                            smart_text(e).encode('utf-8'))])
                    break

        except csv.Error:
            self._errors['csvfile'] = self.error_class([
                self.INVALID_FILE_FORMAT])
