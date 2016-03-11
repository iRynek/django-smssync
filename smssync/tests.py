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
from django.conf import settings

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

    def assertIncomingMessageExists(self, id):
        self.assertTrue(IncomingMessage.objects.filter(id=id).exists())

    def assertIncomingMessageCount(self, count):
        db_count = IncomingMessage.objects.all().count()
        msg = "Incoming message count wasn't %d: %d" % (count, db_count)
        self.assertEqual(count, db_count, msg=msg)

    def assertUnreceivedIncomingMessageCount(self, count):
        db_count = IncomingMessage.objects.filter(received=False).count()
        msg = "Unreceived message count wasn't %d: %d" % (count, db_count)
        self.assertEqual(count, db_count, msg=msg)

    def assertOutgoingMessageExists(self, id):
        self.assertTrue(OutgoingMessage.objects.filter(id=id).exists())

    def assertOutgoingMessageCount(self, count):
        db_count = OutgoingMessage.objects.all().count()
        msg = "Outgoing message count wasn't %d: %d" % (count, db_count)
        self.assertEqual(count, db_count, msg=msg)

    def assertUnsentOutgoingMessageCount(self, count):
        db_count = OutgoingMessage.objects.filter(sent=False).count()
        msg = "Unsent message count wasn't %d: %d" % (count, db_count)
        self.assertEqual(count, db_count, msg=msg)

    def assertStatusCode(self, status_code, response):
        msg = "Status code wasn't %d: %d" % (status_code,
                                          response.status_code)
        self.assertEqual(status_code, response.status_code, msg=msg)

    def assert403(self, response):
        self.assertStatusCode(403, response)

    def assert404(self, response):
        self.assertStatusCode(404, response)

    def assert200(self, response):
        self.assertStatusCode(200, response)

    def assert503(self, response):
        self.assertStatusCode(503, response)


class ModelTests(SMSSyncBaseTest):

    def test_mark_as_sent(self):
        m0 = mommy.make(OutgoingMessage, to="+000-000-000")
        assert not m0.sent
        m0.mark_as_sent()
        assert m0.sent
        from django.utils import timezone
        assert m0.sent_timestamp < timezone.now()

    def test_mark_as_received(self):
        m0 = mommy.make(IncomingMessage, sent_from="+000-000-000")
        assert not m0.received
        m0.mark_as_received()
        assert m0.received
        from django.utils import timezone
        assert m0.received_timestamp < timezone.now()

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
        self.secret = settings.SMSSYNC_SECRET_KEY
        self.post_params = {'from': "+000-000-0000",
                            'message': "sample text",
                            'secret': self.secret,
                            'device_id': "1",
                            'sent_timestamp': "1298244863000",
                            'message_id': "6b5232ad-2bb3-4d94-8dcb-3a50ffbcadc9"}

    def test_post_message(self):
        """
        Test smssync posting a message to the server as example from SMSSync dev:

        $ curl -D - -X POST http://localhost/demo.php \
            -F "from=+000-000-0000" \
            -F "message=sample text message" \
            -F "secret=123456" \
            -F "device_id=1" \
            -F "sent_timestamp=123456789" \
            -F "message_id=80" \
        """

        response = self.client.post(self.url, self.post_params)
        self.assert200(response)
        self.assertPayloadSuccess(response)
        self.assertIncomingMessageCount(1)
        self.assertIncomingMessageExists("6b5232ad-2bb3-4d94-8dcb-3a50ffbcadc9")

    def test_post_message_missing_required_fields(self):
        for field in IncomingMessage.REQUIRED_KEYWORDS:
            _params = self.post_params.copy()
            _params[field] = ""
            response = self.client.post(self.url, _params)
            self.assert200(response)
            expected_error_msg = "Required keyword(s) missing: {}".format(field)
            self.assertPayloadFail(response, expected_error_msg)

    def test_post_message_bad_message_id(self):
        """
        although SMSSync example's message_id is '80' we should expect an UUID
        """
        _params = self.post_params.copy()
        _params['message_id'] = "80"
        response = self.client.post(self.url, _params)
        self.assert200(response)
        expected_error_msg = "badly formed hexadecimal UUID string"
        self.assertPayloadFail(response, expected_error_msg)

    def test_post_message_bad_secret(self):
        """
        make sure the secret is being checked by the views
        """
        _params = self.post_params.copy()
        _params['secret'] = "42"
        response = self.client.post(self.url, _params)
        self.assert403(response)
        expected_error_msg = ("The secret value sent from the device does "
                              "not match the one on the server")
        self.assertPayloadFail(response, expected_error_msg)

    def test_get_task(self):
        m0 = mommy.make(OutgoingMessage, to="+000-000-000")
        m1 = mommy.make(OutgoingMessage, to="+000-000-000")
        get_params = {'task': "send",
                      'secret': self.secret}
        response = self.client.get(self.url, get_params)
        self.assert200(response)
        self.assertPayloadSecret(response, self.secret)
        self.assertPayloadMessageCount(response, 2)
        self.assertPayloadTask(response, 'send')
        self.assertUnsentOutgoingMessageCount(0)
        self.assertOutgoingMessageCount(2)
        # send more messages and check if database is ok
        m2 = mommy.make(OutgoingMessage, to="+000-000-000")
        self.assertUnsentOutgoingMessageCount(1)
        response = self.client.get(self.url, get_params)
        self.assert200(response)
        self.assertUnsentOutgoingMessageCount(0)
        self.assertOutgoingMessageCount(3)


