from django.utils import timezone
from django.core.exceptions import ValidationError
from django.test import TestCase, override_settings
from django.utils.dateparse import parse_datetime

from globee.core import GlobeePayment
from globee.models import GlobeeIPN


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

    def test_create_payment_object_valid(self):
        payment_data = {
            "id": "a1B2c3D4e5F6g7H8i9J0kL",
            "status": "paid",
            "total": float("123.45"),
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
        created_at = parse_datetime(payment_data['created_at'])
        expires_at = parse_datetime(payment_data['expires_at'])
        defaults = {
            'payment_status': payment_data['status'],
            'total': payment_data['total'],
            'currency': payment_data['currency'],
            'custom_payment_id': payment_data['custom_payment_id'],
            'callback_data': payment_data['callback_data'],
            'customer_email': payment_data['customer']['email'],
            'customer_name': payment_data['customer']['name'],
            'created_at': timezone.datetime(created_at.year, created_at.month, created_at.day, created_at.hour, created_at.minute, created_at.second),
            'expires_at': timezone.datetime(expires_at.year, expires_at.month, expires_at.day, expires_at.hour, expires_at.minute, expires_at.second),
        }
        count_before = 0
        self.assertEqual(count_before, GlobeeIPN.objects.all().count())
        payment, created = GlobeeIPN.objects.get_or_create(payment_id=payment_data['id'], defaults=defaults)
        payment.status = payment_data['status']
        payment.save()
        self.assertEqual(count_before + 1, GlobeeIPN.objects.all().count())
