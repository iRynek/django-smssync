# -*- coding: utf-8 -*-
#
# (C) 2016 Rodrigo Rodrigues da Silva <pitanga@members.fsf.org>
#
# This file is part of django-smssync
#
# django-smssync is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# django-smssync is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with django-smssync.  If not, see <http://www.gnu.org/licenses/>.

from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.generic import View
from django.utils.decorators import method_decorator
from django.core.exceptions import ValidationError
from django.db import transaction
from django.conf import settings

from smssync.models import IncomingMessage, OutgoingMessage
from smssync.decorators import secret_required

import logging
logger = logging.getLogger(__name__)


def get_msg_kwargs(request_dict):
    KEYWORDS = ['from',
                'message',
                'message_id',
                'sent_to',
                'secret',
                'device_id',
                'sent_timestamp',]
    return {k:v for k,v in request_dict.items() if k in KEYWORDS}


@method_decorator([csrf_exempt, secret_required], name='dispatch')
class SyncView(View):

    @transaction.atomic
    def post(self, request):
        task = request.POST.get('task', '')
        if task == 'result':
            response = get_sms_delivery_report(
                get_msg_kwargs(request.POST))
        elif task == 'sent':
            response = get_sent_message_uuids(
                get_msg_kwargs(request.POST))
        else:
            response = get_message(
                get_msg_kwargs(request.POST))

        return JsonResponse(response)

    @transaction.atomic
    def get(self, request):
        task = request.GET.get('task', '')
        if task == 'send':
            response = send_task(request.GET)
        elif task == 'result':
            response = send_messages_uuids_for_sms_delivery_report(request.GET)
        return JsonResponse(response)


def get_message(params):
    logger.info("Receiving message: {}".format(repr(params)))
    payload={}
    payload['success'] = False
    payload['error'] = None

    try:
        IncomingMessage.create(**params)
    except (KeyError, ValueError, ValidationError) as e:
        payload['error'] = str(e.args[0])
    except Exception:
        raise
    else:
        payload['success'] = True

    return {"payload":payload}


def send_task(params):

    payload={}
    payload['task'] = 'send'
    payload['secret'] = settings.SMSSYNC_SECRET_VALUE
    payload['messages'] = get_outgoing_messages()
    payload['error'] = None

    return {"payload":payload}


def get_outgoing_messages():

    messages = []

    for m in OutgoingMessage.objects.outgoing():
        m.mark_as_sent()
        messages.append(m.task_dict)
        logger.info("Sending message: {}".format(repr(m.task_dict)))
    return messages
