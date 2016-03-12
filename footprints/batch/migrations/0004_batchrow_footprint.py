# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0020_auto_20160229_1455'),
        ('batch', '0003_auto_20160308_0921'),
    ]

    operations = [
        migrations.AddField(
            model_name='batchrow',
            name='footprint',
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.SET_NULL,
                blank=True, to='main.Footprint', null=True),
        ),
    ]
