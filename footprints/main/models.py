from datetime import date
from decimal import Decimal

from audit_log.models.fields import LastUserField, CreatingUserField
from django.db import models
from django.db.models.query_utils import Q
from django.template import loader
from django.template.context import Context
from edtf import EDTF, edtf_date
from geoposition import Geoposition
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

MEDIUM_CHOICES = [
    'Approbation in imprint',
    'Booklist/estate inventory',
    'Bookseller/auction catalog  (pre-1850)',
    'Bookseller/auction catalog (1850-present)',
    'Bookseller marking in extant copy',
    'Censor signature in extant copy',
    'Dedication in imprint',
    'Library catalog/union catalog',
    'Owner signature/bookplate in extant copy',
    'Reference in another text',
    'Subscription list in imprint'
]


SLUG_VIAF = 'VIAF'
SLUG_BHB = 'BHB'


class ExtendedDateManager(models.Manager):

    def to_edtf(self, millenium, century, decade, year, month, day,
                approximate, uncertain):

        dt = ''

        if day is not None:
            dt = '{}{}{}{}-{:0>2d}-{:0>2d}'.format(
                millenium, century, decade, year, month, day)
        elif month is not None:
            dt = '{}{}{}{}-{:0>2d}'.format(
                millenium, century, decade, year, month)
        elif year is not None:
            dt = '{}{}{}{}'.format(millenium, century, decade, year)
        elif decade is not None:
            dt = '{}{}{}x'.format(millenium, century, decade)
        elif century is not None:
            dt = '{}{}xx'.format(millenium, century)
        elif millenium is not None:
            dt = '{}xxx'.format(millenium)
        else:
            return 'unknown'

        dt = append_uncertain(dt, uncertain)
        dt = append_approximate(dt, approximate)

        return dt

    def from_dict(self, values):
        dt = self.to_edtf(
            values['millenium1'], values['century1'], values['decade1'],
            values['year1'], values['month1'], values['day1'],
            values['approximate1'], values['uncertain1'])

        if values['is_range']:
            dt2 = self.to_edtf(
                values['millenium2'], values['century2'], values['decade2'],
                values['year2'], values['month2'], values['day2'],
                values['approximate2'], values['uncertain2'])

            dt = '{}/{}'.format(dt, dt2)

        return ExtendedDate(edtf_format=dt)

    def create_from_string(self, date_str):
        edtf = unicode(EDTF.from_natural_text(date_str))
        return ExtendedDate.objects.create(edtf_format=edtf)


def append_uncertain(dt, uncertain):
    if uncertain:
        dt = '{}?'.format(dt)
    return dt


def append_approximate(dt, approximate):
    if approximate:
        dt = '{}~'.format(dt)
    return dt


