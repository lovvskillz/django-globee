import json
import logging
from django.http import HttpResponse
from django.utils import timezone
from django.utils.dateparse import parse_datetime
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
        created_at = parse_datetime(payment_data['created_at'])
        expires_at = parse_datetime(payment_data['expires_at'])
        defaults = {
            'payment_status': payment_data['status'],
            'total': payment_data['total'],
            'currency': payment_data['currency'],
            'custom_payment_id': payment_data['custom_payment_id'],
            'callback_data': payment_data['callback_data'],
            'customer_email': payment_data['customer']['email'],
            'customer_name': payment_data['customer']['name'],
            'created_at': timezone.datetime(created_at.year, created_at.month, created_at.day, created_at.hour,
                                            created_at.minute, created_at.second),
            'expires_at': timezone.datetime(expires_at.year, expires_at.month, expires_at.day, expires_at.hour,
                                            expires_at.minute, expires_at.second),
        }
        payment, created = GlobeeIPN.objects.get_or_create(payment_id=payment_data['id'], defaults=defaults)
        payment.status = payment_data['status']
        payment.save()
        payment.send_valid_signal()
    return HttpResponse("Ok")
