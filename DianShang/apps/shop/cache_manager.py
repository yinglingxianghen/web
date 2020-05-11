
# -*- coding:utf-8 -*-
# from redis_cache import get_redis_connection

from django.core.cache import cache
import redis
import time

import sys
from redis.sentinel import Sentinel

#哨兵连接
# from redis.sentinel import Sentinel
# from django.conf import settings
#
# global mysentinel
# global master
# global slave
#
# sentineaddress = settings.REDIS_SENTINELADDRESS

# try :
#     if mysentinel:
#         pass
#     else:
#         #mysentinel = Sentinel([('127.0.0.1',26379),('127.0.0.1',26380),('127.0.0.1',26381)],socket_timeout=1000)
#         mysentinel = Sentinel(sentineaddress, socket_timeout=1000)
#         master = mysentinel.master_for('seckill',socket_timeout=1000)
#         slave = mysentinel.slave_for('seckill',socket_timeout=1000)
# except Exception as e:
#     mysentinel = Sentinel(sentineaddress, socket_timeout=1000)
#     master = mysentinel.master_for('seckill', socket_timeout=1000)
#     slave = mysentinel.slave_for('seckill', socket_timeout=1000)



#redis  master-slave连接
master = redis.Redis(connection_pool=redis.BlockingConnectionPool(max_connections=15, host='localhost', port=6379))
slave = redis.Redis(connection_pool=redis.BlockingConnectionPool(max_connections=15, host='localhost', port=6380))
# pool = redis.ConnectionPool(host='localhost', port=6379)
# sec_redis = redis.Redis(connection_pool=pool)


def setcache( key,time, value):
    # master.setex(key,value,time) #单机redis连接
   master.setex(key, time, value)

def getcache(key):
   return slave.get(key)

def exists(key):
    return slave.get(key)


#初始化库存
def init_stock(key,qty):
    if master.exists(key):
        pass
    else:
        master.set(key, qty)
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

def get_keylist(key):
    return master.keys(pattern=key)