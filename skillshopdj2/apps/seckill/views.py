# -*- coding:utf-8 -*-
from django.shortcuts import render
from .models import *
import datetime
from django.conf import settings
import os
import sys
from django.template.loader import render_to_string
from .cache_manage import *
import pickle
import random
from .util import add_text_to_image,get_pyletter
#from io import StringIO
import io
from django.http import HttpResponse, Http404
from django.http import HttpResponseRedirect,JsonResponse
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_protect
from django.db import transaction
from account.models import BlackUser,Profile
from decimal import Decimal
from orders.models import Order, OrderItem
import qrcode
from pay.wxpay import UnifiedOrder_pub,Wxpay_client_pub,WxPayConf_pub,Wxpay_server_pub
from pay.alipay import alipay_trade_page_pay,alipay_response, alipay_notify_check,alipay_trade_query
import logging
import codecs

logger = logging.getLogger("seckill") # 为loggers中定义的名称
# Create your views here.
HTML_DIR=os.path.join(settings.BASE_DIR, 'templates/html')
EXPIREMAXTIME = 6
REQUEST_LIMITMAX = 5   #1分钟内不能超过5次请求

#MEDIA_ROOT = os.path.join(settings.BASE_DIR,'media')
MEDIA_ROOT = settings.MEDIA_ROOT

def index(request):

    # 取当天时间的
    todays = datetime.date.today()
    indexhtml = 'index_{}.html'.format(todays)
    index_html = os.path.join(HTML_DIR,indexhtml)
    if not os.path.exists(index_html) or request.user:
        if request.user:
            user = request.user
        # 分类数据
        category_key = 'category'
        category_list = getcache(category_key)
        if category_list:
            category_list = pickle.loads(category_list)
        elif category_list is None:
            category_list = Category.objects.all()
            setcache(category_key, 60 * 60, pickle.dumps(category_list))

        #商品数据
        product_list_key =  'product_list_{}'.format(todays)
        product_list = getcache(product_list_key)
        if product_list:
            product_list = pickle.loads(product_list)
        elif product_list is None:
            product_list = SaleProducts.objects.filter(startdatetime__gt=todays,
                                                       startdatetime__lt=todays + datetime.timedelta(days=1)) \
                                                       .filter(status=1)
            setcache(product_list_key, 60 * 60, pickle.dumps(product_list))


        #构造时间段列表
        hour_list= get_hourlist(product_list)
        content = render_to_string('seckill/index.html',locals())
        #with open(index_html,'w') as static_file:
        with  codecs.open(index_html, 'w', encoding='utf-8') as static_file:
            static_file.write(content)
    return render(request, index_html, locals())
    #return render(request, 'seckill/index.html', locals())
def busy(request):
    return render(request, 'seckill/busy.html', locals())
#构造时间段列表
def get_hourlist(product_list):
    hour_list = []
    starthour = 0
    if product_list:
        for product in product_list:
            if starthour != product.startdatetime.hour:
                starthour = product.startdatetime.hour
                endhour = int(starthour) + 1
                hours = {'starthour': starthour, 'endhour': endhour}
                hour_list.append(hours)
    return hour_list

# 分类
def category(request):
    # 取当天时间的
    id = request.GET.get('cateid')
    todays = datetime.date.today()
    indexhtml = 'index_{}_{}.html'.format(todays,id)
    index_html = os.path.join(HTML_DIR, indexhtml)
    # if not os.path.exists(index_html):
    #     # 分类数据
    #     category_list = Category.objects.all()
    #     # 商品数据
    #     product_list = SaleProducts.objects.filter(startdatetime__gt=todays,
    #                        startdatetime__lt=todays + datetime.timedelta(days=1)) \
    #                        .filter(status=1).filter(protduct__category=id)
    #
    #     # 构造时间段列表
    #     if product_list:
    #         hour_list = []
    #         starthour = 0
    #         for product in product_list:
    #             if starthour != product.startdatetime.hour:
    #                 starthour = product.startdatetime.hour
    #                 endhour = int(starthour) + 1
    #                 hours = {'starthour': starthour, 'endhour': endhour}
    #                 hour_list.append(hours)
    #     content = render_to_string('seckill/index.html', locals())
    #     with open(index_html, 'w') as static_file:
    #         static_file.write(content)
    if not os.path.exists(index_html) or request.user:
        if request.user:
            user = request.user
        # 分类数据
        category_key = 'category'
        category_list = getcache(category_key)
        if category_list:
            category_list = pickle.loads(category_list)
        elif category_list is None:
            category_list = Category.objects.all()
            setcache(category_key, 60 * 60, pickle.dumps(category_list))

        # 商品数据
        product_list_category_key = 'product_list_{}_{}'.format(todays,id)
        product_list = getcache(product_list_category_key)
        if product_list:
            product_list = pickle.loads(product_list)
        elif product_list is None:
            product_list = SaleProducts.objects.filter(startdatetime__gt=todays,
                                                       startdatetime__lt=todays + datetime.timedelta(days=1)) \
                .filter(status=1).filter(protduct__category=id)
            setcache(product_list_category_key, 60 * 60, pickle.dumps(product_list))

        # 构造时间段列表
        hour_list = get_hourlist(product_list)
        content = render_to_string('seckill/index.html', locals())
        #with open(index_html, 'w') as static_file:
        with  codecs.open(index_html, 'w', encoding='utf-8') as static_file:
            static_file.write(content)
    return render(request, index_html, locals())