class APITests(SMSSyncBaseTest):

    def _setup_incoming(self, count):
        for i in range(count):
            mommy.make(IncomingMessage,
                       sent_from="+000-000-00{}".format(str(i)))

    def test_send(self):
        from smssync import smssync
        self.assertOutgoingMessageCount(0)
        om = smssync.send("Hello", "+000-000-000")
        assert isinstance (om, OutgoingMessage)
        self.assertOutgoingMessageExists(om.id)
        self.assertUnsentOutgoingMessageCount(1)

    def test_receive(self):
        """
        Test if messages are correctly marked as reveived when received
        """
        initial = 4
        self._setup_incoming(initial)
        from smssync import smssync
        self.assertIncomingMessageCount(initial)
        self.assertUnreceivedIncomingMessageCount(initial)
        received_count = 0
        for im in smssync.receive():
            assert isinstance(im, IncomingMessage)
            self.assertIncomingMessageExists(im.id)
            received_count += 1
        self.assertUnreceivedIncomingMessageCount(0)
        self.assertEqual(received_count, initial)
        self.assertIncomingMessageCount(initial)

    def test_receive_from(self):
        """
        Test if the sent_from receiver filter filters out messages from other
        senders, preventing them from being received
        """
        initial = 4
        self._setup_incoming(initial)
        from smssync import smssync
        self.assertIncomingMessageCount(initial)
        self.assertUnreceivedIncomingMessageCount(initial)
        received_count = 0
        #put another message from the same sender
        mommy.make(IncomingMessage, sent_from="+000-000-000")
        for im in smssync.receive("+000-000-000"):
            received_count += 1
        self.assertEqual(received_count, 2)
        self.assertUnreceivedIncomingMessageCount((initial+1)-received_count)
        self.assertIncomingMessageCount(initial+1)

    def test_receive_break(self):
        """
        Test the receive() generator works, that is, the messages are marked as
        received only if they are actually iterated through.
        """
        initial = 8
        stop = 3
        self._setup_incoming(initial)
        from smssync import smssync
        self.assertIncomingMessageCount(initial)
        self.assertUnreceivedIncomingMessageCount(initial)
        received_count = 0
        for im in smssync.receive():
            received_count += 1
            if received_count == stop:
                break
        self.assertEqual(received_count, stop)
        self.assertUnreceivedIncomingMessageCount(initial-stop)
        self.assertIncomingMessageCount(initial)
