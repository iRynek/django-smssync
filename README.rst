==============
django-smssync
==============

django-smssync is a reusable app to integrate Django with `SMSSync <http://smssync.ushahidi.com/>`_, a simple SMS gateway for
Android.

Currently django-smssync can send and receive SMS. All messages are stored in the database (we might have another backend in the future). Message Results API is not supported yet.

django-smssync was inspired by `SMSsync-Python-Django-webservice <https://github.com/cwanjau/SMSsync-Python-Django-webservice/>`_
.

Quick start
-----------

1. Add `smssync` to your INSTALLED_APPS setting like this::

    INSTALLED_APPS = [
        ...
        'smssync',
    ]

2. Include the smssync URLconf in your project `urls.py` like this::

    url(r'^smssync/', include('smssync.urls')),

3. Run `python manage.py migrate` to create the django-smssync models.

4. `Add a SMSSync URL <http://smssync.ushahidi.com/configure/>`_ pointing to your server URL, which will be something like `http://yourdomain/smssync/` by default. Make sure your firewall and web server are configured properly.

5. If you set up a Secret Key in the previous step (recommended), add the following line to your `settings.py`::

    SMSSYNC_SECRET_KEY = 'some secret'

6. Start the development server and visit http://127.0.0.1:8000/admin/smssync to manage sent and received messages (you'll need the `admin` app enabled).

7. To send/receive messages programatically from your app::

    from smssync import smssync

    # send a message
    om = smssync.send("Hello", "+000-000-000")

    # receive all incoming messages
    for im in smssync.receive():
	    do_something(im)

    # receive all incoming messages from +000-000-000
    for im in smssync.receive("+000-000-000"):
	    do_something(im)