def search(request):
    searchq = request.GET.get('searchq')
    todays = datetime.date.today()
    # 分类数据
    category_list = Category.objects.all()
    if searchq:
        product_list = SaleProducts.objects.filter(title__contains=searchq)\
                           .filter(startdatetime__gt=todays,
                           startdatetime__lt=todays + datetime.timedelta(days=1)) \
                           .filter(status=1)
    else:
        product_list = SaleProducts.objects.filter(startdatetime__gt=todays,
                           startdatetime__lt=todays + datetime.timedelta(days=1)) \
                           .filter(status=1)
    # 构造时间段列表
    hour_list = get_hourlist(product_list)
    # if product_list:
    #     hour_list = []
    #     starthour = 0
    #     for product in product_list:
    #         if starthour != product.startdatetime.hour:
    #             starthour = product.startdatetime.hour
    #             endhour = int(starthour) + 1
    #             hours = {'starthour': starthour, 'endhour': endhour}
    #             hour_list.append(hours)
    return render(request,'seckill/index.html', locals())

#商品详情页显示
def productdetail(request):
    # 初始化标识是否开始秒杀，是否过期失效均为False
    isbegin = False
    isexpire = False
    hasstockqty = True

    product_id = request.GET.get('product_id')
    product_key = 'product_{}'.format(product_id)
    product_detail = getcache(product_key)
    if product_detail:
        product_detail =  pickle.loads(product_detail)
    elif   product_detail is None:
        product_detail = SaleProducts.objects.filter(id=product_id)
        setcache(product_key,60*10,pickle.dumps(product_detail))

    stock_key = 'stock_{}'.format(product_id)
    stock_qty = getcache(stock_key)
    if stock_qty is None:
        stock_qty = product_detail[0].stock_total
        setcache(stock_key,60*10,stock_qty)
        hasstockqty = True
    else:
        if int(stock_qty) > 0:
            hasstockqty = True
        else:
            hasstockqty = False

    # 检查秒杀时间
    nowtime = datetime.datetime.now()
    # 开始时间
    startdatetime = product_detail[0].startdatetime
    # 结束时间
    enddatetime = product_detail[0].enddatetime

    diffstarttime = nowtime - startdatetime
    #失效期
    expiretime = nowtime.hour - enddatetime.hour
    # if datetime.strptime(product_detail[0].startdatetime, "%Y-%m-%d %H:%M:%S")>nowtime:
    if diffstarttime.days >= 0 and expiretime <= EXPIREMAXTIME:
        isbegin = True  # 开始
    elif diffstarttime.days < 0:
        isbegin = False  # 还未开始
    elif expiretime > EXPIREMAXTIME:  # 超过6小时间失效
        isexpire = True  # 过期

    return render(request, 'seckill/productdetail.html', locals())

def set_check(request):
    # 附机从Ziku取出一问题和答案，如无答案，则产生答案，并保存到数据库及redis缓存中
    totalcount = Ziku.objects.all().count()
    i = random.randint(1, totalcount)
    ziku = Ziku.objects.get(id=i)
    if ziku:
        answer = ziku.answer
        if not answer:
            answer = get_pyletter(ziku.qustion)
            ziku.answer = answer
            ziku.save()

        request.session['answer'] = answer
        #python2.7
        #mstream = StringIO.StringIO()
        #python3.5
        mstream = io.BytesIO()
        txt = ziku.qustion + u'拼音首字母是'
        img = add_text_to_image(txt)
        img.save(mstream, "png")
    return HttpResponse(mstream.getvalue(), "image/png")

