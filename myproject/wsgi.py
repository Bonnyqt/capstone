"""
WSGI config for myproject project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/5.1/howto/deployment/wsgi/
"""

import os
from django.core.wsgi import get_wsgi_application
from whitenoise import WhiteNoise

# Set the default settings module for the 'myproject' project.
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'myproject.settings')

# Create the default WSGI application
application = get_wsgi_application()

# Add WhiteNoise to serve static files
application = WhiteNoise(application)

# Add custom static files directories if needed
application.add_files("/capstone/myapp/static/", prefix="more-files/")

# Optionally, you can also set the root directory where static files are served
application.root = "staticfiles"  # You can modify this as needed
