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


def format_name(last_name, first_name, middle_name, suffix):
    name = last_name

    if first_name or middle_name or suffix:
        name = name + ','

    if first_name:
        name = name + ' ' + first_name

    if middle_name:
        name = name + ' ' + middle_name

    if suffix:
        name = name + ' ' + suffix

    return name


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
    file = models.FileField(upload_to="digitalobjects/%Y/%m/%d/")

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
    last_name = models.CharField(max_length=256)
    first_name = models.CharField(max_length=256, null=True, blank=True)
    middle_name = models.CharField(max_length=256, null=True, blank=True)
    suffix = models.CharField(max_length=256, null=True, blank=True)

    date_of_birth = models.CharField(max_length=256, null=True, blank=True)
    date_of_death = models.CharField(max_length=256, null=True, blank=True)

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
        ordering = ['last_name', 'first_name']

    def __unicode__(self):
        return format_name(self.last_name, self.first_name,
                           self.middle_name, self.suffix)


class Actor(models.Model):
    person = models.ForeignKey(Person)
    role = models.ForeignKey(Role)

    alternate_last_name = models.CharField(max_length=256,
                                           null=True, blank=True)
    alternate_first_name = models.CharField(max_length=256,
                                            null=True, blank=True)
    alternate_middle_name = models.CharField(max_length=256,
                                             null=True, blank=True)
    alternate_suffix = models.CharField(max_length=256,
                                        null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    modified_at = models.DateTimeField(auto_now=True)

    created_by = CreatingUserField(related_name='actor_created_by')
    last_modified_by = LastUserField(
        related_name='actor_last_modified_by')

    def __unicode__(self):
        last_name = self.alternate_last_name or self.person.last_name
        first_name = self.alternate_first_name or self.person.first_name
        middle_name = self.alternate_middle_name or self.person.middle_name
        suffix = self.alternate_suffix or self.person.suffix

        name = format_name(last_name, first_name, middle_name, suffix)
        return "%s (%s)" % (name, self.role)


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
        parts = []
        if self.city:
            parts.append(self.city)
        if self.country:
            parts.append(self.country)
        if self.region:
            parts.append(self.region)
        parts.append(dict(CONTINENTS)[self.continent])

        return ', '.join(parts)


class Collection(models.Model):
    name = models.CharField(max_length=512, unique=True)
    actor = models.ManyToManyField(Actor, null=True, blank=True)

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
    actor = models.ManyToManyField(
        Actor, null=True, blank=True,
        help_text="The author or creator of the work. ")
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
    publication_date = models.CharField(max_length=256, null=True, blank=True)
    place = models.ForeignKey(Place, null=True, blank=True)

    actor = models.ManyToManyField(Actor, null=True, blank=True)

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
        label = self.title or self.work.__unicode__()
        if self.publication_date:
            label += " (%s)" % self.publication_date
        return label


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
        verbose_name_plural = "Book Copies"

    def __unicode__(self):
        return self.imprint.__unicode__()


class Footprint(models.Model):
    book_copy = models.ForeignKey(BookCopy)
    medium = models.CharField(max_length=256)
    provenance = models.CharField(max_length=256)

    title = models.TextField()
    language = models.ForeignKey(Language, null=True, blank=True)
    place = models.ForeignKey(Place, null=True, blank=True)

    recorded_date = models.CharField(max_length=256, null=True, blank=True)

    call_number = models.CharField(max_length=256, null=True, blank=True)
    collection = models.ForeignKey(Collection, null=True, blank=True)

    digital_object = models.ManyToManyField(
        DigitalObject, null=True, blank=True)

    actor = models.ManyToManyField(
        Actor, null=True, blank=True,
        help_text="An owner or other person related to this footprint")

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