#实时库存
def getstock(request):
    #product_id = request.REQUEST.get('product_id')
    product_id = request.POST.get('product_id')
    stock_key = 'stock_{}'.format(product_id)
    stock_qty = getcache(stock_key)
    if stock_qty:
        if int(stock_qty) > 0:
            hasstockqty = True
        else:
            hasstockqty = False
    else:
        stock_qty=0
        hasstockqty = False
    return JsonResponse({"hasstockqty": hasstockqty, "stock_qty": int(stock_qty)})

def getserverdatetime(request):
    #return datetime.datetime.now()
    return HttpResponse('ok')

@login_required
@csrf_protect
@transaction.atomic
def secaddcart(request):
    '''
    1、验证码检查
    2、检查黑名单
    3、从缓存中取秒杀商品信息
    4、检查提交时间是否在有效时间内
    5、防刷，一分钟内不能超过5次请求
    6、检查队列大小超过库存数，则直接将访问转移
    7、秒杀修改库存
    8、生成订单、修改数据库库存
    :param request:
    :return:
    '''
    try:
        product_id = request.POST.get('product_id')
        quantity = request.POST.get('amount')
        answer = request.POST.get('answer')
        # posttime = request.POST.get('posttime') #不能取提交过来的时间，应取服务器时间
        posttime = datetime.datetime.now()
        que_user = str(request.user.id)
        isjoin = OrderItem.objects.filter(product_id=product_id).filter(order__user=request.user).exists()
        if isjoin:
            msg = u'已参与！不能再参加'
            status = 300
            orderid = -1
        else:
            # 验证码检查
            if answer == request.session['answer']:
                # 检查黑名单
                check_blackuser = BlackUser.objects.filter(user=request.user).exists()
                if check_blackuser:
                    msg = u'系统忙！请重试'
                    status = 300
                    orderid = -1
                else:
                    # 保存秒杀商品信息key
                    procut_key = 'procut_{}'.format(product_id)
                    # 从缓存中取秒杀商品信息
                    product_detail = getcache(procut_key)
                    if product_detail:
                        # 对取出的值进行转化，pickle.loads取出值 对象化
                        product_detail = pickle.loads(product_detail)
                    elif product_detail is None:
                        # 如无值，从数据库取值
                        product_detail = SaleProducts.objects.filter(id=product_id)
                        # pickle.dumps将list对象序列化后保存到redis缓存
                        product_detail_to = pickle.dumps(product_detail)
                        setcache(procut_key, 60 * 5, product_detail_to)

                    # 检查提交时间是否在有效时间内
                    # 开始时间
                    startdatetime = product_detail[0].startdatetime
                    # 结束时间
                    enddatetime = product_detail[0].enddatetime
                    diffstarttime = posttime - startdatetime
                    diffendtime = enddatetime - posttime
                    expiretime = posttime.hour - enddatetime.hour
                    # 时间验证，提交的时间必须在开始时间和6小时之内
                    if diffstarttime.days >= 0 and expiretime < EXPIREMAXTIME:
                        session_key = request.session.session_key
                        ua_key = 'user_{}'.format(session_key)
                        # 防刷，一分钟内不能超过5次请求
                        if check_request_limit(ua_key, REQUEST_LIMITMAX):
                            # 保存秒杀商品库存key
                            key_stock = 'stock_{}'.format(product_id)
                            # 定义队列key
                            queue_procut_key = 'queue_' + procut_key
                            # 取出当时缓存库存
                            stock_qty = int(getcache(key_stock))
                            # 检查队列大小，如不符合，则不进队列
                            # 取队列大小
                            total_quesize = queuesize(queue_procut_key)
                            # 假如检查队列大小超过库存数，则直接将访问转移
                            if total_quesize > 2 * stock_qty:
                                msg = u'系统忙！请重试'
                                status = 300
                                orderid = -1
                            else:
                                # 入队列排队
                                setqueue(queue_procut_key, que_user)
                                price = product_detail[0].price
                                if update_stock(key_stock, product_id, request.user.id, quantity, price):
                                    # 增加事务，产生订单时必须保持事务一致
                                    with transaction.atomic():
                                        # 队列取出一位
                                        # user=que_cart.get()
                                        user = popqueue
                                        amount = Decimal(int(quantity) * price)
                                        profile = Profile.objects.get(user_id=request.user.id)
                                        product = SaleProducts.objects.get(id=product_id)
                                        order = Order.objects.create(user=request.user, status='2', amount=amount,
                                                                      name=request.user.username,
                                                                      email=request.user.email,
                                                                      mobile=profile.moible, address=profile.address)
                                        OrderItem.objects.create(order=order,
                                                                  product=product,
                                                                  price=price,
                                                                  quantity=quantity)
                                        stock_qty = getcache(key_stock)
                                        # 更改库存
                                        product.stock_total = stock_qty
                                        product.save()

                                        status = 200
                                        orderid = order.id
                                        msg = u'生成订单'
                                else:
                                    msg = u'库存不足'
                                    status = 300
                                    orderid = -1
                        else:
                            msg = u'请求次数超过{}次'.format(REQUEST_LIMITMAX)
                            status = 300
                            orderid = -1
                    else:
                        msg = u'时间不正确'
                        status = 300
                        orderid = -1
            else:
                msg = u'验证码不正确'
                status = 300
                orderid = -1
    except Exception as e:
        logger.info(e)
        status = 400
        orderid = -1
        msg = u'数据错误，联系管理员'
    return JsonResponse({"status": status, "msg": msg, "orderid": orderid})


