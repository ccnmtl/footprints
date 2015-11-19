# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0017_remove_standardizedidentification_identifier_type'),
    ]

    operations = [
        migrations.AlterField(
            model_name='bookcopy',
            name='digital_object',
            field=models.ManyToManyField(to='main.DigitalObject', blank=True),
        ),
        migrations.AlterField(
            model_name='collection',
            name='actor',
            field=models.ManyToManyField(to='main.Actor', blank=True),
        ),
        migrations.AlterField(
            model_name='footprint',
            name='actor',
            field=models.ManyToManyField(help_text=b'An owner or other person related to this footprint. ', to='main.Actor', blank=True),
        ),
        migrations.AlterField(
            model_name='footprint',
            name='digital_object',
            field=models.ManyToManyField(to='main.DigitalObject', blank=True),
        ),
        migrations.AlterField(
            model_name='footprint',
            name='language',
            field=models.ManyToManyField(to='main.Language', blank=True),
        ),
        migrations.AlterField(
            model_name='imprint',
            name='actor',
            field=models.ManyToManyField(to='main.Actor', blank=True),
        ),
        migrations.AlterField(
            model_name='imprint',
            name='digital_object',
            field=models.ManyToManyField(to='main.DigitalObject', blank=True),
        ),
        migrations.AlterField(
            model_name='imprint',
            name='language',
            field=models.ManyToManyField(to='main.Language', blank=True),
        ),
        migrations.AlterField(
            model_name='imprint',
            name='standardized_identifier',
            field=models.ManyToManyField(to='main.StandardizedIdentification', blank=True),
        ),
        migrations.AlterField(
            model_name='person',
            name='digital_object',
            field=models.ManyToManyField(to='main.DigitalObject', blank=True),
        ),
        migrations.AlterField(
            model_name='place',
            name='digital_object',
            field=models.ManyToManyField(to='main.DigitalObject', blank=True),
        ),
        migrations.AlterField(
            model_name='writtenwork',
            name='actor',
            field=models.ManyToManyField(help_text=b'The author or creator of the work. ', to='main.Actor', blank=True),
        ),
        migrations.AlterField(
            model_name='writtenwork',
            name='standardized_identifier',
            field=models.ManyToManyField(to='main.StandardizedIdentification', blank=True),
        ),
    ]
