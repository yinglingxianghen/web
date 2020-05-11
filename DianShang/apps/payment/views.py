from decimal import Decimal
import os
import random
import datetime
from django.conf import settings
from django.http import HttpResponse, Http404,JsonResponse
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_protect
from django.shortcuts import render, get_object_or_404
#from paypal.standard.forms import PayPalPaymentsForm
from orders.models import Order,OrderItem
from django.views.decorators.csrf import csrf_exempt
from decimal import Decimal
from pay.alipay import alipay_trade_page_pay,alipay_response, alipay_notify_check,alipay_trade_query
from pay.wxpay import Common_util_pub,WxPayConf_pub, UnifiedOrder_pub
from pay.wxpay import NativeCall_pub,NativeLink_pub,Wxpay_server_pub, OrderQuery_pub
import qrcode
from django.db import transaction

@csrf_exempt
def payment_done(request):
    return render(request, 'payment/done.html')


@csrf_exempt
def payment_canceled(request):
    return render(request, 'payment/canceled.html')
    

def payment_process(request):
    order_id = request.session.get('order_id')
    order = get_object_or_404(Order, id=order_id)
    host = request.get_host()

    paypal_dict = {
        'business': settings.PAYPAL_RECEIVER_EMAIL,
        'amount': '%.2f' % order.get_total_cost().quantize(Decimal('.01')),
        'item_name': 'Order {}'.format(order.id),
        'invoice': str(order.id),
        'currency_code': 'USD',
        # 'notify_url': 'http://{}{}'.format(host, reverse('paypal-ipn')),
        # 'return_url': 'http://{}{}'.format(host, reverse('payment:done')),
        # 'cancel_return': 'http://{}{}'.format(host, reverse('payment:canceled')),
    }
    form = ''
    return render(request, 'payment/process.html', {'order': order,
                                                    'form':form})

@login_required
@csrf_protect
def paychoice(request):
    order_id = request.GET.get('order_id')
    order=Order.objects.get(id=order_id)
    return render(request, 'pay/pay.html', locals())

@login_required
@csrf_protect
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
    try:
       if pay_amount == realpayamount and pay_amount > 0:
            user_id = request.user.id
            subject = '购买商品:' + order.get_productname[0]
            if order.status == '2':
                if pay_type == 1:
                    # 微信支付
                    #result_src = paying_for_weixin_pay(request,order_id,user_id ,realpayamount)
                     result_src = paying_code_weixin_pay(order_id, user_id)
                     url = "/payment/wxpaying?order_id=" + str(order_id)+"&result_src="+result_src
                     return JsonResponse({'result': "success", 'msg': u"请求微信支付页面成功!", 'url': url})
                elif pay_type == 2:
                    # 支付宝即时到帐支付
                    url = alipay_trade_page_pay(order_id, subject, realpayamount)
                    return JsonResponse({'result': "success", 'msg': u"请求支付宝支付页面成功!", 'url': url})
            else :
                return JsonResponse({'result': "failed", 'msg': u"订单信息异常,不能支付!", 'url': ''})

    except Exception as e:
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
        str_url = getcode_url(orderid)
        if str_url:
            img = qrcode.make(str_url)
            curDateTime = datetime.datetime.now().strftime('%Y%m%d%H%M%S')
            randNum = random.randint(1000, 9999)
            mch_vno = curDateTime + str(randNum) + str(orderid)
            path = settings.MEDIA_ROOT + 'qrcode'
            if not os.path.exists(path):
                os.makedirs(path)
            result_src = os.path.join(path, mch_vno + ".png")
            newresult_src = settings.MEDIA_URL + os.path.join('qrcode', mch_vno + ".png")
            img.save(result_src)
        else:
            return u'订单不存在'
    except Exception as e:
        print (e)
    return newresult_src