@login_required
@csrf_protect
def paychoice(request):
    order_id = request.GET.get('order_id')
    order=Order.objects.get(id=order_id)
    return render(request, 'pay/pay.html', locals())

def paying(request):
    try:
        order_id = int(request.POST.get("order_id"))
        pay_type = int(request.POST.get("pay_type"))
        pay_amount = Decimal(request.POST.get("pay_amount"))

    except ValueError:
        raise Http404(u"参数错误，请求支付失败！")
    result_src = ""
    order = Order.objects.get(id=order_id)
    realpayamount = order.amount
    # 判断支付金额是否一致

    if pay_amount == realpayamount and pay_amount > 0:
        user_id = request.user.id
        # subject = '秒杀商品:' + order.get_productname[0]
        subject = '秒杀商品:'
        if order.status == '2':
            try:
                if pay_type == 1:
                    # 微信支付
                    # result_src = paying_for_weixin_pay(request,order_id,user_id ,realpayamount)
                    result_src = paying_code_weixin_pay(order_id, user_id)
                    url = "/wxpaying?order_id=" + str(order_id) + "&result_src=" + result_src+ "&amount=" + str(realpayamount)
                    return JsonResponse({'result': "success", 'msg': u"请求微信支付页面成功!", 'url': url})
                elif pay_type == 2:
                    # 支付宝即时到帐支付
                    url = alipay_trade_page_pay(order_id, subject, realpayamount)
                    return JsonResponse({'result': "success", 'msg': u"请求支付宝支付页面成功!", 'url': url})
            except Exception as e:
                logger.info(e)
                return JsonResponse({'result': "failed", 'msg': u"订单信息异常,不能支付!", 'url': ''})

 # 微信支付,生成支付二维码 ,模式二,先生成预支付单,根据返回的code_url生成二维码
def paying_code_weixin_pay(orderid, user_id):
    """
    微信支付,生成支付二维码
    :param orderid:
    :param user_id:
    :return:    """

    # 定义变量
    result_src = ""  # 存储路径
    newresult_src = ""  # 访问的路径
    try:
        #生成预支付单
        str_url = getcode_url(orderid)
        #app_path = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        #media_path = os.path.join(app_path, 'media')
        media_path = settings.MEDIA_ROOT
        if str_url:
            img = qrcode.make(str_url)
            curDateTime = datetime.datetime.now().strftime('%Y%m%d%H%M%S')
            randNum = random.randint(1000, 9999)
            mch_vno = curDateTime + str(randNum) + str(orderid)
            #path = settings.MEDIA_ROOT + 'qrcode'
            path =os.path.join(media_path, 'qrcode')
            logger.info(path)
            if not os.path.exists(path):
                os.makedirs(path)
            result_src = os.path.join(path, mch_vno + ".png")
            logger.info(result_src)
            #newresult_src = settings.MEDIA_URL + os.path.join('qrcode', mch_vno + ".png")
            newresult_src = os.path.join(settings.MEDIA_URL,os.path.join('qrcode', mch_vno + ".png"))
            img.save(result_src)
        else:
            return u'订单不存在'
    except Exception as e:
        logger.info(e)
    return newresult_src

