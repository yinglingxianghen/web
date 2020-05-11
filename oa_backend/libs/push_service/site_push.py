"""
function：site_push 推送
describe：开站推送主逻辑文件和两个辅助验证方法
date：20171127
author：gjf
version:1.09
"""
import time
import logging
from django.http import JsonResponse
from libs.push_service.basehelp import *
from libs.push_service.b2b_siteid import *
from libs.push_service.b2c_siteid import *
logger = logging.getLogger('django')
"""
function:infopush
describe:开站推送主逻辑文件和两个辅助验证方法
param: string @siteid
return: json
"""
def infopush(siteid):
    try:
        # oa数据库信息
        oa_dbcon = dbcon_oa()
        # 根据企业id查询绑定的哪个节点
        if oa_dbcon == False:
            logger.info('oa库连接失败')
            data = {'status': False, 'error': 'oa库连接失败'}
            return JsonResponse(data, safe=False)
        # 判断站点是开通还是关闭
        sql = 'select openstationmanage.online_status from \
              workorder_manage_stationinfo as stationinfo LEFT JOIN \
              workorder_manage_openstationmanage as openstationmanage ON stationinfo.id=openstationmanage.station_info_id where \
              stationinfo.company_id="%s"' % (siteid)
        stationinfo = oa_dbcon.select(sql)
        if stationinfo == False:
            logger.info('基本站点信息为空')
            data = {'status': False, 'error': 'oa 基本站点信息为空'}
            return JsonResponse(data, safe=False)
        # 判断站点是开通还是关闭
        sql = 'select openstationmanage.online_status from \
              workorder_manage_stationinfo as stationinfo LEFT JOIN \
              workorder_manage_openstationmanage as openstationmanage ON stationinfo.id=openstationmanage.station_info_id where \
              stationinfo.company_id="%s"' % (siteid)
        stationinfo = oa_dbcon.select(sql)
        if stationinfo == False:
            logger.info('oa 基本站点信息为空')
            data = {'status': False, 'error': 'oa 基本站点信息为空'}
            return JsonResponse(data, safe=False)
        data = checkversion(siteid)
        if data=='b2b':
            # 开通b2b站
            if int(stationinfo[0]['online_status']) == 0:
                data = B2b_create_siteid(siteid, oa_dbcon)
            else:
                data = B2b_close_siteid(siteid, oa_dbcon)
        elif data=='b2c':
            # 开通b2c站
            if int(stationinfo[0]['online_status']) == 0:
                data = B2c_create_siteid(siteid, oa_dbcon)
            else:
                data = B2c_close_siteid(siteid, oa_dbcon)
        else:
            logger.info('企业id不规范')
            data = {'status': False, 'error': '企业id不规范'}
            return JsonResponse(data, safe=False)
        return JsonResponse(data, safe=False)
    except Exception as e:
        logger.error(str(e))
        data = {'status': False, 'error': '推送失败'}
        return JsonResponse(data, safe=False)
"""
function:node_msg_notice
describe:根据节点id找对应咨询库；查询节点咨询数量大于2w则不显示该节点
param: int @grid_id 节点id
return: bool
"""
def node_msg_notice(grid_id):
    # oa数据库信息
    try:
        kf_dbcon = dbcon_grid(grid_id, 'kf')
        if kf_dbcon == False:
            return True
        endtime = int(time.time())
        starttime = endtime - 86400
        sql = 'select count(*) from t2d_chatscene where starttime>=%d and starttime<=%d' % (starttime, endtime)
        chatscene_num = kf_dbcon.select(sql)
        if chatscene_num >= 20000:
            return False
        else:
            return True
    except Exception as e:
        logger.error(e)
        return True
"""
function:node_msg_notice
describe:根据节点id找对应咨询库；查询企业id是否存在
param: int @grid_id 节点id
param: string @siteid 企业id
return: bool
"""
def checksiteid(grid_id,siteid):
    # oa数据库信息
    try:
        kf_dbcon = dbcon_grid(grid_id, 'kf')
        if kf_dbcon == False:
            return False
        sql = 'select count(*) as num from t2d_enterpriseinfo where siteid="%s"' % (siteid)
        chatscene_num = kf_dbcon.select(sql)
        if chatscene_num[0]['num']==0:
            return True
        else:
            return False
    except Exception as e:
        logger.error(e)
        return False
"""
function:delsiteid
describe:根据节点id找对应咨询库；删除企业id所在的kf库内信息
param: int @grid_id 节点id
param: string @siteid 企业id
return: bool
"""
def delsiteid(grid_id,siteid):
    try:
        kf_dbcon = dbcon_grid(grid_id,'kf')
        if kf_dbcon == False:
            return False
        data = checkversion(siteid)
        if data == 'b2c':
            data = B2c_del_siteid(siteid,kf_dbcon)
            if data == False:
                return False
        elif data == 'b2b':
            data = B2b_del_siteid(siteid,kf_dbcon)
            if data == False:
                return False
        return True
    except Exception as e:
        logging.error(e)
        return False

