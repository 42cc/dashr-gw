# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models
from django.utils.translation import ugettext as _


class Page(models.Model):
    slug = models.SlugField(max_length=300, db_index=True, unique=True)
    title = models.CharField(verbose_name=_("Title"), max_length=200)
    description = models.TextField(verbose_name=_("Description"), blank=True)

    class Meta:
        ordering = ('-title', )

    def __str__(self):
        return self.title
