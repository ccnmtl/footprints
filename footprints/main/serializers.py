from rest_framework import serializers

from footprints.main.models import Footprint


class TitleSerializer(serializers.Serializer):
    object_type = serializers.CharField()
    title = serializers.CharField(max_length=None, min_length=1)


class NameSerializer(serializers.Serializer):
    object_id = serializers.CharField()
    object_type = serializers.CharField()
    name = serializers.CharField(max_length=None, min_length=1)


class FootprintSerializer(serializers.HyperlinkedModelSerializer):
    language = serializers.PrimaryKeyRelatedField()

    class Meta:
        model = Footprint
        fields = ('medium', 'provenance', 'title', 'language',
                  'document_type', 'call_number', 'notes')
