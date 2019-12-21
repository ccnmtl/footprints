# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0007_auto_20150211_1240'),
    ]

    operations = [
        migrations.AlterField(
            model_name='digitalobject',
            name='digital_format',
            field=models.ForeignKey(blank=True,
                                    to='main.DigitalFormat', null=True, on_delete=models.CASCADE),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='digitalobject',
            name='file',
            field=models.FileField(upload_to=b'%Y/%m/%d/'),
            preserve_default=True,
        ),
    ]
