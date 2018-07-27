from django.db import models

from globee.signals import globee_valid_ipn

PAYMENT_STATUS_GLOBEE_UNPAID = 'unpaid'
PAYMENT_STATUS_GLOBEE_PAID = 'paid'
PAYMENT_STATUS_GLOBEE_UNDERPAID = 'underpaid'
PAYMENT_STATUS_GLOBEE_OVERPAID = 'overpaid'
PAYMENT_STATUS_GLOBEE_PAID_LATE = 'paid_late'
PAYMENT_STATUS_GLOBEE_CONFIRMED = 'confirmed'
PAYMENT_STATUS_GLOBEE_COMPLETED = 'completed'

SPEED_STATUS_GLOBEE_LOW = 'low'
SPEED_STATUS_GLOBEE_MEDIUM = 'medium'
SPEED_STATUS_GLOBEE_HIGH = 'high'


class GlobeeIPN(models.Model):

    PAYMENT_STATUS_CHOICES = (
        (PAYMENT_STATUS_GLOBEE_UNPAID, 'unpaid - ready to receive payment'),
        (PAYMENT_STATUS_GLOBEE_PAID, 'waiting for confirmations'),
        (PAYMENT_STATUS_GLOBEE_UNDERPAID, 'user has paid less'),
        (PAYMENT_STATUS_GLOBEE_OVERPAID, 'user has mistakenly paid more'),
        (PAYMENT_STATUS_GLOBEE_PAID_LATE, 'the payment was made outside of the quotation window'),
        (PAYMENT_STATUS_GLOBEE_CONFIRMED, 'payment has been confirmed'),
        (PAYMENT_STATUS_GLOBEE_COMPLETED, 'payment-request is now completed'),
    )

    SPEED_STATUS_CHOICES = (
        (SPEED_STATUS_GLOBEE_LOW, 'low speed / low risk'),
        (SPEED_STATUS_GLOBEE_MEDIUM, 'medium speed / medium risk'),
        (SPEED_STATUS_GLOBEE_HIGH, 'high speed with / risk'),
    )

    payment_status = models.CharField(max_length=12, choices=PAYMENT_STATUS_CHOICES, help_text='Globee payment status')
    payment_id = models.CharField(max_length=255, help_text='Globee payment ID')
    total = models.FloatField(help_text='The amount in fiat or crypto-currency')
    customer_email = models.EmailField(help_text='The email address of your customer')
    customer_name = models.CharField(max_length=50, null=True, blank=True, help_text='The name of your customer')
    currency = models.CharField(max_length=3, default='USD', help_text='ISO 4217 currency codes')
    custom_payment_id = models.CharField(max_length=255, blank=True, null=True, help_text='A reference or custom identifier that you can use to link the payment back to your system')
    callback_data = models.CharField(max_length=255, blank=True, null=True, help_text='Passthrough data that will be returned in the IPN callback')
    notification_email = models.CharField(max_length=255, blank=True, null=True, help_text='An email address that the system will send a notification email to once the payment has been confirmed')
    confirmation_speed = models.CharField(max_length=50, choices=SPEED_STATUS_CHOICES, default=SPEED_STATUS_GLOBEE_MEDIUM)
    created_at = models.DateTimeField()
    expires_at = models.DateTimeField()

    def send_valid_signal(self):
        globee_valid_ipn.send(sender=self)
