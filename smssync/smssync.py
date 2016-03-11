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

from django.apps import apps

OutgoingMessage = apps.get_model(app_label='smssync',
                                 model_name='OutgoingMessage')
IncomingMessage = apps.get_model(app_label='smssync',
                                 model_name='IncomingMessage')

def send(text, to):
    om = OutgoingMessage.create(text, to)
    try:
        om.save()
    except Exception:
        raise
    else:
        return om


def receive(sent_from=None):
    qs = IncomingMessage.objects.incoming()
    if sent_from:
        qs = qs.sent_from(sent_from)
    for m in qs:
        yield m.mark_as_received()
    return


def register_receive_handler():
    pass
