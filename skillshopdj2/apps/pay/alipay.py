# -*- coding: utf-8 -*-
'''
支付宝接口
@author:
'''
import types
#from urllib import urlencode, urlopen
from urllib.request import urlopen
from  urllib.parse import urlencode
from .config import settings
from .alipay_core import make_payment_request, analysis_ali_response, notify_check_sign
import datetime
now = datetime.datetime.now()

#取当前时间


# 网关地址
_GATEWAY = 'https://openapi.alipay.com/gateway.do'
precreate_GATEWAY='https://openapi.alipaydev.com/gateway.do?'   #测试环境https://openapi.alipaydev.com/gateway.do


def smart_str(s, encoding='utf-8', strings_only=False, errors='strict'):
    """
    Returns a bytestring version of 's', encoded as specified in 'encoding'.

    If strings_only is True, don't convert (some) non-string-like objects.
    """
    if strings_only and isinstance(s, (types.NoneType, int)):
        return s
    #if not isinstance(s, basestring):
    if not isinstance(s, str):
        try:
            return str(s)
        except UnicodeEncodeError:
            if isinstance(s, Exception):
                # An Exception subclass containing non-ASCII data that doesn't
                # know how to print itself properly. We shouldn't raise a
                # further exception.
                return ' '.join([smart_str(arg, encoding, strings_only,
                        errors) for arg in s])
            return str(s, 'utf-8').encode(encoding, errors)
    elif isinstance(s, str(s, 'utf-8')):
        return s.encode(encoding, errors)
    elif s and encoding != 'utf-8':
        return s.decode('utf-8', errors).encode(encoding, errors)
    else:
        return s


#统一收单下单并支付页面接口alipay.trade.page.pay
def  alipay_trade_page_pay(order_id, subject, total_fee):
    params = {}
    params['method'] = 'alipay.trade.page.pay'
    params['version'] = '1.0'
    params['app_id'] = settings.APP_ID
    params['timestamp'] = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    params['charset'] = settings.ALIPAY_INPUT_CHARSET
    params['notify_url'] = settings.ALIPAY_NOTIFY_URL
    params['return_url'] = settings.ALIPAY_RETURN_URL
    params['format'] = 'JSON'
    params['sign_type'] = 'RSA'

    # 获取配置文件
    biz_content = {}

    # 从订单数据中动态获取到的必填参数
    biz_content['out_trade_no'] = order_id  # 请与贵网站订单系统中的唯一订单号匹配
    biz_content['subject'] = subject  # 订单名称，显示在支付宝收银台里的“商品名称”里，显示在支付宝的交易管理的“商品名称”的列表里。
    biz_content['body'] = subject
    biz_content['total_amount'] = total_fee  # 订单总金额，显示在支付宝收银台里的“应付总额”里
    biz_content['product_code'] = 'FAST_INSTANT_TRADE_PAY'
    biz_content['qr_pay_mode'] = '2' #跳转模式下，用户的扫码界面是由支付宝生成的，不在商户的域名下。2：订单码-跳转模式
    biz_content['timeout_express'] = '60m'  # 订单60分钟订单允许的最晚付款时间，逾期将关闭交易。
    biz_content['auth_token'] = ''#获取用户相关数据时，用于标识用户授权关系
    biz_content['enable_pay_channels'] = 'pcredit,moneyFund,debitCardExpress,credit_group,bankPay,balance,coupon'
    params['biz_content'] = biz_content

    encode_params = make_payment_request(params)

    return precreate_GATEWAY + encode_params

#统一收单线下交易查询alipay.trade.query
    """
 AlipayClient alipayClient = new DefaultAlipayClient("https://openapi.alipay.com/gateway.do", APP_ID, APP_PRIVATE_KEY, "json", CHARSET, ALIPAY_PUBLIC_KEY, "RSA2"); //获得初始化的AlipayClient
 AlipayTradeQueryRequest request = new AlipayTradeQueryRequest();//创建API对应的request类
 request.setBizContent("{" +
 "    \"out_trade_no\":\"20150320010101001\"," +
 "    \"trade_no\":\"2014112611001004680073956707\"" +
 "  }");//设置业务参数
 AlipayTradeQueryResponse response = alipayClient.execute(request);//通过alipayClient调用API，获得对应的response类
 System.out.print(response.getBody());
 //根据response中的结果继续业务逻辑处理
 out_trade_no	支付时传入的商户订单号，与trade_no必填一个
 trade_no	支付时返回的支付宝交易号，与out_trade_no必填一个
  """
def  alipay_trade_query(order_id, trade_no):
 params = {}
 params['method'] = 'alipay.trade.query'
 params['app_id'] = settings.APP_ID
 params['timestamp'] = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
 params['charset'] = settings.ALIPAY_INPUT_CHARSET
 params['format'] = 'JSON'
 params['sign_type'] = 'RSA'


 # 获取配置文件
 biz_content = {}
 biz_content['out_trade_no'] = order_id
 biz_content['trade_no'] = trade_no
 params['biz_content']=biz_content

 encode_params = make_payment_request(params)

 return precreate_GATEWAY + encode_params

def alipay_bill_downloadurl_query(type, date):
    #查询对账单下载
    params = {}
    params['method'] = 'alipay.data.dataservice.bill.downloadurl.query'
    params['version'] = '1.0'
    params['app_id'] = settings.APP_ID
    params['timestamp'] = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    params['charset'] = settings.ALIPAY_INPUT_CHARSET
    params['sign_type'] = 'RSA'

    # 获取配置文件
    biz_content = {}

    # 从订单数据中动态获取到的必填参数
    biz_content['bill_type'] = type  # 账单类型，商户通过接口或商户经开放平台授权后其所属服务商通过接口可以获取以下账单类型：trade、signcustomer；trade指商户基于支付宝交易收单的业务账单；signcustomer是指基于商户支付宝余额收入及支出等资金变动的帐务账单；
    biz_content['bill_date'] = date  # 账单时间：日账单格式为yyyy-MM-dd，月账单格式为yyyy-MM。


    params['biz_content'] = biz_content

    encode_params = make_payment_request(params)

    return precreate_GATEWAY + encode_params


def alipay_trade_precreate(tn, subject, total_fee):

    params = {}
    params['method'] = 'alipay.trade.precreate'
    params['version']='1.0'
    params['app_id'] = settings.APP_ID
    params['timestamp'] = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    params['charset']=settings.ALIPAY_INPUT_CHARSET
    params['notify_url'] = settings.ALIPAY_NOTIFY_URL
    params['sign_type']='RSA'

    # 获取配置文件
    biz_content={}

    # 从订单数据中动态获取到的必填参数
    biz_content['out_trade_no'] =tn   # 请与贵网站订单系统中的唯一订单号匹配
    biz_content['subject'] = subject  # 订单名称，显示在支付宝收银台里的“商品名称”里，显示在支付宝的交易管理的“商品名称”的列表里。
    biz_content['total_amount'] = total_fee  # 订单总金额，显示在支付宝收银台里的“应付总额”里

    params['biz_content']=biz_content

    encode_params=make_payment_request(params)

    return precreate_GATEWAY + encode_params





def alipay_response(body):
    '''
    对当前付款的返回的response进行解析 校验并且返回相关信息
    :param body: 返回的报文体
    :return:
    '''
    result=analysis_ali_response(body)
    return result


def alipay_notify_check(params):
    '''
    异步通知报文进行签名校验
    :param params: 通知报文参数 type dict
    :return:
    '''
    result=notify_check_sign(params)
    return result