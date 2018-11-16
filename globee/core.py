from django.conf import settings
from django.core.exceptions import ValidationError
import requests
from django.core.validators import validate_email


class GlobeePayment:
    """
    Globee Payment
    """
    payment_data = dict()
    payment_id = None
    redirect_url = None
    test_mode = True
    auth_key = None
    api_url = 'https://globee.com/payment-api/v1'
    headers = None

    def __init__(self, payment_data=None, payment_id=None):
        """
        Init Globee payment
        :param payment_data: dict with payment data
        :param payment_id: the payment id that identifies the payment request
        """
        self.payment_data = dict() if payment_data is None else payment_data
        self.payment_id = payment_id
        self.redirect_url = None
        self.testnet = getattr(settings, 'GLOBEE_TEST_MODE', True)

        self.auth_key = getattr(settings, 'GLOBEE_AUTH_KEY', None)

        if self.auth_key is None:
            raise ValidationError('GLOBEE_AUTH_KEY not found!')
        elif not isinstance(self.auth_key, str):
            raise ValidationError('GLOBEE_AUTH_KEY is not a string!')
        elif not self.auth_key:
            raise Validationerror('GLOBEE_AUTH_KEY is empty!')

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
            raise ValidationError('result: %s' % response['result'])
        raise ValidationError("status code %s: %s" % (r.status_code, response['errors']['message']))

    def check_required_fields(self):
        """
        Checks all required fields.
        :return: returns True if required fields are set
        """
        try:
            total = self.payment_data['total']
            email = self.payment_data['customer']['email']
            if not isinstance(total, (int, float)):
                raise ValidationError('total is not a int or float!')
        except KeyError as e:
            raise KeyError("%s not set" % e)
        try:
            validate_email(self.payment_data['customer']['email'])
        except ValidationError as e:
            raise ValidationError(e)
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

    def get_payment_by_id(self, payment_id=None):
        """
        Fetches a previously created payment request by payment_id.
        :param payment_id: the payment id that identifies the payment request
        :return: payment data
        """
        payment_id = self.payment_id if payment_id is None else payment_id
        if payment_id is None:
            raise ValidationError('payment_id is None')
        r = requests.get('%s/payment-request/%s' % (self.api_url, payment_id), headers=self.headers)
        response = r.json()
        if r.status_code == 200 and response['success'] is True:
            return response['data']
        raise ValidationError('status code: %s - %s' % (r.status_code, response))

    def update_payment_request(self, payment_id=None, payment_data=None):
        """
        Updates an existing payment request.
        :param payment_id: the payment id that identifies the payment request
        :param payment_data: dict with payment data
        :return: response data
        """
        payment_id = self.payment_id if payment_id is None else payment_id
        payment_data = self.payment_data if payment_data is None else payment_data
        if payment_id is None:
            raise ValidationError('payment_id is None')
        if payment_data is None:
            raise ValidationError('payment_data is None')
        try:
            email = self.payment_data['customer']['email']
        except KeyError as e:
            raise KeyError("%s not set" % e)
        try:
            validate_email(payment_data['customer']['email'])
        except ValidationError as e:
            raise ValidationError(e)
        r = requests.put('%s/payment-request/%s' % (self.api_url, payment_id), headers=self.headers, json=payment_data)
        response = r.json()
        if r.status_code == 200 and response['success'] is True:
            return response['data']
        raise ValidationError('status code: %s - %s' % (r.status_code, response))

    def get_payment_details(self, payment_id=None):
        """
        Returns the accepted crypto-currencies and associated address information for the payment-request associated with the given id.
        :param payment_id: the payment id that identifies the payment request
        :return: return payment details like accepted crypto-currencies and associated address information
        """
        payment_id = self.payment_id if payment_id is None else payment_id
        if payment_id is None:
            raise ValidationError('payment_id is None')
        r = requests.get('%s/payment-request/%s/payment-methods' % (self.api_url, payment_id), headers=self.headers)
        response = r.json()
        if r.status_code == 200 and response['success'] is True:
            return response['data']
        raise ValidationError('status code: %s - %s' % (r.status_code, response))

    def get_payment_currency_details(self, curreny_id, payment_id=None, address_id=None):
        """
        Generates and returns the payment details for a given payment request and payment currency.
        :param curreny_id: one of the currency id's: BTC, XMR, LTC, DOGE, ETH, XRP etc.
        :param payment_id: the payment id that identifies the payment request
        :param address_id: the address id if it has been assigned. Examples: default, lightning_address
        :return: returns the payment details for a given payment request and payment currency
        """
        payment_id = self.payment_id if payment_id is None else payment_id
        if payment_id is None:
            raise ValidationError('payment_id is None')
        url = '%s/payment-request/%s/addresses/%s' % (self.api_url, payment_id, curreny_id)
        if address_id is not None:
            url = '%s/%s' % (url, address_id)
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
