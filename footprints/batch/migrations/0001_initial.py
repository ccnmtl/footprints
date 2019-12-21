# flake8: noqa
# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
from django.conf import settings
import audit_log.models.fields


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='BatchJob',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('processed', models.BooleanField(default=False)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('created_by', audit_log.models.fields.CreatingUserField(editable=False, to=settings.AUTH_USER_MODEL, null=True)),
            ],
        ),
        migrations.CreateModel(
            name='BatchRow',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('catalog_url', models.TextField(null=True, verbose_name=b'Catalog Link', blank=True)),
                ('bhb_number', models.TextField()),
                ('imprint_title', models.TextField(verbose_name=b'Imprint')),
                ('writtenwork_title', models.TextField(null=True, verbose_name=b'Literary Work', blank=True)),
                ('writtenwork_author', models.TextField(null=True, verbose_name=b'Literary Work Author', blank=True)),
                ('writtenwork_author_viaf', models.TextField(null=True, verbose_name=b'Literary Work Author VIAF', blank=True)),
                ('writtenwork_author_birth_date', models.TextField(null=True, verbose_name=b'Literary Work Author Birth Date', blank=True)),
                ('writtenwork_author_death_date', models.TextField(null=True, verbose_name=b'Literary Work Author Death Date', blank=True)),
                ('publisher', models.TextField(null=True, blank=True)),
                ('publisher_viaf', models.TextField(null=True, blank=True)),
                ('publication_location', models.TextField(null=True, blank=True)),
                ('publication_date', models.TextField(null=True, blank=True)),
                ('medium', models.TextField(verbose_name=b'Evidence Type')),
                ('provenance', models.TextField(verbose_name=b'Evidence Location')),
                ('call_number', models.TextField(null=True, blank=True)),
                ('footprint_actor', models.TextField(null=True, blank=True)),
                ('footprint_actor_viaf', models.TextField(null=True, blank=True)),
                ('footprint_actor_role', models.TextField(null=True, blank=True)),
                ('footprint_actor_birth_date', models.TextField(null=True, blank=True)),
                ('footprint_actor_death_date', models.TextField(null=True, blank=True)),
                ('footprint_notes', models.TextField(null=True, blank=True)),
                ('footprint_location', models.TextField(null=True, blank=True)),
                ('footprint_date', models.TextField(null=True, blank=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('job', models.ForeignKey(to='batch.BatchJob', on_delete=models.CASCADE)),
            ],
        ),
    ]
