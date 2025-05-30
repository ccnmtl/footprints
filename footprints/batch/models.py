from audit_log.models.fields import CreatingUserField
from django.core.exceptions import ValidationError
from django.core.validators import URLValidator
from django.db import models
from django.db.models.query_utils import Q

from footprints.batch.validators import validate_date, validate_numeric
from footprints.main.models import Footprint, Imprint, Role, MEDIUM_CHOICES, \
    BookCopy
from footprints.main.utils import format_bhb_number


class BatchJob(models.Model):
    processed = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    created_by = CreatingUserField()
    errors = ''

    def rows(self):
        return self.batchrow_set.all().order_by('id')

    def __str__(self):
        return str(self.id)


class BatchRow(models.Model):

    FIELD_MAPPING = [
        'catalog_url',
        'bhb_number',
        'imprint_title',
        'writtenwork_title',
        'writtenwork_author',
        'writtenwork_author_viaf',
        'writtenwork_author_birth_date',
        'writtenwork_author_death_date',
        'publisher',
        'publisher_viaf',
        'publication_location',
        'publication_date',
        'book_copy_call_number',
        'medium',  # Evidence Type
        'medium_description',  # Evidence Description
        'provenance',  # Evidence Location
        'call_number',
        'footprint_actor',
        'footprint_actor_viaf',
        'footprint_actor_role',
        'footprint_actor_birth_date',
        'footprint_actor_death_date',
        'footprint_notes',
        'footprint_location',
        'footprint_date',
        'footprint_narrative',
        'imprint_notes'
    ]

    DATE_HELP_TEXT = (
        "This value is invalid. See <a target='_blank' href='"
        "https://github.com/ccnmtl/footprints/wiki/Batch-Import-Format'>"
        "date formats</a> for rules.")
    VIAF_HELP_TEXT = (
        "This value is invalid. "
        "Please enter a numeric VIAF identifier.")
    LOCATION_HELP_TEXT = (
        "This value is invalid. Please enter a geocode, e.g. "
        "51.752021,-1.2577.")
    FOOTPRINT_ACTOR_ROLE_HELP_TEXT = (
        "A role is required when an actor's name is specified. The value is "
        "invalid or missing. See <a target='_blank' "
        "href='https://github.com/ccnmtl/footprints/wiki/Batch-Import-Format'>"
        "roles</a> for a list of choices.")
    IMPRINT_INTEGRITY = (
        "A <a href='/writtenwork/{}/#imprint-{}'>matching imprint</a> "
        "has conflicting data: <b>{}</b>.")
    BOOK_COPY_INTEGRITY = (
        "Multiple book copies have the same call number: {}.")
    BOOK_COPY_CALL_NUMBER_INTEGRITY = (
        "This call number is identified with a different BHB number ")
    FOOTPRINT_ACTOR_HELP_TEXT = (
        "An actor name is required when a role is specified.")

    job = models.ForeignKey(BatchJob, on_delete=models.CASCADE)

    catalog_url = models.TextField(
        null=True, blank=True, verbose_name='Catalog Link',
        help_text='Please enter a valid url format.')
    bhb_number = models.TextField(
        verbose_name='BHB Number',
        help_text=("This field is required. Please enter a numeric "
                   "BHB identifier."))
    imprint_title = models.TextField(
        verbose_name='Imprint', help_text="This field is required.")
    writtenwork_title = models.TextField(
        null=True, blank=True, verbose_name='Literary Work')
    writtenwork_author = models.TextField(
        null=True, blank=True, verbose_name='Literary Work Author')
    writtenwork_author_viaf = models.TextField(
        null=True, blank=True, verbose_name='Literary Work Author VIAF',
        help_text=VIAF_HELP_TEXT)
    writtenwork_author_birth_date = models.TextField(
        null=True, blank=True, verbose_name='Literary Work Author Birth Date',
        help_text=DATE_HELP_TEXT)
    writtenwork_author_death_date = models.TextField(
        null=True, blank=True, verbose_name='Literary Work Author Death Date',
        help_text=DATE_HELP_TEXT)

    # imprint publisher/printer/notes information
    publisher = models.TextField(
        null=True, blank=True, verbose_name='Publisher')
    publisher_viaf = models.TextField(
        null=True, blank=True, verbose_name='Publisher VIAF',
        help_text=VIAF_HELP_TEXT)
    publication_location = models.TextField(
        null=True, blank=True, verbose_name='Publication Location',
        help_text=LOCATION_HELP_TEXT)
    publication_date = models.TextField(
        null=True, blank=True, help_text=DATE_HELP_TEXT,
        verbose_name='Publication Date')
    imprint_notes = models.TextField(
        null=True, blank=True, verbose_name='Imprint Notes')

    # book copy call number
    book_copy_call_number = models.CharField(
        max_length=256, null=True, blank=True,
        verbose_name='Book Copy Call Number',
        help_text=BOOK_COPY_CALL_NUMBER_INTEGRITY)

    medium = models.TextField(
        verbose_name='Evidence Type', help_text='This field is required.')
    medium_description = models.TextField(
        verbose_name='Evidence Description', null=True, blank=True)
    provenance = models.TextField(
        verbose_name='Evidence Location', help_text='This field is required.')
    call_number = models.TextField(
        null=True, blank=True, verbose_name='Evidence Call Number')

    footprint_actor = models.TextField(
        null=True, blank=True, verbose_name='Footprint Actor',
        help_text=FOOTPRINT_ACTOR_HELP_TEXT)
    footprint_actor_viaf = models.TextField(
        null=True, blank=True, verbose_name='Footprint Actor VIAF',
        help_text=VIAF_HELP_TEXT)
    footprint_actor_role = models.TextField(
        null=True, blank=True, verbose_name='Footprint Actor Role',
        help_text=FOOTPRINT_ACTOR_ROLE_HELP_TEXT)
    footprint_actor_birth_date = models.TextField(
        null=True, blank=True, verbose_name='Footprint Actor Birth Date',
        help_text=DATE_HELP_TEXT)
    footprint_actor_death_date = models.TextField(
        null=True, blank=True, verbose_name='Footprint Actor Death Date',
        help_text=DATE_HELP_TEXT)
    footprint_notes = models.TextField(
        null=True, blank=True, verbose_name='Footprint Notes')
    footprint_location = models.TextField(
        null=True, blank=True, verbose_name='Footprint Location',
        help_text=LOCATION_HELP_TEXT)
    footprint_date = models.TextField(
        null=True, blank=True, verbose_name='Footprint Date',
        help_text=DATE_HELP_TEXT)

    footprint = models.ForeignKey(
        Footprint, on_delete=models.SET_NULL, blank=True, null=True)

    footprint_narrative = models.TextField(
        null=True, blank=True, verbose_name='Footprint Narrative')

    created_at = models.DateTimeField(auto_now_add=True)

    @classmethod
    def imported_fields(cls):
        return [BatchRow._meta.get_field(name) for name in cls.FIELD_MAPPING]

    def save(self, *args, **kwargs):
        if (self.writtenwork_title.endswith('.')):
            self.writtenwork_title = self.writtenwork_title[:-1]

        super(BatchRow, self).save(*args, **kwargs)

    def aggregate_notes(self):
        notes = ''
        if self.catalog_url and len(self.catalog_url) > 0:
            notes = u'{}<br />{}'.format(
                self.catalog_url, self.footprint_notes)
        else:
            notes = self.footprint_notes

        return notes

    def get_writtenwork_title(self):
        if self.writtenwork_title is None or len(self.writtenwork_title) < 1:
            return self.imprint_title
        return self.writtenwork_title

    def check_imprint_integrity(self):
        msg = None

        imprints = Imprint.objects.filter(
            standardized_identifier__identifier=self.bhb_number)
        imprint = imprints.select_related('work').first()

        if imprint is None:
            return msg

        # writtenwork title must match
        if (self.writtenwork_title and
                imprint.work.title.lower() != self.writtenwork_title.lower()):
            fields = ['literary work title']
            msg = self.IMPRINT_INTEGRITY.format(
                imprint.work.id, imprint.id, ', '.join(fields))

        return msg

    def check_book_copy_integrity(self):
        msg = None
        books = BookCopy.objects.filter(call_number=self.book_copy_call_number)

        if books.count() > 1:
            msg = self.BOOK_COPY_INTEGRITY.format(self.book_copy_call_number)

        return msg

    def similar_footprints(self):
        kwargs = {
            'medium': self.medium,
            'provenance': self.provenance,
            'call_number': self.call_number,
            'notes': self.aggregate_notes(),
            'book_copy__imprint__work__title__iexact':
                self.get_writtenwork_title()
        }

        bhb = self.bhb_number
        args = [
            Q(book_copy__imprint__standardized_identifier__identifier=bhb) |
            Q(book_copy__imprint__title__iexact=self.imprint_title)
        ]

        author = self.writtenwork_author
        if author:
            args.append(
                Q(book_copy__imprint__work__actor__person__name=author) |
                Q(book_copy__imprint__work__actor__alias=author))

        if self.publisher:
            args.append(
                Q(book_copy__imprint__actor__person__name=self.publisher) |
                Q(book_copy__imprint__actor__alias=self.publisher))

        if (self.publication_location and
                self.validate_publication_location()):
            fld = 'book_copy__imprint__place__canonical_place__geoname_id'
            kwargs[fld] = self.publication_location

        if self.footprint_actor:
            args.append(
                Q(actor__person__name=self.footprint_actor) |
                Q(actor__alias=self.footprint_actor))

        if (self.footprint_location and
                self.validate_footprint_location()):
            kwargs['place__canonical_place__geoname_id'] = \
                self.footprint_location

        qs = Footprint.objects.filter(*args, **kwargs)
        return qs.values_list('id', flat=True)

    def validate_catalog_url(self):
        try:
            if self.catalog_url:
                URLValidator()(self.catalog_url)
            return True
        except ValidationError:
            return False

    def validate_bhb_number(self):
        return validate_numeric(self.bhb_number)

    def validate_writtenwork_author_viaf(self):
        return validate_numeric(self.writtenwork_author_viaf)

    def validate_writtenwork_author_birth_date(self):
        return validate_date(self.writtenwork_author_birth_date)

    def validate_writtenwork_author_death_date(self):
        return validate_date(self.writtenwork_author_death_date)

    def validate_publisher_viaf(self):
        return validate_numeric(self.publisher_viaf)

    def validate_publication_date(self):
        return validate_date(self.publication_date)

    def validate_publication_location(self):
        return validate_numeric(self.publication_location)

    def validate_book_copy_call_number(self):
        if not self.book_copy_call_number:
            return True

        try:
            # does a book copy exist with this call number?
            copy = BookCopy.objects.get(call_number=self.book_copy_call_number)

            # make sure the imprint BHB numbers match
            return format_bhb_number(self.bhb_number) == \
                format_bhb_number(copy.imprint.get_bhb_number().identifier)
        except BookCopy.MultipleObjectsReturned:
            return True
        except BookCopy.DoesNotExist:
            return True
        except AttributeError:
            # copy's imprint does not have a bhb number
            return False

    def validate_medium(self):
        if not self.medium:
            return True

        return self.medium in MEDIUM_CHOICES

    def validate_footprint_actor(self):
        # if role is specified, actor must be specified
        if self.footprint_actor_role and not self.footprint_actor:
            return False

        return True

    def validate_footprint_actor_viaf(self):
        return validate_numeric(self.footprint_actor_viaf)

    def validate_footprint_actor_birth_date(self):
        return validate_date(self.footprint_actor_birth_date)

    def validate_footprint_actor_death_date(self):
        return validate_date(self.footprint_actor_death_date)

    def validate_footprint_date(self):
        return validate_date(self.footprint_date)

    def validate_footprint_actor_role(self):
        # if actor is specified, role must be specified
        if self.footprint_actor and not self.footprint_actor_role:
            return False

        if not self.footprint_actor_role:
            return True

        # role must be known
        return Role.objects.for_footprint().filter(
            name=self.footprint_actor_role).exists()

    def validate_footprint_location(self):
        return validate_numeric(self.footprint_location)
