from audit_log.models.fields import CreatingUserField
from django.db import models
from geoposition import Geoposition

from footprints.batch.validators import validate_publication_location, \
    validate_footprint_location
from footprints.main.models import Footprint


class BatchJob(models.Model):
    processed = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    created_by = CreatingUserField()


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
        'medium',
        'provenance',
        'call_number',
        'footprint_actor',
        'footprint_actor_viaf',
        'footprint_actor_role',
        'footprint_actor_birth_date',
        'footprint_actor_death_date',
        'footprint_notes',
        'footprint_location',
        'footprint_date'
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
    ROLE_HELP_TEXT = (
        "This value is invalid. See <a target='_blank' "
        "href='https://github.com/ccnmtl/footprints/wiki/Batch-Import-Format'>"
        "roles</a> for a list of choices.")

    job = models.ForeignKey(BatchJob)

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

    # imprint publisher/printer information
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

    medium = models.TextField(
        verbose_name='Evidence Type', help_text='This field is required.')
    provenance = models.TextField(
        verbose_name='Evidence Location', help_text='This field is required.')
    call_number = models.TextField(
        null=True, blank=True, verbose_name='Call Number')

    footprint_actor = models.TextField(
        null=True, blank=True, verbose_name='Footprint Actor')
    footprint_actor_viaf = models.TextField(
        null=True, blank=True, verbose_name='Footprint Actor VIAF',
        help_text=VIAF_HELP_TEXT)
    footprint_actor_role = models.TextField(
        null=True, blank=True, verbose_name='Footprint Actor Role',
        help_text=ROLE_HELP_TEXT)
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

    created_at = models.DateTimeField(auto_now_add=True)

    @classmethod
    def imported_fields(cls):
        return [BatchRow._meta.get_field(name) for name in cls.FIELD_MAPPING]

    def aggregate_notes(self):
        notes = ''
        if self.catalog_url and len(self.catalog_url) > 0:
            notes = u'{}<br />{}'.format(
                self.catalog_url, self.footprint_notes)
        else:
            notes = self.footprint_notes

        return notes

    def similar_footprints(self):
        params = {
            'medium': self.medium,
            'provenance': self.provenance,
            'book_copy__imprint__standardized_identifier__identifier':
                self.bhb_number,
            'book_copy__imprint__title': self.imprint_title,
            'call_number': self.call_number,
            'notes': self.aggregate_notes,
            'book_copy__imprint__work__title': self.writtenwork_title
        }

        if self.writtenwork_author:
            params['book_copy__imprint__work__actor__person__name'] = \
                self.writtenwork_author

        if self.publisher:
            params['book_copy__imprint__actor__person__name'] = self.publisher

        if (self.publication_location and
                validate_publication_location(self.publication_location)):
            latlong = self.publication_location.split(',')
            gp = Geoposition(latlong[0], latlong[1])
            params['book_copy__imprint__place__position'] = gp

        if self.footprint_actor:
            params['actor__person__name'] = self.footprint_actor

        if (self.footprint_location and
                validate_footprint_location(self.footprint_location)):
            latlong = self.footprint_location.split(',')
            params['place__position'] = Geoposition(latlong[0], latlong[1])

        return Footprint.objects.filter(**params).values_list('id', flat=True)