# 微信支付,生成预支付单,并返回code_url
def getcode_url(orderid):
    unifiedorder_pub = UnifiedOrder_pub()

    corder = Order.objects.get(id=int(orderid))
    total_fee = 0
    if corder:
        total_fee = corder.amount * 100  # 实际支付金额,微信需以整数,单位为分
        #body = corder.get_productname[0]
        body = 'products'
        if len(body) > 127:
            body = body[0:127]

        unifiedorder_pub.setParameter("body", body)
        out_trade_no = create_TradeId(orderid)
        unifiedorder_pub.setParameter("out_trade_no", out_trade_no)
        unifiedorder_pub.setParameter("detail", body)
        # unifiedorder_pub.setParameter("total_fee", str(total_fee))
        unifiedorder_pub.setParameter("total_fee", "1")
        unifiedorder_pub.setParameter("trade_type", "NATIVE")

        prepay_id, url = unifiedorder_pub.getPrepayId()
        # print url
        if url:
            return url
#微信支付,生成支付二维码
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
        order_id = int(request.GET.get("order_id"))
        order = Order.objects.get(id=order_id)
        orderid = str(order_id)
        buy_title =  '秒杀商品:'
        pay_amount=order.amount
        #检查存放路径
        path = settings.MEDIA_ROOT + 'qrcode'
        if not os.path.exists(path):
            os.makedirs(path)
        curDateTime = datetime.datetime.now().strftime('%Y%m%d%H%M%S')
        randNum = random.randint(1000, 9999)
        mch_vno = curDateTime + str(randNum) + orderid
        result_src = os.path.join(path, mch_vno + ".png")
        newresult_src = settings.MEDIA_URL + os.path.join('qrcode', mch_vno + ".png")
        #newresult_src = settings.MEDIA_URL + result_src
        #检查文件是否已存在
        if not os.path.isfile(result_src):
            navtivelink=NativeLink_pub()
            navtivelink.setParameter('product_id',orderid)
            str_url=navtivelink.getUrl()
            img=qrcode.make(str_url)
            img.save(result_src)
    except Exception as e:
        print (e)
    #return newresult_src
    return render(request, 'pay/wxpay.html', locals())
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
                    dicBack['PAYSTATUS'] = 1  # u'支付
                    oid_str= recovery_order_id(out_trade_no)
                    if oid_str:
                        oid=int(oid_str)
                        if int(oid)>0:
                            lock.acquire() # 从这里进入线程安全区
                            corder=Order.objects.get(id=int(oid))
                            lock.release() # 从这里离开线程安全区
                            if corder:
                                if corder.status=='paying' :
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
        PAYTYPE=(('1',u'订单'),('2',u'充值'),('3',u'推荐'),('4',u'其他'),)
        PAYSOURCE=(('1',u'积分支付'),('2',u'微信支付'),('3',u'银联支付'),('4',u'支付宝支付'),('5',u'其他'),)
        PAYSTATUS = (('1', u'支付'), ('2', u'生成取款单'),('3', u'取款'),('4', u'取消'),('5', u'退款'), ('6', u'开票'),)
    """

    #logging.info('>> return url handler start')
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

    # logging.info(">>notify url handler start...")
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

#支付成功后回写订单
def pay_success_commit_corder(request,order_id, dicBack):
        """
        支付成功后的业务处理
        主要分为购买订单后的业务处理
        #1、业务 更新订单状态和交易号、交易时间等信息、推荐人。
        :param corder:
        :param dicBack:
         PAYTYPE=(('1',u'订单'),('2',u'充值'),('3',u'推荐'),('4',u'其他'),)
         PAYSOURCE=(('1',u'积分支付'),('2',u'微信支付'),('3',u'银联支付'),('4',u'支付宝支付'),('5',u'其他'),)
         orderSTATUS = (('1', u'生成'),('0', u'取消'), ('2', u'待支付'),('3', u'已支付'),('5', u'退款'), ('4', u'评价'),)
        :return:
        """
        flag = False
        order = Order.objects.get(id=int(order_id))
       # logging.info(order.status)

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

def checkorderstatus(request):
    try :
        order_id = request.POST.get('order_id')
        orders = Order.objects.get(id=order_id)
        if orders.status == '3':
            msg = u'订单支付成功'
            status = 200
        elif orders.status == '2':
            msg = u'订单待支付'
            status = 301
    except Exception as e:
        status = 400
        msg = u'数据错误，联系管理员'
    return JsonResponse({"status": status, "msg": msg})

def paysuccessed(request):
    pass