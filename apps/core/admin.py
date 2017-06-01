# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from ckeditor.widgets import CKEditorWidget

from django import forms
from django.contrib import admin

from apps.core.models import Page


class PageAdminForm(forms.ModelForm):
    description = forms.CharField(widget=CKEditorWidget())

    class Meta:
        model = Page
        fields = '__all__'


class PageAdmin(admin.ModelAdmin):
    form = PageAdminForm


admin.site.register(Page, PageAdmin)
