from django.contrib.auth.models import User
from rest_framework import viewsets

from footprints.main.models import (
    Footprint, Actor, Person, Role, WrittenWork, Language, ExtendedDateFormat,
    Place, Imprint, BookCopy, StandardizedIdentification)
from footprints.main.permissions import IsStaffOrReadOnly
from footprints.main.serializers import (
    FootprintSerializer, LanguageSerializer, RoleSerializer,
    ExtendedDateFormatSerializer, ActorSerializer, PersonSerializer,
    PlaceSerializer, WrittenWorkSerializer, UserSerializer, ImprintSerializer,
    BookCopySerializer, StandardizedIdentificationSerializer)


class FootprintViewSet(viewsets.ModelViewSet):
    queryset = Footprint.objects.all()
    serializer_class = FootprintSerializer
    permission_classes = (IsStaffOrReadOnly,)


class LanguageViewSet(viewsets.ModelViewSet):
    queryset = Language.objects.all()
    serializer_class = LanguageSerializer
    permission_classes = (IsStaffOrReadOnly,)


class RoleViewSet(viewsets.ModelViewSet):
    queryset = Role.objects.all()
    serializer_class = RoleSerializer
    permission_classes = (IsStaffOrReadOnly,)


class ExtendedDateFormatViewSet(viewsets.ModelViewSet):
    queryset = ExtendedDateFormat.objects.all()
    serializer_class = ExtendedDateFormatSerializer
    permission_classes = (IsStaffOrReadOnly,)


class PersonViewSet(viewsets.ModelViewSet):
    queryset = Person.objects.all()
    serializer_class = PersonSerializer
    permission_classes = (IsStaffOrReadOnly,)


class PlaceViewSet(viewsets.ModelViewSet):
    queryset = Place.objects.all()
    serializer_class = PlaceSerializer
    permission_classes = (IsStaffOrReadOnly,)


class ActorViewSet(viewsets.ModelViewSet):
    queryset = Actor.objects.all()
    serializer_class = ActorSerializer
    permission_classes = (IsStaffOrReadOnly,)


class WrittenWorkViewSet(viewsets.ModelViewSet):
    queryset = WrittenWork.objects.all()
    serializer_class = WrittenWorkSerializer
    permission_classes = (IsStaffOrReadOnly,)


class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = (IsStaffOrReadOnly,)


class ImprintViewSet(viewsets.ModelViewSet):
    queryset = Imprint.objects.all()
    serializer_class = ImprintSerializer
    permission_classes = (IsStaffOrReadOnly,)


class BookCopyViewSet(viewsets.ModelViewSet):
    queryset = BookCopy.objects.all()
    serializer_class = BookCopySerializer
    permission_classes = (IsStaffOrReadOnly,)


class StandardizedIdentificationViewSet(viewsets.ModelViewSet):
    queryset = StandardizedIdentification.objects.all()
    serializer_class = StandardizedIdentificationSerializer
    permission_classes = (IsStaffOrReadOnly,)
