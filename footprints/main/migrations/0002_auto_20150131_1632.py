# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0001_initial'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='place',
            options={'ordering': ['continent', 'country', 'city'],
                     'verbose_name': 'Place'},
        ),
        migrations.RemoveField(
            model_name='place',
            name='region',
        ),
    ]
