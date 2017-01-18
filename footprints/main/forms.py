import urllib
from datetime import date
from django import forms
from django.forms.models import ModelForm
from django.utils.translation import ugettext_lazy as _
from haystack.forms import ModelSearchForm
from haystack.utils import get_model_ct

from footprints.main.models import Footprint, DigitalObject, WrittenWork, \
    ExtendedDate


class DigitalObjectForm(ModelForm):
    class Meta:
        model = DigitalObject
        fields = ['name', 'url', 'description']


class FootprintSearchForm(ModelSearchForm):
    def __init__(self, *args, **kwargs):
        super(FootprintSearchForm, self).__init__(*args, **kwargs)

        choices = [
            (get_model_ct(Footprint), 'Footprint'),
            (get_model_ct(WrittenWork), 'Literary Work'),
        ]
        self.fields['models'] = forms.MultipleChoiceField(
            choices=choices, required=False, label=_('Search By Record Type'),
            widget=forms.CheckboxSelectMultiple(
                attrs={'class': 'regDropDown'}))
        self.fields['q'].widget.attrs['class'] = 'form-control'
        self.fields['q'].widget.attrs['placeholder'] = 'Titles, People, Places'

    def search(self):
        if not self.is_valid():
            return self.no_query_found()

        if not self.cleaned_data.get('q'):
            sqs = self.searchqueryset.all()
        else:
            sqs = self.searchqueryset.auto_query(self.cleaned_data['q'])

        sqs = sqs.exclude(django_ct__in=["main.imprint",
                                         "main.place",
                                         "main.person"])

        if self.load_all:
            sqs = sqs.load_all()

        sqs = sqs.models(*self.get_models())
        sqs = sqs.order_by('sort_by')
        return sqs

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

        if cleaned_data['subject'] == '-----':
            self._errors["subject"] = self.error_class([
                "Please specify a subject"])

        if 'decoy' in cleaned_data and len(cleaned_data['decoy']) > 0:
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

        display_format = edt.__unicode__()
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
