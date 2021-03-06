# -*- coding: utf-8 -*-
# Generated by Django 1.9.12 on 2017-03-06 16:45
from __future__ import unicode_literals

from django.db import migrations


def remove_affil_groups(apps, schema_editor):
    Group = apps.get_model("auth", "Group")
    Group.objects.exclude(name='FootprintsStaff').delete()


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0026_auto_20170221_1616'),
    ]

    operations = [
        migrations.RunPython(remove_affil_groups),
    ]
