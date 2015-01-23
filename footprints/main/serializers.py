from django.core.exceptions import ObjectDoesNotExist
from rest_framework.fields import CharField
from rest_framework.relations import StringRelatedField, PrimaryKeyRelatedField
from rest_framework.serializers import Serializer, HyperlinkedModelSerializer
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
        fields = ('id', 'edtf_format',)


class RoleSerializer(HyperlinkedModelSerializer):
    class Meta:
        model = Role
        fields = ('id', 'name',)


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
    actor = PrimaryKeyRelatedField(many=True, queryset=Actor.objects.all())

    class Meta:
        model = Footprint
        fields = ('id', 'medium', 'provenance', 'title', 'language',
                  'actor', 'call_number', 'notes', 'associated_date')