# 微信支付,生成预支付单,并返回code_url
def getcode_url(orderid):
    try:
        unifiedorder_pub = UnifiedOrder_pub()

        corder = Order.objects.get(id=int(orderid))
        total_fee = 0
        if corder:
            total_fee = corder.amount * 100  # 实际支付金额,微信需以整数,单位为分
            #body = corder.get_productname[0]
            body = 'seckill'
            if len(body) > 127:
                body = body[0:127]

            unifiedorder_pub.setParameter("body", body)
            out_trade_no = create_TradeId(orderid)
            unifiedorder_pub.setParameter("out_trade_no", out_trade_no)
            unifiedorder_pub.setParameter("detail", body)
            #unifiedorder_pub.setParameter("total_fee", str(total_fee))
            unifiedorder_pub.setParameter("total_fee", "1")
            unifiedorder_pub.setParameter("trade_type", "NATIVE")
            #生成预支付单
            prepay_id, url = unifiedorder_pub.getPrepayId()
            # print url
            if url:
                return url
    except Exception as e:
        logger.info(e)
        return False
#返回一个唯一数
def create_TradeId(pid):
    """
    返回一个唯一数
    :param pid:
    :return:
    """
    curDateTime=datetime.datetime.now().strftime('%Y%m%d')
    mch_vno = curDateTime +  str(pid)
    return mch_vno

##微信支付:获取原始的订单号
def recovery_order_id(out_trade_id):
    """
    获取原始的订单号
    :param out_trade_id:
    :return:
    """
    if out_trade_id and len(out_trade_id)>18:
        oid=out_trade_id[18:len(out_trade_id)]
    else:
        oid="0"
    return oid

#微信支付,显示支付二维码页面
@login_required
@csrf_protect
def paying_for_weixin_pay(request):
    """
    微信支付,生成支付二维码
    :param orderid:
    :param user_id:
    :return:    """

    #定义变量
    result_src="" #存储路径
    newresult_src="" #访问的路径
    try:
        order_id = int(request.POST.get("order_id"))
        newresult_src = request.POST.get("result_src")
        pay_amount = request.POST.get("amount")
        orderid = str(order_id)
        buy_title =  '秒杀商品:'

       # newresult_src = settings.MEDIA_URL + result_src

    except Exception as e :
        logger.info(e)

    #return newresult_src
    return render(request, 'pay/wxpay.html', locals())

