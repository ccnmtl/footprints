# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0006_auto_20150209_1418'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='standardizedidentification',
            name='identifier_text',
        ),
        migrations.AlterField(
            model_name='standardizedidentification',
            name='permalink',
            field=models.URLField(null=True, blank=True),
            preserve_default=True,
        ),
    ]
