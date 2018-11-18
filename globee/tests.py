import json

from django.core.exceptions import ValidationError
from django.test import TestCase, override_settings, Client
from django.urls import reverse

from globee.core import GlobeePayment
from globee.models import GlobeeIPN


class GlobeeInitTestCase(TestCase):

    def test_init_valid(self):
        globee_payment = GlobeePayment()
        self.assertTrue(globee_payment.ping())

    @override_settings(GLOBEE_AUTH_KEY=None)
    def test_init_invalid_key_is_none(self):
        with self.assertRaises(ValidationError):
            globee_payment = GlobeePayment()

    @override_settings(GLOBEE_AUTH_KEY=1)
    def test_init_invalid_key_isnt_a_string(self):
        with self.assertRaises(ValidationError):
            globee_payment = GlobeePayment()

    @override_settings(GLOBEE_AUTH_KEY="")
    def test_init_invalid_key_is_empty(self):
        with self.assertRaises(ValidationError):
            globee_payment = GlobeePayment()


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
        globee_payment = GlobeePayment(payment_data=data)
        self.assertTrue(globee_payment.check_required_fields())

    def test_required_fields_invalid_total(self):
        data = {
            'total': 'foobar',
            'customer': {
                'email': 'foobar@example.com'
            },
        }
        globee_payment = GlobeePayment(payment_data=data)
        with self.assertRaises(ValidationError):
            globee_payment.check_required_fields()

    def test_required_fields_invalid_email(self):
        data = {
            'total': 13.37,
            'customer': {
                'email': 'invalid_mail.com'
            },
        }
        globee_payment = GlobeePayment(payment_data=data)
        with self.assertRaises(ValidationError):
            globee_payment.check_required_fields()

    def test_required_fields_invalid_total_not_set(self):
        data = {
            'customer': {
                'email': 'foobar@example.com'
            },
        }
        globee_payment = GlobeePayment(payment_data=data)
        with self.assertRaises(KeyError):
            globee_payment.check_required_fields()

    def test_required_fields_invalid_email_not_set(self):
        data = {
            'total': 13.37,
        }
        globee_payment = GlobeePayment(payment_data=data)
        with self.assertRaises(KeyError):
            globee_payment.check_required_fields()


@override_settings(GLOBEE_TESTNET=True)
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
        globee_payment = GlobeePayment(payment_data=data)
        self.assertTrue(globee_payment.check_required_fields())
        self.assertIn("https://test.globee.com/", globee_payment.create_request())
        self.assertIn("https://test.globee.com/", globee_payment.get_payment_url())

    def test_get_payment_valid(self):
        data = {
            'total': 13.37,
            'currency': 'EUR',
            'customer': {
                'name': 'foobar',
                'email': 'foobar@example.com'
            },
        }
        globee_payment = GlobeePayment(payment_data=data)
        self.assertTrue(globee_payment.check_required_fields())
        self.assertIn("https://test.globee.com/", globee_payment.create_request())
        self.assertIsInstance(globee_payment.get_payment_by_id(globee_payment.payment_id), dict)

    def test_get_payment_invalid(self):
        globee_payment = GlobeePayment()
        with self.assertRaises(ValidationError):
            globee_payment.get_payment_by_id("INVALID_KEY")

    def test_get_payment_invalid_empty_key(self):
        globee_payment = GlobeePayment()
        with self.assertRaises(ValidationError):
            globee_payment.get_payment_by_id()

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
        globee_payment = GlobeePayment(payment_data=data)
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
        globee_payment = GlobeePayment(payment_data=data)
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
        globee_payment = GlobeePayment(payment_data=data)
        self.assertTrue(globee_payment.check_required_fields())
        with self.assertRaises(ValidationError):
            globee_payment.create_request()


