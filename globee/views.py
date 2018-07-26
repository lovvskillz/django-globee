import json
import logging
from datetime import datetime

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
        payment = GlobeeIPN.objects.get_or_create(payment_id=payment_data['id'])
        payment.status = payment_data['status']
        payment.total = float(payment_data['total'])
        payment.currency = payment_data['currency']
        payment.custom_payment_id = payment_data['custom_payment_id']
        payment.callback_data = payment_data['callback_data']
        payment.customer_email = payment_data['customer']['email']
        payment.customer_name = payment_data['customer']['name']
        payment.created_at = datetime.strptime(payment_data['created_at'], "%Y-%m-%d %H:%M:%S")
        payment.expires_at = datetime.strptime(payment_data['expires_at'], "%Y-%m-%d %H:%M:%S")
        payment.save()
        payment.send_valid_signal()
    return HttpResponse("Ok")