class ExtendedDate(models.Model):
    objects = ExtendedDateManager()
    edtf_format = models.CharField(max_length=256)

    month_names = {
        1: 'January', 2: 'February', 3: 'March', 4: 'April',
        5: 'May', 6: 'June', 7: 'July', 8: 'August', 9: 'September',
        10: 'October', 11: 'November', 12: 'December'}

    class Meta:
        verbose_name = 'Extended Date Format'

    def __unicode__(self):
        e = self.as_edtf()

        if e.is_interval:
            return "%s - %s" % (self.fmt(e.date_obj.start, True),
                                self.fmt(e.date_obj.end, True))
        else:
            return self.fmt(e.date_obj, False)

    def as_edtf(self):
        return EDTF(self.edtf_format)

    def ordinal(self, n):
        # cribbed from http://codegolf.stackexchange.com/
        # questions/4707/outputting-ordinal-numbers-1st-2nd-3rd#answer-4712
        return "%d%s" % (
            n, "tsnrhtdd"[(n / 10 % 10 != 1) * (n % 10 < 4) * n % 10::4])

    def fmt_modifier(self, date_obj):
        if date_obj == 'open':
            return 'present'
        if date_obj == 'unknown':
            return '?'

    def fmt_century(self, year, is_interval):
        if is_interval:
            return '{}s'.format(year)

        century = int(str(year)[:2]) + 1

        return '{} century'.format(self.ordinal(century))

    def fmt_millenium(self, millenium):
        millenium = int(millenium) + 1
        return '{} millenium'.format(self.ordinal(millenium))

    def fmt(self, date_obj, is_interval):
        if isinstance(date_obj, basestring):
            return self.fmt_modifier(date_obj)

        precision = date_obj.precision

        if precision is None:
            return 'invalid'

        result = self._fmt_precision(precision, date_obj, is_interval)

        result = fmt_uncertain(date_obj, result)
        result = fmt_approximate(date_obj, result)

        return result

    def _fmt_precision(self, precision, date_obj, is_interval):
        result = ''

        if precision == edtf_date.PRECISION_MILLENIUM:
            result = self.fmt_millenium(date_obj._millenium)
        elif precision == edtf_date.PRECISION_CENTURY:
            yr = date_obj._precise_year(edtf_date.EARLIEST)
            result = self.fmt_century(yr, is_interval)
        elif precision == edtf_date.PRECISION_DECADE:
            result = '%ss' % date_obj._precise_year(edtf_date.EARLIEST)
        elif precision == edtf_date.PRECISION_YEAR:
            result = '%s' % date_obj.get_year()
        elif precision == edtf_date.PRECISION_MONTH:
            result = '%s %s' % (self.month_names[date_obj.get_month()],
                                date_obj.get_year())
        elif precision == edtf_date.PRECISION_DAY:
            result = '%s %s, %s' % (
                self.month_names[date_obj.get_month()],
                date_obj.get_day(),
                date_obj.get_year())
        return result

    def _validate_python_date(self, dt):
        # the python-edtf library returns "date.max" on a ValueError
        # and, if approximate or uncertain are set, the day/month are adjusted
        # just compare the year 9999 to the returned year
        return None if dt.year == date.max.year else dt

    def start(self):
        edtf = self.as_edtf()

        if edtf.is_interval:
            dt = edtf.start_date_earliest()
        else:
            dt = edtf.date_earliest()

        return self._validate_python_date(dt)

    def end(self):
        edtf = self.as_edtf()

        if not edtf.is_interval:
            return None

        return self._validate_python_date(edtf.end_date_earliest())

    def match_string(self, date_str):
        return self.edtf_format == unicode(EDTF.from_natural_text(date_str))


def fmt_uncertain(date_obj, result):
    if date_obj.is_uncertain:
        result += '?'
    return result


def fmt_approximate(date_obj, result):
    if date_obj.is_approximate:
        result = 'c. ' + result
    return result


class RoleQuerySet(models.query.QuerySet):

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

    def for_footprint(self):
        return self.get_queryset().for_footprint()

    def for_imprint(self):
        return self.get_queryset().for_imprint()

    def for_work(self):
        return self.get_queryset().for_work()


class Role(models.Model):
    OWNER = 'Owner'
    AUTHOR = 'Author'
    PUBLISHER = 'Publisher'
    PRINTER = 'Printer'

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
        verbose_name = 'Digital Format'

    def __unicode__(self):
        return self.name


class DigitalObject(models.Model):
    name = models.CharField(max_length=500)
    file = models.FileField(upload_to="%Y/%m/%d/")
    url = models.TextField(blank=True)
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

    def viaf(self):
        return self.get(slug=SLUG_VIAF)

    def bhb(self):
        return self.get(slug=SLUG_BHB)


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

    def viaf(self):
        if not hasattr(self, 'viaf_type'):
            self.viaf_type = self.get_queryset().viaf()
        return self.viaf_type

    def bhb(self):
        if not hasattr(self, 'bhb_type'):
            self.bhb_type = self.get_queryset().bhb()
        return self.bhb_type


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
        if self.identifier_type:
            return self.identifier_type.name
        else:
            return None


