"""
function：b2c开站和关闭
describe：b2c开站和关闭
date：20171127
author：gjf
version:1.09
"""
import time
import logging
from urllib import parse
from django.conf import settings
from libs.push_service.cdn import Cdn
from libs.push_service.configjs import Configjs
from libs.push_service.functionset import Functionset
from libs.push_service.basehelp import *

logger = logging.getLogger('django')
"""
function:B2c_close_siteid
describe:关闭b2c站点
param: string @siteid 企业id
param: pymysql.cursors.Cursor @oa_dbcon oa库游标
return: json
"""


def B2c_close_siteid(siteid, oa_dbcon):
    # oa获取需要开站的企业基本详细信息
    sql = 'SELECT stationinfo.id,stationinfo.grid_id,stationinfo.company_id, stationinfo.open_station_time, stationinfo.close_station_time, companyinfo.company_name, companyinfo.company_email, companyinfo.service_area FROM \
          workorder_manage_stationinfo AS stationinfo LEFT JOIN \
          workorder_manage_openstationmanage AS openstationmanage ON stationinfo.id = openstationmanage.station_info_id LEFT JOIN \
          workorder_manage_companyinfo AS companyinfo ON companyinfo.id = openstationmanage.company_info_id WHERE \
          company_id = "%s"' % (siteid)
    stationinfo_data = oa_dbcon.select(sql)
    if stationinfo_data == False:
        logger.info('stationinfo is empty')
        return {'status': False, 'error': 'stationinfo is empty'}
    grid_id = stationinfo_data[0]['grid_id']
    kf_dbcon = dbcon_grid(grid_id, 'kf')
    sql = 'update t2d_enterpriseinfo set online_status = 2,deadline = 0,mode="official" where siteid="%s"' % (siteid)
    enterpriseinfo_data = kf_dbcon.add_up_de_commit(sql)
    if enterpriseinfo_data == False:
        logger.info('enterpriseinfo execution failure')
        return {'status': False, 'error': 'enterpriseinfo execution failure'}
    return {'status': True, 'error': 'null'}


"""
function:B2c_close_siteid
describe:开通b2c站点
param: string @siteid 企业id
param: pymysql.cursors.Cursor @oa_dbcon oa库游标
return: json
"""


