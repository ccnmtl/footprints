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
    ('VIAF', 'Virtual International Authority File'),
    ('GETT', 'The Getty Thesaurus of Geographic Names')
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
    name = models.TextField()
    sort_by = models.TextField()

    created_by = CreatingUserField(related_name="name_created_by")
    last_modified_by = LastUserField(related_name="name_last_modified_by")

    class Meta:
        ordering = ['sort_by', 'name']
        verbose_name = 'Name'

    def __unicode__(self):
        return self.name

    def save(self, *args, **kwargs):
        if self.sort_by is None or len(self.sort_by) < 1:
            self.sort_by = self.name
        super(Name, self).save(*args, **kwargs)


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
    name = models.OneToOneField(Name, related_name="person_name")
    alternate_spellings = models.ManyToManyField(
        Name, related_name="person_alternate_spellings", null=True, blank=True)

    birth_date = models.OneToOneField(ExtendedDateFormat,
                                      null=True, blank=True,
                                      related_name="birth_date")
    death_date = models.OneToOneField(ExtendedDateFormat,
                                      null=True, blank=True,
                                      related_name="death_date")

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


class Actor(models.Model):
    person = models.ForeignKey(Person)
    role = models.ForeignKey(Role)

    actor_alternate_name = models.TextField(null=True, blank=True)

    notes = models.TextField(null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    modified_at = models.DateTimeField(auto_now=True)

    created_by = CreatingUserField(related_name='actor_created_by')
    last_modified_by = LastUserField(
        related_name='actor_last_modified_by')

    def __unicode__(self):
        if self.actor_alternate_name:
            name = self.actor_alternate_name.__unicode__()
        else:
            name = self.person.__unicode__()

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

    standardized_identification = models.ForeignKey(StandardizedIdentification,
                                                    null=True,
                                                    blank=True)

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
    title = models.TextField()
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
        ordering = ['title']
        verbose_name = "Written Work"

    def __unicode__(self):
        return self.title


class Imprint(models.Model):
    work = models.ForeignKey(WrittenWork)

    title = models.TextField(null=True, blank=True)
    language = models.ForeignKey(Language, null=True, blank=True)
    date_of_publication = models.OneToOneField(ExtendedDateFormat, null=True,
                                               blank=True)
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
        if self.date_of_publication:
            label += " (%s)" % self.date_of_publication
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
    medium = models.CharField(
        "Medium of Evidence", max_length=256,
        help_text='''Where the footprint is derived or deduced from, e.g.
            an extant copy with an owner's signature''')
    provenance = models.CharField(
        "Provenance of Evidence", max_length=256,
        help_text='''Where can one find the evidence now: a particular
        library, archive, a printed book, a journal article etc.''')

    title = models.TextField()
    language = models.ForeignKey(Language, null=True, blank=True)
    document_type = models.CharField(max_length=256, null=True, blank=True)
    place = models.ForeignKey(Place, null=True, blank=True)

    associated_date = models.OneToOneField(ExtendedDateFormat,
                                           null=True, blank=True)

    call_number = models.CharField(max_length=256, null=True, blank=True)
    collection = models.ForeignKey(Collection, null=True, blank=True)

    digital_object = models.ManyToManyField(
        DigitalObject, null=True, blank=True)

    actor = models.ManyToManyField(
        Actor, null=True, blank=True,
        help_text="An owner or other person related to this footprint. ")

    notes = models.TextField(null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    modified_at = models.DateTimeField(auto_now=True)

    created_by = CreatingUserField(related_name='footprint_created_by')
    last_modified_by = LastUserField(related_name='footprint_last_modified_by')

    class Meta:
        ordering = ['title']
        verbose_name = "Footprint"

    def __unicode__(self):
        return self.provenance
