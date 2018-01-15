from django.test import TestCase

from apps.core import forms


class DepositTransactionModelFormTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.form = forms.DepositTransactionModelForm
        cls.valid_form = cls.form(
            data={
                'ripple_address': 'rp2PaYDxVwDvaZVLEQv7bHhoFQEyX1mEx7',
                'dash_to_transfer': 1,
            },
        )

    def test_form_without_data(self):
        self.assertFalse(self.form(data={}).is_valid())

    def test_form_with_invalid_ripple_address(self):
        form = self.form(data={'ripple_address': 'Invalid address'})
        self.assertFalse(form.is_valid())
        self.assertIn('ripple_address', form.errors)
        self.assertIn(
            'The Ripple address is not valid.',
            form.errors['ripple_address'],
        )

    def test_form_with_valid_ripple_address(self):
        self.assertTrue(self.valid_form.is_valid())
