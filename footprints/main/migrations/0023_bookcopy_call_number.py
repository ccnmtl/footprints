# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0022_auto_20160321_1137'),
    ]

    operations = [
        migrations.AddField(
            model_name='bookcopy',
            name='call_number',
            field=models.CharField(max_length=256, null=True, blank=True),
        ),
    ]
