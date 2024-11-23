"""
WSGI config for myproject project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/5.1/howto/deployment/wsgi/
"""

import os
from django.core.wsgi import get_wsgi_application
from whitenoise import WhiteNoise
from myproject import MyWSGIApp



application = MyWSGIApp()
application = WhiteNoise(application, root="/path/to/static/files")
application.add_files("/capstone/myapp/static/", prefix="more-files/")
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'myproject.settings')

application = get_wsgi_application()