def B2c_create_siteid(siteid, oa_dbcon):
    # oa获取需要开站的企业基本详细信息
    sql = 'SELECT stationinfo.id,stationinfo.grid_id,stationinfo.company_id, stationinfo.open_station_time, stationinfo.close_station_time, companyinfo.company_name, companyinfo.company_email, companyinfo.service_area FROM \
          workorder_manage_stationinfo AS stationinfo LEFT JOIN \
          workorder_manage_openstationmanage AS openstationmanage ON stationinfo.id = openstationmanage.station_info_id LEFT JOIN \
          workorder_manage_companyinfo AS companyinfo ON companyinfo.id = openstationmanage.company_info_id WHERE \
          company_id = "%s"' % (siteid)
    stationinfo_data = oa_dbcon.select(sql)
    if stationinfo_data == False:
        return {'status': False, 'error': 'stationinfo is empty'}
    grid_id = stationinfo_data[0]['grid_id']
    kf_dbcon = dbcon_grid(grid_id, 'kf')
    if kf_dbcon == False:
        return {'status': False, 'error': 'kf connection failed'}
    # 获取开站的企业默认用户
    sql = 'select accountconf.* from workorder_manage_accountconf as accountconf LEFT JOIN workorder_manage_openstationmanage as openstationmanage ON accountconf.station_id=openstationmanage.id where openstationmanage.station_info_id=%d' % (
        stationinfo_data[0]['id'])
    accountconf_data = oa_dbcon.select(sql)
    if accountconf_data == False:
        return {'status': False, 'error': 'accountconf is empty'}
    # 获取开站的企业URl
    sql = 'select * from workorder_manage_companyurl where company_info_id=%d' % (stationinfo_data[0]['id'])
    companyurl_data = oa_dbcon.select(sql)
    if companyurl_data == False:
        url = ''
    else:
        url = companyurl_data[0]['company_url']
    # 推送给kf库的t2d_enterpriseinfo表
    try:
        version_id = 'grid'
        name = stationinfo_data[0]['company_name']
        email = stationinfo_data[0]['company_email']
        createtime = int(time.time())
        timeArray = time.strptime(str(stationinfo_data[0]['close_station_time']), "%Y-%m-%d")
        deadline = int(time.mktime(timeArray))
        timeArray = time.strptime(str(stationinfo_data[0]['open_station_time']), "%Y-%m-%d")
        online_time_trial = int(time.mktime(timeArray))
        sql = 'select * from t2d_enterpriseinfo where siteid="%s"' % (siteid)
        enterpriseinfo_data = kf_dbcon.select(sql)
        if enterpriseinfo_data == False:
            sql = 'insert into t2d_enterpriseinfo(siteid,deadline,online_time_trial,online_status,mode,url,version_id,createtime,name,smarteye,captureimage,online_time,phoneservice,call_center,hot_phone,domain_name,call_username,call_password,call_managerID,call_passkey,iserp,isweixin) values \
                  ("%s","%s","%s",1,"official","%s","%s",%d,"%s",1,1,0,"","","","","","","","",0,0)' % \
                  (siteid, deadline, online_time_trial, url, version_id, createtime, name)
            enterpriseinfo_data = kf_dbcon.add_up_de(sql)
            if enterpriseinfo_data == False:
                kf_dbcon.rollback()
                return {'status': False, 'error': 'enterpriseinfo execution failure'}
            # 在kf库创建行政组t2d_group
            sql = 'select * from t2d_group where siteid="%s" and groupname="%s"' % (
                siteid, '小能技术支持(勿删)')
            group_data = kf_dbcon.select(sql)
            if group_data == False:
                sql = 'insert into t2d_group(siteid,groupname) values ("%s","小能技术支持(勿删)")' % \
                      (siteid)
                group_data = kf_dbcon.add_up_de(sql)
            if group_data == False:
                kf_dbcon.rollback()
                return {'status': False, 'error': 'group execution failure'}
            # 推送给kf库的t2d_user表并分配行政组
            sql = 'select id,groupname from t2d_group where siteid="%s" and groupname="小能技术支持(勿删)"' % (
                siteid)
            group_data = kf_dbcon.select(sql)
            if group_data == False:
                kf_dbcon.rollback()
                return {'status': False, 'error': 'group is empty'}
            group_data_arr = {}
            for v in group_data:
                group_data_arr[v['groupname']] = v['id']
            pwd = accountconf_data[0]['set_pwd']
            userid_kefu01 = siteid + '_ISME9754_T2D_kefu01'
            userid_kefu02 = siteid + '_ISME9754_T2D_kefu02'
            userid_kefu03 = siteid + '_ISME9754_T2D_kefu03'
            # 默认测试账号
            passIndex_ntalker_steven = md5Encode(
                "ntalker_steven" + settings.MONTH_KEY[time.strftime("%m")] + time.strftime("%Y%m"))
            passIndex_ntalker_steven = passIndex_ntalker_steven[0:8]
            passIndex_ntalker_lizhipeng = md5Encode(
                "ntalker_lizhipeng" + settings.MONTH_KEY[time.strftime("%m")] + time.strftime("%Y%m"))
            passIndex_ntalker_lizhipeng = passIndex_ntalker_lizhipeng[0:8]

            passIndex_ralf = md5Encode(
                "ralf" + settings.MONTH_KEY[time.strftime("%m")] + time.strftime("%Y%m"))
            passIndex_ralf = passIndex_ralf[0:8]
            maliqun_pwd_sql = 'select `password` from t2d_user where userid like "%maliqun" limit 1'
            ali_dbcon = ali_dbcon_kf()
            passIndex_maliqun = ali_dbcon.select(maliqun_pwd_sql)
            passIndex_maliqun = passIndex_maliqun[0]['password']
            userid_ntalker_steven = siteid + '_ISME9754_T2D_ntalker_steven'
            userid_ntalker_maliqun = siteid + '_ISME9754_T2D_ntalker_maliqun'
            userid_ntalker_lizhipeng = siteid + '_ISME9754_T2D_ntalker_lizhipeng'
            userid_ralf = siteid + '_ISME9754_T2D_ralf'
            userid = siteid + '_ISME9754_T2D_' + str(accountconf_data[0]['user_name'])
            sql = 'replace into t2d_user(name,nickname,externalname,active,password,siteid,createtime,userid,role,gid) values \
                          ("%s","admin","admin",1,"%s","%s",%d,"%s","admin",%d),\
                          ("kefu01","kefu01","kefu01",1,"%s","%s",%d,"%s","admin",%d),\
                          ("kefu02","kefu02","kefu02",1,"%s","%s",%d,"%s","sale",%d),\
                          ("kefu03","kefu03","kefu03",1,"%s","%s",%d,"%s","sale",%d),\
                          ("ntalker_steven","ntalker_steven","ntalker_steven",1,"%s","%s",%d,"%s","admin",%d),\
                          ("ntalker_maliqun","ntalker_maliqun","ntalker_maliqun",1,"%s","%s",%d,"%s","admin",%d),\
                          ("ntalker_lizhipeng","ntalker_lizhipeng","ntalker_lizhipeng",1,"%s","%s",%d,"%s","admin",%d),\
                          ("ralf","ralf","ralf",1,"%s","%s",%d,"%s","admin",%d)' % \
                  (accountconf_data[0]['user_name'], pwd, siteid, createtime, userid, group_data_arr['小能技术支持(勿删)'],
                   pwd, siteid, createtime, userid_kefu01, group_data_arr['小能技术支持(勿删)'], \
                   pwd, siteid, createtime, userid_kefu02, group_data_arr['小能技术支持(勿删)'], \
                   pwd, siteid, createtime, userid_kefu03, group_data_arr['小能技术支持(勿删)'], \
                   passIndex_ntalker_steven, siteid, createtime, userid_ntalker_steven, group_data_arr['小能技术支持(勿删)'], \
                   passIndex_maliqun, siteid, createtime, userid_ntalker_maliqun, group_data_arr['小能技术支持(勿删)'], \
                   passIndex_ntalker_lizhipeng, siteid, createtime, userid_ntalker_lizhipeng,
                   group_data_arr['小能技术支持(勿删)'], \
                   passIndex_ralf, siteid, createtime, userid_ralf, group_data_arr['小能技术支持(勿删)'])
            user_data = kf_dbcon.add_up_de(sql)
            if user_data == False:
                kf_dbcon.rollback()
                return {'status': False, 'error': sql}
            t = time.time()
            rand = int(round(t * 1000))
            rand1 = int(round(t * 1000)) + 1
            rand2 = int(round(t * 1000)) + 2
            settingid = siteid + '_' + str(rand)
            settingid2 = siteid + '_' + str(rand1)
            settingid3 = siteid + '_' + str(rand2)
            iconid = settingid + '_icon'
            listid = settingid + '_list'
            toolbarid = settingid + '_toolbar'
            iconid2 = settingid2 + '_icon'
            listid2 = settingid2 + '_list'
            toolbarid2 = settingid2 + '_toolbar'
            iconid3 = settingid3 + '_icon'
            listid3 = settingid3 + '_list'
            toolbarid3 = settingid3 + '_toolbar'
            settingname = '默认代码'
            settingname2 = '正式代码'
            settingname3 = '小能技术支持(勿删)'
            mode = 'embed'
            invitecontent = '尊敬的客户您好，欢迎光临本公司网站！我是今天的在线值班客服，点击“开始交谈”即可与我对话。'
            invitetitle = '在线客服'
            invitedelay = 15000
            autoinvite = 0
            sql = 'select * from t2d_syssetting where siteid="%s" and mode="%s"' % (siteid, mode)
            syssetting_data = kf_dbcon.select(sql)
            if syssetting_data == False:
                sql = 'insert into t2d_syssetting(id,name,siteid,createtime,autoinvite,invitedelay,invitetitle,invitecontent,mode) values \
                              ("%s","%s","%s",%d,%d,%d,"%s","%s","%s"),\
                              ("%s","%s","%s",%d,%d,%d,"%s","%s","%s"),\
                              ("%s","%s","%s",%d,%d,%d,"%s","%s","%s")' % \
                      (settingid, settingname, siteid, createtime, autoinvite, invitedelay, invitetitle, invitecontent,
                       mode, \
                       settingid2, settingname2, siteid, createtime, autoinvite, invitedelay, invitetitle,
                       invitecontent, mode, \
                       settingid3, settingname3, siteid, createtime, autoinvite, invitedelay, invitetitle,
                       invitecontent, mode)
                syssetting_data = kf_dbcon.add_up_de(sql)
            if syssetting_data == False:
                kf_dbcon.rollback()
                return {'status': False, 'error': 'syssetting execution failure'}
            sql = 'select * from t2d_syssetting_mode where siteid="%s" and mode="icon"' % (siteid)
            syssetting_mode_data = kf_dbcon.select(sql)
            if syssetting_mode_data == False:
                sql = 'insert into t2d_syssetting_mode(modeid,settingid,mode,siteid,enabled) values \
                              ("%s","%s","icon","%s",1),\
                              ("%s","%s","icon","%s",1),\
                              ("%s","%s","icon","%s",1)' % \
                      (iconid, settingid, siteid, \
                       iconid2, settingid2, siteid, \
                       iconid3, settingid3, siteid)
                syssetting_mode_data = kf_dbcon.add_up_de(sql)
            if syssetting_mode_data == False:
                kf_dbcon.rollback()
                return {'status': False, 'error': 'syssetting_mode execution failure "icon"'}
            sql = 'select * from t2d_syssetting_mode where siteid="%s" and mode="list"' % (siteid)
            syssetting_mode2 = kf_dbcon.select(sql)
            if syssetting_mode2 == False:
                sql = 'insert into t2d_syssetting_mode(modeid,settingid,mode,siteid,enabled) values \
                              ("%s","%s","list","%s",0),\
                              ("%s","%s","list","%s",0),\
                              ("%s","%s","list","%s",0)' % \
                      (listid, settingid, siteid, \
                       listid2, settingid2, siteid, \
                       listid3, settingid3, siteid)
                syssetting_mode2 = kf_dbcon.add_up_de(sql)
            if syssetting_mode2 == False:
                kf_dbcon.rollback()
                return {'status': False, 'error': 'syssetting_mode execution failure "list"'}
            sql = 'select * from t2d_syssetting_mode where siteid="%s" and mode="list"' % (siteid)
            syssetting_mode3 = kf_dbcon.select(sql)
            if syssetting_mode3 == False:
                sql = 'insert into t2d_syssetting_mode(modeid,settingid,mode,siteid,enabled,enablemap,enablecall) values \
                              ("%s","%s","toolbar","%s",0,0,0),\
                              ("%s","%s","toolbar","%s",0,0,0),\
                              ("%s","%s","toolbar","%s",0,0,0)' % \
                      (toolbarid, settingid, siteid, \
                       toolbarid2, settingid2, siteid, \
                       toolbarid3, settingid3, siteid)
                syssetting_mode3 = kf_dbcon.add_up_de(sql)
            if syssetting_mode3 == False:
                kf_dbcon.rollback()
                return {'status': False, 'error': 'syssetting_mode execution failure "toolbar"'}
            groupid = siteid + '_ISME9754_GT2D_embed_' + iconid
            groupid2 = siteid + '_ISME9754_GT2D_embed_' + iconid2
            groupid3 = siteid + '_ISME9754_GT2D_embed_' + iconid3
            # 将所有账号添加到默认代码接待组中
            sql = 'select * from t2d_chosenuser where siteid="%s"' % (siteid)
            chosenuser = kf_dbcon.select(sql)
            if chosenuser == False:
                sql = 'insert into t2d_chosenuser(settingid,modeid,userid,username,groupid,siteid) select "%s","%s",userid,externalname,"%s",siteid from t2d_user where siteid="%s"' % \
                      (settingid, iconid, groupid, siteid)
                chosenuser_data = kf_dbcon.add_up_de(sql)
                if chosenuser_data == False:
                    kf_dbcon.rollback()
                    return {'status': False, 'error': 'chosenuser execution failure "iconid"'}
                sql = 'insert into t2d_chosenuser(settingid,modeid,userid,username,groupid,siteid) select "%s","%s",userid,externalname,"%s",siteid from t2d_user where siteid="%s" and gid=%d' % \
                      (settingid2, iconid2, groupid2, siteid, group_data[0]['id'])
                chosenuser_data2 = kf_dbcon.add_up_de(sql)
                if chosenuser_data2 == False:
                    kf_dbcon.rollback()
                    return {'status': False, 'error': 'chosenuser execution failure "iconid2"'}
                sql = 'insert into t2d_chosenuser(settingid,modeid,userid,username,groupid,siteid) select "%s","%s",userid,externalname,"%s",siteid from t2d_user where siteid="%s" and gid=%d' % \
                      (settingid3, iconid3, groupid3, siteid, group_data[0]['id'])
                chosenuser_data3 = kf_dbcon.add_up_de(sql)
                if chosenuser_data3 == False:
                    kf_dbcon.rollback()
                    return {'status': False, 'error': 'chosenuser execution failure "iconid3"'}
            # 根据节点找服务组 根据服务组找服务 根据服务找地址t_wdk_sit
            sql = 'SELECT servers.ser_id,seraddress.ser_address,servergroup.group_name FROM \
                          `production_manage_servergroup` AS servergroup \
                          LEFT JOIN production_manage_servergroup_ser_address AS servergroup_ser_address ON servergroup.id = servergroup_ser_address.servergroup_id \
                          LEFT JOIN production_manage_seraddress AS seraddress ON servergroup_ser_address.seraddress_id = seraddress.id \
                          LEFT JOIN production_manage_server AS servers ON seraddress.server_id = servers.id \
                          LEFT JOIN production_manage_sertype as sertype ON servers.ser_id=sertype.id \
                          LEFT JOIN workorder_manage_stationinfo as stationinfo ON stationinfo.server_grp_id=servergroup.id WHERE \
                          stationinfo.company_id = "%s"' % (siteid)
            fuwu_data = oa_dbcon.select(sql)
            if fuwu_data == False:
                kf_dbcon.rollback()
                return {'status': False, 'error': 'Service is empty'}
            sql = 'select * from t_wdk_sit where sitid="%s"' % (siteid)
            t_wdk_sit_data = kf_dbcon.select(sql)
            if t_wdk_sit_data == False:
                fides = val = ''
                for k in fuwu_data:
                    fides = fides + ',' + str(k['ser_id'])
                    val = val + ',"' + str(k['ser_address']) + '"'
                sql = 'INSERT INTO t_wdk_sit(sitid%s) VALUES("%s"%s)' % (fides, siteid, val)
                t_wdk_sit_data = kf_dbcon.add_up_de(sql)
            if t_wdk_sit_data == False:
                kf_dbcon.rollback()
                return {'status': False, 'error': 't_wdk_sit execution failure'}
            # 添加路由
            sql = 'SELECT seraddress.ser_address FROM \
                          production_manage_server AS servers \
                          LEFT JOIN production_manage_seraddress as seraddress ON seraddress.server_id=servers.id \
                          LEFT JOIN production_manage_serip as serip ON serip.ser_address_id=seraddress.id \
                          LEFT JOIN production_manage_servergroup_ser_address as servergroup_ser_address ON servergroup_ser_address.seraddress_id=seraddress.id \
                          LEFT JOIN production_manage_servergroup as servergroup ON servergroup.id=servergroup_ser_address.servergroup_id \
                          LEFT JOIN workorder_manage_stationinfo as stationinfo ON stationinfo.server_grp_id=servergroup.id \
                          WHERE servers.ser_id = "historyurl" and stationinfo.company_id="%s"' % (siteid)
            historyurl_address = oa_dbcon.select(sql)
            if historyurl_address == False:
                kf_dbcon.rollback()
                return {'status': False, 'error': 'Route data is empty'}
            if historyurl_address[0]['ser_address']:
                parts = parse.urlparse(historyurl_address[0]['ser_address'])
                host = parts.netloc
            else:
                return {'status': False, 'error': 'host is empty'}
            scripturl = 'http://%s/js/xn6/' % (host)
            downturl = 'http://%s/downt/t2d/' % (host)
            updateurl = 'http://%s/downt/update/' % (host)
            apiurl = 'http://%s/downt/update/' % (host)
            ali_dbcon = ali_dbcon_kf()
            if ali_dbcon == False:
                return {'status': False, 'error': 'ali connection failed'}
            sql = 'select * from t2d_route_url where siteid="%s"' % (siteid)
            route_url = ali_dbcon.select(sql)
            if route_url == False:
                route_url_sql = 'insert into t2d_route_url(siteid,scripturl,downturl,updateurl,authorization_id,apiurl) values ("%s","%s","%s","%s","","%s")' % \
                                (siteid, scripturl, downturl, updateurl, apiurl)
            else:
                route_url_sql = 'update t2d_route_url set scripturl="%s",downturl="%s",updateurl="%s",apiurl="%s" where siteid="%s"' % \
                                (scripturl, downturl, updateurl, apiurl, siteid)
            ali_dbcon.add_up_de_commit(route_url_sql)
            # letao库site表写入
            site_sql = 'select * from t2d_site where website="%s"' % (siteid)
            letao_dbcon = dbcon_grid(grid_id, 'letaotrailcenter')
            if letao_dbcon == False:
                return {'status': False, 'error': 'letao connection failed'}
            site_list = letao_dbcon.select(site_sql)
            if site_list == False:
                site_sql = 'insert into t2d_site(website,region_code) values ("%s",(SELECT site.region_code FROM t2d_site as site GROUP BY site.region_code ORDER BY count(site.region_code) asc LIMIT 1))' % \
                           (siteid)
                site_data = letao_dbcon.add_up_de_commit(site_sql)
                if site_data == False:
                    return {'status': False, 'error': 'letao  execution failure'}
        else:
            sql = 'update t2d_enterpriseinfo set version_id="%s",createtime=%d,name="%s",url="%s",deadline="%s",online_time_trial="%s",mode="%s",online_status=1 where siteid="%s"' % (
                version_id, createtime, name, url, deadline, online_time_trial, "official", siteid)
            enterpriseinfo_data = kf_dbcon.add_up_de(sql)
            if enterpriseinfo_data == False:
                kf_dbcon.rollback()
                return {'status': False, 'error': 'enterpriseinfo execution failure'}
        # 根据企业id 找开通了那些功能
        sql = 'SELECT functioninfo.func_code,functioninfo.func_name,singleselection.select_value FROM \
              `workorder_manage_stationinfo` AS stationinfo \
              LEFT JOIN workorder_manage_openstationmanage AS openstationmanage ON stationinfo.id = openstationmanage.station_info_id \
              LEFT JOIN workorder_manage_openstationmanage_func_list AS func_list ON openstationmanage.id = func_list.openstationmanage_id \
              LEFT JOIN production_manage_singleselection AS singleselection ON func_list.singleselection_id = singleselection.id \
              LEFT JOIN production_manage_functioninfo AS functioninfo ON singleselection.function_id = functioninfo.id WHERE \
              stationinfo.company_id = "%s"' % (siteid)
        func_lists = oa_dbcon.select(sql)
        if func_lists == False:
            kf_dbcon.rollback()
            return {'status': False, 'error': 'functionswitch is empty'}
        functionset = Functionset(kf_dbcon)
        func_error = ''
        for v in func_lists:
            func_code = str(v['func_code'])
            func_val = str(v['select_value'])
            is_func = hasattr(functionset, func_code)
            if is_func == False:
                func_error = func_error + func_code + '开通方法不存在,'
            else:
                func = functionset.__getattribute__(func_code)
                func_data = func(siteid, func_val)  # functionset."%s"(siteid,1)%(func_code)
                if func_data == False:
                    func_error = func_error + func_code + '开通失败,'
        if func_error:
            data = {'status': False, 'error': func_error}
        else:
            # 更新configjs
            configjs_obj = Configjs(kf_dbcon)
            configjs_data1 = configjs_obj.configjs(siteid)
            if configjs_data1 == False:
                kf_dbcon.rollback()
                return {'status': False, 'error': '更新configjs 失败'}
            kf_commit = kf_dbcon.commit()
            if kf_commit == False:
                kf_dbcon.rollback()
                data = {'status': False, 'error': '提交kf库失败'}
            else:
                # 推送cdn
                #cdn_obj = Cdn(oa_dbcon)
                #cdn_obj.pushcdn_b2b(siteid)
                data = {'status': True, 'error': 'null'}
        return data
    except Exception as e:
        logging.error(e)
        kf_dbcon.rollback()
        data = {'status': False, 'error': '异常'}
        return data


