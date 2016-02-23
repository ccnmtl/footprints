# flake8: noqa
# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations


def calculate_percent_complete(footprint):
    required = 11.0  # not including call_number & collection
    completed = 4  # book copy, title, medium & provenance are required

    if footprint.language is not None:
        completed += 1
    if footprint.call_number is not None:
        completed += 1
    if footprint.place is not None:
        completed += 1
    if footprint.associated_date is not None:
        completed += 1
    if footprint.digital_object.count() > 0:
        completed += 1
    if footprint.actor.count() > 0:
        completed += 1
    if footprint.notes is not None and len(footprint.notes) > 0:
        completed += 1
    return int(completed/required * 100)


def set_percent_complete(apps, schema_editor):
    Footprint = apps.get_model("main", "Footprint")

    for footprint in Footprint.objects.all():
        footprint.percent_complete = calculate_percent_complete(footprint)
        footprint.save()


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0013_footprint_percent_complete'),
    ]

    operations = [
        migrations.RunPython(set_percent_complete),
    ]
