from django.shortcuts import render, redirect
# from hashlib import sha1
from df_user.models import Passport, Address
from django.http import JsonResponse
from django.views.decorators.http import require_GET, require_POST, require_http_methods
from utils.get_hash import get_hash
# from django.core.mail import send_mail
# from django.conf import settings
from df_user.tasks import send_register_success_mail
from utils.decorators import login_requird


# Create your views here.
@require_http_methods(['GET', 'POST'])
def register(request):
    # print(has_username)
    if request.method == 'GET':
        return render(request,
                      'df_user/register.html')
    else:
        username = request.POST.get('user_name')
        password = request.POST.get('pwd')
        email = request.POST.get('email')
        # 不存在该用户名
        Passport.objects.add_one_passport(username=username,
                                          password=password,
                                          email=email)
        send_register_success_mail(username=username,
                                   password=password,
                                   email=email)
        # send_register_success_mail.delay(username=username,
        #                                  password=password,
        #                                  email=email)
        return redirect('/user/login/')


# def register_handle(request):
#     """实现用户注册"""
#     # 1接受用户注册信息
#     username = request.POST.get('user_name')
#     password = request.POST.get('pwd')
#     email = request.POST.get('email')
#
#     spassword = sha1(password.encode()).hexdigest()
#     # ihas_username = Passport.objects.filter(username=username).count()
#     Passport.objects.add_one_passport(username=username,
#                                       password=spassword,
#                                       email=email)
#     send_register_success_mail.delay(username=username,
#                                      password=password,
#                                      email=email)
#     return redirect('/user/login/')


# def has_username(request, name):
#     # 方法1
#     # print(name)
#     # 对数据库操作放到models中
#     ihas_username = Passport.objects.filter(username=name).count()
#     # print("has_username"+str(ihas_username))
#     if (ihas_username):
#         return JsonResponse({'res': 1})
#     else:
#         return JsonResponse({'res': 0})


@require_GET
def check_user_exit(request):
    # 方法2, 通过request.get获取
    username = request.GET.get('username')
    passport = Passport.objects.get_one_passport(username=username)
    if passport:
        return JsonResponse({'res': 0})
    else:
        return JsonResponse({'res': 1})


def login(request):
    print('request.COOKIES:')
    if 'username' in request.COOKIES:
        username = request.COOKIES['username']
    else:
        username = ''
    print('request.COOKIES2:')
    return render(request,
                  'df_user/login.html',
                  {'username': username})


def login_check(request):
    # 取得输入得用户名和密码
    username = request.POST.get('username')
    password = request.POST.get('password')
    # 进行匹配
    # print("username" + username)
    # print("pas" + password)
    passport = Passport.objects.get_one_passport(username=username,
                                                 password=password)
    # print(passport)
    if passport:
        if request.session.has_key('pre_url_path'):
            next = request.session['pre_url_path']
            print('next:%s' % next)
        else:
            next = '/user/'

        jres = JsonResponse({'res': 1, 'next': next})
        remember = request.POST.get('remember')
        if remember == 'true':
            jres.set_cookie('username', username, max_age=14 * 24 * 3600)
        print("islogin_true")
        request.session['islogin'] = True
        request.session['username'] = username
        print('login_check{}'.format(passport.id))
        request.session['passport_id'] = passport.id
        return jres
    else:
        return JsonResponse({'res': 0})


def logout(request):
    # 退出用户登陆状态
    request.session.flush()
    # 跳转到首页
    return redirect('/user/')


@login_requird
def user(request):
    # 获取登陆用户的passport_id
    passport_id = request.session.get('passport_id')
    addr = Address.objects.get_one_address(passport_id=passport_id)
    return render(request,
                  'df_user/user_center_info.html',
                  {'addr': addr,
                   'page': 'user'})


@require_http_methods(['GET', 'POST'])
@login_requird
def address(request):
    # print('view_addr')
    passport_id = request.session.get('passport_id')
    print('addr_passport_id'+str(passport_id))
    if request.method == 'GET':
        addr = Address.objects.get_one_address(passport_id=passport_id)
        return render(request,
                      'df_user/user_center_site.html',
                      {'addr': addr,
                       'page': 'address'})
    else:
        recipient_name = request.POST.get('username')
        recipient_addr = request.POST.get('addr')
        zipcode = request.POST.get('zip_code')
        recipient_phone = request.POST.get('phone')
        Address.objects.add_one_address(passport_id=passport_id,
                                        recipient_name=recipient_name,
                                        recipient_addr=recipient_addr,
                                        recipient_phone=recipient_phone,
                                        zip_code=zipcode)
        # 刷新本页面
        return redirect('/user/address/')


@login_requird
def order(request):
    return render(request,
                  'df_user/user_center_order.html',
                  {'page': 'order'})


@login_requird
def index(request):
    return render(request,
                  'df_goods/index3.html',
                  )
