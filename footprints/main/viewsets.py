from django.db.models.query_utils import Q
from rest_framework import viewsets

from footprints.main.models import (
    Footprint, Actor, Person, Role, WrittenWork, Language, ExtendedDate,
    Place, Imprint, BookCopy, StandardizedIdentification, DigitalFormat,
    DigitalObject, StandardizedIdentificationType)
from footprints.main.serializers import (
    FootprintSerializer, LanguageSerializer, RoleSerializer,
    ExtendedDateSerializer, ActorSerializer, PersonSerializer,
    PlaceSerializer, WrittenWorkSerializer, ImprintSerializer,
    BookCopySerializer, StandardizedIdentificationSerializer,
    DigitalFormatSerializer, DigitalObjectSerializer,
    StandardizedIdentificationTypeSerializer)
from footprints.pathmapper.forms import (
    ActorSearchForm,
    ImprintSearchForm, WrittenWorkSearchForm, PlaceSearchForm)


class FootprintViewSet(viewsets.ModelViewSet):
    queryset = Footprint.objects.all()
    serializer_class = FootprintSerializer


class LanguageViewSet(viewsets.ModelViewSet):
    queryset = Language.objects.all()
    serializer_class = LanguageSerializer


class RoleViewSet(viewsets.ModelViewSet):
    queryset = Role.objects.all()
    serializer_class = RoleSerializer


class ExtendedDateViewSet(viewsets.ModelViewSet):
    queryset = ExtendedDate.objects.all()
    serializer_class = ExtendedDateSerializer


class PersonViewSet(viewsets.ModelViewSet):
    queryset = Person.objects.all()
    serializer_class = PersonSerializer


class PlaceViewSet(viewsets.ModelViewSet):
    model = Place
    serializer_class = PlaceSerializer

    def get_queryset(self):
        form = PlaceSearchForm(self.request.GET)
        if form.is_valid():
            loc_id = form.cleaned_data.get('selected', '')
            if loc_id:
                ids = [loc_id]
            else:
                ids = form.search()

            qs = Place.objects.filter(id__in=ids)

            q = form.cleaned_data.get('q', '')
            if q:
                qs = qs.filter(Q(city__contains=q) | Q(country__contains=q))

            return qs
        return Place.objects.none()


class ActorViewSet(viewsets.ModelViewSet):
    queryset = Actor.objects.all()
    serializer_class = ActorSerializer

    def get_queryset(self):
        form = ActorSearchForm(self.request.GET)
        if form.is_valid():
            actor_id = form.cleaned_data.get('selected', '')
            if actor_id:
                ids = [actor_id]
            else:
                ids = form.search()

            qs = Actor.objects.filter(id__in=ids).distinct()
            q = form.cleaned_data.get('q', '')
            if q:
                qs = qs.filter(person__name__contains=q)
            return qs.order_by('person__name')

        return Actor.objects.none()


class WrittenWorkViewSet(viewsets.ModelViewSet):
    model = WrittenWork
    serializer_class = WrittenWorkSerializer

    def get_queryset(self):
        form = WrittenWorkSearchForm(self.request.GET)
        if form.is_valid():
            sqs = form.search()

            # this translation from haystack search results
            # to serializable Django set is slow
            # @todo - consider making two views, one for search results
            # and one for full editing
            ids = sqs.values_list('object_id', flat=True)
            return WrittenWork.objects.filter(id__in=ids)
        return WrittenWork.objects.none()


class ImprintViewSet(viewsets.ModelViewSet):
    model = Imprint
    serializer_class = ImprintSerializer

    def get_queryset(self):
        form = ImprintSearchForm(self.request.GET)
        if form.is_valid():
            sqs = form.search()

            # this translation from haystack search results
            # to serializable Django set is slow
            # @todo - consider making two views, one for search results
            # and one for full editing
            ids = sqs.values_list('object_id', flat=True)
            return Imprint.objects.filter(id__in=ids)
        return Imprint.objects.none()


class BookCopyViewSet(viewsets.ModelViewSet):
    model = BookCopy
    serializer_class = BookCopySerializer

    def get_queryset(self):
        qs = BookCopy.objects.all()

        imprint_id = self.request.GET.get('imprint', None)
        if imprint_id:
            qs = qs.filter(imprint__id=imprint_id)

        return qs


class StandardizedIdentificationViewSet(viewsets.ModelViewSet):
    queryset = StandardizedIdentification.objects.all()
    serializer_class = StandardizedIdentificationSerializer


class StandardizedIdentificationTypeViewSet(viewsets.ModelViewSet):
    queryset = StandardizedIdentificationType.objects.all()
    serializer_class = StandardizedIdentificationTypeSerializer


class DigitalFormatViewSet(viewsets.ModelViewSet):
    queryset = DigitalFormat.objects.all()
    serializer_class = DigitalFormatSerializer


class DigitalObjectViewSet(viewsets.ModelViewSet):
    queryset = DigitalObject.objects.all()
    serializer_class = DigitalObjectSerializer
