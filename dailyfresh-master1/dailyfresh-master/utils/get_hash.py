# -*-coding:utf-8-*-
from hashlib import sha1


def get_hash(str, salt=None):
    str = '!#!@#' + str + '%^&%^'
    if salt:
        str = str + salt
    sh = sha1()
    sh.update(str.encode('utf-8'))
    return sh.hexdigest()
