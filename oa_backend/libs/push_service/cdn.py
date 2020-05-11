"""
function：Configjs操作类
describe：Configjs操作类封装
date：20171127
author：gjf
version:1.09
"""
# coding=utf-8
import requests
import time
import logging
from django.conf import settings

logger = logging.getLogger('django')
class Cdn:
    """
    function:__init__
    describe:构造函数初始连接数据库kf库
    param: pymysql.cursors.Cursor @dbcon kf库
    return: json
    """
    def __init__(self,oa_dbcon):
        self.oa_dbcon = oa_dbcon
    """
    function:getip
    describe:根据企业id找节点然后找服务，根据服务（historyurl）找ip
    param: string @siteid 企业id
    return: json
    """
    def getip(self,siteid):
        # 根据节点找服务
        sql = 'SELECT serip.ser_ip FROM \
                      production_manage_servergroup AS servergroup \
                      LEFT JOIN production_manage_servergroup_ser_address AS servergroup_ser_address ON servergroup.id = servergroup_ser_address.servergroup_id \
                      LEFT JOIN production_manage_seraddress as seraddress ON servergroup_ser_address.seraddress_id=seraddress.id \
                      LEFT JOIN production_manage_serip as serip ON seraddress.id=serip.ser_address_id \
                      LEFT JOIN production_manage_server as servers ON servers.id=seraddress.server_id \
                      LEFT JOIN workorder_manage_stationinfo as stationinfo ON stationinfo.grid_id=servergroup.grid_id \
                      WHERE servers.ser_id="historyurl" and stationinfo.company_id="%s"' % (siteid)
        data = self.oa_dbcon.select(sql)
        if data==False:
            logger.info('ser_ip为空')
            return False
        return data

    """
    function:pushcdn_b2c
    describe:推送cdn，b2c企业
    param: string @siteid 企业id
    return: bool
    """
    def pushcdn_b2c(self,siteid):
        # b2c
        try:
            ip_data=self.getip(siteid)
            state = 0
            for k in ip_data:
                rand_time = int(time.time())
                url_1 = "http://%s/js/xn6/dynamic_script_package.php?act=update&siteid=%s&rnd=%d" % (k['ser_ip'],siteid,rand_time)
                logger.info(url_1)
                result = requests.post(url_1)
                result_json_1 = result.json()
                if 'ok' not in result_json_1:
                    state = 1
                url_2 = "http://%s/js/xn6/dynamic_script_package.php?act=copy&siteid=%s&rnd=%d" % (k['ser_ip'],siteid,rand_time)
                logger.info(url_2)
                result = requests.post(url_2)
                result_json_2 = result.json()
                if 'ok' not in result_json_2:
                    state = 1
            url = "%s/js/xn6/dynamic_script_package.php?act=cdn&siteid=%s&rnd=%d" % ('http://dl.ntalker.com', siteid,rand_time)
            logger.info(url)
            result = requests.post(url)
            result_json = result.json()
            if 'ok' not in result_json:
                logger.info('【b2b推送cdn】失败')
                return False
            else:
                logger.info('【b2c推送cdn】成功')
                return True
        except Exception as e:
            logger.error(e)
            return False

    """
    function:pushcdn_b2b
    describe:推送cdn，b2c企业
    param: string @siteid 企业id
    return: bool
    """
    def pushcdn_b2b(self,siteid):
        # b2b
        try:
            ip_data=self.getip(siteid)
            state = 0
            for k in ip_data:
                rand_time = int(time.time())
                url_1 = "http://%s/js/b2b/dynamic_script_package.php?act=update&siteid=%s&rnd=%d" % (k['ser_ip'],siteid,rand_time)
                logger.info(url_1)
                result = requests.post(url_1)
                result_json_1 = result.json()
                if 'ok' not in result_json_1:
                    state = 1
                url_2 = "http://%s/js/b2b/dynamic_script_package.php?act=copy&siteid=%s&rnd=%d" % (k['ser_ip'],siteid,rand_time)
                logger.info(url_2)
                result = requests.post(url_2)
                result_json_2 = result.json()
                if 'ok' not in result_json_2:
                    state = 1
            url = "%s/js/b2b/dynamic_script_package.php?act=cdn&siteid=%s&rnd=%d" % ('http://dl.ntalker.com', siteid,rand_time)
            logger.info(url)
            result = requests.post(url)
            result_json = result.json()
            if 'ok' not in result_json:
                logger.info('【b2b推送cdn】失败')
                return False
            else:
                logger.info('【b2b推送cdn】成功')
                return True
        except Exception as e:
            logger.error(e)
            return False