#微信支付:用户支付完成后,回写系统数据
@csrf_protect
def native_notify(request):
    """
    微信支付成功后接到微信发回的通知，在确认通知成功后，进行业务处理
    <xml>
  <appid><![CDATA[wx2421b1c4370ec43b]]></appid>
  <attach><![CDATA[支付测试]]></attach>
  <bank_type><![CDATA[CFT]]></bank_type>
  <fee_type><![CDATA[CNY]]></fee_type>
  <is_subscribe><![CDATA[Y]]></is_subscribe>
  <mch_id><![CDATA[10000100]]></mch_id>
  <nonce_str><![CDATA[5d2b6c2a8db53831f7eda20af46e531c]]></nonce_str>
  <openid><![CDATA[oUpF8uMEb4qRXf22hE3X68TekukE]]></openid>
  <out_trade_no><![CDATA[1409811653]]></out_trade_no>
  <result_code><![CDATA[SUCCESS]]></result_code>
  <return_code><![CDATA[SUCCESS]]></return_code>
  <sign><![CDATA[B552ED6B279343CB493C5DD0D78AB241]]></sign>
  <sub_mch_id><![CDATA[10000100]]></sub_mch_id>
  <time_end><![CDATA[20140903131540]]></time_end>
  <total_fee>1</total_fee>
  <trade_type><![CDATA[JSAPI]]></trade_type>
  <transaction_id><![CDATA[1004400740201409030005092168]]></transaction_id>
</xml>
    """
    global lock,dish

    #接收微信发回的通知
    postdata = request.body
    #微信操作类
    wxpayconf_pub= WxPayConf_pub()
    wxpay_server_pub=Wxpay_server_pub()
    wxpay_server_pub.saveData(postdata)
    #wechatpush=WechatPush(wxpayconf_pub.APPID,wxpayconf_pub.APPSECRET)

    #通过微信签名
    if wxpay_server_pub.checkSign():
        dicwxBack=wxpay_server_pub.getData()
        if dicwxBack and dicwxBack.has_key("return_code"):
            if dicwxBack["return_code"]=="SUCCESS":
                if dicwxBack["result_code"]=="SUCCESS":
                    out_trade_no=dicwxBack["out_trade_no"]
                    dicBack = {}
                    dicBack['trade_type']="wx"
                    dicBack['out_trade_no'] = recovery_order_id(out_trade_no)
                    dicBack['trade_no'] = dicwxBack["transaction_id"]
                    dicBack['total_amount'] = dicwxBack["total_fee"]
                    dicBack['desc'] = dicwxBack["attach"]
                    dicBack['auth_token'] = dicwxBack["openid"]
                    dicBack['PAYTYPE'] = 1  # u'订单'
                    dicBack['PAYSOURCE'] = 2  # u'微信支付'
                    dicBack['PAYSTATUS'] = 3  # u'支付
                    oid_str= recovery_order_id(out_trade_no)
                    if oid_str:
                        oid=int(oid_str)
                        if int(oid)>0:
                            lock.acquire() # 从这里进入线程安全区
                            corder=Order.objects.get(id=int(oid))
                            lock.release() # 从这里离开线程安全区
                            if corder:
                                if corder.status=='2' :
                                    #－－－支付成功后的业务逻辑－－－
                                    flag,description=pay_success_commit_corder(request,corder.id, dicBack)
                                else:
                                    return HttpResponse("SUCCESS")
                            else:
                                return HttpResponse("FAILED")
                        else:
                            return HttpResponse("FAILED")
            if dicBack["return_code"]=="FAIL":
                return HttpResponse("FAILED")

    else:
        return HttpResponse("FAILED")


#支付成功后回写订单
def pay_success_commit_corder(request,order_id, dicBack):
        """
        支付成功后的业务处理
        主要分为购买订单后的业务处理
        #1、业务 更新订单状态和交易号、交易时间等信息、推荐人。
        :param corder:
        :param dicBack:
        orderSTATUS = (('1', u'生成'),('0', u'取消'), ('2', u'待支付'),('3', u'已支付'),('4', u'退款'), ('5', u'评价'),)
        :return:
        """
        flag = False
        order = Order.objects.get(id=int(order_id))

        #判断支付金额与订单须支付金额相等
        if order.amount== dicBack["total_amount"]:
            with transaction.atomic():
                if order.status == '2':
                    reply_dump = u'交易单号：'+dicBack["trade_no"]+u'支付类型：'+dicBack["trade_type"]+u'支付金额：'+str(dicBack["total_amount"])+u'支付人：'+dicBack['auth_token']
                    reference_number = dicBack["trade_no"]
                    # 1、业务 更新订单状态和交易号、交易时间等信息。
                    order=Order.objects.filter(id=int(order_id)).update(reply_dump=reply_dump,reference_number=reference_number,status='3')
                    return  True,order
                else:
                    return False

