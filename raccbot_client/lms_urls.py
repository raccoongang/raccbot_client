from django.conf.urls import include, patterns, url
from raccbot_client import api

from django.conf import settings


urlpatterns = patterns(
    '', url(r'', include('lms.urls')),
    url(r'^api/bot/courses/$', api.CourseList.as_view()),
    url(r'^api/bot/courses/{}'.format(settings.COURSE_KEY_PATTERN), api.CourseDetailView.as_view(), name="course-detail"),
)
