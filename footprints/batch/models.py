from audit_log.models.fields import CreatingUserField
from django.db import models
from django.core.validators import URLValidator
from django.core.exceptions import ValidationError

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

    job = models.ForeignKey(BatchJob)

    catalog_url = models.TextField(
        null=True, blank=True, verbose_name='Catalog Link')
    bhb_number = models.TextField()
    imprint_title = models.TextField(
        verbose_name='Imprint')
    writtenwork_title = models.TextField(
        null=True, blank=True, verbose_name='Literary Work')
    writtenwork_author = models.TextField(
        null=True, blank=True, verbose_name='Literary Work Author')
    writtenwork_author_viaf = models.TextField(
        null=True, blank=True, verbose_name='Literary Work Author VIAF')
    writtenwork_author_birth_date = models.TextField(
        null=True, blank=True, verbose_name='Literary Work Author Birth Date')
    writtenwork_author_death_date = models.TextField(
        null=True, blank=True, verbose_name='Literary Work Author Death Date')

    # imprint publisher/printer information
    publisher = models.TextField(null=True, blank=True)
    publisher_viaf = models.TextField(null=True, blank=True)
    publication_location = models.TextField(null=True, blank=True)
    publication_date = models.TextField(null=True, blank=True)

    medium = models.TextField(verbose_name='Evidence Type')
    provenance = models.TextField(verbose_name='Evidence Location')
    call_number = models.TextField(null=True, blank=True)

    footprint_actor = models.TextField(null=True, blank=True)
    footprint_actor_viaf = models.TextField(null=True, blank=True)
    footprint_actor_role = models.TextField(null=True, blank=True)
    footprint_actor_birth_date = models.TextField(null=True, blank=True)
    footprint_actor_death_date = models.TextField(null=True, blank=True)
    footprint_notes = models.TextField(null=True, blank=True)
    footprint_location = models.TextField(null=True, blank=True)
    footprint_date = models.TextField(null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)

    def aggregate_notes(self):
        notes = ''
        if self.catalog_url and len(self.catalog_url) > 0:
            notes = '{}<br />{}'.format(self.catalog_url, self.footprint_notes)
        else:
            notes = self.footprint_notes

        return notes

    def check_for_duplication(self):
        # 1st pass: duplicate medium, provenance, call_number, notes
        # imprint title, written work title
        matches = Footprint.objects.filter(
            medium=self.medium, provenance=self.provenance,
            call_number=self.call_number, notes=self.aggregate_notes(),
            book_copy__imprint__title=self.imprint_title,
            book_copy__imprint__work__title=self.writtenwork_title)

        # @todo - 2nd pass:
        # ['bhb_number', 'writtenwork_author', 'publisher',
        #  'publication_location', 'publication_date',
        #  'footprint_actor', 'footprint_actor_role',
        # 'footprint_location', 'footprint_date'

        return matches.count() > 0

    def validate_catalog_url(self):
        try:
            if self.catalog_url:
                URLValidator()(self.catalog_url)
            return True
        except ValidationError:
            return False
