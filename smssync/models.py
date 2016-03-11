# -*- coding: utf-8 -*-
#
# (C) 2016 Rodrigo Rodrigues da Silva <pitanga@members.fsf.org>
#
# This file is part of django-smssync
#
# django-smssync is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# django-smssync is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with django-smssync.  If not, see <http://www.gnu.org/licenses/>.

import uuid
import datetime

from django.db import models
from django.utils import timezone
from phonenumber_field.modelfields import PhoneNumberField

from smssync.managers import IncomingMessageQuerySet, OutgoingMessageQuerySet

from django.utils.formats import get_format
datetime_formats = get_format('DATETIME_INPUT_FORMATS')

class MessageBase():
    pass

class Message(MessageBase, models.Model):

    id = models.UUIDField(primary_key=True,
                          default=uuid.uuid4,
                          editable=False)

    message = models.CharField(max_length=160,
                               null=False,
                               blank=True)

    created = models.DateTimeField(auto_now_add=True,
                                   null=False,
                                   blank=False,
                                   editable=False)
    

    class Meta:
        abstract=True
        ordering = ['-created']


class IncomingMessage(Message):

    objects = IncomingMessageQuerySet.as_manager()

    sent_from = PhoneNumberField(blank=False)

    message_id = models.CharField(max_length=32,
                                  null=False,
                                  blank=False)

    sent_to = models.CharField(max_length=32,
                               null=False,
                               blank=True)

    device_id = models.CharField(max_length=32,
                                 null=False,
                                 blank=True)

    sent_timestamp = models.DateTimeField(null=False,
                                          blank=False)

    received = models.BooleanField(default=False,
                                   null=False,
                                   editable=False)

    received_timestamp = models.DateTimeField(null=True,
                                              blank=True)


    @classmethod
    def validate_before(cls, kwargs):
        REQUIRED_KEYWORDS = ['from',
                             'message',
                             'sent_timestamp',
                             'message_id',]
        
        missing = []
        error = None

        for f in REQUIRED_KEYWORDS:
            if not len(kwargs.get(f,'')):
                missing.append(f)

        if len(missing):
            raise KeyError("Required keyword(s) missing: {}"
                            .format(", ".join(missing)))

    @classmethod
    def create(cls, **kwargs):
        cls.validate_before(kwargs)
        millis = float(kwargs.get('sent_timestamp'))/1000
        sent_timestamp = datetime.datetime.fromtimestamp(millis)
        message = cls(sent_from=kwargs.get('from'),
                      message=kwargs.get('message'),
                      sent_timestamp=sent_timestamp,
                      message_id=kwargs.get('message_id'),
                      sent_to=kwargs.get('sent_to',""),
                      device_id=kwargs.get('device_id',""),
        )
        return message
        
    def mark_as_received(self):
        self.received = True
        self.received_timestamp = timezone.now()
        self.save()


class OutgoingMessage(Message):

    objects = OutgoingMessageQuerySet.as_manager()

    to = PhoneNumberField(null=False,
                          blank=False,
                          editable=False)

    #in_reply_to = models.ForeignKey(IncomingMessage,
    #                             related_name="replies")

    sent = models.BooleanField(default=False,
                               null=False,
                               editable=False)

    sent_timestamp = models.DateTimeField(null=True,
                                          blank=True)

    # queued = models.BooleanField(default=False)
    # queued_timestamp = models.DateTimeField(null=False)
    #
    # sms_sent = models.BooleanField(null=False, default=False)
    # sms_sent_result_code = models.IntegerField(null=True)
    # sms_sent_result_message = models.CharField(max_length=32,
    #                                        null=True,
    #                                        blank=True)
    # sms_sent_report_timestamp = models.DateTimeField(null=True)
    
    # sms_delivered = models.BooleanField(null=False, default=False)
    # sms_delivered_result_code = models.IntegerField(null=True)
    # sms_delivered_result_message = models.CharField(max_length=32,
    #                                             null=True,
    #                                             blank=True)
    # sms_delivered_report_timestamp = models.DateTimeField(null=True)

    def mark_as_sent(self):
        self.sent = True
        self.sent_timestamp = timezone.now()
        self.save()

    @property
    def task_dict(self):
        return {'to': str(self.to),
                'message': self.message,
                'uuid': self.id,}
