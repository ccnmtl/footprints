from django.contrib.auth.models import User
from rest_framework import viewsets

from footprints.main.models import (
    Footprint, Actor, Person, Role, WrittenWork, Language, ExtendedDateFormat,
    Place, Imprint, BookCopy, StandardizedIdentification, DigitalFormat,
    DigitalObject, StandardizedIdentificationType)
from footprints.main.permissions import IsLoggedInOrReadOnly
from footprints.main.serializers import (
    FootprintSerializer, LanguageSerializer, RoleSerializer,
    ExtendedDateFormatSerializer, ActorSerializer, PersonSerializer,
    PlaceSerializer, WrittenWorkSerializer, UserSerializer, ImprintSerializer,
    BookCopySerializer, StandardizedIdentificationSerializer,
    DigitalFormatSerializer, DigitalObjectSerializer,
    StandardizedIdentificationTypeSerializer)


class FootprintViewSet(viewsets.ModelViewSet):
    queryset = Footprint.objects.all()
    serializer_class = FootprintSerializer
    permission_classes = (IsLoggedInOrReadOnly,)


class LanguageViewSet(viewsets.ModelViewSet):
    queryset = Language.objects.all()
    serializer_class = LanguageSerializer
    permission_classes = (IsLoggedInOrReadOnly,)


class RoleViewSet(viewsets.ModelViewSet):
    queryset = Role.objects.all()
    serializer_class = RoleSerializer
    permission_classes = (IsLoggedInOrReadOnly,)


class ExtendedDateFormatViewSet(viewsets.ModelViewSet):
    queryset = ExtendedDateFormat.objects.all()
    serializer_class = ExtendedDateFormatSerializer
    permission_classes = (IsLoggedInOrReadOnly,)


class PersonViewSet(viewsets.ModelViewSet):
    queryset = Person.objects.all()
    serializer_class = PersonSerializer
    permission_classes = (IsLoggedInOrReadOnly,)


class PlaceViewSet(viewsets.ModelViewSet):
    queryset = Place.objects.all()
    serializer_class = PlaceSerializer
    permission_classes = (IsLoggedInOrReadOnly,)


class ActorViewSet(viewsets.ModelViewSet):
    queryset = Actor.objects.all()
    serializer_class = ActorSerializer
    permission_classes = (IsLoggedInOrReadOnly,)


class WrittenWorkViewSet(viewsets.ModelViewSet):
    queryset = WrittenWork.objects.all()
    serializer_class = WrittenWorkSerializer
    permission_classes = (IsLoggedInOrReadOnly,)


class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = (IsLoggedInOrReadOnly,)


class ImprintViewSet(viewsets.ModelViewSet):
    model = Imprint
    serializer_class = ImprintSerializer
    permission_classes = (IsLoggedInOrReadOnly,)

    def get_queryset(self):
        qs = Imprint.objects.all()

        work_id = self.request.GET.get('work', None)
        if work_id:
            qs = qs.filter(work__id=work_id)

        return qs


class BookCopyViewSet(viewsets.ModelViewSet):
    model = BookCopy
    serializer_class = BookCopySerializer
    permission_classes = (IsLoggedInOrReadOnly,)

    def get_queryset(self):
        qs = BookCopy.objects.all()

        imprint_id = self.request.GET.get('imprint', None)
        if imprint_id:
            qs = qs.filter(imprint__id=imprint_id)

        return qs


class StandardizedIdentificationViewSet(viewsets.ModelViewSet):
    queryset = StandardizedIdentification.objects.all()
    serializer_class = StandardizedIdentificationSerializer
    permission_classes = (IsLoggedInOrReadOnly,)


class StandardizedIdentificationTypeViewSet(viewsets.ModelViewSet):
    queryset = StandardizedIdentificationType.objects.all()
    serializer_class = StandardizedIdentificationTypeSerializer
    permission_classes = (IsLoggedInOrReadOnly,)


class DigitalFormatViewSet(viewsets.ModelViewSet):
    queryset = DigitalFormat.objects.all()
    serializer_class = DigitalFormatSerializer
    permission_classes = (IsLoggedInOrReadOnly,)


class DigitalObjectViewSet(viewsets.ModelViewSet):
    queryset = DigitalObject.objects.all()
    serializer_class = DigitalObjectSerializer
    permission_classes = (IsLoggedInOrReadOnly,)
