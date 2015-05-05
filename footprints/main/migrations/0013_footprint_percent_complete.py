# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0012_auto_20150303_1339'),
    ]

    operations = [
        migrations.AddField(
            model_name='footprint',
            name='percent_complete',
            field=models.IntegerField(default=0),
            preserve_default=True,
        ),
    ]
