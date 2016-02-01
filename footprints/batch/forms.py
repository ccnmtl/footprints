import csv

from django import forms

from footprints.batch.models import BatchRow


class CreateBatchJobForm(forms.Form):
    INVALID_FILE_FORMAT = ("The selected file is not formatted properly. "
                           "Please select a valid data file.")

    csvfile = forms.FileField(required=True)

    def clean(self):
        cleaned_data = super(CreateBatchJobForm, self).clean()

        if 'csvfile' not in cleaned_data:
            self._errors['csvfile'] = self.error_class([
                'Please select a data file'])
            return cleaned_data

        # do some rudimentary validation on the file
        try:
            column_count = len(BatchRow.FIELD_MAPPING)
            for row in csv.reader(cleaned_data['csvfile']):
                num_cols = len(row)
                if num_cols != column_count:
                    self._errors['csvfile'] = self.error_class([
                        self.INVALID_FILE_FORMAT])
                    break
        except csv.Error:
            self._errors['csvfile'] = self.error_class([
                self.INVALID_FILE_FORMAT])

        return cleaned_data
