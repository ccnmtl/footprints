# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0020_auto_20160229_1455'),
    ]

    operations = [
        migrations.AddField(
            model_name='digitalobject',
            name='url',
            field=models.TextField(blank=True),
        ),
    ]
