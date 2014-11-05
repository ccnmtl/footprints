from django.contrib.auth.models import User
import factory

from footprints.main.models import Language, ExtendedDateFormat, Role, Name, \
    DigitalFormat, StandardizedIdentification, Person, DigitalObject, \
    Contributor, Place, Collection, WrittenWork, Imprint, BookCopy, Footprint


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
    last_name = 'Last'
    first_name = 'First'
    middle_name = 'Middle'
    suffix = 'Esq'


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
    date_of_birth = factory.SubFactory(ExtendedDateFormatFactory)
    standardized_identifier = factory.SubFactory(
        StandardizedIdentificationFactory)


class DigitalObjectFactory(factory.DjangoModelFactory):
    FACTORY_FOR = DigitalObject
    name = "Test Digital Object"
    digital_format = factory.SubFactory(DigitalFormatFactory)


class ContributorFactory(factory.DjangoModelFactory):
    FACTORY_FOR = Contributor

    person = factory.SubFactory(PersonFactory)
    role = factory.SubFactory(RoleFactory)
    alternate_name = factory.SubFactory(NameFactory,
                                        last_name='Homer', first_name='',
                                        middle_name='', suffix='')


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
    def contributors(self, create, extracted, **kwargs):
        if create:
            role = Role.objects.create(name='Caretaker')
            self.contributor.add(ContributorFactory(role=role))


class WrittenWorkFactory(factory.DjangoModelFactory):
    FACTORY_FOR = WrittenWork

    standardized_title = 'The Odyssey'

    @factory.post_generation
    def authors(self, create, extracted, **kwargs):
        if create:
            role = RoleFactory()
            self.author.add(ContributorFactory(role=role))


class ImprintFactory(factory.DjangoModelFactory):
    FACTORY_FOR = Imprint

    work = factory.SubFactory(WrittenWorkFactory)
    title = 'The Odyssey, Edition 1'
    language = factory.SubFactory(LanguageFactory)
    publication_date = factory.SubFactory(ExtendedDateFormatFactory)
    place = factory.SubFactory(PlaceFactory)

    @factory.post_generation
    def contributors(self, create, extracted, **kwargs):
        if create:
            role = RoleFactory()
            self.contributor.add(ContributorFactory.create(role=role))

    @factory.post_generation
    def standardized_identification(self, create, extracted, **kwargs):
        if create:
            identifier = StandardizedIdentificationFactory()
            self.standardized_identifier.add(identifier)


class BookCopyFactory(factory.DjangoModelFactory):
    FACTORY_FOR = BookCopy

    imprint = factory.SubFactory(ImprintFactory)


class FootprintFactory(factory.DjangoModelFactory):
    FACTORY_FOR = Footprint

    book_copy = factory.SubFactory(BookCopyFactory)
    medium = 'Medium'
    provenance = 'Provenance'

    title = 'Odyssey'
    language = factory.SubFactory(LanguageFactory)
    place = factory.SubFactory(PlaceFactory)

    recorded_date = factory.SubFactory(ExtendedDateFormatFactory)

    call_number = 'call number'
    collection = factory.SubFactory(CollectionFactory)
