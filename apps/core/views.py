# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.shortcuts import render
from django.views.generic.base import TemplateView


class IndexView(TemplateView):
    """
    Index page view
    """
    template_name = 'core/index.html'