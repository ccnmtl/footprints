import urllib

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
        fields = ['name', 'file', 'description']


class FootprintSearchForm(ModelSearchForm):
    def __init__(self, *args, **kwargs):
        super(FootprintSearchForm, self).__init__(*args, **kwargs)

        choices = [
            (get_model_ct(Footprint), 'Footprint'),
            (get_model_ct(WrittenWork), 'Written Work'),
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

        if not cleaned_data['millenium1']:
            if not cleaned_data['millenium2']:
                # date1 can be unknown if a date2 is specified
                self._errors['__all__'] = self.error_class([
                    'Please specify a date or date range'])

        dt = self.get_edtf().__unicode__()
        if 'invalid' in dt or 'None' in dt:
            self._errors['__all__'] = self.error_class([
                    'Please fill out all required fields'])

        return cleaned_data

    def get_attr(self):
        return self.cleaned_data['attr']

    def get_edtf(self):
        return ExtendedDate.objects.from_dict(self.cleaned_data)

    def save(self):
        edtf = self.get_edtf()
        edtf.save()
        return edtf
