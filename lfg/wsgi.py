"""
WSGI config for lfg project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/1.8/howto/deployment/wsgi/
"""

import os
import sys
import site
from django.core.wsgi import get_wsgi_application

os.environ["DJANGO_SETTINGS_MODULE"] = "lfg.settings"

application = get_wsgi_application()

# Add the site-packages of the chosen virtualenv to work with
site.addsitedir('~/.virtualenvs/lfg/lib/python2.7/site-packages')

# Add the app's directory to the PYTHONPATH
sys.path.append('/home/vlafa/Desktop/Projekti/lfg_project')
sys.path.append('/home/vlafa/Desktop/Projekti/lfg_project/lfg')

# Activate your virtual env
activate_env=os.path.expanduser("~/.virtualenvs/lfg/bin/activate_this.py")
execfile(activate_env, dict(__file__=activate_env))