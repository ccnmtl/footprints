# flake8: noqa
# -*- coding: utf-8 -*-
# Generated by Django 1.9.12 on 2017-02-21 21:16
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0025_footprint_verified'),
    ]

    operations = [
        migrations.AlterField(
            model_name='footprint',
            name='provenance',
            field=models.TextField(help_text=b'Where can one find the evidence now: a particular\n        library, archive, a printed book, a journal article etc.', verbose_name=b'Evidence Location'),
        ),
    ]
