import os

from django.contrib.auth.models import User
import factory

from footprints.main.models import (
    Language, ExtendedDateFormat, Role, DigitalFormat,
    StandardizedIdentification, Person, Actor, Place, Collection, WrittenWork,
    Imprint, BookCopy, Footprint, DigitalObject, IMPRINT_LEVEL,
    StandardizedIdentificationType)


TEST_MEDIA_PATH = os.path.join(os.path.dirname(__file__), 'test.txt')


class UserFactory(factory.DjangoModelFactory):
    FACTORY_FOR = User
    username = factory.Sequence(lambda n: "user%03d" % n)
    password = factory.PostGenerationMethodCall('set_password', 'test')


class ExtendedDateFormatFactory(factory.DjangoModelFactory):
    FACTORY_FOR = ExtendedDateFormat
    edtf_format = '1984~'


class RoleFactory(factory.DjangoModelFactory):
    FACTORY_FOR = Role
    name = factory.Sequence(lambda n: "Author%03d" % n)
    level = 'footprint'


class LanguageFactory(factory.DjangoModelFactory):
    FACTORY_FOR = Language
    name = factory.Sequence(lambda n: "Language%03d" % n)


class DigitalFormatFactory(factory.DjangoModelFactory):
    FACTORY_FOR = DigitalFormat
    name = factory.Sequence(lambda n: "format%03d" % n)


class DigitalObjectFactory(factory.DjangoModelFactory):
    FACTORY_FOR = DigitalObject
    name = factory.Sequence(lambda n: "image%03d" % n)
    digital_format = factory.SubFactory(DigitalFormatFactory)

    file = factory.django.FileField(data=b"uhuh",
                                    filename=TEST_MEDIA_PATH)


class StandardizedIdentificationTypeFactory(factory.DjangoModelFactory):
    FACTORY_FOR = StandardizedIdentificationType

    name = factory.Sequence(lambda n: "name%03d" % n)
    slug = factory.Sequence(lambda n: "%03d" % n)
    level = IMPRINT_LEVEL


class StandardizedIdentificationFactory(factory.DjangoModelFactory):
    FACTORY_FOR = StandardizedIdentification

    identifier = factory.Sequence(lambda n: "identifier%03d" % n)
    identifier_type = factory.SubFactory(StandardizedIdentificationTypeFactory)


class PersonFactory(factory.DjangoModelFactory):
    FACTORY_FOR = Person

    name = factory.Sequence(lambda n: "Name%03d" % n)
    birth_date = factory.SubFactory(ExtendedDateFormatFactory)
    death_date = factory.SubFactory(ExtendedDateFormatFactory)
    standardized_identifier = factory.SubFactory(
        StandardizedIdentificationFactory)
    notes = "notes"


class ActorFactory(factory.DjangoModelFactory):
    FACTORY_FOR = Actor

    person = factory.SubFactory(PersonFactory)
    role = factory.SubFactory(RoleFactory)
    alias = factory.Sequence(lambda n: "Name%03d" % n)


class PlaceFactory(factory.DjangoModelFactory):
    FACTORY_FOR = Place

    country = 'Poland'
    city = 'Cracow'
    position = '50.064650,19.944979'


class CollectionFactory(factory.DjangoModelFactory):
    FACTORY_FOR = Collection

    name = factory.Sequence(lambda n: "Collection%03d" % n)

    @factory.post_generation
    def actors(self, create, extracted, **kwargs):
        if create:
            self.actor.add(ActorFactory())


class WrittenWorkFactory(factory.DjangoModelFactory):
    FACTORY_FOR = WrittenWork

    title = 'The Odyssey'
    notes = 'epic'

    @factory.post_generation
    def actors(self, create, extracted, **kwargs):
        if create:
            role = RoleFactory()
            self.actor.add(ActorFactory(role=role))


class ImprintFactory(factory.DjangoModelFactory):
    FACTORY_FOR = Imprint

    work = factory.SubFactory(WrittenWorkFactory)
    title = 'The Odyssey, Edition 1'
    date_of_publication = factory.SubFactory(ExtendedDateFormatFactory)
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


class BookCopyFactory(factory.DjangoModelFactory):
    FACTORY_FOR = BookCopy

    imprint = factory.SubFactory(ImprintFactory)
    notes = "lorem ipsum"


class FootprintFactory(factory.DjangoModelFactory):
    FACTORY_FOR = Footprint

    book_copy = factory.SubFactory(BookCopyFactory)
    medium = 'Medium'
    provenance = 'Provenance'

    title = 'Odyssey'
    place = factory.SubFactory(PlaceFactory)

    associated_date = factory.SubFactory(ExtendedDateFormatFactory)

    call_number = 'call number'
    collection = factory.SubFactory(CollectionFactory)

    notes = "lorem ipsum"

    @factory.post_generation
    def actors(self, create, extracted, **kwargs):
        if create:
            role = RoleFactory()
            self.actor.add(ActorFactory.create(role=role))

    @factory.post_generation
    def language(self, create, extracted, **kwargs):
        if create:
            self.language.add(LanguageFactory())
