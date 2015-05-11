# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0016_auto_20150508_0953'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='standardizedidentification',
            name='identifier_type',
        ),
        migrations.RenameField(
            model_name='standardizedidentification',
            old_name='new_identifier_type',
            new_name='identifier_type',
        ),
    ]
