# django-globee

django-globee is a Django app to integrate Globee Payments.

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
