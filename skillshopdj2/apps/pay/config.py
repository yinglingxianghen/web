
# -*- coding:utf-8 -*-

class settings:

    ALIPAY_INPUT_CHARSET = 'utf-8'
    # 合作身份者ID，以2088开头的16位纯数字
    #ALIPAY_PARTNER = 'xxxxxxxx'
    ALIPAY_PARTNER = 'xxxxxxxx'

    # 签约支付宝账号或卖家支付宝帐户
    #ALIPAY_SELLER_EMAIL = 'xxxxxxxx'
    ALIPAY_SELLER_EMAIL = 'xxxxxxxx'

    APP_ID = 'xxxxxxxx'

    # 付完款后跳转的页面（同步通知） 要用 http://格式的完整路径，不允许加?id=123这类自定义参数
    ALIPAY_RETURN_URL = 'xxxxxxxx/shoppingcart/alipaysuccess/'
    #ALIPAY_RETURN_URL = 'http://68a9c447.ngrok.io/shoppingorder/alipaysuccess/'
    # 交易过程中服务器异步通知的页面 要用 http://格式的完整路径，不允许加?id=123这类自定义参数
    ALIPAY_NOTIFY_URL = 'xxxxxxxx/shoppingcart/alipayasyncnotify/'
    #ALIPAY_NOTIFY_URL = 'http://68a9c447.ngrok.io/shoppingorder/alipayasyncnotify/'

    ALIPAY_SHOW_URL = ''

    # 请求时出错的通知地址可以是请求参数中提交的error_notify_url，也可以是支付宝为商户配置好的商户指定通知地址。如果两者都有设置，则以error_notify_url为准。
    ERROR_NOTIFY_URL = "xxxxxxxx/shoppingcart/errornotify/"
    # 访问模式,根据自己的服务器是否支持ssl访问，若支持请选择https；若不支持请选择http
    ALIPAY_TRANSPORT = 'https'

    ALIPAY_SHOW_URL = ''

    # 访问模式,根据自己的服务器是否支持ssl访问，若支持请选择https；若不支持请选择http
    ALIPAY_TRANSPORT = 'https'

    SIGN_TYPE = "RSA"



    # 商户私钥