"""
function:B2c_close_siteid
describe:删除b2c站点相关信息
param: string @siteid 企业id
param: pymysql.cursors.Cursor @kf_dbcon kf库游标
return: bool
"""


def B2c_del_siteid(siteid, kf_dbcon):
    try:
        sql = 'DELETE from `t2d_enterpriseinfo` where siteid="%s"' % (siteid)
        data = kf_dbcon.add_up_de(sql)
        if data == False:
            kf_dbcon.rollback()
            return False
        sql = 'DELETE from `t2d_group` where siteid="%s"' % (siteid)
        data = kf_dbcon.add_up_de(sql)
        if data == False:
            kf_dbcon.rollback()
            return False
        sql = 'DELETE from `t2d_user` where siteid="%s"' % (siteid)
        data = kf_dbcon.add_up_de(sql)
        if data == False:
            kf_dbcon.rollback()
            return False
        sql = 'DELETE from `t2d_syssetting` where siteid="%s"' % (siteid)
        data = kf_dbcon.add_up_de(sql)
        if data == False:
            kf_dbcon.rollback()
            return False
        sql = 'DELETE from `t2d_syssetting_mode` where siteid="%s"' % (siteid)
        data = kf_dbcon.add_up_de(sql)
        if data == False:
            kf_dbcon.rollback()
            return False
        sql = 'DELETE from `t2d_chosenuser` where siteid="%s"' % (siteid)
        data = kf_dbcon.add_up_de(sql)
        if data == False:
            kf_dbcon.rollback()
            return False
        sql = 'DELETE from `t2d_enterpriseinfo_extend` where siteid="%s"' % (siteid)
        data = kf_dbcon.add_up_de(sql)
        if data == False:
            kf_dbcon.rollback()
            return False
        data = kf_dbcon.commit()
        if data == False:
            kf_dbcon.rollback()
            return False
        return True
    except Exception as e:
        logging.error(e)
        return False