@override_settings(GLOBEE_TESTNET=True)
class GlobeePaymentIPNTestCase(TestCase):

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
        response = client.generic('POST', reverse('globee-ipn'), bytes(json.dumps(payment_data), 'utf-8'))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(count_before + 1, GlobeeIPN.objects.all().count())

    @override_settings(ROOT_URLCONF='globee.urls')
    def test_ipn_view_invalid_payment_id_not_provided(self):
        count_before = 0
        self.assertEqual(count_before, GlobeeIPN.objects.all().count())
        payment_data = {
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
        response = client.generic('POST', reverse('globee-ipn'), bytes(json.dumps(payment_data), 'utf-8'))
        self.assertEqual(response.status_code, 400)
        self.assertEqual(count_before, GlobeeIPN.objects.all().count())

    @override_settings(ROOT_URLCONF='globee.urls')
    def test_ipn_view_invalid_key_error(self):
        count_before = 0
        self.assertEqual(count_before, GlobeeIPN.objects.all().count())
        payment_data = {
            "id": "a1B2c3D4e5F6g7H8i9J0kL",
        }
        client = Client()
        response = client.generic('POST', reverse('globee-ipn'), bytes(json.dumps(payment_data), 'utf-8'))
        self.assertEqual(response.status_code, 400)
        self.assertEqual(count_before, GlobeeIPN.objects.all().count())

    @override_settings(ROOT_URLCONF='globee.urls')
    def test_ipn_view_invalid_total(self):
        count_before = 0
        self.assertEqual(count_before, GlobeeIPN.objects.all().count())
        payment_data = {
            "id": "a1B2c3D4e5F6g7H8i9J0kL",
            "status": "paid",
            "total": "ERROR",
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
        response = client.generic('POST', reverse('globee-ipn'), bytes(json.dumps(payment_data), 'utf-8'))
        self.assertEqual(response.status_code, 400)
        self.assertEqual(count_before, GlobeeIPN.objects.all().count())


@override_settings(GLOBEE_TESTNET=True)
class GlobeeUpdatePaymentTestCase(TestCase):

    def test_update_payment_valid(self):
        data = {
            'total': 13.37,
            'currency': 'EUR',
            'customer': {
                'name': 'foobar',
                'email': 'foobar@example.com'
            },
        }
        globee_payment = GlobeePayment(payment_data=data)
        self.assertTrue(globee_payment.check_required_fields())
        self.assertIn("https://test.globee.com/", globee_payment.create_request())
        custom_payment_id = "NEWID"
        custom_store_reference = "NEWSTOREREF"
        updated_data = {
            "custom_payment_id": custom_payment_id,
            "custom_store_reference": custom_store_reference,
            'customer': {
                'email': 'foobar@example.com'
            },
        }
        globee_payment.payment_data = updated_data
        response = globee_payment.update_payment_request()
        self.assertEqual(response['id'], globee_payment.payment_id)
        self.assertEqual(response['custom_payment_id'], custom_payment_id)
        self.assertEqual(response['custom_store_reference'], custom_store_reference)

    def test_update_payment_invalid_email_not_set(self):
        data = {
            'total': 13.37,
            'currency': 'EUR',
            'customer': {
                'name': 'foobar',
                'email': 'foobar@example.com'
            },
        }
        globee_payment = GlobeePayment(payment_data=data)
        self.assertTrue(globee_payment.check_required_fields())
        self.assertIn("https://test.globee.com/", globee_payment.create_request())
        custom_payment_id = "NEWID"
        custom_store_reference = "NEWSTOREREF"
        updated_data = {
            "custom_payment_id": custom_payment_id,
            "custom_store_reference": custom_store_reference,
        }
        globee_payment.payment_data = updated_data
        with self.assertRaises(KeyError):
            globee_payment.update_payment_request()

    def test_update_payment_invalid_payment_id_is_none(self):
        globee_payment = GlobeePayment()
        custom_payment_id = "NEWID"
        custom_store_reference = "NEWSTOREREF"
        updated_data = {
            "custom_payment_id": custom_payment_id,
            "custom_store_reference": custom_store_reference,
        }
        globee_payment.payment_data = updated_data
        globee_payment.payment_id = None
        with self.assertRaises(ValidationError):
            globee_payment.update_payment_request()

    def test_update_payment_invalid_payment_data_is_none(self):
        globee_payment = GlobeePayment()
        globee_payment.payment_data = None
        globee_payment.payment_id = "SOME KEY"
        with self.assertRaises(ValidationError):
            globee_payment.update_payment_request()

    def test_update_payment_invalid_payment_id(self):
        globee_payment = GlobeePayment()
        custom_payment_id = "NEWID"
        custom_store_reference = "NEWSTOREREF"
        updated_data = {
            "custom_payment_id": custom_payment_id,
            "custom_store_reference": custom_store_reference,
            'customer': {
                'email': 'foobar@example.com'
            },
        }
        globee_payment.payment_data = updated_data
        with self.assertRaises(ValidationError):
            globee_payment.update_payment_request("INVALID_KEY")


@override_settings(GLOBEE_TESTNET=True)
class GlobeeAcceptedPaymentMethodsTestCase(TestCase):

    def test_get_payment_methods_valid(self):
        globee_payment = GlobeePayment()
        response = globee_payment.get_payment_methods()
        self.assertIsInstance(response, list)

    @override_settings(GLOBEE_AUTH_KEY="INVALID_KEY")
    def test_get_payment_methods_invalid(self):
        globee_payment = GlobeePayment()
        with self.assertRaises(ValidationError):
            globee_payment.get_payment_methods()


@override_settings(GLOBEE_TESTNET=True)
class GlobeePaymentDetailsTestCase(TestCase):

    def test_get_payment_details_valid(self):
        data = {
            'total': 13.37,
            'currency': 'EUR',
            'customer': {
                'name': 'foobar',
                'email': 'foobar@example.com'
            },
        }
        globee_payment = GlobeePayment(payment_data=data)
        self.assertTrue(globee_payment.check_required_fields())
        self.assertIn("https://test.globee.com/", globee_payment.create_request())
        response = globee_payment.get_payment_details()
        self.assertIsInstance(response, list)

    def test_get_payment_details_for_currency_valid(self):
        data = {
            'total': 13.37,
            'currency': 'EUR',
            'customer': {
                'name': 'foobar',
                'email': 'foobar@example.com'
            },
        }
        globee_payment = GlobeePayment(payment_data=data)
        self.assertTrue(globee_payment.check_required_fields())
        self.assertIn("https://test.globee.com/", globee_payment.create_request())
        response = globee_payment.get_payment_currency_details("BTC")
        self.assertIsInstance(response, dict)

    def test_get_payment_details_invalid_payment_id_is_none(self):
        globee_payment = GlobeePayment()
        with self.assertRaises(ValidationError):
            globee_payment.get_payment_details()

    def test_get_payment_details_invalid_payment_id_is_invalid(self):
        globee_payment = GlobeePayment()
        with self.assertRaises(ValidationError):
            globee_payment.get_payment_details("INVALID_KEY")

    def test_get_payment_details_for_currency_invalid_payment_id_is_none(self):
        globee_payment = GlobeePayment()
        with self.assertRaises(ValidationError):
            globee_payment.get_payment_currency_details("BTC")

    def test_get_payment_details_for_currency_invalid_payment_id_is_invalid(self):
        globee_payment = GlobeePayment()
        with self.assertRaises(ValidationError):
            globee_payment.get_payment_currency_details("BTC", "INVALID_KEY")
