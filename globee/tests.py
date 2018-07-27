import json

from django.core.exceptions import ValidationError
from django.test import TestCase, override_settings, Client
from django.urls import reverse

from globee.core import GlobeePayment
from globee.models import GlobeeIPN


class GlobeePingTestCase(TestCase):

    def test_ping_valid(self):
        globee_payment = GlobeePayment()
        self.assertTrue(globee_payment.ping())

    @override_settings(GLOBEE_AUTH_KEY="INVALID_KEY")
    def test_ping_invalid_key(self):
        globee_payment = GlobeePayment()
        with self.assertRaises(ValidationError):
            globee_payment.ping()


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


@override_settings(GLOBEE_TEST_MODE=True)
class GlobeeCreatePaymentTestCase(TestCase):

    def test_create_payment_valid(self):
        data = {
            'total': 13.37,
            'currency': 'EUR',
            'customer': {
                'name': 'foobar',
                'email': 'foobar@example.com'
            },
        }
        globee_payment = GlobeePayment(data=data)
        self.assertTrue(globee_payment.check_required_fields())
        self.assertTrue(globee_payment.create_request())

    def test_create_payment_invalid_empty_data(self):
        globee_payment = GlobeePayment()
        with self.assertRaises(KeyError):
            globee_payment.check_required_fields()
        with self.assertRaises(ValidationError):
            globee_payment.create_request()

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


@override_settings(GLOBEE_TEST_MODE=True)
class GlobeeCreatePaymentObjectTestCase(TestCase):

    def setUp(self):
        GlobeeIPN.objects.all().delete()
        self.assertEqual(0, GlobeeIPN.objects.count())

    @override_settings(ROOT_URLCONF='globee.urls')
    def test_ipn_view_valid(self):
        count_before = 0
        self.assertEqual(count_before, GlobeeIPN.objects.all().count())
        payment_data = {
            "id": "a1B2c3D4e5F6g7H8i9J0kL",
            "status": "paid",
            "total": "123.45",
            "currency": "USD",
            "custom_payment_id": "742",
            "callback_data": "example data",
            "customer": {
                "name": "John Smit",
                "email": "john.smit@example.com"
            },
            "redirect_url": "http:\/\/globee.com\/invoice\/a1B2c3D4e5F6g7H8i9J0kL",
            "success_url": "https:\/\/www.example.com/success",
            "cancel_url": "https:\/\/www.example.com/cancel",
            "ipn_url": "https:\/\/www.example.com/globee/ipn-callback",
            "notification_email": None,
            "confirmation_speed": "medium",
            "expires_at": "2018-01-25 12:31:04",
            "created_at": "2018-01-25 12:16:04"
        }
        client = Client()
        client.generic('POST', reverse('globee-ipn'), bytes(json.dumps(payment_data), 'utf-8'))
        self.assertEqual(count_before + 1, GlobeeIPN.objects.all().count())
