# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations

from footprints.main.models import WRITTENWORK_LEVEL, IMPRINT_LEVEL, \
    PERSON_LEVEL, PLACE_LEVEL


def create_identification_types(apps, schema_editor):

    StandardizedIdentificationType = \
        apps.get_model("main", "StandardizedIdentificationType")

    StandardizedIdentificationType.objects.get_or_create(
        name='Library of Congress', slug='LOC', level=WRITTENWORK_LEVEL)

    StandardizedIdentificationType.objects.get_or_create(
        name='Bibliography of the Hebrew Book', slug='BHB',
        level=IMPRINT_LEVEL)

    StandardizedIdentificationType.objects.get_or_create(
        name='WorldCat (OCLC)', slug='WLD',  level=IMPRINT_LEVEL)

    StandardizedIdentificationType.objects.get_or_create(
        name='VIAF Identifier', slug='VIAF', level=PERSON_LEVEL)

    StandardizedIdentificationType.objects.get_or_create(
        name='The Getty Thesaurus of Geographic Names', slug='GETT',
        level=PLACE_LEVEL)


def migrate_identification_types(apps, schema_editor):
    StandardizedIdentificationType = \
        apps.get_model("main", "StandardizedIdentificationType")
    StandardizedIdentification = \
        apps.get_model("main", "StandardizedIdentification")

    for stid in StandardizedIdentification.objects.all():
        sttype = StandardizedIdentificationType.objects.get(
            slug=stid.identifier_type)
        stid.new_identifier_type = sttype
        stid.save()


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0015_auto_20150508_0947'),
    ]

    operations = [
        migrations.RunPython(create_identification_types),
        migrations.RunPython(migrate_identification_types),
    ]
