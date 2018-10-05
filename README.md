# django-globee

[![GitHub license](https://img.shields.io/badge/license-MIT-brightgreen.svg)](https://raw.githubusercontent.com/lovvskillz/django-globee/master/LICENSE)
[![PyPI version](https://badge.fury.io/py/django-globee.svg)](https://badge.fury.io/py/django-globee)

django-globee is a Django app to integrate [GloBee](https://globee.com/) Payments.

You can find the GloBee API docs [here](https://globee.com/docs/payment-api/v1).

Quick start
-----------

1. Add "globee" to your INSTALLED_APPS setting like this:
```python
    INSTALLED_APPS = [
        ...
        'globee',
    ]
```
2. Include the globee URLconf in your project urls.py like this:
```python
    path('globee/', include('globee.urls')),
```
    
3. Include your globee key and test or live env in your project settings.py
```python
    GLOBEE_AUTH_KEY = "YOUR GLOBEE X-AUTH-KEY"
    GLOBEE_TEST_MODE = True # or False
```


4. Run `python manage.py migrate` to create the globee models.


## example

### ping
```python
from globee.core import GlobeePayment

def ping():
    payment = GlobeePayment()
    response = payment.ping()
    # response contains merchant name and url
    print(response)
```

### create GloBee payment

```python
from random import randint
from django.http import HttpResponseRedirect
from django.urls.base import reverse
from globee.core import GlobeePayment

def my_payment_view(request):
    custom_payment_id = 'your-custom-payment-id-%s' % randint(1, 9999999)
    payment_data = {
        'total': 10.50, # total is required
        'currency': 'USD',
        'custom_payment_id': custom_payment_id,
        'customer': {
            'name': request.user.username,
            'email': request.user.email # email is required
        },
        'success_url': request.build_absolute_uri(reverse('your-success-url')),
        'cancel_url': request.build_absolute_uri(reverse('your-cancel-url')),
        'ipn_url': request.build_absolute_uri(reverse('globee-ipn')),
    }
    payment = GlobeePayment(payment_data=payment_data)
    # check required fields for globee payments
    if payment.check_required_fields():
        # create payment request
        redirect_url = payment.create_request()
        # redirect to globee payment page
        return HttpResponseRedirect(redirect_url)
```

### get GloBee ipn signal

```python
from django.dispatch import receiver
from globee.models import PAYMENT_STATUS_GLOBEE_CONFIRMED
from globee.signals import globee_valid_ipn

@receiver(globee_valid_ipn)
def crypto_payment_ipn(sender, **kwargs):
    payment = sender
    
    # check if payment is confirmed or use any other payment status
    if payment.payment_status == PAYMENT_STATUS_GLOBEE_CONFIRMED:
        # get some payment infos
        amount = payment.total # payment amount
        currency = payment.currency # payment currency
        payment_id = payment.payment_id # payment id from GloBee
        custom_payment_id = payment.custom_payment_id # your custom payment id
        customer_email = payment.customer_email # customer email
        
        # Do more stuff
        # ...
        
```

if you don't trust the ipn response, you can also get the payment data from GloBee

```python
from django.dispatch import receiver
from django.core.exceptions import ValidationError
from globee.models import PAYMENT_STATUS_GLOBEE_CONFIRMED
from globee.signals import globee_valid_ipn
from globee.core import GlobeePayment

@receiver(globee_valid_ipn)
def crypto_payment_ipn(sender, **kwargs):
    payment = sender
    globee_payment = GlobeePayment()
    # OR set payment id in init
    # globee_payment = GlobeePayment(payment_id=payment.payment_id)
    
    try:
        # get the payment data from globee
        payment_data = globee_payment.get_payment_by_id(payment.payment_id)
        # you don't need to set the payment id if you have already set the payment id in GlobeePayment init
        # payment_data = globee_payment.get_payment_by_id()
        
        # check if payment is confirmed or use any other payment status
        if payment_data['status'] == PAYMENT_STATUS_GLOBEE_CONFIRMED:
            # get some payment infos
            amount = float(payment_data['total']) # payment amount
            currency = payment_data['currency'] # payment currency
            payment_id = payment_data['payment_id'] # payment id from GloBee
            custom_payment_id = payment_data['custom_payment_id'] # your custom payment id
            customer_email = payment_data['customer']['email'] # customer email
            
            # Do more stuff
            # ...
    except ValidationError as e:
        # payment not found or other error
        print(e)
```

### update an existing payment
```python
from random import randint
from django.core.exceptions import ValidationError
from globee.core import GlobeePayment

def update_payment():
    new_payment_id = 'your-new-custom-payment-id-%s' % randint(1, 9999999)
    # dict with updated values for payment request
    data = {
        "custom_payment_id": new_payment_id,
        "custom_store_reference": "abc",
        "callback_data": "example data",
        "customer": {
            "name": "John Smit",
            "email": "john.smit@hotmail.com" # email is required
        },
    }
    globee_payment = GlobeePayment(payment_id="PAYMENT_ID", payment_data=data)
    try:
        # updates an existing payment request
        response = globee_payment.update_payment_request()
        print(response)
    except ValidationError as e:
        # payment not found or other error
        print(e)
```