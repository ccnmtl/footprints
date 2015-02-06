from django.contrib.auth.models import User
from django.core.exceptions import ObjectDoesNotExist
from rest_framework.fields import CharField, ReadOnlyField, empty
from rest_framework.relations import (ManyRelatedField, MANY_RELATION_KWARGS)
from rest_framework.serializers import Serializer, HyperlinkedModelSerializer, \
    raise_errors_on_nested_writes
from rest_framework.utils import html
import six

from footprints.main.models import Footprint, Language, Role, Actor, \
    ExtendedDateFormat, Person, Place, WrittenWork


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

            return dictionary.getlist(self.field_name)

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

    def get_value(self, dictionary):
        # We override the default field access in order to support
        # nested HTML forms.
        if html.is_html_input(dictionary):
            return html.parse_html_dict(dictionary, prefix=self.field_name)
        return dictionary.get(self.field_name, empty)

    def run_validation(self, data=empty):
        """
        We override the default `run_validation`, because the validation
        performed by validators and the `.validate()` method should
        be coerced into an error dictionary with a 'non_fields_error' key.
        """
        (is_empty_value, data) = self.validate_empty_values(data)
        if is_empty_value:
            return data

        value = self.to_internal_value(data)
        try:
            self.run_validators(value)
            value = self.validate(value)
            assert value is not None, '.validate() should return the validated data'
        except (ValidationError, DjangoValidationError) as exc:
            raise ValidationError(detail=get_validation_error_detail(exc))

        return value
    @classmethod
    def many_init(cls, *args, **kwargs):
        list_kwargs = {'child_relation': cls(*args, **kwargs)}
        for key in kwargs.keys():
            if key in MANY_RELATION_KWARGS:
                list_kwargs[key] = kwargs[key]
        return ManyRelatedFieldEx(**list_kwargs)


class ExtendedDateFormatSerializer(HyperlinkedModelSerializer):
    class Meta:
        model = ExtendedDateFormat
        fields = ('id', 'edtf_format',)


class RoleSerializer(HyperlinkedModelSerializer):
    class Meta:
        model = Role
        fields = ('id', 'name',)


class PersonSerializer(HyperlinkedModelSerializer):
    class Meta:
        model = Person
        fields = ('id', 'name')


class PlaceSerializer(HyperlinkedModelSerializer):
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

    @classmethod
    def many_init(cls, *args, **kwargs):
        list_kwargs = {'child_relation': cls(*args, **kwargs)}
        for key in kwargs.keys():
            if key in MANY_RELATION_KWARGS:
                list_kwargs[key] = kwargs[key]
        return ManyRelatedFieldEx(**list_kwargs)


class WrittenWorkSerializer(HyperlinkedModelSerializer):
    actor = ActorSerializer(many=True)

    class Meta:
        model = WrittenWork
        fields = ('id', 'title', 'actor', 'notes')


class FootprintSerializer(HyperlinkedModelSerializer):
    associated_date = ExtendedDateFormatSerializer()
    language = LanguageSerializer(many=True)
    actor = ActorSerializer(many=True)
    place = PlaceSerializer()

    class Meta:
        model = Footprint
        fields = ('id', 'medium', 'medium_description',
                  'provenance', 'title', 'language', 'actor', 'call_number',
                  'notes', 'associated_date', 'place', 'narrative')

    def update(self, instance, validated_data):
        raise_errors_on_nested_writes('update', self, validated_data)

        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()

        return instance
