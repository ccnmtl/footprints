from rest_framework import viewsets

from footprints.pathmapper.models import MapLayerCollection
from footprints.pathmapper.serializers import MapLayerCollectionSerializer


class MapLayerCollectionViewSet(viewsets.ModelViewSet):
    queryset = MapLayerCollection.objects.all()
    serializer_class = MapLayerCollectionSerializer
