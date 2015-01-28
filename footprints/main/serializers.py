from django.core.exceptions import ObjectDoesNotExist
from rest_framework.fields import CharField, empty
from rest_framework.relations import (StringRelatedField,
                                      PrimaryKeyRelatedField,
                                      ManyRelatedField, MANY_RELATION_KWARGS)
from rest_framework.serializers import Serializer, HyperlinkedModelSerializer
from rest_framework.utils import html
import six

from footprints.main.models import Footprint, Language, Role, Actor, \
    ExtendedDateFormat, Person


class TitleSerializer(Serializer):
    object_type = CharField()
    title = CharField(max_length=None, min_length=1)


class NameSerializer(Serializer):
    object_id = CharField()
    name = CharField(max_length=None, min_length=1)


class LanguageSerializer(HyperlinkedModelSerializer):
    class Meta:
        model = Language
        fields = ('name',)


class ExtendedDateFormatSerializer(HyperlinkedModelSerializer):
    class Meta:
        model = ExtendedDateFormat
        fields = ('pk', 'edtf_format',)


class RoleSerializer(HyperlinkedModelSerializer):
    class Meta:
        model = Role
        fields = ('id', 'name',)


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


class ActorRelatedField(PrimaryKeyRelatedField):

    @classmethod
    def many_init(cls, *args, **kwargs):
        list_kwargs = {'child_relation': cls(*args, **kwargs)}
        for key in kwargs.keys():
            if key in MANY_RELATION_KWARGS:
                list_kwargs[key] = kwargs[key]
        return ManyRelatedFieldEx(**list_kwargs)


class LanguageRelatedField(StringRelatedField):
    class Meta:
        model = Language
        fields = ('id', 'name',)

    def get_queryset(self):
        return Language.objects.all()

    def to_representation(self, value):
        return six.text_type(value)

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


class PersonSerializer(HyperlinkedModelSerializer):
    class Meta:
        model = Person
        fields = ('id', 'name')


class ActorSerializer(HyperlinkedModelSerializer):
    person = PersonSerializer()
    role = RoleSerializer()

    class Meta:
        model = Actor
        fields = ('id', 'alias', 'person', 'role')
        depth = 1


class FootprintSerializer(HyperlinkedModelSerializer):
    associated_date = StringRelatedField()
    language = LanguageRelatedField(many=True)
    actor = ActorRelatedField(many=True, queryset=Actor.objects.all())

    class Meta:
        model = Footprint
        fields = ('id', 'medium', 'medium_description',
                  'provenance', 'title', 'language',
                  'actor', 'call_number', 'notes', 'associated_date')
