from django.contrib.auth.models import User
from django.core.exceptions import ObjectDoesNotExist
from django.utils import timezone
from django.utils.encoding import smart_text
from rest_framework import serializers
from rest_framework.fields import CharField, ReadOnlyField
from rest_framework.serializers import Serializer, HyperlinkedModelSerializer

from footprints.main.models import Footprint, Language, Role, Actor, \
    ExtendedDate, Person, Place, WrittenWork, Imprint, BookCopy, \
    StandardizedIdentification, DigitalObject, DigitalFormat, \
    StandardizedIdentificationType, CanonicalPlace


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
        fields = ('id', 'name', 'birth_date', 'death_date', 'gender',
                  'standardized_identifier')


class CanonicalPlaceSerializer(HyperlinkedModelSerializer):
    latitude = ReadOnlyField()
    longitude = ReadOnlyField()

    class Meta:
        model = CanonicalPlace
        fields = ('id', 'canonical_name', 'latitude', 'longitude')


class PlaceSerializer(HyperlinkedModelSerializer):
    latitude = ReadOnlyField()
    longitude = ReadOnlyField()
    canonical_place = CanonicalPlaceSerializer()

    class Meta:
        model = Place
        fields = ('id', 'display_title', 'canonical_place',
                  'latitude', 'longitude')


class DigitalObjectSerializer(HyperlinkedModelSerializer):
    class Meta:
        model = DigitalObject
        fields = ('id', 'name', 'description', 'url')


class ActorSerializer(HyperlinkedModelSerializer):
    person = PersonSerializer()
    role = RoleSerializer()
    display_title = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = Actor
        fields = ('id', 'alias', 'person', 'role', 'display_title')

    def get_queryset(self):
        return Actor.objects.all()

    def get_display_title(self, obj):
        return smart_text(obj)

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

    work_title = serializers.SerializerMethodField(read_only=True)
    imprint_title = serializers.SerializerMethodField(read_only=True)
    book_copy_identifier = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = Footprint
        fields = ('id', 'medium', 'medium_description',
                  'provenance', 'title', 'language', 'actor', 'call_number',
                  'notes', 'associated_date', 'place', 'narrative',
                  'percent_complete', 'digital_object',
                  'work_title', 'imprint_title', 'book_copy_identifier',
                  'flags', 'verified', 'verified_modified_at',
                  'created_at', 'modified_at',
                  'created_by', 'last_modified_by')

    def get_work_title(self, obj):
        return smart_text(obj.book_copy.imprint.work.title)

    def get_imprint_title(self, obj):
        return smart_text(obj.book_copy.imprint.title)

    def get_book_copy_identifier(self, obj):
        return smart_text(obj.book_copy.identifier())


class PathmapperImprintSerializer(HyperlinkedModelSerializer):
    work_id = serializers.CharField(source='work.id', read_only=True)
    work_title = serializers.CharField(source='work.title', read_only=True)
    place = PlaceSerializer()
    display_date = serializers.CharField(source='publication_date')
    sort_date = serializers.DateField()

    class Meta:
        model = Imprint
        fields = ('id', 'title', 'place', 'display_date', 'sort_date',
                  'work_id', 'work_title')


class PathmapperFootprintSerializer(HyperlinkedModelSerializer):
    place = PlaceSerializer()
    display_date = serializers.CharField(source='associated_date')
    narrative = serializers.CharField()
    sort_date = serializers.DateField()
    owners = serializers.CharField(source='owner_description')
    is_terminal = serializers.BooleanField()

    class Meta:
        model = Footprint
        fields = ('id', 'title', 'place', 'display_date', 'sort_date',
                  'narrative', 'owners', 'call_number', 'identifier',
                  'is_terminal')


class PathmapperRouteSerializer(HyperlinkedModelSerializer):
    imprint = PathmapperImprintSerializer(read_only=True)
    footprints = PathmapperFootprintSerializer(many=True, read_only=True)

    class Meta:
        model = BookCopy
        fields = ('id', 'identifier', 'imprint', 'footprints')


class PathmapperEventSerializer(Serializer):
    year = serializers.CharField(read_only=True)
    count = serializers.IntegerField(read_only=True)

    class Meta:
        fields = ('year', 'count')


class PathmapperTableRowSerializer(Serializer):
    work_id = serializers.CharField(read_only=True)
    work_title = serializers.CharField(
        source='object.book_copy.imprint.work.title', read_only=True)
    imprint_id = serializers.CharField(read_only=True)
    imprint_title = serializers.CharField(
        source='object.book_copy.imprint.display_title', read_only=True)
    pub_date = serializers.CharField(
        source='object.book_copy.imprint.publication_date')
    pub_location = serializers.CharField(
        source='imprint_location_title')
    book_copy_identifier = serializers.CharField(read_only=True)
    footprint_id = serializers.CharField(source='object_id', read_only=True)
    footprint_title = serializers.CharField(source='title', read_only=True)
    footprint_date = serializers.CharField(
        source='object.associated_date', read_only=True)
    footprint_location = serializers.CharField(
        source='footprint_location_title')
    censored = serializers.CharField(
        source='object.book_copy.imprint.has_censor')
    expurgated = serializers.CharField(
        source='object.has_expurgator')

    class Meta:
        fields = (
            'work_id', 'work_title',
            'imprint_id', 'imprint_title', 'pub_date', 'pub_location',
            'book_copy_identifier',
            'footprint_id', 'footprint_title', 'footprint_date',
            'footprint_location', 'expurgated', 'censored')


class DigitalObjectExtendedSerializer(HyperlinkedModelSerializer):
    footprints = PathmapperFootprintSerializer(
        many=True, read_only=True, source='footprint_set')

    class Meta:
        model = DigitalObject
        fields = ('id', 'name', 'description', 'url', 'footprints')
