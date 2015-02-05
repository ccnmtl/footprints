# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0003_auto_20150202_1459'),
    ]

    operations = [
        migrations.AlterField(
            model_name='imprint',
            name='work',
            field=models.ForeignKey(default=1, to='main.WrittenWork'),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='writtenwork',
            name='title',
            field=models.TextField(null=True, blank=True),
            preserve_default=True,
        ),
    ]
