from django.conf.urls import include, patterns, url
from telegram_bot import api


urlpatterns = patterns(
    '', url(r'', include('lms.urls')),
    url(r'^api/bot/courses/$', api.CourseList.as_view()),
)
