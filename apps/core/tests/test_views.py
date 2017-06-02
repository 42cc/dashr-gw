from __future__ import unicode_literals

import json

from django.core.urlresolvers import reverse
from django.test import TestCase
from django.test.client import Client

from apps.core.models import Page


class GetPageDetailsViewTest(TestCase):
    """ Tests for GetPageDetailsView view """

    def setUp(self):
        self.client = Client()
        self.page = Page.objects.create(title='test', slug='test')

    def test_getting_page_by_slug_valid(self):
        """ Test getting page by valid slug """

        response = self.client.get(
            reverse('page', kwargs={'slug': self.page.slug}),
            HTTP_X_REQUESTED_WITH='XMLHttpRequest'
        )

        content = json.loads(response.content)
        self.assertEqual(response.status_code, 200)
        self.assertIn('success', content)
        self.assertIn('page', content)
        self.assertTrue(content['success'])
        self.assertEqual(content['page']['id'], self.page.pk)
        self.assertEqual(content['page']['slug'], self.page.slug)
        self.assertEqual(content['page']['title'], self.page.title)

    def test_getting_page_by_slug_invalid(self):
        """ Test getting page by invalid slug """

        response = self.client.get(
            reverse('page', kwargs={'slug': 'invalid'}),
            HTTP_X_REQUESTED_WITH='XMLHttpRequest'
        )

        content = json.loads(response.content)
        self.assertEqual(response.status_code, 200)
        self.assertIn('success', content)
        self.assertIn('page', content)
        self.assertIn('message', content)
        self.assertFalse(content['success'])
        self.assertEqual(content['message'], 'Page does not exists')
        self.assertEqual(len(content['page']), 0)

    def test_get_page_non_ajax(self):
        """ Test getting page by valid slug """

        response = self.client.get(
            reverse('page', kwargs={'slug': self.page.slug}),
        )
        redirected_url = '{0}?next=/{1}/'.format(
            reverse('index'), self.page.slug)

        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, redirected_url)
