# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.views.generic.base import TemplateView, View
from django.http import JsonResponse
from django.core import serializers
from .models import Page


class IndexView(TemplateView):
    """
    Index page view
    """
    template_name = 'core/index.html'


class GetPageDetailsView(View):
    """
    View returns given by url serialized page instance
    """
    def get(self, request, slug):
        ctx = {'page': [], 'success': True}
        pages = Page.objects.filter(slug=slug)

        if not pages.exists():
            ctx['success'] = False
            ctx['message'] = 'Page does not exists'
        else:
            ctx['page'] = serializers.serialize('json', pages)

        return JsonResponse(ctx, safe=False)
