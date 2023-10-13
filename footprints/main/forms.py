from datetime import date, datetime
import re
import urllib

from django import forms
from django.db.models.query_utils import Q
from django.forms.fields import MultipleChoiceField
from django.forms.models import ModelForm
from django.utils.encoding import smart_str
from haystack.forms import ModelSearchForm
from registration.forms import RegistrationForm

from footprints.main.models import DigitalObject, ExtendedDate


class DigitalObjectForm(ModelForm):
    class Meta:
        model = DigitalObject
        fields = ['name', 'url', 'description']


DIRECTION_CHOICES = (
    ('asc', 'Ascending'),
    ('desc', 'Descending'),
)

PRECISION_CHOICES = (
    ('exact', 'Exact'),
    ('contains', 'Contains'),
    ('startswith', 'Starts with'),
    ('endswith', 'Ends with'),
)

SORT_CHOICES = (
    ('added', 'Added'),
    ('complete', 'Complete'),
    ('fdate', 'Footprint Date'),
    ('flocation', 'Footprint Location'),
    ('ftitle', 'Footprint Title'),
    ('owners', 'Owners'),
    ('wtitle', 'Literary Work')
)


class MultipleChoiceFieldNoValidation(MultipleChoiceField):
    def validate(self, value):
        pass


class FootprintSearchForm(ModelSearchForm):
    footprint_start_year = forms.IntegerField(required=False, min_value=1000)
    footprint_end_year = forms.IntegerField(required=False, min_value=1000)
    footprint_range = forms.BooleanField(
        required=False, widget=forms.HiddenInput())
    pub_start_year = forms.IntegerField(required=False, min_value=1000)
    pub_end_year = forms.IntegerField(required=False, min_value=1000)
    pub_range = forms.BooleanField(
        required=False, widget=forms.HiddenInput())
    gallery_view = forms.BooleanField(required=False, initial=False)

    precision = forms.ChoiceField(
        choices=PRECISION_CHOICES, initial='exact',
        required=True, widget=forms.HiddenInput())

    direction = forms.ChoiceField(
        choices=DIRECTION_CHOICES, initial='asc',
        required=True, widget=forms.HiddenInput())

    sort_by = forms.ChoiceField(
        choices=SORT_CHOICES, initial='ftitle',
        required=True, widget=forms.HiddenInput())

    page = forms.IntegerField(
        required=True, initial=1, widget=forms.HiddenInput())

    search_level = forms.BooleanField(required=False)

    actor = MultipleChoiceFieldNoValidation(
        choices=[], required=False)
    footprint_location = MultipleChoiceFieldNoValidation(
        choices=[], required=False)
    imprint_location = MultipleChoiceFieldNoValidation(
        choices=[], required=False)

    def clean_year(self, fieldname):
        year = self.cleaned_data.get(fieldname, '')

        if not isinstance(year, int):
            return

        now = datetime.now()
        if self.cleaned_data[fieldname] > now.year:
            self._errors[fieldname] = self.error_class([
                "No future year"])
        if self.cleaned_data[fieldname] < 1000:
            self._errors[fieldname] = self.error_class([
                "No past 1000 year"])

    def clean(self):
        cleaned_data = super(FootprintSearchForm, self).clean()

        self.clean_year('footprint_start_year')
        self.clean_year('footprint_end_year')

        if (cleaned_data.get('footprint_start_year', None) and
            cleaned_data.get('footprint_end_year', None) and
            cleaned_data['footprint_start_year'] >
                cleaned_data['footprint_end_year']):
            self._errors['footprint_start_year'] = self.error_class([
                "Start year must be less than end year"])

        self.clean_year('pub_start_year')
        self.clean_year('pub_end_year')

        if (cleaned_data.get('pub_start_year', None) and
            cleaned_data.get('pub_end_year', None) and
            cleaned_data['pub_start_year'] >
                cleaned_data['pub_end_year']):
            self._errors['pub_start_year'] = self.error_class([
                "Start year must be less than end year"])

        if (cleaned_data.get('search_level', False) and
            not cleaned_data.get('q', None) and
            not (cleaned_data.get('footprint_start_year', None) or
                 cleaned_data.get('footprint_end_year', None)) and
            not (cleaned_data.get('pub_start_year', None) or
                 cleaned_data.get('pub_end_year', None))):
            self._errors['q'] = self.error_class([
                "Either a search term or year required"])

        return cleaned_data

    def handle_image(self, args):
        if self.cleaned_data.get('gallery_view'):
            args.append(Q(has_image=True))
        return args

    def handle_creator(self, q, args):
        pattern = 'creator:(\w+)'
        m = re.search(pattern, q)
        if m:
            args.append(Q(creator__contains=m.group(1)))
            q = re.sub(pattern, '', q)
        return q

    def handle_content(self, q, args):
        if q:
            q = q.strip()
            precision = self.cleaned_data.get('precision', 'exact')
            if precision == 'exact':
                args.append(Q(content__content=q))
            elif precision == 'contains':
                args.append(Q(content__fuzzy=q))
            elif precision == 'startswith':
                args.append(Q(content__startswith=q))
            elif precision == 'endswith':
                args.append(Q(content__startswith=q))
        return q

    def handle_actor(self):
        a = []
        if self.cleaned_data['actor']:
            for actor in self.cleaned_data['actor']:
                a.append(Q(actor_title_exact__in=[actor]))
        return a

    def search(self):
        args = []
        kwargs = {
            'django_ct': 'main.footprint',
        }

        q = self.cleaned_data.get('q', '')

        self.handle_image(args)

        q = self.handle_creator(q, args)

        q = self.handle_content(q, args)

        args += self.handle_actor()

        kwargs.update(self.handle_footprint_year())
        kwargs.update(self.handle_pub_year())
        args += self.handle_footprint_location()
        args += self.handle_imprint_location()

        sqs = self.searchqueryset.filter(*args, **kwargs)

        if self.load_all:
            sqs = sqs.load_all()

        return sqs

    def handle_range(self, field_name1, field_name2, start_year, end_year):
        kwargs = {}
        if start_year:
            kwargs['{}__gte'.format(field_name1)] = date(
                start_year, 1, 1)
        if end_year:
            kwargs['{}__lte'.format(field_name2)] = date(
                end_year, 12, 31)
        return kwargs

    def handle_single_year(self, field_name, start_year):
        kwargs = {}
        kwargs['{}__gte'.format(field_name)] = date(
            start_year, 1, 1)
        kwargs['{}__lte'.format(field_name)] = date(
            start_year, 12, 31)
        return kwargs

    def handle_footprint_year(self):
        kwargs = {}
        footprint_start_year = self.cleaned_data.get(
            'footprint_start_year')
        footprint_end_year = self.cleaned_data.get(
            'footprint_end_year')

        if self.cleaned_data.get('footprint_range'):
            kwargs.update(self.handle_range(
                'footprint_start_date', 'footprint_end_date',
                footprint_start_year, footprint_end_year))
        elif footprint_start_year:
            kwargs.update(self.handle_single_year(
                'footprint_start_date', footprint_start_year))
        return kwargs

    def handle_pub_year(self):
        kwargs = {}
        pub_start_year = self.cleaned_data.get(
            'pub_start_year')
        pub_end_year = self.cleaned_data.get(
            'pub_end_year')

        if self.cleaned_data.get('pub_range'):
            kwargs.update(self.handle_range(
                'pub_start_date', 'pub_end_date',
                pub_start_year, pub_end_year))
        elif pub_start_year:
            kwargs.update(self.handle_single_year(
                'pub_start_date', pub_start_year))
        return kwargs

    def handle_footprint_location(self):
        args = []
        if self.cleaned_data['footprint_location']:
            lst = self.cleaned_data['footprint_location']
            args.append(Q(footprint_location_title_exact__in=lst))
        return args

    def handle_imprint_location(self):
        args = []
        if self.cleaned_data['imprint_location']:
            lst = self.cleaned_data['imprint_location']
            args.append(Q(imprint_location_title_exact__in=lst))
        return args

    def get_query_params(self):
        return urllib.urlencode(self.cleaned_data, doseq=True)


