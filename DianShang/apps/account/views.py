# -*- coding:utf-8 -*-
from django.http import HttpResponse,JsonResponse
from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .forms import LoginForm, UserRegistrationForm
from .models import Profile,UserFav,UserAddress,Provinces,Areas,Cities,UserMessage
from orders.models import Order, OrderItem
from shop.models import Product
from coupons.models import CouponRedemption
from comments.models import Comments,Tag,Commentspic
from cart.models import Cart
# from cart.cart import Cart
from datetime import datetime
from django.urls import reverse
from django.conf import settings
from c_tasks import tasks
from django.core.mail import send_mail
from rest_framework.authtoken.models import Token
from rest_framework.authentication  import authenticate as authenticatetoken
from shop.cache_manager import setcache,getcache
'''
在Django内置认证系统中，会使用session和中间件来拦截请求中的request对象到认证系统中。
它们在每个请求上提供一个request.user属性，表示当前的用户。
若当前的用户没有登入，该属性将设置成AnonymousUser的一个实例，否则它将是User的实例。
我们可以在模板文件中通过is_authenticated()来判断用户是否认证，
'''
def user_login(request):
    # 获取用户登录之前访问的url地址，默认跳转到首页
    redirect_url = request.POST.get('next', request.GET.get('next', ''))
    if request.method == 'POST':
        # 1.接收参数
        form = LoginForm(request.POST)
        # 2.参数校验(后端校验)
        if form.is_valid():
            cd = form.cleaned_data
            # 3.业务处理：登录校验
            user = authenticate(username=cd['username'], password=cd['password'])
            if user is not None:
                # 用户已激活
                if user.is_active:
                    # 记住用户的登录状态，Django提供了login()`数来完成，它接受一个HttpRequest对象和一个User对象，
                    # 然后利用Django的session框架将用户ID保存到session中。
                    login(request, user)
                    token = Token.objects.get_or_create(user=user)
                    # 存储到缓存中
                    TIME_OUT = 24 * 60 * 60
                    setcache(user.username, token, TIME_OUT)
                    #return HttpResponse('Authenticated successfully')
                    if redirect_url:
                        return redirect(redirect_url)
                    else:
                        # 跳转到首页
                        return redirect('/')
                else:
                    return HttpResponse('帐户名或密码错')
            else:
                return HttpResponse('帐户名或密码错')
    else:
        form = LoginForm()
    return render(request, 'account/login.html', {'form': form})


def register(request):
    if request.method == 'POST':
        user_form = UserRegistrationForm(request.POST)

        if user_form.is_valid():
            # Create a new user object but avoid saving it yet

            new_user = user_form.save(commit=False)
            # Set the chosen password
            new_user.set_password(user_form.cleaned_data['password'])
            if new_user.email is None:
               new_user.email = new_user.username
            # Save the User object
            new_user.save()
            # Create the user profile
            profile = Profile.objects.create(user=new_user)

            # 对用户的身份信息进行加密，生成激活token信息
            token = Token.objects.create(user=new_user)
            login(request, new_user)
            # 存储到缓存中
            TIME_OUT = 24*60*60
            setcache(new_user.username, token, TIME_OUT)

            #邮件信息
            subject = '电商平台欢迎你'
            message = 'test'
            sender = settings.EMAIL_FROM
            receiver = ['18922709290@189.cn']
            html_message = """
                        <h1>%s, 欢迎您注册会员</h1>
                        请点击一下链接激活您的账号(24小时之内有效)<br/>
                        <a href="http://127.0.0.1:8001/active/?key=%s">http://127.0.0.1:8001/active/?key=%s</a>
                    """ % (new_user.username, token, token)

            # 发送激活邮件
            # send_mail(subject='邮件标题',
            #           message='邮件正文',
            #           from_email='发件人',
            #           recipient_list='收件人列表')
            i=send_mail(subject, message, sender, receiver, html_message=html_message)
            #tasks.send_register_active_email.delay(new_user.email, new_user.username, token.key)

            return render(request,
                          'account/register_done.html',
                          {'new_user': new_user})
    else:
        user_form = UserRegistrationForm()
    return render(request, 'account/login.html', {'user_form': user_form})

