from models import TeleramReg
from django.contrib.auth.models import User
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django.views.generic import View
import hashlib


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

    def post(self, request):
        token = request.POST.get('token')
        tel_name = request.POST.get('tel_name')
        user = TeleramReg.objects.filter(token=token).first()
        if user:
            user.update(
                token='null',
                tel_name=tel_name,
                verified=True
            )
            user.save()
            return JsonResponse(status_code=200)
        else:
            return JsonResponse(status_code=401)
