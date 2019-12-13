from datetime import date, datetime

from django import forms
from haystack.forms import ModelSearchForm

from footprints.main.models import BookCopy, Imprint, WrittenWork
from footprints.main.utils import camel_to_snake, snake_to_camel


class ModelSearchFormEx(ModelSearchForm):

    def transform_data(self):
        for key, value in self.data.items():
            snake_key = camel_to_snake(key)
            self.cleaned_data[snake_key] = value

    def transform_errors(self):
        errors = {}
        for key, value in self.errors.items():
            snake_key = snake_to_camel(key)
            errors[snake_key] = value
        self.errors.update(errors)

    def clean_year(self, fieldname):
        year = self.cleaned_data.get(fieldname, '')

        if not isinstance(year, int):
            return

        now = datetime.now()
        if self.cleaned_data[fieldname] > now.year:
            self._errors[fieldname] = self.error_class([
                'No future year'])
        if self.cleaned_data[fieldname] < 1000:
            self._errors[fieldname] = self.error_class([
                'Year must be greater than 1000'])

    def handle_single_year(self, field_name, start_year):
        kwargs = {}
        start_year = int(start_year)
        kwargs['{}__gte'.format(field_name)] = date(
            start_year, 1, 1)
        kwargs['{}__lte'.format(field_name)] = date(
            start_year, 12, 31)
        return kwargs

    def handle_range(self, field_name1, field_name2, start_year, end_year):
        kwargs = {}
        if start_year:
            start_year = int(start_year)
            kwargs['{}__gte'.format(field_name1)] = date(
                start_year, 1, 1)
        if end_year:
            end_year = int(end_year)
            kwargs['{}__lte'.format(field_name2)] = date(
                end_year, 12, 31)
        return kwargs

    def handle_footprint_year(self):
        kwargs = {}
        start_year = self.cleaned_data.get('footprint_start')
        end_year = self.cleaned_data.get('footprint_end')
        ranged = self.cleaned_data.get('footprint_range') == 'true'

        if ranged:
            kwargs.update(self.handle_range(
                'footprint_start_date', 'footprint_end_date',
                start_year, end_year))
        elif start_year:
            kwargs.update(self.handle_single_year(
                'footprint_start_date', start_year))
        return kwargs

    def handle_pub_year(self):
        kwargs = {}
        start_year = self.cleaned_data.get('pub_start')
        end_year = self.cleaned_data.get('pub_end')
        ranged = self.cleaned_data.get('pub_range') == 'true'

        if ranged:
            kwargs.update(self.handle_range(
                'pub_start_date', 'pub_end_date',
                start_year, end_year))
        elif start_year:
            kwargs.update(self.handle_single_year(
                'pub_start_date', start_year))
        return kwargs

    def clean(self):
        self.transform_data()
        cleaned_data = super().clean()

        self.clean_year('footprint_start')
        self.clean_year('footprint_end')

        if (cleaned_data.get('footprint_start', None) and
            cleaned_data.get('footprint_end', None) and
            cleaned_data['footprint_start'] >
                cleaned_data['footprint_end']):
            self._errors['footprint_start'] = self.error_class([
                'Start year must be less than end year'])

        self.clean_year('pub_start')
        self.clean_year('pub_end')

        if (cleaned_data.get('pub_start', None) and
            cleaned_data.get('pub_end', None) and
            cleaned_data['pub_start'] >
                cleaned_data['pub_end']):
            self._errors['pub_start'] = self.error_class([
                'Start year must be less than end year'])

        self.transform_errors()


