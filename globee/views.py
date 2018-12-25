from datetime import datetime
from logging import getLogger
from json import loads as json_loads, dumps as json_dumps
from pytz import utc as pytz_utc

from django.conf import settings
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST

from globee.models import GlobeeIPN


logger = getLogger(__name__)


@require_POST
@csrf_exempt
def globee_ipn_view(request):
    paranoid = getattr(settings, 'GLOBEE_PARANOID_MODE')
    payment_data = json_loads(request.body.decode("utf-8"))

    pretty_data = json_dumps(payment_data, indent=4, sort_keys=True)
    logger.debug('Globee POST data: %s' % pretty_data)

    try:
        created_at = datetime.strptime(payment_data['created_at'], '%Y-%m-%d %H:%M:%S')
        expires_at = datetime.strptime(payment_data['expires_at'], '%Y-%m-%d %H:%M:%S')

        defaults = {
            'payment_status': payment_data['status'],
            'total': float(payment_data['total']),
            'currency': payment_data['currency'],
            'custom_payment_id': payment_data['custom_payment_id'],
            'callback_data': payment_data['callback_data'],
            'customer_email': payment_data['customer']['email'],
            'customer_name': payment_data['customer']['name'],
            'created_at': pytz_utc.localize(created_at),
            'expires_at': pytz_utc.localize(expires_at),
        }

        payment, created = GlobeeIPN.objects.update_or_create(
            payment_id=payment_data['id'],
            defaults=defaults
        )
        payment.send_valid_signal()
    except KeyError as e:
        logger.error('Key %s not found in payment data.' % e)
        status = 200 if paranoid else 400
        return HttpResponse(status=status)
    except ValueError as e:
        logger.error(e)
        status = 200 if paranoid else 400
        return HttpResponse(status=status)

    return HttpResponse(status=200)

