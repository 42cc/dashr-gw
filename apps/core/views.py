# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.forms.models import model_to_dict
from django.views.generic.base import TemplateView, View
from django.http import JsonResponse
from django.shortcuts import render

from .models import Page


class IndexView(TemplateView):
    """
    Index page view
    """
    template_name = 'base.html'


class GetPageDetailsView(View):
    """
    View returns given by url serialized page instance
    """
    def get(self, request, slug):
        if request.is_ajax():
            ctx = {'page': [], 'success': True}
            page = Page.objects.filter(slug=slug)

            if not page.exists():
                ctx['success'] = False
                ctx['message'] = 'Page does not exists'
            else:
                ctx['page'] = model_to_dict(page[0])

            return JsonResponse(ctx, safe=False)
        return render(request, 'base.html')
