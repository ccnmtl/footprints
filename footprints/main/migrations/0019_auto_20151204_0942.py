# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0018_auto_20151119_1259'),
    ]

    operations = [
        migrations.RenameModel(
            old_name='ExtendedDateFormat',
            new_name='ExtendedDate',
        ),
    ]