SUBJECT_CHOICES = (
    ('-----', '-----'),
    ('info', 'Request more information'),
    ('contribute', 'Learn more about how to contribute'),
    ('bug', 'Correction or bug report'),
    ('other', 'Other (please specify)')
)


class ContactUsForm(forms.Form):
    name = forms.CharField(required=True, max_length=512)
    email = forms.EmailField(required=True)

    subject = forms.ChoiceField(
        required=True, choices=SUBJECT_CHOICES,
        widget=forms.Select(attrs={'class': "form-control"}))

    description = forms.CharField(
        widget=forms.Textarea(attrs={'class': "form-control"}),
        required=True)

    decoy = forms.CharField(widget=forms.Textarea, required=False)

    def clean(self):
        cleaned_data = super(ContactUsForm, self).clean()

        if 'subject' not in cleaned_data or cleaned_data['subject'] == '-----':
            self._errors["subject"] = self.error_class([
                "Please specify a subject"])

        if ('decoy' not in cleaned_data or
                ('decoy' in cleaned_data and len(cleaned_data['decoy']) > 0)):
            self._errors["decoy"] = self.error_class([
                "Please leave this field blank"])

        return cleaned_data


class ExtendedDateForm(forms.Form):
    attr = forms.CharField(min_length=1, required=False)
    is_range = forms.BooleanField(initial=False, required=False)

    millenium1 = forms.IntegerField(min_value=1, max_value=2, required=False)
    century1 = forms.IntegerField(min_value=0, max_value=9, required=False)
    decade1 = forms.IntegerField(min_value=0, max_value=9, required=False)
    year1 = forms.IntegerField(min_value=0, max_value=9, required=False)
    month1 = forms.IntegerField(min_value=1, max_value=12, required=False)
    day1 = forms.IntegerField(min_value=1, max_value=31, required=False)
    approximate1 = forms.BooleanField(initial=False, required=False)
    uncertain1 = forms.BooleanField(initial=False, required=False)

    millenium2 = forms.IntegerField(min_value=1, max_value=2, required=False)
    century2 = forms.IntegerField(min_value=0, max_value=9, required=False)
    decade2 = forms.IntegerField(min_value=0, max_value=9, required=False)
    year2 = forms.IntegerField(min_value=0, max_value=9, required=False)
    month2 = forms.IntegerField(min_value=1, max_value=12, required=False)
    day2 = forms.IntegerField(min_value=1, max_value=31, required=False)
    approximate2 = forms.BooleanField(initial=False, required=False)
    uncertain2 = forms.BooleanField(initial=False, required=False)

    def clean(self):
        cleaned_data = super(ExtendedDateForm, self).clean()
        edt = self.get_extended_date()

        display_format = smart_str(edt)
        if 'invalid' in display_format or 'None' in display_format:
            self._errors['__all__'] = self.error_class([
                'Please fill out all required fields'])
            return

        self._set_errors(edt, cleaned_data)
        return cleaned_data

    def get_attr(self):
        return self.cleaned_data['attr']

    def get_extended_date(self):
        return ExtendedDate.objects.from_dict(self.cleaned_data)

    def get_error_messages(self):
        msg = ''
        for key, val in self.errors.items():
            if key != '__all__':
                msg += key + ': '
            msg += val[0]
            msg += '<br />'
        return msg

    def get_start_date(self, edt):
        try:
            return edt.start()
        except ValueError:
            return None

    def get_end_date(self, edt):
        try:
            return edt.end()
        except ValueError:
            return None

    def _set_errors(self, edt, cleaned_data):
        start = self.get_start_date(edt)

        if cleaned_data['is_range']:
            end = self.get_end_date(edt)
            self._set_errors_is_range(start, end)
        elif start is None:
            self._errors['__all__'] = self.error_class([
                'Please specify a valid date'])
        elif start > date.today():
            self._errors['__all__'] = self.error_class([
                'The date must be today or earlier'])

    def _set_errors_is_range(self, start, end):
        if start is None:
            self._errors['__all__'] = self.error_class([
                'Please specify a valid start date'])
        elif end is None:
            self._errors['__all__'] = self.error_class([
                'Please specify a valid end date'])
        elif start > date.today() or end > date.today():
            self._errors['__all__'] = self.error_class([
                'All dates must be today or earlier'])
        elif start > end:
            self._errors['__all__'] = self.error_class([
                'The start date must be earlier than the end date.'])

    def save(self):
        edtf = self.get_extended_date()
        edtf.save()
        return edtf


class CustomRegistrationForm(RegistrationForm):
    first_name = forms.CharField(required=True)
    last_name = forms.CharField(required=True)
    username = forms.CharField(required=True)
    email = forms.CharField(required=True)
    password1 = forms.CharField(required=True)
    password2 = forms.CharField(required=True)
    decoy = forms.CharField(required=False)

    def clean(self):
        cleaned_data = super(CustomRegistrationForm, self).clean()

        if 'decoy' in cleaned_data and len(cleaned_data['decoy']) > 0:
            self._errors["decoy"] = self.error_class([
                "Please leave this field blank"])

        return cleaned_data
