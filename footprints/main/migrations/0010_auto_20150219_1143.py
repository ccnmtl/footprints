# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0009_auto_20150214_2039'),
    ]

    operations = [
        migrations.AlterField(
            model_name='footprint',
            name='book_copy',
            field=models.ForeignKey(default=1, to='main.BookCopy', on_delete=models.CASCADE),
            preserve_default=False,
        ),
    ]
