"""
WSGI config for ISARA_loader project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/2.1/howto/deployment/wsgi/
"""

import os

from django.core.wsgi import get_wsgi_application
#from whitenoise.django import DjangoWhiteNoise

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ISARA_loader.settings')



os.environ['http_proxy']="http://control.maxiv.lu.se:8888"
os.environ['https_proxy']="http://control.maxiv.lu.se:8888"
os.environ['no_proxy']="127.0.0.1,localhost,b-v-biomax-web-0,172.16.117.12,172.16.118.44,172.16.119.9,172.16.119.11,b-v-biomax-cc-0,172.16.118.48,b-biomax-eiger-dc-1,b311a-e-ctl-aem-01,b311a-e-ctl-aem-02,b311a-e-ctl-aem-03,172.16.119.15,b-v-biomax-web-1,172.16.116.23"


application = get_wsgi_application()
#application = DjangoWhiteNoise(application)
