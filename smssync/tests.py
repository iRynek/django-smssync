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


from django.test import TestCase, RequestFactory, Client
from django.core.urlresolvers import reverse_lazy

from model_mommy import mommy

from smssync.views import SyncView
from smssync.models import IncomingMessage, OutgoingMessage


class SMSSyncBaseTest(TestCase):

    def assertPayloadSuccess(self, response):
        assert response.json()['payload']['success']
        self.assertIsNone(response.json()['payload']['error'])

    def assertPayloadFail(self, response, error=None):
        assert not response.json()['payload']['success']
        self.assertPayloadError(response, error)

    def assertPayloadError(self, response, error=None):
        payload = response.json()['payload']['error']
        assert len(payload)
        if error:
            msg = "Error msg wasn't {}: {}".format(payload, error)
            self.assertEqual(payload, error, msg=msg)

    def assertPayloadSecret(self, response, secret):
        payload = response.json()['payload']['secret']
        msg = "Secret wasn't {}: {}".format(payload, secret)
        self.assertEqual(payload, secret, msg=msg)

    def assertPayloadMessageCount(self, response, count):
        payload = response.json()['payload']['messages']
        msg = "Message count wasn't {}: {}".format(len(payload), count)
        self.assertEqual(len(payload), count, msg=msg)

    def assertPayloadTask(self, response, task):
        payload = response.json()['payload']['task']
        msg = "Task wasn't {}: {}".format(payload, task)
        self.assertEqual(payload, task, msg=msg)

    def assertIncomingMessageExists(self, message_id):
        self.assertTrue(IncomingMessage.objects
                        .filter(message_id=message_id).exists())

    def assertIncomingMessageCount(self, count):
        db_count = IncomingMessage.objects.all().count()
        msg = "Incoming message count wasn't %d: %d" % (count, db_count)
        self.assertEqual(count, db_count, msg=msg)

    def assertUnreceivedIncomingMessageCount(self, count):
        db_count = IncomingMessage.objects.filter(received=False).count()
        msg = "Incoming message count wasn't %d: %d" % (count, db_count)
        self.assertEqual(count, db_count, msg=msg)

    def assertOutgoingMessageExists(self, id):
        self.assertTrue(OutgoingMessage.objects
                        .filter(id=id).exists())

    def assertOutgoingMessageCount(self, count):
        db_count = OutgoingMessage.objects.all().count()
        msg = "Outgoing message count wasn't %d: %d" % (count, db_count)
        self.assertEqual(count, db_count, msg=msg)

    def assertUnsentOutgoingMessageCount(self, count):
        db_count = OutgoingMessage.objects.filter(sent=False).count()
        msg = "Outgoing unsent message count wasn't %d: %d" % (count, db_count)
        self.assertEqual(count, db_count, msg=msg)

    def assertStatusCode(self, status_code, response):
        msg = "Status code wasn't %d: %d" % (status_code,
                                          response.status_code)
        self.assertEqual(status_code, response.status_code, msg=msg)

    def assert404(self, response):
        self.assertStatusCode(404, response)

    def assert200(self, response):
        self.assertStatusCode(200, response)

    def assert503(self, response):
        self.assertStatusCode(500, response)


class ModelTests(SMSSyncBaseTest):
    def test_incoming_from_filter(self):
        m0 = mommy.make(IncomingMessage, sent_from="+000-000-000")
        m1 = mommy.make(IncomingMessage, sent_from="+000-000-001")
        self.assertEqual(m1.id,IncomingMessage.objects.
                         sent_from("+000-000-001").first().id)

    def test_incoming_filter(self):
        m0 = mommy.make(IncomingMessage, sent_from="+000-000-000",received=True)
        m1 = mommy.make(IncomingMessage, sent_from="+000-000-001",received=False)
        self.assertIncomingMessageCount(2)
        self.assertUnreceivedIncomingMessageCount(1)


    def test_outgoing_filter(self):
        m0 = mommy.make(OutgoingMessage, to="+000-000-000", sent=True)
        m1 = mommy.make(OutgoingMessage, to="+000-000-001", sent=False)
        self.assertOutgoingMessageCount(2)
        self.assertUnsentOutgoingMessageCount(1)


class SyncViewTests(SMSSyncBaseTest):
    def setUp(self):
        self.url = reverse_lazy("sync_url")
        self.factory = RequestFactory()
        self.client = Client()


    def test_post_message(self):
        """
        Test smssync posting a message to the server:

        $ curl -D - -X POST http://localhost/demo.php \
            -F "from=+000-000-0000" \
            -F "message=sample text message" \
            -F "secret=123456" \
            -F "device_id=1" \
            -F "sent_timestamp=123456789" \
            -F "message_id=80" \
        """

        params = {'from': "+000-000-0000",
                  'message': "sample text",
                  'secret': "123456",
                  'device_id': "1",
                  'sent_timestamp': "1298244863",
                  'message_id': "80",
                  }

        response = self.client.post(self.url, params)
        self.assert200(response)
        self.assertPayloadSuccess(response)
        self.assertIncomingMessageExists(message_id='80')
        self.assertIncomingMessageCount(1)

    def test_post_message_missing_from(self):
        params = {'from': "",
                  'message': "sample text",
                  'secret': "123456",
                  'device_id': "1",
                  'sent_timestamp': "1298244863",
                  'message_id': "80",
                  }

        response = self.client.post(self.url, params)
        self.assert200(response)
        expected_error_msg = "Required keyword(s) missing: from"
        self.assertPayloadFail(response, expected_error_msg)

    def test_post_message_bad_timestamp(self):
        params = {'from': "",
                  'message': "sample text",
                  'secret': "123456",
                  'device_id': "1",
                  'sent_timestamp': "1298244863",
                  'message_id': "80",
                  }

        response = self.client.post(self.url, params)
        self.assert200(response)
        self.assertPayloadFail(response)

    def test_get_task(self):
        m0 = mommy.make(OutgoingMessage, to="+000-000-000")
        m1 = mommy.make(OutgoingMessage, to="+000-000-000")
        params = {'task': "send",}
        response = self.client.get(self.url, params)
        self.assert200(response)
        self.assertPayloadSecret(response, '123456')
        self.assertPayloadMessageCount(response, 2)
        self.assertPayloadTask(response, 'send')
        self.assertUnsentOutgoingMessageCount(0)
        self.assertOutgoingMessageCount(2)
        # send more messages and check if database is ok
        m2 = mommy.make(OutgoingMessage, to="+000-000-000")
        self.assertUnsentOutgoingMessageCount(1)
        response = self.client.get(self.url, params)
        self.assert200(response)
        self.assertUnsentOutgoingMessageCount(0)
        self.assertOutgoingMessageCount(3)
