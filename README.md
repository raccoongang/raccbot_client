from aws import *

#TEMPLATE_DIRS.insert(0, '/edx/app/edxapp/venvs/edxapp/src/raccbot_client/telegram_bot')
MAKO_TEMPLATES['main'] = ['/edx/app/edxapp/venvs/edxapp/src/raccbot_client/telegram_bot/templates/lms'] + MAKO_TEMPLATES['main']

ROOT_URLCONF = 'telegram_bot.lms_urls'
