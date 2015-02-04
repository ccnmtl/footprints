# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations
import datetime
import geoposition.fields
from django.utils.timezone import utc


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0002_auto_20150131_1632'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='place',
            options={'ordering': ['country', 'city'], 'verbose_name': 'Place'},
        ),
        migrations.RemoveField(
            model_name='place',
            name='continent',
        ),
        migrations.AlterField(
            model_name='place',
            name='position',
            field=geoposition.fields.GeopositionField(
                default=datetime.datetime(2015, 2, 2, 19, 59, 0, 360275,
                                          tzinfo=utc), max_length=42),
            preserve_default=False,
        ),
    ]
