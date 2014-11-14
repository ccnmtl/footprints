from django import forms
from django.forms.models import ModelForm

from footprints.main.models import Footprint, Role, DigitalObject, \
    ExtendedDateFormat, Name, Language, DigitalFormat, \
    StandardizedIdentification, Person, Actor, Place, Collection, \
    WrittenWork, Imprint, BookCopy


class RoleForm(ModelForm):
    class Meta:
        model = Role


class ExtendedDateFormatForm(ModelForm):
    class Meta:
        model = ExtendedDateFormat


class NameForm(ModelForm):
    class Meta:
        model = Name


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
