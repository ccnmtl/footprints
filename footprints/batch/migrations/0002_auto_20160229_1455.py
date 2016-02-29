# flake8: noqa
# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('batch', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='batchrow',
            name='bhb_number',
            field=models.TextField(help_text=b'This field is required. Please enter a numeric BHB identifier.', verbose_name=b'BHB Number'),
        ),
        migrations.AlterField(
            model_name='batchrow',
            name='call_number',
            field=models.TextField(null=True, verbose_name=b'Call Number', blank=True),
        ),
        migrations.AlterField(
            model_name='batchrow',
            name='catalog_url',
            field=models.TextField(help_text=b'Please enter a valid url format.', null=True, verbose_name=b'Catalog Link', blank=True),
        ),
        migrations.AlterField(
            model_name='batchrow',
            name='footprint_actor',
            field=models.TextField(null=True, verbose_name=b'Footprint Actor', blank=True),
        ),
        migrations.AlterField(
            model_name='batchrow',
            name='footprint_actor_birth_date',
            field=models.TextField(help_text=b"This value is invalid. See <a target='_blank' href='https://github.com/ccnmtl/footprints/wiki/Batch-Import-Format'>date formats</a> for rules.", null=True, verbose_name=b'Footprint Actor Birth Date', blank=True),
        ),
        migrations.AlterField(
            model_name='batchrow',
            name='footprint_actor_death_date',
            field=models.TextField(help_text=b"This value is invalid. See <a target='_blank' href='https://github.com/ccnmtl/footprints/wiki/Batch-Import-Format'>date formats</a> for rules.", null=True, verbose_name=b'Footprint Actor Death Date', blank=True),
        ),
        migrations.AlterField(
            model_name='batchrow',
            name='footprint_actor_role',
            field=models.TextField(help_text=b"This value is invalid. See <a target='_blank' href='https://github.com/ccnmtl/footprints/wiki/Batch-Import-Format'>roles</a> for a list of choices.", null=True, verbose_name=b'Footprint Actor Role', blank=True),
        ),
        migrations.AlterField(
            model_name='batchrow',
            name='footprint_actor_viaf',
            field=models.TextField(help_text=b'This value is invalid. Please enter a numeric VIAF identifier.', null=True, verbose_name=b'Footprint Actor VIAF', blank=True),
        ),
        migrations.AlterField(
            model_name='batchrow',
            name='footprint_date',
            field=models.TextField(help_text=b"This value is invalid. See <a target='_blank' href='https://github.com/ccnmtl/footprints/wiki/Batch-Import-Format'>date formats</a> for rules.", null=True, verbose_name=b'Footprint Date', blank=True),
        ),
        migrations.AlterField(
            model_name='batchrow',
            name='footprint_location',
            field=models.TextField(help_text=b'This value is invalid. Please enter a geocode, e.g. 51.752021,-1.2577.', null=True, verbose_name=b'Footprint Location', blank=True),
        ),
        migrations.AlterField(
            model_name='batchrow',
            name='footprint_notes',
            field=models.TextField(null=True, verbose_name=b'Footprint Notes', blank=True),
        ),
        migrations.AlterField(
            model_name='batchrow',
            name='imprint_title',
            field=models.TextField(help_text=b'This field is required.', verbose_name=b'Imprint'),
        ),
        migrations.AlterField(
            model_name='batchrow',
            name='medium',
            field=models.TextField(help_text=b'This field is required.', verbose_name=b'Evidence Type'),
        ),
        migrations.AlterField(
            model_name='batchrow',
            name='provenance',
            field=models.TextField(help_text=b'This field is required.', verbose_name=b'Evidence Location'),
        ),
        migrations.AlterField(
            model_name='batchrow',
            name='publication_date',
            field=models.TextField(help_text=b"This value is invalid. See <a target='_blank' href='https://github.com/ccnmtl/footprints/wiki/Batch-Import-Format'>date formats</a> for rules.", null=True, verbose_name=b'Publication Date', blank=True),
        ),
        migrations.AlterField(
            model_name='batchrow',
            name='publication_location',
            field=models.TextField(help_text=b'This value is invalid. Please enter a geocode, e.g. 51.752021,-1.2577.', null=True, verbose_name=b'Publication Location', blank=True),
        ),
        migrations.AlterField(
            model_name='batchrow',
            name='publisher',
            field=models.TextField(null=True, verbose_name=b'Publisher', blank=True),
        ),
        migrations.AlterField(
            model_name='batchrow',
            name='publisher_viaf',
            field=models.TextField(help_text=b'This value is invalid. Please enter a numeric VIAF identifier.', null=True, verbose_name=b'Publisher VIAF', blank=True),
        ),
        migrations.AlterField(
            model_name='batchrow',
            name='writtenwork_author_birth_date',
            field=models.TextField(help_text=b"This value is invalid. See <a target='_blank' href='https://github.com/ccnmtl/footprints/wiki/Batch-Import-Format'>date formats</a> for rules.", null=True, verbose_name=b'Literary Work Author Birth Date', blank=True),
        ),
        migrations.AlterField(
            model_name='batchrow',
            name='writtenwork_author_death_date',
            field=models.TextField(help_text=b"This value is invalid. See <a target='_blank' href='https://github.com/ccnmtl/footprints/wiki/Batch-Import-Format'>date formats</a> for rules.", null=True, verbose_name=b'Literary Work Author Death Date', blank=True),
        ),
        migrations.AlterField(
            model_name='batchrow',
            name='writtenwork_author_viaf',
            field=models.TextField(help_text=b'This value is invalid. Please enter a numeric VIAF identifier.', null=True, verbose_name=b'Literary Work Author VIAF', blank=True),
        ),
    ]