# 注销
def do_logout(request):
    try:
        # 清除用户登录状态,内置的logout函数会自动清除当前session
        logout(request)
    except Exception as e:
        pass
        #logger.error(e)
    return redirect(request.META['HTTP_REFERER'])
def updateuserinfo(request):
    userprofile = Profile.objects.filter(user=request.user)
    if request.method == 'POST':
        date_of_birth = request.POST.get('date_of_birth')
        photo = request.POST.get('128img')
        # photo = request.FILES['128img']
        gender = request.POST.get('gender')
        mobile = request.POST.get('mobilephone')
        email = request.POST.get('infoemail')
        username = request.POST.get('rname')
        userprofile = userprofile.update(date_of_birth=date_of_birth, photo=photo, gender=gender, mobile=mobile,
                                         email=email)
    else:
        userprofile = Profile.objects.get(user=request.user)

    return render(request, 'account/userinfo.html', locals())

# 激活
def Active(request):
    """激活"""

    key = request.GET.get('key')
    try:
        # 解密
        #token = Token.objects.select_related('user').get(key=key)
        token = Token.objects.get(key=key)
        user_id = token.user_id
        username = token.user.username
        #user = authenticatetoken(key)
        # 获取待激活用户id
        #user_id = user[0]

        #从缓存中取出此用户的token
        last_token = getcache(username).decode("utf-8")
        if last_token:
            if  last_token == key:
                # 激活用户
                user = User.objects.get(id=user_id)
                user.is_active = 1
                user.save()
            else :
                return HttpResponse('激活链接已失效')
        # 跳转登录页面
        return redirect(reverse('login'))
    except Exception as e:
        # 激活链接已失效
        # 实际开发: 返回页面，让用户点击链接再发激活邮件
        return HttpResponse('激活链接已失效')

@login_required
def address(request):
    id = request.GET.get('id')
    action = request.GET.get('action')
    flag = request.GET.get('flag')

    if id and action =='del':
        address = UserAddress.objects.filter(id=id).delete()

    if id and action == 'update' and flag == '1':
        address = UserAddress.objects.filter(id=id).update(flag=1)
    if id and action == 'update':
        address = UserAddress.objects.get(id=id)

    address_list= UserAddress.objects.filter(user=request.user)
    provinces = Provinces.objects.all()

    if request.method == 'POST':
        id = request.POST.get('id')
        provinces = Provinces.objects.get(province_code=request.POST.get('province'))
        city = Cities.objects.get(city_code=request.POST.get('city'))
        area = Areas.objects.get(area_code=request.POST.get('district'))
        straddress = request.POST.get('addressDetail')
        signername = request.POST.get('fullName')
        post = request.POST.get('post')
        mobile = request.POST.get('mobile')
        tel = request.POST.get('phoneCode')
        flag = request.POST.get('defaultAddress',0)
        if id :
            address = UserAddress.objects.filter(id=id).update(provinces=provinces, city=city,area=area,address=straddress,
                                        signername=signername,post=post,mobile=mobile,tel=tel,flag=flag)
        else :
            address = UserAddress(user=request.user,provinces=provinces, city=city,area=area,address=straddress,
                                        signername=signername,post=post,mobile=mobile,tel=tel,flag=flag)
            address.save()

    return render(request, 'account/address.html',locals())


#获得省份
def getProvince(request):
     provinces = Provinces.objects.all()
     res = []
     for i in provinces:
         res.append( [i.province_code , i.province] )
     return JsonResponse({'provinces':res})

#获得城市
def getCity(request):
     province_code = request.GET.get('province_code')
     cities = Cities.objects.filter(province_code=province_code)
     res = []
     for i in cities:
         res.append([i.city_code, i.city])
     return JsonResponse({'cities':res})

#获得区 县
def getAreas(request):
     city_code = request.GET.get('city_code')
     areas = Areas.objects.filter(city_code=city_code)
     res = []
     for i in areas:
         res.append([i.area_code, i.area])
     return JsonResponse({'district': res})



