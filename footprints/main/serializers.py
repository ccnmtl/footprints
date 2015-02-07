from django.contrib.auth.models import User
from django.core.exceptions import ObjectDoesNotExist
from rest_framework.fields import CharField, ReadOnlyField, empty
from rest_framework.relations import (ManyRelatedField, MANY_RELATION_KWARGS)
from rest_framework.serializers import Serializer, HyperlinkedModelSerializer
from rest_framework.utils import html

from footprints.main.models import Footprint, Language, Role, Actor, \
    ExtendedDateFormat, Person, Place, WrittenWork, Imprint, BookCopy


# Fixes a django-restframework bug, patch submitted & will be available 3.0.5
class ManyRelatedFieldEx(ManyRelatedField):
    def get_value(self, dictionary):
        # We override the default field access in order to support
        # lists in HTML forms.
        if html.is_html_input(dictionary):
            # Don't return [] if the update is partial
            if self.field_name not in dictionary:
                if getattr(self.root, 'partial', False):
                    return empty
            elif len(dictionary[self.field_name]) < 1:
                return []
            else:
                return dictionary.getlist(self.field_name)

        return dictionary.get(self.field_name, empty)


class HyperlinkedModelSerializerEx(HyperlinkedModelSerializer):
    def get_value(self, dictionary):
        # We override the default field access in order to support
        # lists in HTML forms.
        if html.is_html_input(dictionary):
            # Don't return [] if the update is partial
            if self.field_name not in dictionary:
                if getattr(self.root, 'partial', False):
                    return empty
            elif len(dictionary[self.field_name]) < 1:
                return {}

        return dictionary.get(self.field_name, empty)


class TitleSerializer(Serializer):
    object_type = CharField()
    title = CharField(max_length=None, min_length=1)


class NameSerializer(Serializer):
    object_id = CharField()
    name = CharField(max_length=None, min_length=1)


class UserSerializer(Serializer):
    class Meta:
        model = User
        fields = ('username',)


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

    @classmethod
    def many_init(cls, *args, **kwargs):
        list_kwargs = {'child_relation': cls(*args, **kwargs)}
        for key in kwargs.keys():
            if key in MANY_RELATION_KWARGS:
                list_kwargs[key] = kwargs[key]
        return ManyRelatedFieldEx(**list_kwargs)


class ExtendedDateFormatSerializer(HyperlinkedModelSerializerEx):
    class Meta:
        model = ExtendedDateFormat
        fields = ('id', 'edtf_format',)

    def get_queryset(self):
        return ExtendedDateFormat.objects.all()


class RoleSerializer(HyperlinkedModelSerializer):
    class Meta:
        model = Role
        fields = ('id', 'name',)


class PersonSerializer(HyperlinkedModelSerializer):
    birth_date = ExtendedDateFormatSerializer()
    death_date = ExtendedDateFormatSerializer()

    class Meta:
        model = Person
        fields = ('id', 'name', 'birth_date', 'death_date')


class PlaceSerializer(HyperlinkedModelSerializerEx):
    display_title = ReadOnlyField(source='__unicode__')
    latitude = ReadOnlyField()
    longitude = ReadOnlyField()

    class Meta:
        model = Place
        fields = ('id', 'display_title', 'country', 'city',
                  'position', 'latitude', 'longitude')


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

    @classmethod
    def many_init(cls, *args, **kwargs):
        list_kwargs = {'child_relation': cls(*args, **kwargs)}
        for key in kwargs.keys():
            if key in MANY_RELATION_KWARGS:
                list_kwargs[key] = kwargs[key]
        return ManyRelatedFieldEx(**list_kwargs)


class WrittenWorkSerializer(HyperlinkedModelSerializerEx):
    actor = ActorSerializer(many=True)

    class Meta:
        model = WrittenWork
        fields = ('id', 'title', 'actor', 'notes')


class ImprintSerializer(HyperlinkedModelSerializerEx):
    work = WrittenWorkSerializer()
    language = LanguageSerializer(many=True)
    actor = ActorSerializer(many=True)
    place = PlaceSerializer()
    date_of_publication = ExtendedDateFormatSerializer()

    class Meta:
        model = Imprint
        # @todo digital_object, standardized_identifier
        fields = ('id', 'work', 'title', 'language', 'place',
                  'date_of_publication', 'actor', 'notes')

    def update(self, instance, validated_data):
        if 'language' in validated_data:
            instance.language = validated_data['language']
            instance.save()
        else:
            instance = super(ImprintSerializer, self).update(
                instance, validated_data)

        return instance


class BookCopySerializer(HyperlinkedModelSerializer):
    imprint = ImprintSerializer()

    class Meta:
        model = BookCopy
        fields = ('id', 'imprint', 'notes')


class FootprintSerializer(HyperlinkedModelSerializer):
    associated_date = ExtendedDateFormatSerializer()
    language = LanguageSerializer(many=True)
    actor = ActorSerializer(many=True)
    place = PlaceSerializer()

    class Meta:
        model = Footprint
        fields = ('id', 'medium', 'medium_description',
                  'provenance', 'title', 'language', 'actor', 'call_number',
                  'notes', 'associated_date', 'place', 'narrative',
                  'percent_complete')

    def update(self, instance, validated_data):
        if 'language' in validated_data:
            # all related languages are posted
            instance.language = validated_data['language']
            instance.save()
        else:
            instance = super(FootprintSerializer, self).update(
                instance, validated_data)

        return instance
