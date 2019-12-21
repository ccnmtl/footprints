# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0014_auto_20150505_1400'),
    ]

    operations = [
        migrations.CreateModel(
            name='StandardizedIdentificationType',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False,
                                        auto_created=True, primary_key=True)),
                ('name', models.CharField(unique=True, max_length=256)),
                ('slug', models.CharField(unique=True, max_length=5)),
                ('level', models.CharField(
                    max_length=25, choices=[(b'footprint', b'Footprint'),
                                            (b'imprint', b'Imprint'),
                                            (b'writtenwork', b'WrittenWork'),
                                            (b'place', b'Place'),
                                            (b'person', b'Person')])),
            ],
            options={
                'ordering': ['name'],
                'verbose_name': 'Standardized Identification Type',
            },
            bases=(models.Model,),
        ),
        migrations.AddField(
            model_name='standardizedidentification',
            name='new_identifier_type',
            field=models.ForeignKey(blank=True,
                                    to='main.StandardizedIdentificationType',
                                    null=True, on_delete=models.CASCADE),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='writtenwork',
            name='standardized_identifier',
            field=models.ManyToManyField(to='main.StandardizedIdentification',
                                         null=True, blank=True),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='role',
            name='level',
            field=models.CharField(
                max_length=25, choices=[(b'footprint', b'Footprint'),
                                        (b'imprint', b'Imprint'),
                                        (b'writtenwork', b'WrittenWork'),
                                        (b'place', b'Place'),
                                        (b'person', b'Person')]),
            preserve_default=True,
        ),
    ]
