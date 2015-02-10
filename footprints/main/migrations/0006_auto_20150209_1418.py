# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0005_role_level'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='name',
            name='created_by',
        ),
        migrations.RemoveField(
            model_name='name',
            name='last_modified_by',
        ),
        migrations.DeleteModel(
            name='Name',
        ),
    ]
