# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.test import TestCase
from django.db import IntegrityError

from apps.core.models import Page


class PageModelTest(TestCase):
    """ Tests for page model """

    def test_page_creation_valid(self):
        """ Test successfull page creation """
        count_before = Page.objects.count()
        Page.objects.create(
            slug='test',
            title='test title',
            description='lorem ipsum',
        )
        self.assertEquals(Page.objects.count(), count_before + 1)

    def test_page_creation_invalid(self):
        """ Test page creation with invalid args """
        Page.objects.create(slug='test', title='test page')

        with self.assertRaises(IntegrityError) as context:
            Page.objects.create(slug='test', title='duplicate page')

            error_msg = context.exception.message
            self.assertContains('core_page_slug_key', error_msg)
            self.assertContains(
                'duplicate key value violates unique constraint', error_msg
            )
