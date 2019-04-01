# Changes

## 2019-04-01 1.4.0
- set `unique=True` for `payment_id` and `custom_payment_id` 
- set the default payment status to `unpaid`
- add optional `GLOBEE_PARANOID_MODE` setting
    - `True` - IPN view will always respond with status code `200`
    - `False` - IPN view will respond with status code `400` if an `KeyError` or `ValueError` occurs


## 2018-11-16 1.3.0
- IPN view improvements
- removed static variables from the `GlobeePayment` class
- check empty strings and `NoneType`
- fix error message in `ping()`

**breaking changes**
- rename `GLOBEE_TEST_MODE` into `GLOBEE_TESTNET`

## 2018-10-09 1.2.0
- `update_payment_request()` updates an existing payment request 
- `get_payment_methods()` returns the merchant account's accepted crypto-currencies
- `get_payment_details()` returns the accepted crypto-currencies and informations for the payment-request
- `get_payment_currency_details()` returns the payment details for a given payment request and payment currency

**breaking changes**

- `ping()` returns the response from globee
- `create_request()` returns redirect url
- rename `data` parameter into `payment_data` in `GlobeePayment` init

## 2018-10-05 1.1.1
- fix `KeyError` for error message if `ping()` was not successful 

## 2018-07-27 1.1.0
- get a payment by id
- add `ping()` function

## 2018-07-27 1.0.0
- release