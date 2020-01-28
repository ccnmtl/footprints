from rest_framework.serializers import HyperlinkedModelSerializer

from footprints.main.serializers import UserSerializer
from footprints.pathmapper.models import MapLayerCollection


class MapLayerCollectionSerializer(HyperlinkedModelSerializer):
    author = UserSerializer(read_only=True)

    class Meta:
        model = MapLayerCollection
        fields = ('id', 'author', 'uuid', 'layers')