@login_required
def updatepassword(request):
    user = User.objects.get(id=request.user.id)
    oldpwd = request.POST.get('oldpassword')
    newpwd = request.POST.get('newpassword')

    user = authenticate(username=user.username, password=oldpwd)
    if user is  None:
        status = 501
        msg = '原密码错误'
    if user :
        user.set_password(newpwd)
        user.save()
        status = 200
        msg = '密码修改成功'
    return render(request, 'account/updatepassword.html', locals())
@login_required
def myscore(request):
    pass

@login_required
def myorder(request):
    status = request.GET.get('status')
    order_id  = request.GET.get('order_id')
    flag = request.GET.get('flag')
    orders = Order.objects.filter(user=request.user)
    #取消订单（购物车）
    if flag == 'cancel' and order_id:
        orders = orders.filter(id=order_id).update(status=0)
    if status :
        orders = orders.filter(status=status)

    order_items = OrderItem.objects.filter(order__in=orders)
    return render(request, 'account/myorder.html', locals())
@login_required
def mycart(request):
    status = 1 #购物车

    cart_list =  Cart.objects.get_cart_list(request.user)

    return render(request, 'account/mycart.html', locals())

@login_required
def coupon(request):
    coupon = CouponRedemption.objects.filter(user=request.user)
    return render(request, 'account/mycoupon.html', locals())

@login_required
def mymessage(request):
    usermessage = UserMessage.objects.filter(user=request.user)

    return render(request, 'account/mymessage.html', locals())
@login_required
def myfav(request):
    userfav = UserFav.objects.filter(user=request.user)

    return render(request, 'account/myfav.html', locals())

def decode_base64_file(data):

    def get_file_extension(file_name, decoded_file):
        import imghdr

        extension = imghdr.what(file_name, decoded_file)
        extension = "jpg" if extension == "jpeg" else extension

        return extension

    from django.core.files.base import ContentFile
    import base64
    import six
    import uuid

    # Check if this is a base64 string
    if isinstance(data, six.string_types):
        # Check if the base64 string is in the "data:" format
        if 'data:' in data and ';base64,' in data:
            # Break out the header from the base64 content
            header, data = data.split(';base64,')

        # Try to decode the file. Return validation error if it fails.
        try:
            decoded_file = base64.b64decode(data)
        except TypeError:
            TypeError('invalid_image')

        # Generate file name:
        file_name = str(uuid.uuid4())[:12] # 12 characters are more than enough.
        # Get the file name extension:
        file_extension = get_file_extension(file_name, decoded_file)

        complete_file_name = "%s.%s" % (file_name, file_extension, )

        return ContentFile(decoded_file, name=complete_file_name)

@login_required
def mycomment(request):
    order_id = request.GET.get('order_id')
    flag = request.GET.get('flag')
    #orders = Order.objects.filter(id=order_id,user=request.user)
    tag_list = Tag.objects.all()

    orders = OrderItem.objects.filter(order=order_id)[0:1]
    if request.method == 'POST':
        order_id = request.POST.get('order_id')
        order = Order.objects.get(id=order_id)
        product_id = request.POST.get('product_id')
        product = Product.objects.get(id=product_id)
        tags = request.POST.get('select_tag')

        comment=Comments.objects.get_or_create(content = request.POST.get('content',''),
            date_publish = datetime.now(),
            user = request.user,
            email = request.user.email,
            order = order,
            product = product,
            is_showname = request.POST.get('is_showname',''),
            is_good = request.POST.get('is_good',''),
            star_count = request.POST.get('star_count','')
        )
        #写评价标签
        for tagid in list(tags):
            if tagid != ',':
                tag = Tag.objects.get(id=tagid)
                comment[0].tag.add(tag)
                comment[0].save()
        #修改订单状态 #（1、购物车2、待支付3、已购买4、已评介5、已退款0、已取消）
        order.status = '4'
        order.save()
        msg=u'评价成功！'
        redirect(myorder)
        return redirect(reverse('myorder'))

    return render(request, 'account/comments.html', locals())