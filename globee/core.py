import requests

from django.conf import settings
from django.core.exceptions import ValidationError
from django.core.validators import validate_email


class GlobeePayment:
    """
    Globee Payment
    """

    def __init__(self, payment_data: dict = None, payment_id: str = None):
        """
        Init Globee payment
        :param payment_data: dict with payment data
        :param payment_id: the payment id that identifies the payment request
        """
        self.payment_data = payment_data or dict()
        self.payment_id = payment_id
        self.redirect_url = None

        self.auth_key = getattr(settings, 'GLOBEE_AUTH_KEY', None)

        if self.auth_key is None:
            raise ValidationError('GLOBEE_AUTH_KEY not found!')
        elif not isinstance(self.auth_key, str):
            raise ValidationError('GLOBEE_AUTH_KEY is not a string!')
        elif not self.auth_key:
            raise ValidationError('GLOBEE_AUTH_KEY is empty!')

        self.testnet = getattr(settings, 'GLOBEE_TESTNET', True)
        self.api_url = 'https://%sglobee.com/payment-api/v1' % ('test.' if self.testnet else '')

        self.headers = {
            'Accept': 'application/json',
            'X-AUTH-KEY': self.auth_key
        }

    def ping(self):
        """
        Sends a ping to verify that the integration and authentication is done correctly.
        :return: response with the merchant name and url
        """
        r = requests.get('%s/ping' % self.api_url, headers=self.headers)
        response = r.json()
        if r.status_code == 200:
            if response['success']:
                return response
        raise ValidationError("status code %s: %s" % (r.status_code, response['message']))

    def check_required_fields(self):
        """
        Checks all required fields.
        :return: returns True if required fields are set
        """
        try:
            total = self.payment_data['total']
            email = self.payment_data['customer']['email']
            if not isinstance(total, (int, float)):
                raise ValidationError('total is not an int, nor float!')
        except KeyError as e:
            raise ValidationError("key %s not set" % e)

        validate_email(email)
        return True

    def create_request(self):
        """
        Creates a new payment request.
        :return: payment url
        """
        r = requests.post('%s/payment-request' % self.api_url, headers=self.headers, json=self.payment_data)
        response = r.json()
        if r.status_code == 200 and response['success'] is True:
            self.redirect_url = response['data']['redirect_url']
            self.payment_id = response['data']['id']
            return response['data']['redirect_url']
        raise ValidationError('status code: %s - %s' % (r.status_code, response))

    def get_payment_url(self):
        """
        gets the payment url
        :return: payment url
        """
        return self.redirect_url

    def get_payment_by_id(self, payment_id: str = None):
        """
        Fetches a previously created payment request by payment_id.
        :param payment_id: the payment id that identifies the payment request
        :return: payment data
        """
        payment_id = payment_id or self.payment_id
        if not payment_id:
            raise ValidationError('payment_id is None/empty')

        r = requests.get('%s/payment-request/%s' % (self.api_url, payment_id), headers=self.headers)
        response = r.json()
        if r.status_code == 200 and response['success'] is True:
            return response['data']
        raise ValidationError('status code: %s - %s' % (r.status_code, response))

    def update_payment_request(self, payment_id: str = None, payment_data: dict = None):
        """
        Updates an existing payment request.
        :param payment_id: the payment id that identifies the payment request
        :param payment_data: dict with payment data
        :return: response data
        """
        payment_id = payment_id or self.payment_id
        payment_data = payment_data or self.payment_data

        if not payment_id:
            raise ValidationError('payment_id is None/empty')
        elif not payment_data:
            raise ValidationError('payment_data is None/empty')

        try:
            email = self.payment_data['customer']['email']
        except KeyError as e:
            raise KeyError("%s not set" % e)

        validate_email(payment_data['customer']['email'])

        r = requests.put('%s/payment-request/%s' % (self.api_url, payment_id), headers=self.headers, json=payment_data)
        response = r.json()
        if r.status_code == 200 and response['success'] is True:
            return response['data']
        raise ValidationError('status code: %s - %s' % (r.status_code, response))

    def get_payment_details(self, payment_id: str = None):
        """
        Returns the accepted crypto-currencies and associated address information for the payment-request associated with the given id.
        :param payment_id: the payment id that identifies the payment request
        :return: return payment details like accepted crypto-currencies and associated address information
        """
        payment_id = payment_id or self.payment_id
        if not payment_id:
            raise ValidationError('payment_id is None/empty')

        r = requests.get('%s/payment-request/%s/payment-methods' % (self.api_url, payment_id), headers=self.headers)
        response = r.json()
        if r.status_code == 200 and response['success'] is True:
            return response['data']
        raise ValidationError('status code: %s - %s' % (r.status_code, response))

    def get_payment_currency_details(self, currency_id: str, payment_id: str = None, address_id: str = None):
        """
        Generates and returns the payment details for a given payment request and payment currency.
        :param currency_id: one of the currency id's: BTC, XMR, LTC, DOGE, ETH, XRP etc.
        :param payment_id: the payment id that identifies the payment request
        :param address_id: the address id if it has been assigned. Examples: default, lightning_address
        :return: returns the payment details for a given payment request and payment currency
        """
        payment_id = payment_id or self.payment_id
        if not payment_id:
            raise ValidationError('payment_id is None/empty')

        url = '%s/payment-request/%s/addresses/%s' % (self.api_url, payment_id, currency_id)
        if address_id:
            url += '/%s' % address_id

        r = requests.get(url, headers=self.headers)
        response = r.json()
        if r.status_code == 200 and response['success'] is True:
            return response['data']
        raise ValidationError('status code: %s - %s' % (r.status_code, response))

    def get_payment_methods(self):
        """
        This returns the merchant account's accepted crypto-currencies.
        :return: returns accepted crypto-currencies
        """
        r = requests.get('%s/account/payment-methods' % self.api_url, headers=self.headers)
        response = r.json()
        if r.status_code == 200 and response['success'] is True:
            return response['data']
        raise ValidationError('status code: %s - %s' % (r.status_code, response))

