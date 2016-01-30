from aws import *

MAKO_TEMPLATES['main'] = ['/edx/app/edxapp/venvs/edxapp/src/raccbot_client/raccbot_client/templates/lms'] + MAKO_TEMPLATES['main']

ROOT_URLCONF = 'raccbot_client.lms_urls'

INSTALLED_APPS += (
    'raccbot_client',
)
