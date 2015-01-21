from django.core.exceptions import ObjectDoesNotExist
from footprints.main.models import Footprint, Language, Role, Actor
from rest_framework import serializers
from rest_framework.relations import StringRelatedField, PrimaryKeyRelatedField
import six


class TitleSerializer(serializers.Serializer):
    object_type = serializers.CharField()
    title = serializers.CharField(max_length=None, min_length=1)


class NameSerializer(serializers.Serializer):
    object_id = serializers.CharField()
    name = serializers.CharField(max_length=None, min_length=1)


class LanguageSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Language
        fields = ('name',)


class RoleSerializer(serializers.HyperlinkedModelSerializer):
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


class FootprintSerializer(serializers.HyperlinkedModelSerializer):
    language = LanguageRelatedField(many=True)
    actor = PrimaryKeyRelatedField(many=True, queryset=Actor.objects.all())

    class Meta:
        model = Footprint
        fields = ('id', 'medium', 'provenance', 'title', 'language',
                  'actor', 'call_number', 'notes')
