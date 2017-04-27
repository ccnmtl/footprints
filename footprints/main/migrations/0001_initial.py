# flake8: noqa
# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import audit_log.models.fields
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Actor',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('alias', models.TextField(null=True, blank=True)),
                ('notes', models.TextField(null=True, blank=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('modified_at', models.DateTimeField(auto_now=True)),
                ('created_by', audit_log.models.fields.CreatingUserField(related_name='actor_created_by', editable=False, to=settings.AUTH_USER_MODEL, null=True)),
                ('last_modified_by', audit_log.models.fields.LastUserField(related_name='actor_last_modified_by', editable=False, to=settings.AUTH_USER_MODEL, null=True)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='BookCopy',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('notes', models.TextField(null=True, blank=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('modified_at', models.DateTimeField(auto_now=True)),
                ('created_by', audit_log.models.fields.CreatingUserField(related_name='bookcopy_created_by', editable=False, to=settings.AUTH_USER_MODEL, null=True)),
            ],
            options={
                'ordering': ['imprint'],
                'verbose_name': 'Book Copy',
                'verbose_name_plural': 'Book Copies',
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Collection',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(unique=True, max_length=512)),
                ('notes', models.TextField(null=True, blank=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('modified_at', models.DateTimeField(auto_now=True)),
                ('actor', models.ManyToManyField(to='main.Actor', null=True, blank=True)),
                ('created_by', audit_log.models.fields.CreatingUserField(related_name='collection_created_by', editable=False, to=settings.AUTH_USER_MODEL, null=True)),
                ('last_modified_by', audit_log.models.fields.LastUserField(related_name='collection_last_modified_by', editable=False, to=settings.AUTH_USER_MODEL, null=True)),
            ],
            options={
                'ordering': ['name'],
                'verbose_name': 'Collection',
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='DigitalFormat',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(unique=True, max_length=100)),
            ],
            options={
                'ordering': ['name'],
                'verbose_name': 'Digital Format',
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='DigitalObject',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=500)),
                ('file', models.FileField(upload_to=b'digitalobjects/%Y/%m/%d/')),
                ('source_url', models.URLField(null=True, blank=True)),
                ('notes', models.TextField(null=True, blank=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('modified_at', models.DateTimeField(auto_now=True)),
                ('created_by', audit_log.models.fields.CreatingUserField(related_name='digitalobject_created_by', editable=False, to=settings.AUTH_USER_MODEL, null=True)),
                ('digital_format', models.ForeignKey(to='main.DigitalFormat')),
                ('last_modified_by', audit_log.models.fields.LastUserField(related_name='digitalobject_last_modified_by', editable=False, to=settings.AUTH_USER_MODEL, null=True)),
            ],
            options={
                'ordering': ['name'],
                'verbose_name': 'Digital Object',
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='ExtendedDateFormat',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('edtf_format', models.CharField(max_length=256)),
            ],
            options={
                'verbose_name': 'Extended Date Format',
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Footprint',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('medium', models.CharField(help_text=b"Where the footprint is derived or deduced from, e.g.\n            an extant copy with an owner's signature", max_length=256, verbose_name=b'Medium of Evidence')),
                ('medium_description', models.TextField(null=True, blank=True)),
                ('provenance', models.CharField(help_text=b'Where can one find the evidence now: a particular\n        library, archive, a printed book, a journal article etc.', max_length=256, verbose_name=b'Provenance of Evidence')),
                ('title', models.TextField(null=True, verbose_name=b'Footprint Title', blank=True)),
                ('call_number', models.CharField(max_length=256, null=True, blank=True)),
                ('notes', models.TextField(null=True, blank=True)),
                ('narrative', models.TextField(null=True, blank=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('modified_at', models.DateTimeField(auto_now=True)),
                ('actor', models.ManyToManyField(help_text=b'An owner or other person related to this footprint. ', to='main.Actor', null=True, blank=True)),
                ('associated_date', models.OneToOneField(null=True, blank=True, to='main.ExtendedDateFormat', verbose_name=b'Footprint Date')),
                ('book_copy', models.ForeignKey(blank=True, to='main.BookCopy', null=True)),
                ('collection', models.ForeignKey(blank=True, to='main.Collection', null=True)),
                ('created_by', audit_log.models.fields.CreatingUserField(related_name='footprint_created_by', editable=False, to=settings.AUTH_USER_MODEL, null=True)),
                ('digital_object', models.ManyToManyField(to='main.DigitalObject', null=True, blank=True)),
            ],
            options={
                'ordering': ['title'],
                'verbose_name': 'Footprint',
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Imprint',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('title', models.TextField(null=True, verbose_name=b'Imprint Title', blank=True)),
                ('notes', models.TextField(null=True, blank=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('modified_at', models.DateTimeField(auto_now=True)),
                ('actor', models.ManyToManyField(to='main.Actor', null=True, blank=True)),
                ('created_by', audit_log.models.fields.CreatingUserField(related_name='imprint_created_by', editable=False, to=settings.AUTH_USER_MODEL, null=True)),
                ('date_of_publication', models.OneToOneField(null=True, blank=True, to='main.ExtendedDateFormat')),
                ('digital_object', models.ManyToManyField(to='main.DigitalObject', null=True, blank=True)),
            ],
            options={
                'ordering': ['work'],
                'verbose_name': 'Imprint',
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Language',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(unique=True, max_length=100)),
            ],
            options={
                'ordering': ['name'],
                'verbose_name': 'Language',
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Name',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.TextField()),
                ('sort_by', models.TextField(null=True, blank=True)),
                ('created_by', audit_log.models.fields.CreatingUserField(related_name='name_created_by', editable=False, to=settings.AUTH_USER_MODEL, null=True)),
                ('last_modified_by', audit_log.models.fields.LastUserField(related_name='name_last_modified_by', editable=False, to=settings.AUTH_USER_MODEL, null=True)),
            ],
            options={
                'ordering': ['sort_by', 'name'],
                'verbose_name': 'Name',
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Person',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.TextField()),
                ('notes', models.TextField(null=True, blank=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('modified_at', models.DateTimeField(auto_now=True)),
                ('birth_date', models.OneToOneField(related_name='birth_date', null=True, blank=True, to='main.ExtendedDateFormat')),
                ('created_by', audit_log.models.fields.CreatingUserField(related_name='person_created_by', editable=False, to=settings.AUTH_USER_MODEL, null=True)),
                ('death_date', models.OneToOneField(related_name='death_date', null=True, blank=True, to='main.ExtendedDateFormat')),
                ('digital_object', models.ManyToManyField(to='main.DigitalObject', null=True, blank=True)),
                ('last_modified_by', audit_log.models.fields.LastUserField(related_name='person_last_modified_by', editable=False, to=settings.AUTH_USER_MODEL, null=True)),
            ],
            options={
                'ordering': ['name'],
                'verbose_name': 'Person',
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Place',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('continent', models.CharField(max_length=2, choices=[(b'AF', b'Africa'), (b'AS', b'Asia'), (b'EU', b'Europe'), (b'NA', b'North America'), (b'SA', b'South America'), (b'OC', b'Oceania'), (b'AN', b'Antarctica')])),
                ('region', models.CharField(max_length=256, null=True, blank=True)),
                ('country', models.CharField(max_length=256, null=True, blank=True)),
                ('city', models.CharField(max_length=256, null=True, blank=True)),
                ('position', models.CharField(max_length=42, null=True, blank=True)),
                ('notes', models.TextField(null=True, blank=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('modified_at', models.DateTimeField(auto_now=True)),
                ('created_by', audit_log.models.fields.CreatingUserField(related_name='place_created_by', editable=False, to=settings.AUTH_USER_MODEL, null=True)),
                ('digital_object', models.ManyToManyField(to='main.DigitalObject', null=True, blank=True)),
                ('last_modified_by', audit_log.models.fields.LastUserField(related_name='place_last_modified_by', editable=False, to=settings.AUTH_USER_MODEL, null=True)),
            ],
            options={
                'ordering': ['continent', 'region', 'country', 'city'],
                'verbose_name': 'Place',
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Role',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(unique=True, max_length=256)),
            ],
            options={
                'ordering': ['name'],
                'verbose_name': 'Role',
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='StandardizedIdentification',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('identifier', models.CharField(max_length=512)),
                ('identifier_type', models.CharField(max_length=5, choices=[(b'LOC', b'Library of Congress'), (b'BHB', b'Bibliography of the Hebrew Book'), (b'WLD', b'WorldCat (OCLC)'), (b'VIAF', b'VIAF Identifier'), (b'GETT', b'The Getty Thesaurus of Geographic Names')])),
                ('identifier_text', models.TextField(null=True, blank=True)),
                ('permalink', models.URLField(null=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('modified_at', models.DateTimeField(auto_now=True)),
                ('created_by', audit_log.models.fields.CreatingUserField(related_name='standardizedidentification_created_by', editable=False, to=settings.AUTH_USER_MODEL, null=True)),
                ('last_modified_by', audit_log.models.fields.LastUserField(related_name='standardizedidentification_last_modified_by', editable=False, to=settings.AUTH_USER_MODEL, null=True)),
            ],
            options={
                'verbose_name': 'Standardized Identification',
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='WrittenWork',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('title', models.TextField()),
                ('notes', models.TextField(null=True, blank=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('modified_at', models.DateTimeField(auto_now=True)),
                ('actor', models.ManyToManyField(help_text=b'The author or creator of the work. ', to='main.Actor', null=True, blank=True)),
                ('created_by', audit_log.models.fields.CreatingUserField(related_name='writtenwork_created_by', editable=False, to=settings.AUTH_USER_MODEL, null=True)),
                ('last_modified_by', audit_log.models.fields.LastUserField(related_name='writtenwork_last_modified_by', editable=False, to=settings.AUTH_USER_MODEL, null=True)),
            ],
            options={
                'ordering': ['title'],
                'verbose_name': 'Written Work',
            },
            bases=(models.Model,),
        ),
        migrations.AddField(
            model_name='place',
            name='standardized_identification',
            field=models.ForeignKey(blank=True, to='main.StandardizedIdentification', null=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='person',
            name='standardized_identifier',
            field=models.ForeignKey(blank=True, to='main.StandardizedIdentification', null=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='imprint',
            name='language',
            field=models.ManyToManyField(to='main.Language', null=True, blank=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='imprint',
            name='last_modified_by',
            field=audit_log.models.fields.LastUserField(related_name='imprint_last_modified_by', editable=False, to=settings.AUTH_USER_MODEL, null=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='imprint',
            name='place',
            field=models.ForeignKey(blank=True, to='main.Place', null=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='imprint',
            name='standardized_identifier',
            field=models.ManyToManyField(to='main.StandardizedIdentification', null=True, blank=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='imprint',
            name='work',
            field=models.ForeignKey(blank=True, to='main.WrittenWork', null=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='footprint',
            name='language',
            field=models.ManyToManyField(to='main.Language', null=True, blank=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='footprint',
            name='last_modified_by',
            field=audit_log.models.fields.LastUserField(related_name='footprint_last_modified_by', editable=False, to=settings.AUTH_USER_MODEL, null=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='footprint',
            name='place',
            field=models.ForeignKey(verbose_name=b'Footprint Location', blank=True, to='main.Place', null=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='bookcopy',
            name='digital_object',
            field=models.ManyToManyField(to='main.DigitalObject', null=True, blank=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='bookcopy',
            name='imprint',
            field=models.ForeignKey(to='main.Imprint'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='bookcopy',
            name='last_modified_by',
            field=audit_log.models.fields.LastUserField(related_name='bookcopy_last_modified_by', editable=False, to=settings.AUTH_USER_MODEL, null=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='actor',
            name='person',
            field=models.ForeignKey(to='main.Person'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='actor',
            name='role',
            field=models.ForeignKey(to='main.Role'),
            preserve_default=True,
        ),
    ]
