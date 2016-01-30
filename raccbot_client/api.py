import logging

from django.contrib.auth.models import User

from django.core.exceptions import ObjectDoesNotExist
from django.db import transaction
from django.utils.decorators import method_decorator

from rest_framework.generics import RetrieveAPIView, ListAPIView
from django.conf import settings
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import status

from cors_csrf.decorators import ensure_csrf_cookie_cross_domain
from course_modes.models import CourseMode
from course_structure_api.v0 import serializers
from course_structure_api.v0.views import CourseViewMixin
from courseware import courses
from embargo import api as embargo_api
from instructor.offline_gradecalc import student_grades
from opaque_keys.edx.keys import CourseKey
from opaque_keys import InvalidKeyError
from student.models import User, CourseEnrollment
from xmodule.modulestore.django import modulestore

from openedx.core.djangoapps.user_api.preferences.api import update_email_opt_in
from openedx.core.lib.api.authentication import (
    SessionAuthenticationAllowInactiveUser,
    OAuth2AuthenticationAllowInactiveUser,
)
# from openedx.core.lib.api.serializers import PaginationSerializer
from openedx.core.lib.api.permissions import ApiKeyHeaderPermission, ApiKeyHeaderPermissionIsAuthenticated

from enrollment import api
from forms import CourseDetailGetForm


log = logging.getLogger(__name__)

class CourseListMixin(object):
    lookup_field = 'course_id'
    paginate_by = 10
    paginate_by_param = 'page_size'
    serializer_class = serializers.CourseSerializer
    # Using EDX_API_KEY for access to this api
    authentication_classes = []
    permission_classes = []

    def get_queryset(self):
        course_ids = self.request.query_params.get('course_id', None)

        results = []
        if course_ids:
            course_ids = course_ids.split(',')
            for course_id in course_ids:
                course_key = CourseKey.from_string(course_id)
                course_descriptor = courses.get_course(course_key)
                results.append(course_descriptor)
        else:
            results = modulestore().get_courses()

        # Ensure only course descriptors are returned.
        results = (course for course in results if
                   course.scope_ids.block_type == 'course')

        # Sort the results in a predictable manner.
        return sorted(results, key=lambda course: unicode(course.id))


class CourseList(CourseListMixin, ListAPIView):
    """
    Inspired from:
    lms.djangoapps.course_structure_api.v0.views.CourseList

    **Use Case**
        Get a paginated list of courses in the whole edX Platform.
        The list can be filtered by course_id.
        Each page in the list can contain up to 10 courses.
    **Example Requests**
          GET /api/extended/courses/
    **Response Values**
        * count: The number of courses in the edX platform.
        * next: The URI to the next page of courses.
        * previous: The URI to the previous page of courses.
        * num_pages: The number of pages listing courses.
        * results:  A list of courses returned. Each collection in the list
          contains these fields.
            * id: The unique identifier for the course.
            * name: The name of the course.
            * category: The type of content. In this case, the value is always
              "course".
            * org: The organization specified for the course.
            * run: The run of the course.
            * course: The course number.
            * uri: The URI to use to get details of the course.
            * image_url: The URI for the course's main image.
            * start: The course start date.
            * end: The course end date. If course end date is not specified, the
              value is null.
    """
    serializer_class = serializers.CourseSerializer



from django.core.exceptions import ValidationError
from rest_framework.generics import ListAPIView, RetrieveAPIView

from openedx.core.lib.api.paginators import NamespacedPageNumberPagination
from openedx.core.lib.api.view_utils import view_auth_classes, DeveloperErrorViewMixin
from .serializers import CourseDetailSerializer


@view_auth_classes(is_authenticated=False)
class CourseDetailView(DeveloperErrorViewMixin, RetrieveAPIView):
    """
    **Use Cases**

        Request information on a course

    **Example Requests**

        GET /api/courses/v1/courses/{course_key}/

    **Response Values**

        Body consists of the following fields:

        * blocks_url: Used to fetch the course blocks
        * effort: A textual description of the weekly hours of effort expected
            in the course.
        * end: Date the course ends
        * enrollment_end: Date enrollment ends
        * enrollment_start: Date enrollment begins
        * id: A unique identifier of the course; a serialized representation
            of the opaque key identifying the course.
        * media: An object that contains named media items.  Included here:
            * course_image: An image to show for the course.  Represented
              as an object with the following fields:
                * uri: The location of the image
        * name: Name of the course
        * number: Catalog number of the course
        * org: Name of the organization that owns the course
        * overview: A possibly verbose HTML textual description of the course.
            Note: this field is only included in the Course Detail view, not
            the Course List view.
        * short_description: A textual description of the course
        * start: Date the course begins
        * start_display: Readably formatted start of the course
        * start_type: Hint describing how `start_display` is set. One of:
            * `"string"`: manually set
            * `"timestamp"`: generated form `start` timestamp
            * `"empty"`: the start date should not be shown

        Deprecated fields:

        * course_id: Course key (use 'id' instead)

    **Parameters:**

        username (optional):
            The username of the specified user for whom the course data
            is being accessed. The username is not only required if the API is
            requested by an Anonymous user.

    **Returns**

        * 200 on success with above fields.
        * 400 if an invalid parameter was sent or the username was not provided
          for an authenticated request.
        * 403 if a user who does not have permission to masquerade as
          another user specifies a username other than their own.
        * 404 if the course is not available or cannot be seen.

        Example response:

            {
                "blocks_url": "/api/courses/v1/blocks/?course_id=edX%2Fexample%2F2012_Fall",
                "media": {
                    "course_image": {
                        "uri": "/c4x/edX/example/asset/just_a_test.jpg",
                        "name": "Course Image"
                    }
                },
                "description": "An example course.",
                "end": "2015-09-19T18:00:00Z",
                "enrollment_end": "2015-07-15T00:00:00Z",
                "enrollment_start": "2015-06-15T00:00:00Z",
                "course_id": "edX/example/2012_Fall",
                "name": "Example Course",
                "number": "example",
                "org": "edX",
                "overview: "<p>A verbose description of the course.</p>"
                "start": "2015-07-17T12:00:00Z",
                "start_display": "July 17, 2015",
                "start_type": "timestamp"
            }
    """

    serializer_class = CourseDetailSerializer

    def get_object(self):
        """
        Return the requested course object, if the user has appropriate
        permissions.
        """
        user = User.objects.get(username='maxsocl')
        requested_params = self.request.query_params.copy()
        requested_params.update({'course_key': self.kwargs['course_key_string']})

        form = CourseDetailGetForm(requested_params, initial={'requesting_user': user})
        if not form.is_valid():
            raise ValidationError(form.errors)

        return course_detail(
            user,
            form.cleaned_data['course_key'],
        )


from lms.djangoapps.courseware.courses import (
    get_course_overview_with_access,
    get_permission_for_course_about,
)

def course_detail(user, course_key):
    return get_course_overview_with_access(
        user,
        get_permission_for_course_about(),
        course_key,
    )
