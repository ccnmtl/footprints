from rest_framework import serializers

from footprints.main.models import Actor


class TitleSerializer(serializers.Serializer):
    title = serializers.CharField(max_length=None, min_length=1)


class ActorSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Actor