class BookCopySearchForm(ModelSearchFormEx):

    work = forms.IntegerField(required=False)
    imprint = forms.IntegerField(required=False)
    imprint_location = forms.IntegerField(required=False)
    footprint_location = forms.IntegerField(required=False)

    footprint_start = forms.IntegerField(required=False, min_value=1000)
    footprint_end = forms.IntegerField(required=False, min_value=1000)
    footprint_range = forms.BooleanField(
        required=False, widget=forms.HiddenInput())

    pub_start = forms.IntegerField(required=False, min_value=1000)
    pub_end = forms.IntegerField(required=False, min_value=1000)
    pub_range = forms.BooleanField(
        required=False, widget=forms.HiddenInput())

    class Meta:
        model = BookCopy

    def search(self):
        args = []
        kwargs = {
            'django_ct': 'main.bookcopy',
        }

        work_id = self.cleaned_data.get('work')
        if work_id:
            kwargs['work_id'] = work_id

        imprint_id = self.cleaned_data.get('imprint')
        if imprint_id:
            kwargs['imprint_id'] = imprint_id

        imprint_loc = self.cleaned_data.get('imprint_location')
        if imprint_loc:
            kwargs['imprint_location'] = imprint_loc

        footprint_loc = self.cleaned_data.get('footprint_location')
        if footprint_loc:
            kwargs['footprint_locations'] = footprint_loc

        kwargs.update(self.handle_pub_year())
        kwargs.update(self.handle_footprint_year())

        return self.searchqueryset.filter(*args, **kwargs)


class ImprintSearchForm(ModelSearchFormEx):

    q = forms.CharField(required=False)
    work = forms.IntegerField(required=False)
    imprint_location = forms.IntegerField(required=False)
    footprint_location = forms.IntegerField(required=False)

    footprint_start = forms.IntegerField(required=False, min_value=1000)
    footprint_end = forms.IntegerField(required=False, min_value=1000)
    footprint_range = forms.BooleanField(
        required=False, widget=forms.HiddenInput())

    pub_start = forms.IntegerField(required=False, min_value=1000)
    pub_end = forms.IntegerField(required=False, min_value=1000)
    pub_range = forms.BooleanField(
        required=False, widget=forms.HiddenInput())

    class Meta:
        model = Imprint

    def search(self):
        args = []
        kwargs = {
            'django_ct': 'main.imprint',
        }

        q = self.cleaned_data.get('q', '')
        if q:
            kwargs['content'] = q

        work_id = self.cleaned_data.get('work')
        if work_id:
            kwargs['work_id'] = work_id

        imprint_loc = self.cleaned_data.get('imprint_location')
        if imprint_loc:
            kwargs['imprint_location'] = imprint_loc

        footprint_loc = self.cleaned_data.get('footprint_location')
        if footprint_loc:
            kwargs['footprint_locations'] = footprint_loc

        kwargs.update(self.handle_pub_year())
        kwargs.update(self.handle_footprint_year())

        return self.searchqueryset.filter(*args, **kwargs)


class WrittenWorkSearchForm(ModelSearchFormEx):

    q = forms.CharField(required=False)
    imprint_location = forms.IntegerField(required=False)
    footprint_location = forms.IntegerField(required=False)

    footprint_start = forms.IntegerField(required=False, min_value=1000)
    footprint_end = forms.IntegerField(required=False, min_value=1000)
    footprint_range = forms.BooleanField(
        required=False, widget=forms.HiddenInput())

    pub_start = forms.IntegerField(required=False, min_value=1000)
    pub_end = forms.IntegerField(required=False, min_value=1000)
    pub_range = forms.BooleanField(
        required=False, widget=forms.HiddenInput())

    class Meta:
        model = WrittenWork

    def search(self):
        args = []
        kwargs = {
            'django_ct': 'main.writtenwork',
        }

        q = self.cleaned_data.get('q', '')
        if q:
            kwargs['content'] = q

        imprint_loc = self.cleaned_data.get('imprint_location')
        if imprint_loc:
            kwargs['imprint_locations'] = imprint_loc

        footprint_loc = self.cleaned_data.get('footprint_location')
        if footprint_loc:
            kwargs['footprint_locations'] = footprint_loc

        kwargs.update(self.handle_pub_year())
        kwargs.update(self.handle_footprint_year())

        return self.searchqueryset.filter(*args, **kwargs)
