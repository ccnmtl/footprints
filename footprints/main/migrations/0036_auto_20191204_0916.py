# -*- coding: utf-8 -*-
# Generated by Django 1.11.26 on 2019-12-04 14:16
from __future__ import unicode_literals

from django.db import migrations


def fix_extra_space(apps, schema_editor):
    Footprint = apps.get_model('main', 'Footprint')
    for f in Footprint.objects.filter(
            medium='Bookseller/auction catalog  (pre-1850)'):
        f.medium = 'Bookseller/auction catalog (pre-1850)'
        f.save()


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0035_auto_20170911_1204'),
    ]

    operations = [
        migrations.RunPython(fix_extra_space),
    ]
