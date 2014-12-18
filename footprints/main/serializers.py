from rest_framework import serializers


class TitleSerializer(serializers.Serializer):
    title = serializers.CharField(max_length=None, min_length=1)


class PersonSerializer(serializers.Serializer):
    object_id = serializers.CharField()
    name = serializers.CharField(max_length=None, min_length=1)
