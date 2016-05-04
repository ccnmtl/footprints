# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations


def backfill_callnumber(apps, schema_editor):
    Footprint = apps.get_model("main", "Footprint")

    for footprint in Footprint.objects.filter(
        medium='Owner signature/bookplate in extant copy',
            call_number__isnull=False):

        footprint.book_copy.call_number = footprint.call_number
        footprint.book_copy.save()


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0023_bookcopy_call_number'),
    ]

    operations = [
        migrations.RunPython(backfill_callnumber),
    ]