RSA_PRIVATE = """-----BEGIN RSA PRIVATE KEY-----
MIIEogIBAAKCAQEArkqAvZJ7qwqebulObEsDf5RSbNN+3j8c1fScEoKIXqtSDZA+JdB+sfDtS5nkBSB+LvcLwIHab3zMNs5w7ZI5XQoBLbW7PXwEn0/+3zHTV1U0Xvjqr4IVXpEwHIqFcFWtCtX7E4E7pUtYtAfPw44ehZJxWbR50AZKB5SbHsG2+z6CP2sIHyZcGo8jzGxBRIduNcj+ogzUVY3QBe1g76EJF6cf8Gbv5H6/M2MO5uch9HPH+1QvZktPu6TeKx24bC3S0q6pNN0jaMfL5f5uFx0SXu9xbRcoOVRFkj14PruSEIoCAd2KOyIMFKfajho+KEiNu5ACyvFngy730PTAasouIwIDAQABAoIBAEJJSY9Pz8LsZfcuuknLecgiw/ppsX2bKT9iKZ2MkYrXw3wvGMPO+PB5/fXb0HH2uqboBEsx177BCvXpK9/e1fxBmtMko9KtgSCKDxgZ3hP/7swUBUW8xp3RwCeKs1dW7loJqdTwOJwT/OdzdRwdyBPq7zs7vXxVeABMD3byG8KPkaTle+mGa6sYDM43GlMuWtYrRCc4tVuRJPIvKnGkUktXWqDgB43YP5/kN6G4jYmLVhqcmvX/Jnm/frits2naGdsncTUk2oUPnle3TPun+RBrbLeTnA0FTsObE3rg19I+pLwlfUlCJXTr3moRYZqoQaDmZN2JPO63uDAtUFKxfHkCgYEA3YdoJE6MPi2SybA2myr2+Up1kdGLXl6AsINFcC5cVuVW+iz/pdzulid5H8/IHPEM2SVIQ6pdkBYHSfQoIHZnn8K082/Np6cs59SG35yF9SZjuI84K6L23/woQJg25WSOFIY/WHqDBUKQUmP6N070sMiQJW8YeX+s8GWtydfxnuUCgYEAyWlgavqIyb2pJjBCVodp9ibIVZuSRKbsamGX1vJF1jhA0uLA5cmnFxocFLkkLuLqs2jkL/zcEVTtp9nHOE1jpMx7nI8l+t5kiJpr9CEpq9ZcsNB5e+sdqywB8C0lDmsRWlCHktWxRUGZSjYvZS+alcAWOgXUCTi23O4E/RXSQGcCgYAxT37C9ikJfiN6eZruFzY6b3SULMyVCPwkTlQakHdFcG9X6MRPK0qAafDwP9QPfSia/U2EoluJQx4EPDDiaPjP+wtEVNK2SuQYBpqvE6xN0WnJHzglnnTNjtd26WruzN9Dek6HZ13aweJWNKLxxMV6xGoxqvULtnvMVxXEJClIcQKBgGU9MJfVYth1Gwb1DwNLgbmW+O//COC1PvSiJZ6HnQ72q67VB7z5RaHZH/BSt5tRuEOCH+D3Ku8TT3olf3wPelyl5CRn1+Fn1ATOCiFmYfncAC9oOwhMwFcAAeFl79B1hP1uqRbnjvmO5axl3CDycrN/ICz+LPyNo20dvygvxcVVAoGARCrh8nzWXIb+UseAa1RQqwvgi8sM/8C4jOjDk5V87bhNFrmQU/8mewfINd3uJ3boxnWOLHl1l0S3kjKq/v66Z1Sapo9eg2opcpw7XfnCXdWsp3+y7LSnKP4YtJKv7WGtu1cuBvaMg3Vn9mMPgEKVe5E+kEkIHwMH0tNENG4vOaU=
    -----END RSA PRIVATE KEY-----"""

RSA_PUBLIC = """-----BEGIN PUBLIC KEY-----
MIIBIjANBgkqhkiG9w0BAQEFAAOCAQ8AMIIBCgKCAQEArkqAvZJ7qwqebulObEsDf5RSbNN+3j8c1fScEoKIXqtSDZA+JdB+sfDtS5nkBSB+LvcLwIHab3zMNs5w7ZI5XQoBLbW7PXwEn0/+3zHTV1U0Xvjqr4IVXpEwHIqFcFWtCtX7E4E7pUtYtAfPw44ehZJxWbR50AZKB5SbHsG2+z6CP2sIHyZcGo8jzGxBRIduNcj+ogzUVY3QBe1g76EJF6cf8Gbv5H6/M2MO5uch9HPH+1QvZktPu6TeKx24bC3S0q6pNN0jaMfL5f5uFx0SXu9xbRcoOVRFkj14PruSEIoCAd2KOyIMFKfajho+KEiNu5ACyvFngy730PTAasouIwIDAQAB
     -----END PUBLIC KEY-----"""

RSA_ALIPAY_PUBLIC = """-----BEGIN PUBLIC KEY-----
    MIGfMA0GCSqGSIb3DQEBAQUAA4GNADCBiQKBgQDIgHnOn7LLILlKETd6BFRJ0GqgS2Y3mn1wMQmyh9zEyWlz5p1zrahRahbXAfCfSqshSNfqOmAQzSHRVjCqjsAw1jyqrXaPdKBmr90DIpIxmIyKXv4GGAkPyJ/6FTFY99uhpiq0qadD/uSzQsefWo0aTvP/65zi3eof7TcZ32oWpwIDAQAB
    -----END PUBLIC KEY-----"""

