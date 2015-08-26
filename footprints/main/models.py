from audit_log.models.fields import LastUserField, CreatingUserField
from django.db import models
from django.template import loader
from django.template.context import Context
from geoposition.fields import GeopositionField

FOOTPRINT_LEVEL = 'footprint'
IMPRINT_LEVEL = 'imprint'
WRITTENWORK_LEVEL = 'writtenwork'
PLACE_LEVEL = 'place'
PERSON_LEVEL = 'person'

LEVEL_TYPES = (
    (FOOTPRINT_LEVEL, 'Footprint'),
    (IMPRINT_LEVEL, 'Imprint'),
    (WRITTENWORK_LEVEL, 'WrittenWork'),
    (PLACE_LEVEL, 'Place'),
    (PERSON_LEVEL, 'Person')
)


class ExtendedDateFormat(models.Model):
    edtf_format = models.CharField(max_length=256)

    class Meta:
        verbose_name = 'Extended Date Format'

    def __unicode__(self):
        return self.edtf_format


class RoleQuerySet(models.query.QuerySet):
    def get_author_role(self):
        role, created = self.get_or_create(name='Author')
        return role

    def get_owner_role(self):
        role, created = self.get_or_create(name='Owner')
        return role

    def get_publisher_role(self):
        role, created = self.get_or_create(name='Publisher')
        return role

    def get_printer_role(self):
        role, created = self.get_or_create(name='Printer')
        return role

    def for_footprint(self):
        return self.filter(level=FOOTPRINT_LEVEL)

    def for_imprint(self):
        return self.filter(level=IMPRINT_LEVEL)

    def for_work(self):
        return self.filter(level=WRITTENWORK_LEVEL)


class RoleManager(models.Manager):
    def __init__(self, fields=None, *args, **kwargs):
        super(RoleManager, self).__init__(*args, **kwargs)
        self._fields = fields

    def get_queryset(self):
        return RoleQuerySet(self.model, self._fields)

    def get_author_role(self):
        return self.get_queryset().get_author_role()

    def get_owner_role(self):
        return self.get_queryset().get_owner_role()

    def get_publisher_role(self):
        return self.get_queryset().get_publisher_role()

    def get_printer_role(self):
        return self.get_queryset().get_printer_role()

    def for_footprint(self):
        return self.get_queryset().for_footprint()

    def for_imprint(self):
        return self.get_queryset().for_imprint()

    def for_work(self):
        return self.get_queryset().for_work()


