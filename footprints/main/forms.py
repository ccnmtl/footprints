import urllib

from django import forms
from django.forms.models import ModelForm
from django.utils.translation import ugettext_lazy as _
from haystack.forms import ModelSearchForm
from haystack.utils import get_model_ct

from footprints.main.models import Footprint, Role, DigitalObject, \
    ExtendedDateFormat, Language, DigitalFormat, \
    StandardizedIdentification, Person, Actor, Place, Collection, \
    WrittenWork, Imprint, BookCopy


class RoleForm(ModelForm):
    class Meta:
        model = Role


class ExtendedDateFormatForm(ModelForm):
    class Meta:
        model = ExtendedDateFormat


class LanguageForm(ModelForm):
    class Meta:
        model = Language


class DigitalFormatForm(ModelForm):
    class Meta:
        model = DigitalFormat


class DigitalObjectForm(ModelForm):
    class Meta:
        model = DigitalObject


class StandardizedIdentificationForm(ModelForm):
    class Meta:
        model = StandardizedIdentification


class PersonForm(ModelForm):

    last_name = forms.CharField(max_length=256)
    first_name = forms.CharField(max_length=256)
    middle_name = forms.CharField(max_length=256)
    suffix = forms.CharField(max_length=256)

    date_of_birth = forms.CharField(widget=forms.TextInput(),
                                    max_length=256)

    class Meta:
        model = Person
        fields = ['last_name', 'first_name', 'middle_name', 'suffix',
                  'date_of_birth', 'standardized_identifier',
                  'digital_object', 'notes']


class ActorForm(ModelForm):
    role = forms.ModelChoiceField(
        queryset=Role.objects.all(),
        widget=forms.Select(attrs={'class': 'add-another'}))

    person = forms.ModelChoiceField(
        queryset=Person.objects.all(),
        widget=forms.Select(attrs={'class': 'add-another'}))

    last_name = forms.CharField(max_length=256)
    first_name = forms.CharField(max_length=256)
    middle_name = forms.CharField(max_length=256)
    suffix = forms.CharField(max_length=256)

    class Meta:
        model = Actor
        fields = ['person', 'role', 'last_name', 'first_name',
                  'middle_name', 'suffix']


class PlaceForm(ModelForm):
    class Meta:
        model = Place
        fields = ['position']


class CollectionForm(ModelForm):
    class Meta:
        model = Collection


class WrittenWorkForm(ModelForm):
    class Meta:
        model = WrittenWork


class ImprintForm(ModelForm):
    publication_date = forms.CharField(widget=forms.TextInput(),
                                       max_length=256)

    class Meta:
        model = Imprint


class BookCopyForm(ModelForm):
    class Meta:
        model = BookCopy


class FootprintForm(ModelForm):
    recorded_date = forms.CharField(widget=forms.TextInput(),
                                    max_length=256)

    class Meta:
        model = Footprint


class FootprintSearchForm(ModelSearchForm):
    def __init__(self, *args, **kwargs):
        super(FootprintSearchForm, self).__init__(*args, **kwargs)

        choices = [
            (get_model_ct(Footprint), 'Footprint'),
            (get_model_ct(Place), 'Place'),
            (get_model_ct(Person), 'Person'),
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

        sqs = sqs.exclude(django_ct__in=["main.imprint"])

        if self.load_all:
            sqs = sqs.load_all()

        sqs = sqs.models(*self.get_models())
        sqs = sqs.order_by('sort_by')
        return sqs

    def get_query_params(self):
        return urllib.urlencode(self.cleaned_data, doseq=True)
