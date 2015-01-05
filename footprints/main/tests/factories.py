from django.contrib.auth.models import User
import factory

from footprints.main.models import Language, ExtendedDateFormat, Role, \
    DigitalFormat, StandardizedIdentification, Person, \
    Actor, Place, Collection, WrittenWork, Imprint, BookCopy, Footprint, Name


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


class NameFactory(factory.DjangoModelFactory):
    FACTORY_FOR = Name
    name = factory.Sequence(lambda n: "Name%03d" % n)


class LanguageFactory(factory.DjangoModelFactory):
    FACTORY_FOR = Language
    name = factory.Sequence(lambda n: "Language%03d" % n)


class DigitalFormatFactory(factory.DjangoModelFactory):
    FACTORY_FOR = DigitalFormat
    name = 'txt'


class StandardizedIdentificationFactory(factory.DjangoModelFactory):
    FACTORY_FOR = StandardizedIdentification

    identifier = '002978330'
    identifier_type = 'BHB'
    identifier_text = 'The Odyssey / English prose by S.H. Butcher & A. Lang.'


class PersonFactory(factory.DjangoModelFactory):
    FACTORY_FOR = Person

    name = factory.SubFactory(NameFactory)
    birth_date = factory.SubFactory(ExtendedDateFormatFactory)
    death_date = factory.SubFactory(ExtendedDateFormatFactory)
    standardized_identifier = factory.SubFactory(
        StandardizedIdentificationFactory)


class ActorFactory(factory.DjangoModelFactory):
    FACTORY_FOR = Actor

    person = factory.SubFactory(PersonFactory)
    role = factory.SubFactory(RoleFactory)
    actor_name = factory.SubFactory(NameFactory)


class PlaceFactory(factory.DjangoModelFactory):
    FACTORY_FOR = Place

    continent = 'EU'
    region = 'Balkan Peninsula'
    country = 'Greece'
    city = 'Smyrna'


class CollectionFactory(factory.DjangoModelFactory):
    FACTORY_FOR = Collection

    name = 'Judaica Collection'

    @factory.post_generation
    def actors(self, create, extracted, **kwargs):
        if create:
            role = Role.objects.create(name='Caretaker')
            self.actor.add(ActorFactory(role=role))


class WrittenWorkFactory(factory.DjangoModelFactory):
    FACTORY_FOR = WrittenWork

    title = 'The Odyssey'

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

    @factory.post_generation
    def language(self, create, extracted, **kwargs):
        if create:
            self.language.add(LanguageFactory())
