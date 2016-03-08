# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('batch', '0002_auto_20160229_1455'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='batchrow',
            options={'ordering': ['writtenwork_title', 'imprint_title', 'id']},
        ),
        migrations.AlterField(
            model_name='batchrow',
            name='footprint_actor',
            field=models.TextField(help_text=b'An actor name is required when a role is specified.', null=True, verbose_name=b'Footprint Actor', blank=True),
        ),
        migrations.AlterField(
            model_name='batchrow',
            name='footprint_actor_role',
            field=models.TextField(help_text=b"A role is required when an actor's name is specified. The value is invalid or missing. See <a target='_blank' href='https://github.com/ccnmtl/footprints/wiki/Batch-Import-Format'>roles</a> for a list of choices.", null=True, verbose_name=b'Footprint Actor Role', blank=True),
        ),
    ]
