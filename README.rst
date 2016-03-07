==============
django-smssync
==============

django-smssync is a reusable app to integrate Django with
[SMSSync](http://smssync.ushahidi.com/), a simple SMS gateway for
Android.

Currently django-smssync can send and receive SMS. All messages are
stored in the database. Message Results API is not supported yet.

Detailed documentation ~~is~~ will be in the "docs" directory.

Quick start
-----------

1. Add "smssync" to your INSTALLED_APPS setting like this::

    INSTALLED_APPS = [
        ...
        'smssync',
    ]

2. Include the smssync URLconf in your project urls.py like this::

    url(r'^smssync/', include('smssync.urls')),

3. Run `python manage.py migrate` to create the polls models.

4. [Configure SMSSync](http://smssync.ushahidi.com/configure/) to
   point the app to your server URL. Make sure your firewall and web
   server are configured properly.

5. Start the development server and visit http://127.0.0.1:8000/admin/
   to create a message and view received messages (you'll need the
   Admin app enabled).

6. Of course you can also send a message programatically by creating
   an `IncomingMessage` instance and saving it to the database. A
   proper API will be implemented soon.
