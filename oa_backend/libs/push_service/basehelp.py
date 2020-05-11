"""
function：基础公用方法
describe：基础公用操作方法封装
date：20171127
author：gjf
version:1.09
"""
import logging
import hashlib
import re
from django.conf import settings
from libs.hash import decrypt
from libs.push_service.mysqldbhelper import MysqldbHelper
logger = logging.getLogger('django')
"""
function:dbcon_grid
describe:根据节点id获取对应的数据库游标
param: int @grid_id 节点id
param: string @database 数据库库名
return: bool or pymysql.cursors.Cursor
"""
def dbcon_grid(grid_id, database):
    try:
        oa_dbcon = dbcon_oa()
        sql = 'SELECT db.db_type,db.db_address,db.db_name,db.db_port,db.db_pwd,db.db_username FROM \
                              `production_manage_grid` AS grid LEFT JOIN production_manage_databaseinfo AS db ON grid.id = db.grid_id WHERE \
                              grid.id =%d and db_name="%s"' % (grid_id, database)
        griddbinfo = oa_dbcon.select(sql)
        if griddbinfo == False:
            return False
        grid_dbhost = griddbinfo[0]['db_address'].strip()
        grid_dbuser = griddbinfo[0]['db_username'].strip()
        grid_dbpwd = griddbinfo[0]['db_pwd'].strip()
        grid_dbprot = int(griddbinfo[0]['db_port'].strip())
        grid_dbcon = MysqldbHelper(grid_dbhost, grid_dbuser, decrypt(grid_dbpwd), database, grid_dbprot)
        if grid_dbcon == False:
            return False
        return grid_dbcon
    except Exception as e:
        logger.error(e)
        return False
"""
function:ali_dbcon_kf
describe:获取阿里云数据库连接
return: bool or pymysql.cursors.Cursor
"""
def ali_dbcon_kf():
    try:
        # oa数据库信息
        oa_dbhost = 'rdsrypnu7hzxe7f5iwdt7public.mysql.rds.aliyuncs.com'
        oa_dbuser = 'ntalker'
        oa_dbpwd = 'xiaoneng2015'
        oa_dbname = 'kf'
        oa_port = 3306
        oa_dbcon = MysqldbHelper(oa_dbhost, oa_dbuser, oa_dbpwd, oa_dbname, oa_port)
        if oa_dbcon == False:
            return False
        return oa_dbcon
    except Exception as e:
        logger.error(e)
        return False
"""
function:dbcon_oa
describe:获取oa数据库连接
return: bool or pymysql.cursors.Cursor
"""
def dbcon_oa():
    try:
        # oa数据库信息
        oa_dbhost = settings.DATABASES['default']['HOST']
        oa_dbuser = settings.DATABASES['default']['USER']
        oa_dbpwd = settings.DATABASES['default']['PASSWORD']
        oa_dbname = settings.DATABASES['default']['NAME']
        oa_port = settings.DATABASES['default']['PORT']
        oa_dbcon = MysqldbHelper(oa_dbhost, oa_dbuser, oa_dbpwd, oa_dbname, oa_port)
        if oa_dbcon == False:
            return False
        return oa_dbcon
    except Exception as e:
        logger.error(e)
        return False
"""
function:md5Encode
describe:解密
return: string
"""
def md5Encode(string):
    m = hashlib.md5(string.encode("utf-8"))
    return m.hexdigest()
def checkversion(siteid):
    data=re.match(r'^[a-zA-Z]+_\d+',siteid)
    if data is None:
        return False
    if siteid.split('_')[0] != 'kf' and int(siteid.split('_')[1]) == 1000:
        return 'b2b'
    elif siteid.split('_')[0] == 'kf':
        return 'b2c'
    else:
        return False