# flake8: noqa
# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0011_auto_20150302_1039'),
    ]

    operations = [
        migrations.AlterField(
            model_name='footprint',
            name='medium',
            field=models.CharField(help_text=b"Where the footprint is derived or deduced from, e.g.\n            an extant copy with an owner's signature", max_length=256, verbose_name=b'Evidence Type'),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='footprint',
            name='provenance',
            field=models.CharField(help_text=b'Where can one find the evidence now: a particular\n        library, archive, a printed book, a journal article etc.', max_length=256, verbose_name=b'Evidence Location'),
            preserve_default=True,
        ),
    ]
