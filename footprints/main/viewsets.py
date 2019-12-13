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
    ImprintSearchForm, WrittenWorkSearchForm)


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

    def filter_imprint_location(self, qs, work_id, imprint_id):
        if imprint_id:
            qs = qs.filter(imprint__id=imprint_id)
        elif work_id:
            qs = qs.filter(imprint__work__id=work_id)
        else:
            qs = qs.exclude(imprint=None)

        return qs

    def filter_footprint_location(self, qs, work_id, imprint_id):
        if imprint_id:
            qs = qs.filter(footprint__book_copy__imprint__id=imprint_id)
        elif work_id:
            qs = qs.filter(footprint__book_copy__imprint__work__id=work_id)
        else:
            qs = qs.exclude(footprint=None)

        return qs

    def get_queryset(self):
        qs = Place.objects.all()

        imprint_id = self.request.GET.get('imprint', None)
        work_id = self.request.GET.get('work', None)
        search_by = self.request.GET.get('name', None)
        if search_by == 'imprint-location':
            qs = self.filter_imprint_location(qs, work_id, imprint_id)
        elif search_by == 'footprint-location':
            qs = self.filter_footprint_location(qs, work_id, imprint_id)

        term = self.request.GET.get('q', None)
        if term is not None and len(term) > 0:
            qs = qs.filter(
                Q(city__istartswith=term) | Q(country__istartswith=term))

        return qs


class ActorViewSet(viewsets.ModelViewSet):
    queryset = Actor.objects.all()
    serializer_class = ActorSerializer


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
