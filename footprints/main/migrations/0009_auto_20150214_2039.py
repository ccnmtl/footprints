# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0008_auto_20150214_0845'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='digitalobject',
            options={'ordering': ['-created_at'],
                     'verbose_name': 'Digital Object'},
        ),
        migrations.RenameField(
            model_name='digitalobject',
            old_name='notes',
            new_name='description',
        ),
    ]
