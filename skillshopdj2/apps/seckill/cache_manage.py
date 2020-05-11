# -*- coding: utf-8 -*-
""" 
@version: v1.0 
@author: andy 
@license: Apache Licence  
@contact: 93226042@qq.com 
@site:  
@software: PyCharm 
@file: cache_manage.py 
@time: 2018/1/25 10:30 
"""

from redis.sentinel import Sentinel
from django.conf import settings

global mysentinel
global master
global slave

sentineaddress = settings.REDIS_SENTINELADDRESS
try :
    if mysentinel:
        pass
    else:
        #mysentinel = Sentinel([('127.0.0.1',26379),('127.0.0.1',26380),('127.0.0.1',26381)],socket_timeout=1000)
        mysentinel = Sentinel(sentineaddress, socket_timeout=1000)
        master = mysentinel.master_for('seckill',socket_timeout=1000)
        slave = mysentinel.slave_for('seckill',socket_timeout=1000)
except Exception as e:
    mysentinel = Sentinel(sentineaddress, socket_timeout=1000)
    master = mysentinel.master_for('seckill', socket_timeout=1000)
    slave = mysentinel.slave_for('seckill', socket_timeout=1000)

#设置key,value
def setcache(key,time,value):
    master.setex(key,time,value)
#读取key\value
def getcache(key):
    return slave.get(key)

#限制一个api或页面访问的频率，例如单ip或单用户一分钟之内只能访问多少次
def check_request_limit(key, limit):
    key = '{}'.format(key)
    check = master.exists(key)
    if check:
        master.incr(key)
        master.expire(key, 60)
        count=int(master.get(key))
        if count>limit:
            return False
        else:
            return True
    else :
        master.set(key,1)
       # sec_redis.incr(key)
        master.expire(key, 60)
        return True

#设置队列
def setqueue(key,item):
    li=master.lpush(key,item)
    # print li
    # time.sleep(0.1)  # 休眠0.1秒
#取队列元素，先进先出
def popqueue(key):
    popqueue=master.rpop(key)
    # time.sleep(0.1)
    return popqueue
#取队列大小
def queuesize(key):
    return master.llen(key)

#秒杀修改库存
def update_stock(key,productid, userid,qty,price):
    qty=int(qty)
    with master.pipeline() as pipe:
        i=0
        #10 次机会
        cart_key = 'cart:{}'.format(userid)
        while i<10:
            try:
                # 关注一个key,watch 字面就是监视的意思，这里可以看做为数据库中乐观锁的概念，谁都可以读，谁都可以修改，但是修改的人必须保证自己watch的数据没有被别人修改过，否则就修改失败了；
                pipe.watch(key)
                item = "%s-%s-%s-%s" % (userid,productid,qty,price)
                count = int(pipe.get(key))# 取库存
                if count >= qty:  # 有库存
                    # 事务开始
                    pipe.multi()
                    remainqty=count-qty
                    pipe.set(key, remainqty) # 保存剩余库存
                    pipe.sadd(cart_key, item)
                    # 事务结束
                    pipe.execute()
                    # 把命令推送过去
                    return True
                    break
                else:
                    pipe.unwatch()
                    print("库存不足！")
                    return False
            except Exception:
                pass
                continue
            finally:
                pipe.reset()

#获取以参数key开头的所有key列表
def get_keylist(key):
    return master.keys(pattern=key)

#初始化库存
def init_stock(key,qty):
    if master.exists(key):
        pass
    else:
        master.set(key, qty)

def exists(key):
    return slave.get(key)



