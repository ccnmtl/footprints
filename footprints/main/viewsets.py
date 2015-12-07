from django.contrib.auth.models import User
from rest_framework import viewsets

from footprints.main.models import (
    Footprint, Actor, Person, Role, WrittenWork, Language, ExtendedDate,
    Place, Imprint, BookCopy, StandardizedIdentification, DigitalFormat,
    DigitalObject, StandardizedIdentificationType)
from footprints.main.serializers import (
    FootprintSerializer, LanguageSerializer, RoleSerializer,
    ExtendedDateSerializer, ActorSerializer, PersonSerializer,
    PlaceSerializer, WrittenWorkSerializer, UserSerializer, ImprintSerializer,
    BookCopySerializer, StandardizedIdentificationSerializer,
    DigitalFormatSerializer, DigitalObjectSerializer,
    StandardizedIdentificationTypeSerializer)


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
    queryset = Place.objects.all()
    serializer_class = PlaceSerializer


class ActorViewSet(viewsets.ModelViewSet):
    queryset = Actor.objects.all()
    serializer_class = ActorSerializer


class WrittenWorkViewSet(viewsets.ModelViewSet):
    queryset = WrittenWork.objects.all()
    serializer_class = WrittenWorkSerializer

    def get_queryset(self):
        """
        Optionally restricts the works by title
        """
        qs = WrittenWork.objects.all()
        title = self.request.GET.get('q', None)
        if title is not None and len(title) > 0:
            qs = qs.filter(title__istartswith=title)
        return qs


class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer


class ImprintViewSet(viewsets.ModelViewSet):
    model = Imprint
    serializer_class = ImprintSerializer

    def get_queryset(self):
        qs = Imprint.objects.all()

        work_id = self.request.GET.get('work', None)
        if work_id:
            qs = qs.filter(work__id=work_id)

        title = self.request.GET.get('q', None)
        if title is not None and len(title) > 0:
            qs = qs.filter(title__istartswith=title)

        return qs


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
