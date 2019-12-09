from django.contrib.auth.models import User
from django.core.exceptions import ObjectDoesNotExist
from django.utils import timezone
from rest_framework import serializers
from rest_framework.fields import CharField, ReadOnlyField
from rest_framework.serializers import Serializer, HyperlinkedModelSerializer

from footprints.main.models import Footprint, Language, Role, Actor, \
    ExtendedDate, Person, Place, WrittenWork, Imprint, BookCopy, \
    StandardizedIdentification, DigitalObject, DigitalFormat, \
    StandardizedIdentificationType


class NameSerializer(Serializer):
    object_id = CharField()
    name = CharField(max_length=None, min_length=1)


class UserSerializer(HyperlinkedModelSerializer):
    class Meta:
        model = User
        fields = ('first_name', 'last_name', 'username')


class StandardizedIdentificationTypeSerializer(HyperlinkedModelSerializer):
    class Meta:
        model = StandardizedIdentificationType
        fields = ('id', 'name', 'slug')

    def get_queryset(self):
        return StandardizedIdentificationType.objects.all()


class StandardizedIdentificationSerializer(HyperlinkedModelSerializer):
    identifier_type = StandardizedIdentificationTypeSerializer

    class Meta:
        model = StandardizedIdentification
        fields = ('id', 'identifier', 'identifier_type', 'authority')

    def get_queryset(self):
        return StandardizedIdentification.objects.all()


class LanguageSerializer(HyperlinkedModelSerializer):
    class Meta:
        model = Language
        fields = ('id', 'name')

    def get_queryset(self):
        return Language.objects.all()

    def to_internal_value(self, data):
        try:
            return self.get_queryset().get(pk=data)
        except ObjectDoesNotExist:
            self.fail('does_not_exist', pk_value=data)
        except (TypeError, ValueError):
            self.fail('incorrect_type', data_type=type(data).__name__)


class ExtendedDateSerializer(HyperlinkedModelSerializer):
    display = CharField(source='__str__')

    class Meta:
        model = ExtendedDate
        fields = ('id', 'edtf_format', 'display')
        read_only_fields = ('display',)

    def get_queryset(self):
        return ExtendedDate.objects.all()


class RoleSerializer(HyperlinkedModelSerializer):
    class Meta:
        model = Role
        fields = ('id', 'name',)


class DigitalFormatSerializer(HyperlinkedModelSerializer):
    class Meta:
        model = DigitalFormat
        fields = ('id', 'name',)


class PersonSerializer(HyperlinkedModelSerializer):
    birth_date = ExtendedDateSerializer()
    death_date = ExtendedDateSerializer()
    standardized_identifier = StandardizedIdentificationSerializer()

    class Meta:
        model = Person
        fields = ('id', 'name', 'birth_date', 'death_date',
                  'standardized_identifier')


class PlaceSerializer(HyperlinkedModelSerializer):
    display_title = ReadOnlyField()
    search_title = ReadOnlyField()
    latitude = ReadOnlyField()
    longitude = ReadOnlyField()

    class Meta:
        model = Place
        fields = ('id', 'display_title', 'search_title', 'country', 'city',
                  'latitude', 'longitude')


class DigitalObjectSerializer(HyperlinkedModelSerializer):
    class Meta:
        model = DigitalObject
        fields = ('id', 'name', 'description', 'url')


class ActorSerializer(HyperlinkedModelSerializer):
    person = PersonSerializer()
    role = RoleSerializer()

    class Meta:
        model = Actor
        fields = ('id', 'alias', 'person', 'role')

    def get_queryset(self):
        return Actor.objects.all()

    def to_internal_value(self, data):
        try:
            return self.get_queryset().get(pk=data)
        except ObjectDoesNotExist:
            self.fail('does_not_exist', pk_value=data)
        except (TypeError, ValueError):
            self.fail('incorrect_type', data_type=type(data).__name__)


class WrittenWorkSerializer(HyperlinkedModelSerializer):
    actor = ActorSerializer(many=True, read_only=True)
    standardized_identifier = StandardizedIdentificationSerializer(
        many=True, read_only=True)

    class Meta:
        model = WrittenWork
        fields = ('id', 'title', 'actor', 'notes', 'description',
                  'standardized_identifier')


class ImprintSerializer(HyperlinkedModelSerializer):
    work = WrittenWorkSerializer()
    language = LanguageSerializer(many=True, read_only=True)
    actor = ActorSerializer(many=True, read_only=True)
    place = PlaceSerializer()
    publication_date = ExtendedDateSerializer()
    standardized_identifier = StandardizedIdentificationSerializer(
        many=True, read_only=True)

    class Meta:
        model = Imprint
        # @todo digital_object, standardized_identifier
        fields = ('id', 'work', 'title', 'language', 'place',
                  'publication_date', 'actor', 'notes',
                  'standardized_identifier', 'description')


class BookCopySerializer(HyperlinkedModelSerializer):
    imprint = ImprintSerializer()
    owners = ActorSerializer(many=True, read_only=True)
    current_owners = ActorSerializer(many=True, read_only=True)

    class Meta:
        model = BookCopy
        fields = ('id', 'call_number', 'imprint', 'identifier',
                  'notes', 'description', 'owners', 'current_owners')


class DateTimeZoneField(serializers.DateTimeField):

    def to_representation(self, value):
        value = timezone.localtime(value)
        return super(DateTimeZoneField, self).to_representation(value)


class FootprintSerializer(HyperlinkedModelSerializer):
    associated_date = ExtendedDateSerializer()
    language = LanguageSerializer(many=True, read_only=True)
    actor = ActorSerializer(many=True, read_only=True)
    place = PlaceSerializer()
    digital_object = DigitalObjectSerializer(many=True, read_only=True)
    created_by = UserSerializer(read_only=True)
    last_modified_by = UserSerializer(read_only=True)
    created_at = DateTimeZoneField(format='%m/%d/%y %I:%M %p')
    modified_at = DateTimeZoneField(format='%m/%d/%y %I:%M %p')
    verified_modified_at = DateTimeZoneField(format='%m/%d/%y %I:%M %p')

    class Meta:
        model = Footprint
        fields = ('id', 'medium', 'medium_description',
                  'provenance', 'title', 'language', 'actor', 'call_number',
                  'notes', 'associated_date', 'place', 'narrative',
                  'percent_complete', 'digital_object',
                  'flags', 'verified', 'verified_modified_at',
                  'created_at', 'modified_at',
                  'created_by', 'last_modified_by')


class WrittenWorkPathSerializer(HyperlinkedModelSerializer):
    class Meta:
        model = WrittenWork
        fields = ('id', 'title')


class ImprintPathSerializer(HyperlinkedModelSerializer):
    work = WrittenWorkPathSerializer()
    place = PlaceSerializer()
    publication_date = ExtendedDateSerializer()

    class Meta:
        model = Imprint
        fields = ('id', 'work', 'title', 'place', 'publication_date')


class FootprintPathSerializer(HyperlinkedModelSerializer):
    associated_date = ExtendedDateSerializer()
    place = PlaceSerializer()

    class Meta:
        model = Footprint
        fields = ('id', 'title', 'associated_date', 'place', 'sort_date')
