from models import TeleramReg
from django.contrib.auth.models import User
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django.views.generic import View
import hashlib
from student.models import CourseEnrollment


class GenerateToken(View):

    def post(self, request):
        username = request.POST.get('username')
        user = User.objects.get(username=username)
        token = 'hash::{}'.format(hashlib.sha224('hash').hexdigest())
        TeleramReg.objects.create(
            user=user,
            token=token
        )
        return JsonResponse({'token': token})


class Verifying(View):

    def get(self, request):
        token = request.GET.get('token')
        tel_name = request.GET.get('tel_name')
        user = TeleramReg.objects.filter(token=token).first()
        if user:
            user.token = None
            user.tel_name = tel_name
            user.verified = True
            user.save()
            return JsonResponse({'foo': 'bar1'})
        else:
            return JsonResponse({'foo': 'bar2'})


class EnrollmentCourses(View):
    def get(self, request):
        tel_name = request.GET.get('tel_name')
        user = TeleramReg.objects.filter(tel_name=tel_name).first()
        if user:
            courses = CourseEnrollment.enrollments_for_user(user.user)
            serialized = []
	    for course in courses:
                serialized.append(dict(course_name=course.course.display_name, course_id=course.course.__str__()))
            return JsonResponse({'courses': serialized})
        else:
            return JsonResponse({'courses': 'none'})
