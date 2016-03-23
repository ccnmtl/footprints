# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from django.conf import settings
from django.db import migrations


def migrate_urls(apps, schema_editor):
    # We can't import the Person model directly as it may be a newer
    # version than this migration expects. We use the historical version.
    DigitalObject = apps.get_model("main", "DigitalObject")
    for do in DigitalObject.objects.all():
        do.url = '{}{}'.format(settings.MEDIA_URL, do.file)
        do.save()


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0021_digitalobject_url'),
    ]

    operations = [
        migrations.RunPython(migrate_urls),
    ]
