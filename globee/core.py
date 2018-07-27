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

    def check_required_fields(self):
        try:
            total = self.data['total']
            email = self.data['customer']['email']
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
        if r.status_code in [401, 404, 500]:
            raise ValidationError("status code %s: %s" % (r.status_code, response['message']))
        if not r.status_code == 422:
            self.redirect_url = response['data']['redirect_url']
            return True
        raise ValidationError(response)

    def get_payment_url(self):
        return self.redirect_url