class Person(models.Model):
    name = models.TextField()

    birth_date = models.OneToOneField(ExtendedDate,
                                      null=True, blank=True,
                                      related_name="birth_date")
    death_date = models.OneToOneField(ExtendedDate,
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
        if self.digital_object.exists():
            complete += 1
        if self.notes is not None and len(self.notes) > 0:
            complete += 1
        return int(complete/required * 100)


class ActorManager(models.Manager):

    def __init__(self, fields=None, *args, **kwargs):
        super(ActorManager, self).__init__(
            *args, **kwargs)
        self._fields = fields

    def get_or_create_by_attributes(self, name, viaf, role, born, died):
        # find by viaf
        viaf_type = StandardizedIdentificationType.objects.viaf()
        person = Person.objects.filter(
            standardized_identifier__identifier_type=viaf_type,
            standardized_identifier__identifier=viaf).first()

        if person is None:
            # find by name
            person = Person.objects.filter(name=name).first()
            if person is None:
                person = Person.objects.create(name=name)

            if viaf and person.standardized_identifier is None:
                # add identifier
                person.standardized_identifier = \
                    StandardizedIdentification.objects.create(
                        identifier=viaf, identifier_type=viaf_type)

            # update birth date & death date
            if born and person.birth_date is None:
                person.birth_date = ExtendedDate.objects.create(
                    edtf_format=unicode(EDTF.from_natural_text(born)))

            if died and person.death_date is None:
                person.death_date = ExtendedDate.objects.create(
                    edtf_format=unicode(EDTF.from_natural_text(died)))

            person.save()

        alias = None if name == person.name else name

        return Actor.objects.get_or_create(
            role=role, person=person, alias=alias)


class Actor(models.Model):
    objects = ActorManager()

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


class PlaceManager(models.Manager):

    def __init__(self, fields=None, *args, **kwargs):
        super(PlaceManager, self).__init__(
            *args, **kwargs)
        self._fields = fields

    def get_or_create_from_string(self, latlng):
        a = latlng.split(',')
        gp = Geoposition(a[0], a[1])
        return Place.objects.get_or_create(position=gp)


class Place(models.Model):
    objects = PlaceManager()

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

    def match_string(self, latlng):
        a = latlng.split(',')
        return (self.latitude() == Decimal(a[0]) and
                self.longitude() == Decimal(a[1]))


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
        if self.actor.exists():
            complete += 1
        if self.notes is not None and len(self.notes) > 0:
            complete += 1
        return int(complete/required * 100)

    def authors(self):
        return self.actor.filter(
            role__name=Role.AUTHOR).select_related('person')

    def description(self):
        template = loader.get_template('main/writtenwork_description.html')
        ctx = Context({'work': self})
        return template.render(ctx)

    def references(self):
        # how many footprints reference this work?
        return Footprint.objects.filter(book_copy__imprint__work=self).count()

    def imprints(self):
        lst = list(self.imprint_set.all())
        lst.sort(key=lambda obj: obj.sort_date())
        return lst


class ImprintManager(models.Manager):

    def __init__(self, fields=None, *args, **kwargs):
        super(ImprintManager, self).__init__(
            *args, **kwargs)
        self._fields = fields

    def get_or_create_by_attributes(self, bhb_number, work_title, title,
                                    publication_date):
        created = False
        bhb_type = StandardizedIdentificationType.objects.bhb()
        imprint = Imprint.objects.filter(
            standardized_identifier__identifier_type=bhb_type,
            standardized_identifier__identifier=bhb_number).first()

        if imprint is None:
            work, created = WrittenWork.objects.get_or_create(title=work_title)

            imprint, created = Imprint.objects.get_or_create(
                title=title, work=work)

            # add identifier
            if bhb_number:
                si = StandardizedIdentification.objects.create(
                    identifier=bhb_number, identifier_type=bhb_type)
                imprint.standardized_identifier.add(si)

            # add publication date
            if publication_date:
                imprint.publication_date = \
                    ExtendedDate.objects.create_from_string(publication_date)

            imprint.save()

        return imprint, created


class Imprint(models.Model):
    objects = ImprintManager()

    work = models.ForeignKey(WrittenWork)

    title = models.TextField(null=True, blank=True,
                             verbose_name="Imprint Title")
    language = models.ManyToManyField(Language, blank=True)
    publication_date = models.OneToOneField(ExtendedDate,
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

        if self.publication_date:
            label = "%s (%s)" % (label, self.publication_date)
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

    def footprints(self):
        lst = list(Footprint.objects.filter(book_copy__imprint=self))
        lst.sort(key=lambda obj:
                 (obj.book_copy.id,
                  obj.sort_date()))
        return lst

    def photos(self):
        return DigitalObject.objects.filter(
            footprint__in=Footprint.objects.filter(book_copy__imprint=self))

    def has_work(self):
        return self.work is not None

    def has_title(self):
        return self.title is not None

    def has_language(self):
        return self.language is not None

    def has_publication_date(self):
        return self.publication_date is not None

    def has_place(self):
        return self.place is not None

    def has_at_least_one_actor(self):
        return self.actor.exists()

    def has_standardized_identifier(self):
        return self.standardized_identifier is not None

    def has_bhb_number(self):
        # iterating this short list vs. using .filter to
        # take advantage of pre-fetch related
        for si in self.standardized_identifier.all():
            if si.identifier_type.slug == SLUG_BHB:
                return True
        return False

    def has_at_least_one_digital_object(self):
        return self.digital_object.exists()

    def has_notes(self):
        return self.notes is not None

    def percent_complete(self):
        required = 9.0

        checks = [
            self.has_work(),
            self.has_title(),
            self.has_language(),
            self.has_publication_date(),
            self.has_place(),
            self.has_at_least_one_actor(),
            self.has_standardized_identifier(),
            self.has_at_least_one_digital_object(),
            self.has_notes(),
        ]

        completed = sum(1 for c in checks if c)
        return int(completed/required * 100)

    def publishers(self):
        return self.actor.filter(
            role__name=Role.PUBLISHER).select_related('person')

    def printers(self):
        return self.actor.filter(
            role__name=Role.PRINTER).select_related('person')

    def references(self):
        # how many footprints reference this imprint?
        return Footprint.objects.filter(book_copy__imprint=self).count()

    def sort_date(self):
        if self.publication_date:
            return self.publication_date.start()

        return date.min


class BookCopy(models.Model):
    imprint = models.ForeignKey(Imprint)
    call_number = models.CharField(max_length=256, null=True, blank=True)

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

        if self.digital_object.exists():
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
        return Actor.objects.filter(
            role__name=Role.OWNER,
            footprint__in=footprints).select_related('person')

    def current_owners(self):
        footprints = Footprint.objects.filter(book_copy=self)
        if not footprints.exists():
            return Actor.objects.none()

        lst = list(footprints)
        lst.sort(key=lambda obj: obj.sort_date())
        most_recent_footprint = lst[-1]

        qs = Actor.objects.filter(
            role__name=Role.OWNER,
            footprint=most_recent_footprint).select_related('person')

        return qs


class FootprintManager(models.Manager):

    def flagged(self):
        return Footprint.objects.exclude(verified=True).filter(
            Q(percent_complete__lt=50) |
            Q(narrative__isnull=True) |
            Q(medium='Bookseller/auction catalog (1850-present)',
              call_number__isnull=True) |
            ~Q(book_copy__imprint__standardized_identifier__identifier_type__slug=SLUG_BHB))  # noqa:251


class Footprint(models.Model):
    objects = FootprintManager()

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

    associated_date = models.OneToOneField(ExtendedDate,
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

    verified = models.BooleanField(default=False)

    created_at = models.DateTimeField(auto_now_add=True)
    modified_at = models.DateTimeField(auto_now=True)

    created_by = CreatingUserField(related_name='footprint_created_by')
    last_modified_by = LastUserField(related_name='footprint_last_modified_by')

    class Meta:
        ordering = ['title']
        verbose_name = "Footprint"

    def __unicode__(self):
        return self.provenance

    def has_at_least_one_language(self):
        return self.language.exists()

    def has_call_number(self):
        return self.call_number is not None

    def has_place(self):
        return self.place is not None

    def has_associated_date(self):
        return self.associated_date is not None

    def has_at_least_one_digital_object(self):
        return self.digital_object.exists()

    def has_at_least_one_actor(self):
        return self.actor.exists()

    def has_notes(self):
        return self.notes is not None and len(self.notes) > 0

    def calculate_percent_complete(self):
        try:
            required = 11.0  # not including call_number & collection
            completed = 4  # book copy, title, medium & provenance are required

            checks = [
                self.has_at_least_one_language(),
                self.has_call_number(),
                self.has_place(),
                self.has_associated_date(),
                self.has_at_least_one_digital_object(),
                self.has_at_least_one_actor(),
                self.has_notes(),
            ]

            completed += sum(1 for c in checks if c)
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
        return self.actor.filter(
            role__name=Role.OWNER).select_related('person')

    def actors(self):
        return self.actor.all().select_related('person', 'role')

    def is_bare(self):
        return self.book_copy.imprint.work.percent_complete() == 0

    def is_flagged(self):
        return self in Footprint.objects.flagged()

    def description(self):
        template = loader.get_template('main/footprint_description.html')
        ctx = Context({'footprint': self})
        return template.render(ctx)

    def save(self, *args, **kwargs):
        self.percent_complete = self.calculate_percent_complete()
        super(Footprint, self).save(*args, **kwargs)

    def sort_date(self):
        if self.associated_date:
            return self.associated_date.start()

        return date.min
