# -*- coding: utf-8 -*-
# Generated by Django 1.11.8 on 2017-12-11 15:21
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('batch', '0006_auto_20170404_1204'),
    ]

    operations = [
        migrations.AddField(
            model_name='batchrow',
            name='footprint_narrative',
            field=models.TextField(blank=True, null=True,
                                   verbose_name=b'Footprint Narrative'),
        ),
    ]
