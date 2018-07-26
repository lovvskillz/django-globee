from django.core.exceptions import ValidationError
from django.test import TestCase, override_settings

from globee.core import GlobeePayment


class GlobeeRequiredFieldsTestCase(TestCase):

    def test_required_fields_valid(self):
        data = {
            'total': 13.37,
            'customer': {
                'name': 'foobar',
                'email': 'foobar@example.com'
            },
        }
        globee_payment = GlobeePayment(data=data)
        self.assertTrue(globee_payment.check_required_fields())

    def test_required_fields_invalid_total(self):
        data = {
            'total': 'foobar',
            'customer': {
                'email': 'foobar@example.com'
            },
        }
        globee_payment = GlobeePayment(data=data)
        with self.assertRaises(ValidationError):
            globee_payment.check_required_fields()

    def test_required_fields_invalid_email(self):
        data = {
            'total': 13.37,
            'customer': {
                'email': 'invalid_mail.com'
            },
        }
        globee_payment = GlobeePayment(data=data)
        with self.assertRaises(ValidationError):
            globee_payment.check_required_fields()

    def test_required_fields_invalid_total_not_set(self):
        data = {
            'customer': {
                'email': 'foobar@example.com'
            },
        }
        globee_payment = GlobeePayment(data=data)
        with self.assertRaises(KeyError):
            globee_payment.check_required_fields()

    def test_required_fields_invalid_email_not_set(self):
        data = {
            'total': 13.37,
        }
        globee_payment = GlobeePayment(data=data)
        with self.assertRaises(KeyError):
            globee_payment.check_required_fields()


@override_settings(GLOBEE_AUTH_KEY=True)
class GlobeeCreatePaymentTestCase(TestCase):

    def test_create_payment_valid(self):
        data = {
            'total': 13.37,
            'customer': {
                'name': 'foobar',
                'email': 'foobar@example.com'
            },
        }
        globee_payment = GlobeePayment(data=data)
        self.assertTrue(globee_payment.check_required_fields())
        self.assertTrue(globee_payment.create_request())

    @override_settings(GLOBEE_AUTH_KEY="INVALID_KEY")
    def test_create_payment_invalid_key(self):
        data = {
            'total': 13.37,
            'customer': {
                'name': 'foobar',
                'email': 'foobar@example.com'
            },
        }
        globee_payment = GlobeePayment(data=data)
        self.assertTrue(globee_payment.check_required_fields())
        with self.assertRaises(ValidationError):
            globee_payment.create_request()

    def test_create_payment_invalid_email_not_set(self):
        data = {
            'total': 13.37,
            'customer': {
                'name': 'foobar',
            },
        }
        globee_payment = GlobeePayment(data=data)
        with self.assertRaises(ValidationError):
            globee_payment.create_request()

    def test_create_payment_invalid_urls(self):
        data = {
            'total': 13.37,
            'customer': {
                'email': 'foobar@example.com'
            },
            'success_url': 'invalid-url',
            'cancel_url': 'invalid-url',
            'ipn_url': 'invalid-url',
        }
        globee_payment = GlobeePayment(data=data)
        self.assertTrue(globee_payment.check_required_fields())
        with self.assertRaises(ValidationError):
            globee_payment.create_request()
