# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.contrib.auth.models import User
from django.db import models


class MapLayerCollection(models.Model):
    author = models.ForeignKey(User, null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    modified_at = models.DateTimeField(auto_now=True)


class MapLayer(models.Model):
    title = models.TextField()
    collection = models.ForeignKey(MapLayerCollection)
