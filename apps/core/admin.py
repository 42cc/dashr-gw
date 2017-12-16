# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from ckeditor.widgets import CKEditorWidget
from solo.admin import SingletonModelAdmin

from django import forms
from django.contrib import admin

from .models import Page, RippleWalletCredentials


class RippleWalletAdminForm(forms.ModelForm):
    secret = forms.CharField(widget=forms.PasswordInput)

    class Meta:
        model = RippleWalletCredentials
        fields = '__all__'


@admin.register(RippleWalletCredentials)
class RippleWalletAdmin(SingletonModelAdmin):
    form = RippleWalletAdminForm


class PageAdminForm(forms.ModelForm):
    description = forms.CharField(widget=CKEditorWidget())

    class Meta:
        model = Page
        fields = '__all__'


class PageAdmin(admin.ModelAdmin):
    form = PageAdminForm


admin.site.register(Page, PageAdmin)
