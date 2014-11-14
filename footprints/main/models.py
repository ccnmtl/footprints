from django.db import models
from geoposition.fields import GeopositionField
from audit_log.models.fields import LastUserField, CreatingUserField


CONTINENTS = (
    ('AF', 'Africa'),
    ('AS', 'Asia'),
    ('EU', 'Europe'),
    ('NA', 'North America'),
    ('SA', 'South America'),
    ('OC', 'Oceania'),
    ('AN', 'Antarctica'))


IDENTIFIER_TYPES = (
    ('LOC', 'Library of Congress'),
    ('BHB', 'Bibliography of the Hebrew Book'),
    ('WLD', 'WorldCat (OCLC)'),
    ('VIAF', 'Virtual International Authority File')
)

HIDDEN_FIELDS = ['id']


def get_model_fields(the_model):
    return [field.name for field in the_model._meta.fields
            if field.name not in HIDDEN_FIELDS]


class ExtendedDateFormat(models.Model):
    edtf_format = models.CharField(max_length=256)

    class Meta:
        verbose_name = 'Extended Date Format'

    def __unicode__(self):
        return self.edtf_format


class Role(models.Model):
    name = models.CharField(max_length=256, unique=True)

    class Meta:
        ordering = ['name']
        verbose_name = 'Role'

    def __unicode__(self):
        return self.name


class Name(models.Model):
    last_name = models.CharField(max_length=256)
    first_name = models.CharField(max_length=256, null=True, blank=True)
    middle_name = models.CharField(max_length=256, null=True, blank=True)
    suffix = models.CharField(max_length=256, null=True, blank=True)

    created_by = CreatingUserField(related_name="name_created_by")
    last_modified_by = LastUserField(related_name="name_last_modified_by")

    class Meta:
        ordering = ['last_name']
        verbose_name = 'Name'

    def __unicode__(self):
        name = self.last_name

        if self.first_name or self.middle_name or self.suffix:
            name = name + ','

        if self.first_name:
            name = name + ' ' + self.first_name

        if self.middle_name:
            name = name + ' ' + self.middle_name

        if self.suffix:
            name = name + ' ' + self.suffix

        return name


class Language(models.Model):
    name = models.CharField(max_length=100, unique=True)

    class Meta:
        ordering = ['name']
        verbose_name = 'Language'

    def __unicode__(self):
        return self.name


class DigitalFormat(models.Model):
    name = models.CharField(max_length=100, unique=True)

    class Meta:
        ordering = ['name']
        verbose_name = "Digital Format"

    def __unicode__(self):
        return self.name


