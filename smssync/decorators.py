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
from django.conf import settings

def secret_required(function=None, secret_key=None):
    """Check that the secret sent by the device mathces the configuration

    This decorator ensures that the 'secret' field in the requests matches
    the secret configured on the server
    """
    if secret_key is None:
        secret_key = settings.SMSSYNC_SECRET_KEY

    def _dec(view_func):
        def _view(request, *args, **kwargs):
            request_secret = ''
            if request.method == 'GET':
                request_secret = request.GET.get('secret')
            elif request.method == 'POST':
                request_secret = request.POST.get('secret')
            if request_secret == secret_key:
                return view_func(request, *args, **kwargs)
            else:
                payload={}
                payload['success'] = False
                reason_phrase = ("The secret value sent from the device does "
                                 "not match the one on the server")
                payload['error'] = reason_phrase

                return JsonResponse({'payload':payload}, status=403)

        _view.__name__ = view_func.__name__
        _view.__dict__ = view_func.__dict__
        _view.__doc__ = view_func.__doc__

        return _view

    if function is None:
        return _dec
    else:
        return _dec(function)
