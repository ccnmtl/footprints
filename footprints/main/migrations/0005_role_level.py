# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0004_auto_20150204_1502'),
    ]

    operations = [
        migrations.AddField(
            model_name='role',
            name='level',
            field=models.CharField(default='footprint', max_length=25,
                                   choices=[(b'footprint', b'Footprint'),
                                            (b'imprint', b'Imprint'),
                                            (b'writtenwork', b'WrittenWork')]),
            preserve_default=False,
        ),
    ]