class DigitalObject(models.Model):
    name = models.CharField(max_length=500)
    digital_format = models.ForeignKey(DigitalFormat)
    file = models.FileField(upload_to="/%Y/%m/%d/")

    source_url = models.URLField(null=True, blank=True)
    notes = models.TextField(null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    modified_at = models.DateTimeField(auto_now=True)

    created_by = CreatingUserField(related_name="digitalobject_created_by")
    last_modified_by = LastUserField(
        related_name="digitalobject_last_modified_by")

    class Meta:
        verbose_name = "Digital Object"
        ordering = ['name']

    def __unicode__(self):
        return self.name


class StandardizedIdentification(models.Model):
    identifier = models.CharField(max_length=512)
    identifier_type = models.CharField(max_length=5, choices=IDENTIFIER_TYPES)
    identifier_text = models.TextField(null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    modified_at = models.DateTimeField(auto_now=True)

    created_by = CreatingUserField(
        related_name='standardizedidentification_created_by')
    last_modified_by = LastUserField(
        related_name='standardizedidentification_last_modified_by')

    class Meta:
        verbose_name = "Standardized Identification"

    def __unicode__(self):
        type_description = dict(IDENTIFIER_TYPES)[self.identifier_type]

        return '%s [%s] %s' % (
            self.identifier,
            type_description,
            self.identifier_text or '')


class Person(models.Model):
    name = models.ForeignKey(Name)
    date_of_birth = models.ForeignKey(ExtendedDateFormat,
                                      null=True, blank=True)

    standardized_identifier = models.ForeignKey(StandardizedIdentification,
                                                null=True, blank=True)
    digital_object = models.ManyToManyField(
        DigitalObject, null=True, blank=True)

    notes = models.TextField(null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    modified_at = models.DateTimeField(auto_now=True)

    created_by = CreatingUserField(related_name='person_created_by')
    last_modified_by = LastUserField(related_name='person_last_modified_by')

    class Meta:
        verbose_name = "Person"
        ordering = ['name']

    def __unicode__(self):
        return self.name.__unicode__()


class Contributor(models.Model):
    person = models.ForeignKey(Person)
    role = models.ForeignKey(Role)
    alternate_name = models.ForeignKey(Name, null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    modified_at = models.DateTimeField(auto_now=True)

    created_by = CreatingUserField(related_name='contributor_created_by')
    last_modified_by = LastUserField(
        related_name='contributor_last_modified_by')

    def __unicode__(self):
        return "%s (%s)" % (self.alternate_name or self.person.__unicode__(),
                            self.role)


class Place(models.Model):
    continent = models.CharField(max_length=2, choices=CONTINENTS)
    region = models.CharField(max_length=256, null=True, blank=True)
    country = models.CharField(max_length=256, null=True, blank=True)
    city = models.CharField(max_length=256, null=True, blank=True)

    position = GeopositionField(null=True, blank=True)

    digital_object = models.ManyToManyField(
        DigitalObject, null=True, blank=True)

    notes = models.TextField(null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    modified_at = models.DateTimeField(auto_now=True)

    created_by = CreatingUserField(related_name='place_created_by')
    last_modified_by = LastUserField(related_name='place_last_modified_by')

    class Meta:
        ordering = ['continent', 'region', 'country', 'city']
        verbose_name = "Place"

    def __unicode__(self):
        label = dict(CONTINENTS)[self.continent]
        if self.region:
            label += ', ' + self.region
        if self.country:
            label += ', ' + self.country
        if self.city:
            label += ', ' + self.city

        return label


class Collection(models.Model):
    name = models.CharField(max_length=512, unique=True)
    contributor = models.ManyToManyField(Contributor, null=True, blank=True)

    notes = models.TextField(null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    modified_at = models.DateTimeField(auto_now=True)

    created_by = CreatingUserField(related_name='collection_created_by')
    last_modified_by = LastUserField(
        related_name='collection_last_modified_by')

    class Meta:
        ordering = ['name']
        verbose_name = "Collection"

    def __unicode__(self):
        return self.name


class WrittenWork(models.Model):
    standardized_title = models.TextField()
    author = models.ManyToManyField(Contributor, null=True, blank=True)
    notes = models.TextField(null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    modified_at = models.DateTimeField(auto_now=True)

    created_by = CreatingUserField(related_name='writtenwork_created_by')
    last_modified_by = LastUserField(
        related_name='writtenwork_last_modified_by')

    class Meta:
        ordering = ['standardized_title']
        verbose_name = "Written Work"

    def __unicode__(self):
        return self.standardized_title


class Imprint(models.Model):
    work = models.ForeignKey(WrittenWork)

    title = models.TextField(null=True, blank=True)
    language = models.ForeignKey(Language, null=True, blank=True)
    publication_date = models.ForeignKey(ExtendedDateFormat,
                                         null=True, blank=True)
    place = models.ForeignKey(Place, null=True, blank=True)

    contributor = models.ManyToManyField(Contributor, null=True, blank=True)

    standardized_identifier = models.ManyToManyField(
        StandardizedIdentification, null=True, blank=True)

    digital_object = models.ManyToManyField(
        DigitalObject, null=True, blank=True)

    notes = models.TextField(null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    modified_at = models.DateTimeField(auto_now=True)

    created_by = CreatingUserField(related_name='imprint_created_by')
    last_modified_by = LastUserField(related_name='imprint_last_modified_by')

    class Meta:
        ordering = ['work']
        verbose_name = "Imprint"

    def __unicode__(self):
        return self.title or self.work.__unicode__()


class BookCopy(models.Model):
    imprint = models.ForeignKey(Imprint)

    digital_object = models.ManyToManyField(
        DigitalObject, null=True, blank=True)

    notes = models.TextField(null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    modified_at = models.DateTimeField(auto_now=True)

    created_by = CreatingUserField(related_name='bookcopy_created_by')
    last_modified_by = LastUserField(related_name='bookcopy_last_modified_by')

    class Meta:
        ordering = ['imprint']
        verbose_name = "Book Copy"

    def __unicode__(self):
        return self.imprint.__unicode__()


class Footprint(models.Model):
    book_copy = models.ForeignKey(BookCopy)
    medium = models.CharField(max_length=256)
    provenance = models.CharField(max_length=256)

    title = models.TextField()
    language = models.ForeignKey(Language, null=True, blank=True)
    place = models.ForeignKey(Place, null=True, blank=True)

    recorded_date = models.ForeignKey(ExtendedDateFormat,
                                      null=True, blank=True)

    call_number = models.CharField(max_length=256, null=True, blank=True)
    collection = models.ForeignKey(Collection, null=True, blank=True)

    digital_object = models.ManyToManyField(
        DigitalObject, null=True, blank=True)

    notes = models.TextField(null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    modified_at = models.DateTimeField(auto_now=True)

    created_by = CreatingUserField(related_name='footprint_created_by')
    last_modified_by = LastUserField(related_name='footprint_last_modified_by')

    class Meta:
        ordering = ['title']
        verbose_name = "Footprint"

    def __unicode__(self):
        return self.title or self.book_copy.__unicode__()
