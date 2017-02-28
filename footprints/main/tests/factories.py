import os

from django.contrib.auth.models import User
import factory

from footprints.main.models import (
    Language, ExtendedDate, Role, DigitalFormat,
    StandardizedIdentification, Person, Actor, Place, Collection, WrittenWork,
    Imprint, BookCopy, Footprint, DigitalObject, IMPRINT_LEVEL,
    StandardizedIdentificationType)


TEST_MEDIA_PATH = os.path.join(os.path.dirname(__file__), 'test.txt')


class UserFactory(factory.DjangoModelFactory):
    class Meta:
        model = User
    username = factory.Sequence(lambda n: "user%03d" % n)
    password = factory.PostGenerationMethodCall('set_password', 'test')


class ExtendedDateFactory(factory.DjangoModelFactory):
    class Meta:
        model = ExtendedDate
    edtf_format = '1984~'


class RoleFactory(factory.DjangoModelFactory):
    class Meta:
        model = Role
    name = factory.Sequence(lambda n: "Author%03d" % n)
    level = 'footprint'


class LanguageFactory(factory.DjangoModelFactory):
    class Meta:
        model = Language
    name = factory.Sequence(lambda n: "Language%03d" % n)


class DigitalFormatFactory(factory.DjangoModelFactory):
    class Meta:
        model = DigitalFormat
    name = factory.Sequence(lambda n: "format%03d" % n)


class DigitalObjectFactory(factory.DjangoModelFactory):
    class Meta:
        model = DigitalObject
    name = factory.Sequence(lambda n: "image%03d" % n)
    digital_format = factory.SubFactory(DigitalFormatFactory)

    file = factory.django.FileField(data=b"uhuh",
                                    filename=TEST_MEDIA_PATH)


class StandardizedIdentificationTypeFactory(factory.DjangoModelFactory):
    class Meta:
        model = StandardizedIdentificationType

    name = factory.Sequence(lambda n: "name%03d" % n)
    slug = factory.Sequence(lambda n: "%03d" % n)
    level = IMPRINT_LEVEL


class StandardizedIdentificationFactory(factory.DjangoModelFactory):
    class Meta:
        model = StandardizedIdentification

    identifier = factory.Sequence(lambda n: "identifier%03d" % n)
    identifier_type = factory.SubFactory(StandardizedIdentificationTypeFactory)


class PersonFactory(factory.DjangoModelFactory):
    class Meta:
        model = Person

    name = factory.Sequence(lambda n: "Name%03d" % n)
    birth_date = factory.SubFactory(ExtendedDateFactory)
    death_date = factory.SubFactory(ExtendedDateFactory)
    standardized_identifier = factory.SubFactory(
        StandardizedIdentificationFactory)
    notes = "notes"


class ActorFactory(factory.DjangoModelFactory):
    class Meta:
        model = Actor

    person = factory.SubFactory(PersonFactory)
    role = factory.SubFactory(RoleFactory)
    alias = factory.Sequence(lambda n: "Name%03d" % n)


class PlaceFactory(factory.DjangoModelFactory):
    class Meta:
        model = Place

    country = 'Poland'
    city = 'Cracow'
    position = '50.064650,19.944979'


class CollectionFactory(factory.DjangoModelFactory):
    class Meta:
        model = Collection

    name = factory.Sequence(lambda n: "Collection%03d" % n)

    @factory.post_generation
    def actors(self, create, extracted, **kwargs):
        if create:
            self.actor.add(ActorFactory())


class WrittenWorkFactory(factory.DjangoModelFactory):
    class Meta:
        model = WrittenWork

    title = 'The Odyssey'
    notes = 'epic'

    @factory.post_generation
    def actors(self, create, extracted, **kwargs):
        if create:
            role = RoleFactory()
            self.actor.add(ActorFactory(role=role))


class ImprintFactory(factory.DjangoModelFactory):
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


class BookCopyFactory(factory.DjangoModelFactory):
    class Meta:
        model = BookCopy

    imprint = factory.SubFactory(ImprintFactory)
    notes = "lorem ipsum"
    call_number = 'B893.1BC'


class EmptyFootprintFactory(factory.DjangoModelFactory):
    class Meta:
        model = Footprint

    book_copy = factory.SubFactory(BookCopyFactory)
    medium = 'Bookseller/auction catalog (1850-present)'
    provenance = 'Provenance'
    title = 'The Iliad'


class FootprintFactory(factory.DjangoModelFactory):
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

    @factory.post_generation
    def actors(self, create, extracted, **kwargs):
        if create:
            role = RoleFactory()
            self.actor.add(ActorFactory.create(role=role))

    @factory.post_generation
    def language(self, create, extracted, **kwargs):
        if create:
            self.language.add(LanguageFactory())
