from django.conf import settings
from django.core.exceptions import ValidationError
import requests
from django.core.validators import validate_email


class GlobeePayment:

    data = dict()
    redirect_url = None
    test_mode = True
    auth_key = None
    api_url = 'https://globee.com/payment-api/v1'
    headers = None

    def __init__(self, data={}):
        self.data = data
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
        r = requests.get('%s/ping' % self.api_url, headers=self.headers, json=self.data)
        response = r.json()
        if r.status_code == 200:
            if response['success']:
                return response
            raise ValidationError('result: %s' % response['result'])
        raise ValidationError("status code %s: %s" % (r.status_code, response['message']))

    def check_required_fields(self):
        try:
            total = self.data['total']
            if not isinstance(total, (int, float)):
                raise ValidationError('total is not a int or float!')
        except KeyError as e:
            raise KeyError(e)
        try:
            validate_email(self.data['customer']['email'])
        except ValidationError as e:
            raise ValidationError(e)
        return True

    def create_request(self):
        r = requests.post('%s/payment-request' % self.api_url, headers=self.headers, json=self.data)
        response = r.json()
        if r.status_code == 200:
            self.redirect_url = response['data']['redirect_url']
            return True
        raise ValidationError('status code: %s - %s' % (r.status_code, response))

    def get_payment_url(self):
        return self.redirect_url

    def get_payment_by_id(self, payment_id):
        r = requests.get('%s/payment-request/%s' % (self.api_url, payment_id), headers=self.headers, json=self.data)
        response = r.json()
        if r.status_code == 200:
            return response['data']
        raise ValidationError('status code: %s - %s' % (r.status_code, response))
