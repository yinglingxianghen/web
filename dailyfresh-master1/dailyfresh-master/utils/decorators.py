# -*-coding:utf-8-*-
from django.shortcuts import redirect


def login_requird(view_func):
    def wrapper(request, *view_args, **view_kwargs):
        print('decorate')
        if request.session.has_key('islogin'):
            return view_func(request, *view_args, **view_kwargs)
        else:
            return redirect('/user/login/')

    return wrapper
