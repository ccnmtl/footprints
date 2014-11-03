from django.forms.models import ModelForm

from footprints.main.models import Footprint, Role, DigitalObject, \
    ExtendedDateFormat, Name, Language, DigitalFormat, \
    StandardizedIdentification, Person, Contributor, Place, Collection, \
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
    class Meta:
        model = Person


class ContributorForm(ModelForm):
    class Meta:
        model = Contributor


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
    class Meta:
        model = Imprint


class BookCopyForm(ModelForm):
    class Meta:
        model = BookCopy


class FootprintForm(ModelForm):
    class Meta:
        model = Footprint
