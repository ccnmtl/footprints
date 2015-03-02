# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0010_auto_20150219_1143'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='writtenwork',
            options={'ordering': ['title'], 'verbose_name': 'Literary Work'},
        ),
    ]
