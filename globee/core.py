from django.conf import settings
from django.core.exceptions import ValidationError
import requests
from django.core.validators import validate_email


class GlobeePayment:
    """
    Globee Payment
    """
    payment_data = dict()
    redirect_url = None
    test_mode = True
    auth_key = None
    api_url = 'https://globee.com/payment-api/v1'
    headers = None

    def __init__(self, payment_data=None):
        """
        Init Globee payment
        :param payment_data: dict with payment data
        """
        self.payment_data = dict() if payment_data is None else payment_data
        self.test_mode = getattr(settings, 'GLOBEE_TEST_MODE', True)
        self.auth_key = getattr(settings, 'GLOBEE_AUTH_KEY', None)
        if self.auth_key is None:
            raise ValidationError('GLOBEE_AUTH_KEY not found!')
        if not isinstance(self.auth_key, str):
            raise ValidationError('GLOBEE_AUTH_KEY is not a string!')
        if self.test_mode:
            self.api_url = 'https://test.globee.com/payment-api/v1'
        self.headers = {
            'Accept': 'application/json',
            'X-AUTH-KEY': self.auth_key
        }

    def ping(self):
        """
        sends a ping to verify that the integration and authentication is done correctly
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
        checks all required fields
        :return: returns True if required fields are set
        """
        try:
            total = self.payment_data['total']
            if not isinstance(total, (int, float)):
                raise ValidationError('total is not a int or float!')
        except KeyError as e:
            raise KeyError(e)
        try:
            validate_email(self.payment_data['customer']['email'])
        except ValidationError as e:
            raise ValidationError(e)
        return True

    def create_request(self):
        """
        creates a new payment request
        :return: payment url
        """
        r = requests.post('%s/payment-request' % self.api_url, headers=self.headers, json=self.payment_data)
        response = r.json()
        if r.status_code == 200:
            self.redirect_url = response['data']['redirect_url']
            return response['data']['redirect_url']
        raise ValidationError('status code: %s - %s' % (r.status_code, response))

    def get_payment_url(self):
        """
        gets the payment url
        :return: payment url
        """
        return self.redirect_url

    def get_payment_by_id(self, payment_id):
        """
        fetches a previously created payment request by payment_id.
        :param payment_id:
        :return: payment data
        """
        r = requests.get('%s/payment-request/%s' % (self.api_url, payment_id), headers=self.headers)
        response = r.json()
        if r.status_code == 200:
            return response['data']
        raise ValidationError('status code: %s - %s' % (r.status_code, response))
