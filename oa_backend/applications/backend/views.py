import logging

from django.contrib import auth
from django.http import JsonResponse
from django.http.response import HttpResponse
from django.views.decorators.csrf import csrf_exempt
from rest_framework import status
from rest_framework import viewsets
from rest_framework.decorators import api_view
from rest_framework.response import Response

from applications.backend.models import LdapUser
from applications.backend.serializers import Userserializer
from applications.log_manage.models import OperateLog
from libs.push_service.site_push import infopush

log = logging.getLogger('django')


def push_service_infopush(request):
    siteid = request.GET['siteid']
    data = infopush(siteid)
    return data

@api_view(['GET', 'POST'])
def test(request):
    meta = request.META
    return JsonResponse({"data":0})

@csrf_exempt
def login(request):
    # 判断请求类型
    if not request.method == "POST":
        return JsonResponse(status=status.HTTP_405_METHOD_NOT_ALLOWED, data={})
    params = request.POST
    post_code = params.get("check_code", "").lower()
    session_code = request.session.get('verifycode', "").lower()

    # 判断验证码
    if (not post_code) or (session_code != post_code):
        return JsonResponse(status=status.HTTP_417_EXPECTATION_FAILED, safe=False, data={})

    user = auth.authenticate(username=params.get("username", ""),
                             password=params.get("password", ""))

    # 用户校验
    if (not user) or (not user.is_active):
        return JsonResponse(status=status.HTTP_401_UNAUTHORIZED, data={})
    auth.login(request, user)
    OperateLog.login(request)  # 登录日志
    return JsonResponse(status=status.HTTP_200_OK, data={"id": user.id})


def logout(request):
    if not request.method == "GET":
        return JsonResponse(status=status.HTTP_405_METHOD_NOT_ALLOWED, data={})
    if request.user.is_authenticated:
        OperateLog.logout(request)  # 登出日志
    auth.logout(request)
    return HttpResponse('success', status=status.HTTP_200_OK)


class UserViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows users to be viewed or edited.
    """
    queryset = LdapUser.objects.all()
    serializer_class = Userserializer
