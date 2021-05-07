import random

from django.contrib.auth.models import User, Group, Permission
from django.contrib.gis.geos.point import Point
import factory
from factory.fuzzy import BaseFuzzyAttribute

from footprints.main.models import (
    Language, ExtendedDate, Role, DigitalFormat,
    StandardizedIdentification, Person, Actor, Place, Collection, WrittenWork,
    Imprint, BookCopy, Footprint, DigitalObject, IMPRINT_LEVEL,
    StandardizedIdentificationType, CanonicalPlace, ImprintAlternateTitle)
from footprints.main.utils import string_to_point


TEST_MEDIA_PATH = 'test.txt'


BATCH_PERMISSIONS = [
    'add_batchjob', 'change_batchjob', 'delete_batchjob',
    'add_batchrow', 'change_batchrow', 'delete_batchrow']


MODERATION_PERMISSIONS = ['can_moderate']

ADD_CHANGE_PERMISSIONS = [
    'add_role', 'change_role',
    'add_language', 'change_language',
    'add_digitalformat', 'change_digitalformat',
    'add_digitalobject', 'change_digitalobject',
    'add_standardizedidentification', 'change_standardizedidentification',
    'add_person', 'change_person',
    'add_place', 'change_place',
    'add_collection', 'change_collection',
    'add_writtenwork', 'change_writtenwork',
    'add_imprint', 'change_imprint',
    'add_bookcopy', 'change_bookcopy',
    'add_footprint', 'change_footprint',
    'add_actor', 'change_actor',
    'add_standardizedidentificationtype',
    'change_standardizedidentificationtype',
    'add_extendeddate', 'change_extendeddate'
]

DELETE_PERMISSIONS = [
    'delete_role', 'delete_language', 'delete_digitalobject',
    'delete_standardizedidentification', 'delete_person',
    'delete_place', 'delete_collection', 'delete_writtenwork',
    'delete_imprint', 'delete_bookcopy', 'delete_footprint',
    'delete_actor', 'delete_standardizedidentificationtype',
    'delete_extendeddate'
]


class FuzzyPoint(BaseFuzzyAttribute):
    def fuzz(self):
        return Point(random.uniform(-180.0, 180.0),  # nosec
                     random.uniform(-90.0, 90.0))  # nosec


class UserFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = User
    username = factory.Sequence(lambda n: "user%03d" % n)
    password = factory.PostGenerationMethodCall('set_password', 'test')

    @factory.post_generation
    def group(self, create, extracted, **kwargs):
        if not create:
            return

        if extracted:
            self.groups.add(extracted)


class GroupFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Group

    @factory.post_generation
    def permissions(self, create, extracted, **kwargs):
        if not create:
            return

        if extracted:
            lst = list(Permission.objects.filter(codename__in=extracted))
            self.permissions.add(*lst)


class ExtendedDateFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = ExtendedDate
    edtf_format = '1984~'


class RoleFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Role
    name = factory.Sequence(lambda n: "Author%03d" % n)
    level = 'footprint'


class LanguageFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Language
    name = factory.Sequence(lambda n: "Language%03d" % n)
    marc_code = factory.Sequence(lambda n: "%03d" % n)


class DigitalFormatFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = DigitalFormat
    name = factory.Sequence(lambda n: "format%03d" % n)


class DigitalObjectFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = DigitalObject
    name = factory.Sequence(lambda n: "image%03d" % n)
    digital_format = factory.SubFactory(DigitalFormatFactory)

    file = factory.django.FileField(data=b"uhuh",
                                    filename=TEST_MEDIA_PATH)


class StandardizedIdentificationTypeFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = StandardizedIdentificationType

    name = factory.Sequence(lambda n: "name%03d" % n)
    slug = factory.Sequence(lambda n: "%03d" % n)
    level = IMPRINT_LEVEL


class StandardizedIdentificationFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = StandardizedIdentification

    identifier = factory.Sequence(lambda n: "identifier%03d" % n)
    identifier_type = factory.SubFactory(StandardizedIdentificationTypeFactory)


class PersonFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Person

    name = factory.Sequence(lambda n: "Name%03d" % n)
    birth_date = factory.SubFactory(ExtendedDateFactory)
    death_date = factory.SubFactory(ExtendedDateFactory)
    standardized_identifier = factory.SubFactory(
        StandardizedIdentificationFactory)
    notes = "notes"


class ActorFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Actor

    person = factory.SubFactory(PersonFactory)
    role = factory.SubFactory(RoleFactory)
    alias = factory.Sequence(lambda n: "Name%03d" % n)


class CanonicalPlaceFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = CanonicalPlace

    canonical_name = 'Kraków, Poland'
    latlng = FuzzyPoint()
    geoname_id = factory.Sequence(lambda n: 'geo%03d' % n)

    @factory.post_generation
    def position(self, create, extracted, **kwargs):
        if create and extracted:
            self.latlng = string_to_point(extracted)
            self.save()


class PlaceFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Place

    alternate_name = 'Cracow, Poland'
    canonical_place = factory.SubFactory(CanonicalPlaceFactory)


class CollectionFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Collection

    name = factory.Sequence(lambda n: "Collection%03d" % n)

    @factory.post_generation
    def actors(self, create, extracted, **kwargs):
        if create:
            self.actor.add(ActorFactory())


class WrittenWorkFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = WrittenWork

    title = factory.Sequence(lambda n: "The Odyssey%03d" % n)
    notes = 'epic'

    @factory.post_generation
    def actors(self, create, extracted, **kwargs):
        if create:
            role = RoleFactory()
            self.actor.add(ActorFactory(role=role))


class ImprintFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Imprint

    work = factory.SubFactory(WrittenWorkFactory)
    title = 'The Odyssey, Edition 1'
    publication_date = factory.SubFactory(ExtendedDateFactory)
    place = factory.SubFactory(PlaceFactory)
    notes = "lorem ipsum"

    @factory.post_generation
    def actors(self, create, extracted, **kwargs):
        if create:
            role = RoleFactory()
            self.actor.add(ActorFactory.create(role=role))

    @factory.post_generation
    def standardized_identification(self, create, extracted, **kwargs):
        if create:
            identifier = StandardizedIdentificationFactory()
            self.standardized_identifier.add(identifier)

    @factory.post_generation
    def language(self, create, extracted, **kwargs):
        if create:
            self.language.add(LanguageFactory())


class ImprintAlternateTitleFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = ImprintAlternateTitle

    alternate_title = factory.Sequence(lambda n: "Alternate %03d" % n)
    standardized_identifier = factory.SubFactory(
        StandardizedIdentificationFactory)
    language = factory.SubFactory(LanguageFactory)

    @factory.post_generation
    def bhb_number(self, create, extracted, **kwargs):
        if not create:
            return

        if extracted:
            bhb_type = StandardizedIdentificationType.objects.bhb()
            identifier = StandardizedIdentificationFactory(
                identifier_type=bhb_type,
                identifier=extracted)
            self.standardized_identifier = identifier
            self.save()


class BookCopyFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = BookCopy

    imprint = factory.SubFactory(ImprintFactory)
    notes = "lorem ipsum"
    call_number = 'B893.1BC'


class EmptyFootprintFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Footprint

    book_copy = factory.SubFactory(BookCopyFactory)
    medium = 'Bookseller/auction catalog (1850-present)'
    provenance = 'Provenance'
    title = 'The Iliad'
    created_by = factory.SubFactory(UserFactory)


class FootprintFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Footprint

    book_copy = factory.SubFactory(BookCopyFactory)
    medium = 'Medium'
    provenance = 'Provenance'

    title = 'Odyssey'
    place = factory.SubFactory(PlaceFactory)

    associated_date = factory.SubFactory(ExtendedDateFactory)

    call_number = 'call number'
    collection = factory.SubFactory(CollectionFactory)

    notes = 'lorem ipsum'

    narrative = 'Odysseus struggles to return home after the Trojan War.'

    created_by = factory.SubFactory(UserFactory)

    @factory.post_generation
    def actors(self, create, extracted, **kwargs):
        if create:
            role = RoleFactory()
            self.actor.add(ActorFactory.create(role=role))

    @factory.post_generation
    def language(self, create, extracted, **kwargs):
        if create:
            self.language.add(LanguageFactory())
