# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0019_auto_20151204_0942'),
    ]

    operations = [
        migrations.RenameField(
            model_name='imprint',
            old_name='date_of_publication',
            new_name='publication_date',
        ),
    ]
