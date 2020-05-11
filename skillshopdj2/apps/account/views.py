# -*- coding:utf-8 -*-
from django.http import HttpResponse,JsonResponse
from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import Profile,BlackUser
from django.views.decorators.csrf import csrf_protect
import json
from .util import create_validate_code
#from six  import StringIO
import io
from .forms import *

@csrf_protect
def ajax_login(request):
    '''
    1、获取JSON数据，并分解出来相关的数据
    2、验证码验证
    3、用户信息验证
    4、登录
    5、返回jsonreponse

    :param request:
    :return:
    '''
    redirect_url = request.META.get('HTTP_REFERER', request.GET.get('HTTP_REFERER', ''))
    # 只有当请求为 POST 时，才表示用户提交了信息
    if request.method == 'POST':
        #json_data = json.loads(request.body)
        request_data = request.body.decode('utf-8')
        json_data = json.loads(request_data)
        name = json_data["name"]
        username = json_data["username"]
        password = json_data["password"]
        checkcode = json_data["checkcode"]
        if checkcode.upper() != request.session['valicode'].upper():
            result = 'failed'
            msg = u"注册码不正确"
            status = 401
        else:
            user = authenticate(username=username, password=password)
            if user is not None:
                    login(request, user)
                    #跳转
                    result='sucess'
                    status = 200
                    msg = u'sucess'
                    redirect_url = redirect_url
            else:
                result = 'failed'
                msg = u"密码或者用户名不正确"
                status = 401
    else:
        result = 'failed'
        msg = u"密码或者用户名不正确"
        status = 401
    return JsonResponse({'result': result,'status': status, 'msg': msg, 'redirect_url': redirect_url})
def valicode(request):
    #python2.7
    #mstream = StringIO.StringIO()
    #mstream = io.StringIO()
    #python3.5
    mstream = io.BytesIO()
    validate_code = create_validate_code()
    img = validate_code[0]
    img.save(mstream, "GIF")

    request.session['valicode'] = validate_code[1]

    return HttpResponse(mstream.getvalue(), "image/gif")
@csrf_protect
def ajax_register(request):
  '''
    1、获取JSON数据，并分解出来相关的数据
    2、验证码验证
    3、注册、保存到user,然后设置密码 ，同时profile插入一记录
    4、登录
    5、返回jsonreponse
  :param requst:
  :return:
  '''
  redirect_url = request.META.get('HTTP_REFERER', request.GET.get('HTTP_REFERER', ''))
  try:
        # 只有当请求为 POST 时，才表示用户提交了注册信息
        if request.method == 'POST':
            json_data = json.loads(request.body)
            name = json_data["name"]
            username = json_data["username"]
            password = json_data["password"]
            checkcode = json_data["checkcode"]
            if checkcode.upper() != request.session['valicode'].upper():
                result = 'failed'
                msg = u"注册码不正确"
            else:
                new_user = User(username=username, email=name, password=password, is_active=1)
                new_user.save()
                # Set the chosen password
                new_user.set_password(password)
                # Save the User object
                new_user.save()
                Profile.objects.create(user=new_user)
                # 重登录
                user = authenticate(username=username, password=password)
                login(request, user)
                redirect_url = redirect_url
                result = 'success'
                status = 200
                msg = u"注册成功"
        else:
            result = 'failed'
            status = 401
            msg = u"注册不成功"
  except Exception as e:
        print(e)
    # return render(request, 'account/register.html', {'user_form': user_form, 'next': redirect_to})
  return JsonResponse({'result': result, 'status': status, 'msg': msg, 'redirect_url': redirect_url})
# 注销
def do_logout(request):
    try:
        logout(request)
    except Exception as e:
        print(e)
        # logger.error(e)
    return redirect(request.META['HTTP_REFERER'])
@login_required
def edit(request):
    if request.method == 'POST':
        user_form = UserEditForm(instance=request.user,
                                 data=request.POST)
        profile_form = ProfileEditForm(instance=request.user.profile,
                                       data=request.POST,
                                       files=request.FILES)
        if user_form.is_valid() and profile_form.is_valid():
            user_form.save()
            profile_form.save()
            messages.success(request, 'Profile updated successfully')
        else:
            messages.error(request, 'Error updating your profile')
    else:
        user_form = UserEditForm(instance=request.user)
        profile_form = ProfileEditForm(instance=request.user.profile)
    return render(request, 'account/edit.html', {'user_form': user_form,
                                                 'profile_form': profile_form})

@csrf_protect
@login_required
def password_change(request):

    if request.method == "POST":
        form = PasswordchangeForm(user=request.user, data=request.POST)
        if form.is_valid():
            form.save()
            msg='密码修改成功！'
            return render(request, 'account/password_change_form.html',locals())
    else:
        form = PasswordchangeForm(user=request.user)
        context = {
            'form': form,
        }

    return  render(request, 'account/password_change_form.html', context,)