class Role(models.Model):
    objects = RoleManager()

    name = models.CharField(max_length=256, unique=True)
    level = models.CharField(max_length=25, choices=LEVEL_TYPES)

    class Meta:
        ordering = ['name']
        verbose_name = 'Role'

    def __unicode__(self):
        return self.name


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
    file = models.FileField(upload_to="%Y/%m/%d/")
    description = models.TextField(null=True, blank=True)

    digital_format = models.ForeignKey(DigitalFormat, null=True, blank=True)
    source_url = models.URLField(null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    modified_at = models.DateTimeField(auto_now=True)

    created_by = CreatingUserField(related_name="digitalobject_created_by")
    last_modified_by = LastUserField(
        related_name="digitalobject_last_modified_by")

    class Meta:
        verbose_name = "Digital Object"
        ordering = ['-created_at']

    def __unicode__(self):
        return self.name


class StandardizedIdentificationTypeQuerySet(models.query.QuerySet):

    def for_imprint(self):
        return self.filter(level=IMPRINT_LEVEL)

    def for_work(self):
        return self.filter(level=WRITTENWORK_LEVEL)


class StandardizedIdentificationTypeManager(models.Manager):
    def __init__(self, fields=None, *args, **kwargs):
        super(StandardizedIdentificationTypeManager, self).__init__(
            *args, **kwargs)
        self._fields = fields

    def get_queryset(self):
        return StandardizedIdentificationTypeQuerySet(self.model, self._fields)

    def for_imprint(self):
        return self.get_queryset().for_imprint()

    def for_work(self):
        return self.get_queryset().for_work()


class StandardizedIdentificationType(models.Model):
    objects = StandardizedIdentificationTypeManager()

    name = models.CharField(max_length=256, unique=True)
    slug = models.CharField(max_length=5, unique=True)
    level = models.CharField(max_length=25, choices=LEVEL_TYPES)

    class Meta:
        ordering = ['name']
        verbose_name = 'Standardized Identification Type'

    def __unicode__(self):
        return self.name


class StandardizedIdentification(models.Model):
    identifier = models.CharField(max_length=512)
    identifier_type = models.ForeignKey(StandardizedIdentificationType,
                                        null=True, blank=True)
    permalink = models.URLField(null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    modified_at = models.DateTimeField(auto_now=True)

    created_by = CreatingUserField(
        related_name='standardizedidentification_created_by')
    last_modified_by = LastUserField(
        related_name='standardizedidentification_last_modified_by')

    class Meta:
        verbose_name = "Standardized Identification"

    def __unicode__(self):
        return self.identifier

    def authority(self):
        return self.identifier_type.name


class Person(models.Model):
    name = models.TextField()

    birth_date = models.OneToOneField(ExtendedDateFormat,
                                      null=True, blank=True,
                                      related_name="birth_date")
    death_date = models.OneToOneField(ExtendedDateFormat,
                                      null=True, blank=True,
                                      related_name="death_date")

    standardized_identifier = models.ForeignKey(StandardizedIdentification,
                                                null=True, blank=True)
    digital_object = models.ManyToManyField(
        DigitalObject, blank=True)

    notes = models.TextField(null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    modified_at = models.DateTimeField(auto_now=True)

    created_by = CreatingUserField(related_name='person_created_by')
    last_modified_by = LastUserField(related_name='person_last_modified_by')

    class Meta:
        verbose_name = "Person"
        ordering = ['name']

    def __unicode__(self):
        return self.name

    def percent_complete(self):
        required = 6.0
        complete = 1  # name is required

        if self.birth_date is not None:
            complete += 1
        if self.death_date is not None:
            complete += 1
        if self.standardized_identifier is not None:
            complete += 1
        if self.digital_object.count() > 0:
            complete += 1
        if self.notes is not None and len(self.notes) > 0:
            complete += 1
        return int(complete/required * 100)


class Actor(models.Model):
    person = models.ForeignKey(Person)
    role = models.ForeignKey(Role)
    alias = models.TextField(null=True, blank=True)
    notes = models.TextField(null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    modified_at = models.DateTimeField(auto_now=True)

    created_by = CreatingUserField(related_name='actor_created_by')
    last_modified_by = LastUserField(
        related_name='actor_last_modified_by')

    def display_name(self):
        if self.alias:
            return "%s as %s" % (self.person.name, self.alias)
        else:
            return self.person.name

    def __unicode__(self):
        return "%s (%s)" % (self.display_name(), self.role)


class Place(models.Model):
    country = models.CharField(max_length=256, null=True, blank=True)
    city = models.CharField(max_length=256, null=True, blank=True)

    position = GeopositionField()

    digital_object = models.ManyToManyField(
        DigitalObject, blank=True)

    notes = models.TextField(null=True, blank=True)

    standardized_identification = models.ForeignKey(StandardizedIdentification,
                                                    null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    modified_at = models.DateTimeField(auto_now=True)

    created_by = CreatingUserField(related_name='place_created_by')
    last_modified_by = LastUserField(related_name='place_last_modified_by')

    class Meta:
        ordering = ['country', 'city']
        verbose_name = "Place"

    def __unicode__(self):
        parts = []
        if self.city:
            parts.append(self.city)
        if self.country:
            parts.append(self.country)

        return ', '.join(parts)

    def latitude(self):
        return self.position.latitude

    def longitude(self):
        return self.position.longitude


class Collection(models.Model):
    name = models.CharField(max_length=512, unique=True)
    actor = models.ManyToManyField(Actor, blank=True)

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
    title = models.TextField(null=True, blank=True)
    actor = models.ManyToManyField(
        Actor, blank=True,
        help_text="The author or creator of the work. ")
    notes = models.TextField(null=True, blank=True)

    standardized_identifier = models.ManyToManyField(
        StandardizedIdentification, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    modified_at = models.DateTimeField(auto_now=True)

    created_by = CreatingUserField(related_name='writtenwork_created_by')
    last_modified_by = LastUserField(
        related_name='writtenwork_last_modified_by')

    class Meta:
        ordering = ['title']
        verbose_name = "Literary Work"

    def __unicode__(self):
        return self.title if self.title else ''

    def percent_complete(self):
        required = 3.0
        complete = 0

        if self.title is not None and len(self.title) > 0:
            complete += 1
        if self.actor.count() > 0:
            complete += 1
        if self.notes is not None and len(self.notes) > 0:
            complete += 1
        return int(complete/required * 100)

    def authors(self):
        role = Role.objects.get_author_role()
        return self.actor.filter(role=role)

    def description(self):
        return self.__unicode__()

    def references(self):
        # how many footprints reference this work?
        return Footprint.objects.filter(book_copy__imprint__work=self).count()


class Imprint(models.Model):
    work = models.ForeignKey(WrittenWork)

    title = models.TextField(null=True, blank=True,
                             verbose_name="Imprint Title")
    language = models.ManyToManyField(Language, blank=True)
    date_of_publication = models.OneToOneField(ExtendedDateFormat,
                                               null=True, blank=True)
    place = models.ForeignKey(Place, null=True, blank=True)

    actor = models.ManyToManyField(Actor, blank=True)

    standardized_identifier = models.ManyToManyField(
        StandardizedIdentification, blank=True)

    digital_object = models.ManyToManyField(
        DigitalObject, blank=True)

    notes = models.TextField(null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    modified_at = models.DateTimeField(auto_now=True)

    created_by = CreatingUserField(related_name='imprint_created_by')
    last_modified_by = LastUserField(related_name='imprint_last_modified_by')

    class Meta:
        ordering = ['work']
        verbose_name = "Imprint"

    def __unicode__(self):
        label = self.display_title() or "Imprint"

        if self.date_of_publication:
            label = "%s (%s)" % (label, self.date_of_publication)
        return label

    def display_title(self):
        if self.title:
            return self.title
        elif self.work.title:
            return self.work.title
        else:
            return None

    def description(self):
        template = loader.get_template('main/imprint_description.html')
        ctx = Context({'imprint': self})
        return template.render(ctx)

    def percent_complete(self):
        required = 9.0
        completed = 0

        if self.work is not None:
            completed += 1
        if self.title is not None:
            completed += 1
        if self.language is not None:
            completed += 1
        if self.date_of_publication is not None:
            completed += 1
        if self.place is not None:
            completed += 1
        if self.actor.count() > 0:
            completed += 1
        if self.standardized_identifier is not None:
            completed += 1
        if self.digital_object.count() > 0:
            completed += 1
        if self.notes is not None:
            completed += 1
        return int(completed/required * 100)

    def publishers(self):
        publisher = Role.objects.get_publisher_role()
        return self.actor.filter(role=publisher)

    def printers(self):
        printer = Role.objects.get_printer_role()
        return self.actor.filter(role=printer)

    def references(self):
        # how many footprints reference this imprint?
        return Footprint.objects.filter(book_copy__imprint=self).count()


class BookCopy(models.Model):
    imprint = models.ForeignKey(Imprint)

    digital_object = models.ManyToManyField(
        DigitalObject, blank=True)

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
        return "[%s] %s" % (self.id, self.imprint.__unicode__())

    def percent_complete(self):
        required = 3.0
        completed = 1  # imprint is required

        if self.digital_object.count() > 0:
            completed += 1
        if self.notes is not None:
            completed += 1
        return int(completed/required * 100)

    def identifier(self):
        return "%s-%s-%s" % (self.imprint.work.id, self.imprint.id, self.id)

    def description(self):
        template = loader.get_template('main/book_description.html')
        ctx = Context({'book': self})
        return template.render(ctx)

    def owners(self):
        footprints = Footprint.objects.filter(book_copy=self)
        role = Role.objects.get_owner_role()
        return Actor.objects.filter(role=role, footprint__in=footprints)


class Footprint(models.Model):
    MEDIUM_CHOICES = [
        "Approbation in imprint",
        "Booklist/estate inventory",
        "Bookseller/auction catalog  (pre-1850)",
        "Bookseller/auction catalog (1850-present)",
        "Bookseller marking in extant copy",
        "Censor signature in extant copy",
        "Dedication in imprint",
        "Library catalog/union catalog",
        "Owner signature/bookplate in extant copy",
        "Reference in another text",
        "Subscription list in imprint"
    ]

    book_copy = models.ForeignKey(BookCopy)
    medium = models.CharField(
        "Evidence Type", max_length=256,
        help_text='''Where the footprint is derived or deduced from, e.g.
            an extant copy with an owner's signature''')
    medium_description = models.TextField(null=True, blank=True)
    provenance = models.CharField(
        "Evidence Location", max_length=256,
        help_text='''Where can one find the evidence now: a particular
        library, archive, a printed book, a journal article etc.''')

    title = models.TextField(null=True, blank=True,
                             verbose_name='Footprint Title')
    language = models.ManyToManyField(Language, blank=True)
    place = models.ForeignKey(Place, null=True, blank=True,
                              verbose_name='Footprint Location')

    associated_date = models.OneToOneField(ExtendedDateFormat,
                                           null=True, blank=True,
                                           verbose_name='Footprint Date')

    call_number = models.CharField(max_length=256, null=True, blank=True)
    collection = models.ForeignKey(Collection, null=True, blank=True)

    digital_object = models.ManyToManyField(
        DigitalObject, blank=True)

    actor = models.ManyToManyField(
        Actor, blank=True,
        help_text="An owner or other person related to this footprint. ")

    notes = models.TextField(null=True, blank=True)

    narrative = models.TextField(null=True, blank=True)

    percent_complete = models.IntegerField(default=0)

    created_at = models.DateTimeField(auto_now_add=True)
    modified_at = models.DateTimeField(auto_now=True)

    created_by = CreatingUserField(related_name='footprint_created_by')
    last_modified_by = LastUserField(related_name='footprint_last_modified_by')

    class Meta:
        ordering = ['title']
        verbose_name = "Footprint"

    def __unicode__(self):
        return self.provenance

    def calculate_percent_complete(self):
        try:
            required = 11.0  # not including call_number & collection
            completed = 4  # book copy, title, medium & provenance are required

            if self.language.count() > 0:
                completed += 1
            if self.call_number is not None:
                completed += 1
            if self.place is not None:
                completed += 1
            if self.associated_date is not None:
                completed += 1
            if self.digital_object.count() > 0:
                completed += 1
            if self.actor.count() > 0:
                completed += 1
            if self.notes is not None and len(self.notes) > 0:
                completed += 1
            return int(completed/required * 100)
        except ValueError:
            # factoryboy construction may throw ValueErrors
            return 0

    def display_title(self):
        # return written work title OR the footprint title ?
        if (self.book_copy.imprint.work.title is not None and
                len(self.book_copy.imprint.work.title) > 0):
            return self.book_copy.imprint.work.title
        else:
            return self.title

    def owners(self):
        role = Role.objects.get_owner_role()
        return self.actor.filter(role=role)

    def is_bare(self):
        return self.book_copy.imprint.work.percent_complete() == 0

    def description(self):
        template = loader.get_template('main/footprint_description.html')
        ctx = Context({'footprint': self})
        return template.render(ctx)

    def save(self, *args, **kwargs):
        self.percent_complete = self.calculate_percent_complete()
        super(Footprint, self).save(*args, **kwargs)
