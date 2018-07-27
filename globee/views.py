import json
import logging
import datetime

import pytz
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST

from globee.models import GlobeeIPN


logger = logging.getLogger(__name__)


@require_POST
@csrf_exempt
def globee_ipn_view(request):
    payment_data = json.loads(request.body.decode("utf-8"))
    logger.debug("Globee POST data: %s", payment_data)
    if 'id' in payment_data:
        created_at = datetime.datetime.strptime(payment_data['created_at'], '%Y-%m-%d %H:%M:%S')
        expires_at = datetime.datetime.strptime(payment_data['expires_at'], '%Y-%m-%d %H:%M:%S')
        defaults = {
            'payment_status': payment_data['status'],
            'total': payment_data['total'],
            'currency': payment_data['currency'],
            'custom_payment_id': payment_data['custom_payment_id'],
            'callback_data': payment_data['callback_data'],
            'customer_email': payment_data['customer']['email'],
            'customer_name': payment_data['customer']['name'],
            'created_at': pytz.utc.localize(created_at),
            'expires_at': pytz.utc.localize(expires_at),
        }
        payment, created = GlobeeIPN.objects.update_or_create(payment_id=payment_data['id'], defaults=defaults)
        payment.send_valid_signal()
    return HttpResponse("Ok")
