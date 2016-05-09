# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('batch', '0004_batchrow_footprint'),
    ]

    operations = [
        migrations.AddField(
            model_name='batchrow',
            name='book_copy_call_number',
            field=models.CharField(max_length=256, null=True,
                                   verbose_name=b'Book Copy Call Number',
                                   blank=True),
        ),
        migrations.AlterField(
            model_name='batchrow',
            name='call_number',
            field=models.TextField(null=True,
                                   verbose_name=b'Evidence Call Number',
                                   blank=True),
        ),
    ]
