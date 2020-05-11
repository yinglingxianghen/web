# -*-coding:utf-8-*-


class UrlPathRecordMiddleware(object):
    """记录用户访问地址中间件类"""
    exclude_path = ['/user/login/', '/user/register/', '/user/logout/']
    # 排除ajax请求的地址
    # request.is_ajax() 判断是不是一个ajax发起的请求
    # request.path 获取用户访问的url地址

    # 1.若用户没有登录前访问的是 /user/addresss/这个地地址，会有以下过程
    # a) 访问/user/address/                             pre_url_path = /user/address/
    # b) 重定向访问/user/login/                          pre_url_path = /user/address/
    # c) 输入用户名和密码，点击登录访问/user/login_check/   pre_url_path = /user/address/

    # 2.若用户没有登录前访问的是 /user/addresss/这个地地址，会有以下过程
    # a) 访问/user/                                     pre_url_path = /user/
    # b) 重定向访问/user/login/                          pre_url_path = /user/
    # c) 输入用户名和密码，点击登录访问/user/login_check/   pre_url_path = /user/
    def process_view(self, request, view_func, *view_args, **view_kwargs):
        print('request.path:{}'.format(request.path))
        if request.path not in UrlPathRecordMiddleware.exclude_path and not request.is_ajax():
            request.session['pre_url_path'] = request.path