#支付宝支付 同步
@login_required
@csrf_protect
def alipay_success(request):
    """
    GET传递参数 同步
    1.用户在登录成功后会看到一个支付宝提示登录的页面，该页面会停留几秒，然后会自动跳转回商户指定的同步通知页面（参数return_url）。
    2.该页面中获得参数的方式，需要使用GET方式获取，如request.QueryString(“out_trade_no”)、$_GET[‘out_trade_no’]。后续商户可根据获取的信息作处理，譬如，可以把获取到的token放入session中，以便于后续需要使用到token访问支付宝相应服务时，可以便捷地重用。
    3.该方式仅仅在用户登录完成以后进行自动跳转，因此只会进行一次。
    4.该方式不是支付宝主动去调用商户页面，而是支付宝的程序利用页面自动跳转的函数，使用户的当前页面自动跳转。
    5.该方式可在本机而不是只能在服务器上进行调试。
    6.返回URL只有一分钟的有效期，超过一分钟该链接地址会失效，验证则会失败。
    7.设置页面跳转同步通知页面（return_url）的路径时，不要在页面文件的后面再加上自定义参数。
    8.由于支付宝会对页面跳转同步通知页面（return_url）的域名进行合法有效性校验，因此设置页面跳转同步通知页面（return_url）的路径时，不要设置成本机域名，也不能带有特殊字符（如“!”），如：
    买家付款成功后，如果接口中指定有return_url,买家付完款后会调到return_url所在的页面。
    这个页面可以展示给客户看。这个页面只有付款成功后才会跳转。
    ?is_success=T //表示接口调用是否成功，并不表明业务处理结果。
    """


    if alipay_response(request.GET):
        out_trade_no=request.GET.get("out_trade_no","")
        trade_no=request.GET.get("trade_no")
        total_amount=request.GET.get("total_amount")
        auth_token = request.GET.get("auth_token","")
        dicBack={}
        dicBack['out_trade_no']=out_trade_no
        dicBack['trade_no']=trade_no
        dicBack['total_amount']=total_amount
        dicBack['desc'] = request.GET.get("subject","")
        dicBack['trade_type']="alipay"
        dicBack['auth_token'] = auth_token
        dicBack['PAYTYPE'] = 1   #u'订单'
        dicBack['PAYSOURCE'] = 4  #u'支付宝支付'
        dicBack['PAYSTATUS'] = 1  #u'支付'

        flag,order = pay_success_commit_corder(request,out_trade_no, dicBack)
        orderitem=OrderItem.objects.filter(order_id=order.id)
        if flag :
            context = {
                'order': order,
                'orderitem': orderitem,
                'currency_symbol': settings.PAID_COURSE_REGISTRATION_CURRENCY[1],
            }
            return render(request,'paidsuccess.html', context)

    else:
       pass

#支付宝支付 异步
@login_required
@csrf_protect
def alipay_async_notify(request):
    """
     服务器后台通知，买家付完款后，支付宝会调用notify_url这个页面所在的页面，并把相应的参数传递到这个页面，
     这个页面根据支付宝传递过来的参数修改网站订单的状态。
     更新完订单后需要在页面上打印一个success给支付宝，如果反馈给支付宝的不是success,支付宝会继续调用这个页面。
     传递过来的参数是post格式
     商户需要验证该通知数据中的out_trade_no是否为商户系统中创建的订单号，
     并判断total_fee是否确实为该订单的实际金额（即商户订单创建时的金额），
     同时需要校验通知中的seller_id（或者seller_email) 是否为out_trade_no这笔单据的对应的操作方（有的时候，一个商户可能有多个seller_id/seller_email），
     上述有任何一个验证不通过，则表明本次通知是异常通知，务必忽略。
     在上述验证通过后商户必须根据支付宝不同类型的业务通知，正确的进行不同的业务处理，并且过滤重复的通知结果数据。
     在支付宝的业务通知中，只有交易通知状态为TRADE_SUCCESS或TRADE_FINISHED时，支付宝才会认定为买家付款成功。
     如果商户需要对同步返回的数据做验签，必须通过服务端的签名验签代码逻辑来实现。
     如果商户未正确处理业务通知，存在潜在的风险，商户自行承担因此而产生的所有损失。

    """

    if alipay_notify_check(request.GET):
        out_trade_no = request.GET.get("out_trade_no", "")
        trade_no = request.GET.get("trade_no")
        total_amount = request.GET.get("total_amount")
        auth_token = request.GET.get("auth_token", "")
        dicBack = {}
        dicBack['out_trade_no'] = out_trade_no
        dicBack['trade_no'] = trade_no
        dicBack['total_amount'] = total_amount
        dicBack['desc'] = request.GET.get("subject", "")
        dicBack['trade_type'] = "alipay"
        dicBack['auth_token'] = auth_token
        dicBack['PAYTYPE'] = 1  # u'订单'
        dicBack['PAYSOURCE'] = 4  # u'支付宝支付'
        dicBack['PAYSTATUS'] = 1  # u'支付'
        #对后台数据处理
        flag, order = pay_success_commit_corder(request, out_trade_no, dicBack)
        if flag:
            return HttpResponse("success")
        else:
            return HttpResponse("fail")
    else :
        return HttpResponse ("fail")
