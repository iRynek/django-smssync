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


from django.db import models


class OutgoingMessageQuerySet(models.QuerySet):
    def outgoing(self):
        return self.filter(sent=False)


class IncomingMessageQuerySet(models.QuerySet):
    def incoming(self):
        return self.filter(received=False)

    def sent_from(self, sent_from):
        return self.filter(sent_from=sent_from)
