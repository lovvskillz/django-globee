# django-globee

[![GitHub license](https://img.shields.io/badge/license-MIT-brightgreen.svg)](https://raw.githubusercontent.com/lovvskillz/django-globee/master/LICENSE)
[![PyPI version](https://badge.fury.io/py/django-globee.svg)](https://badge.fury.io/py/django-globee)
[![Build Status](https://travis-ci.org/lovvskillz/django-globee.svg?branch=master)](https://travis-ci.org/lovvskillz/django-globee)
[![Coverage Status](https://coveralls.io/repos/github/lovvskillz/django-globee/badge.svg)](https://coveralls.io/github/lovvskillz/django-globee)

django-globee is a Django app to integrate [GloBee](https://globee.com/) Payments.

You can find the GloBee API docs [here](https://globee.com/docs/payment-api/v1).

## Quick start

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
    GLOBEE_TESTNET = True # or False
```


4. Run `python manage.py migrate` to create the globee models.


## examples

see [Docs](docs/README.md)
