"""
function：robot xbot机器人和云问机器人
describe：xbot机器人和云问机器人开通逻辑
date：20171127
author：gjf
version:1.09
"""
# coding=utf-8
import hashlib
import json
import time
import traceback
import logging
import requests
from django.conf import settings
logger = logging.getLogger('django')
class Robot:
    def __init__(self, dbcon):
        self.dbcon = dbcon
    """
    function:createrobot_xbot
    describe:创建机器人xbot机器人
    param: string @siteid 企业id
    return: json
    """
    def createrobot_xbot(self, siteid):
        headers = {'Content-Type': 'application/json'}
        robot_createtime = int(time.time())
        robot_name = 'robot' + str(robot_createtime)
        md5str = hashlib.md5(robot_name.encode(encoding='gb2312'))
        robot_password = md5str.hexdigest()
        robot_userid = siteid + '_ISME9754_T2D_' + robot_name
        issiteid = self.checkRobot(siteid)
        if issiteid==True:
            return True
        url = f"{settings.ROBOT_XBOT_URL}aiapi/ai/robot/v1/create_account"
        postdata = {"companyId": siteid, "companyName": "新开的站", "channel": "29b96bf9-5f95-11e7-8068-000c298b0e32","userName": "admin"}
        result = requests.post(url,  json=postdata)
        result_json = result.json()
        # if int(result_json['code'])==0 or int(result_json['code'])==1007:
        if int(result_json['code']) == 0:
            secret = result_json['data']['secret']
            clientId = result_json['data']['clientId']
            data = self.createRobot_kf(siteid, clientId, secret, robot_createtime, robot_name, robot_password,robot_userid, 'xbot1.0')
            if data == True:
                logger.info('开通机器人成功')
                return '开通机器人成功'
            else:
                logger.error('【开通机器人失败】xbot机器人kf库原因')
                return '开通机器人失败'
        else:
            logger.error('【开通机器人失败】xbot机器人')
            return result_json['code']
    """
    function:createrobot_yunwen
    describe:创建机器人云问机器人
    param: string @siteid 企业id
    return: json
    """
    def createrobot_yunwen(self, siteid):
        robot_createtime = int(time.time())
        robot_name = 'robot' + str(robot_createtime)
        md5str = hashlib.md5(robot_name.encode(encoding='gb2312'))
        robot_password = md5str.hexdigest()[0:16]
        robot_userid = siteid + '_ISME9754_T2D_' + robot_name
        userid = siteid + '_ISME9754_T2D_admin'
        issiteid = self.checkRobot(siteid)
        if issiteid==True:
            logger.info('已开通过机器人')
            return True
        url = "%sXnLogin/doReg?userName=%s&pwd=%s&robotName=%s&webName=%s&invokeKey=faqrobot&siteId=%s" % \
              (settings.ROBOT_YUNWEN_URL, userid, robot_password, robot_userid, siteid, siteid)
        result = requests.post(url)
        result_json = result.json()
        # if int(result_json['code'])==0 or int(result_json['code'])==1007:
        if result_json['apiUser']['appId'] and result_json['apiUser']['secret']:
            secret = result_json['apiUser']['secret']
            clientId = result_json['apiUser']['appId']
            data = self.createRobot_kf(siteid, clientId, secret, robot_createtime, robot_name, robot_password,robot_userid, 'yunwen4.0')
            if data == True:
                logger.info('开通机器人成功')
                return True
            else:
                logger.error('【开通机器人失败】云问机器人kf原因')
                return False
        else:
            logger.error('【开通机器人失败】云问机器人')
            return False
    """
    function:checkRobot
    describe:检查该企业是否开通机器人
    param: string @siteid 企业id
    return: bool
    """
    def checkRobot(self, siteid):
        sql = 'select * from t2d_robot_config where siteid="%s"' % (siteid)
        data = self.dbcon.select(sql)
        if data==False:
            return False
        else:
            enterpriseinfosql = "update t2d_enterpriseinfo set coop=9,robot=2 where siteid='%s'" % \
                                (siteid)
            data = self.dbcon.add_up_de_commit(enterpriseinfosql)
            return True
    """
    function:createRobot_kf
    describe:新建机器人创建相关接待组，机器人id等，kf操作
    param: string @siteid 企业id
    return: json
    """
    def createRobot_kf(self, siteid, robotid, secret, robot_createtime, robot_name, robot_password, robot_userid,
                       robottype):
        robot_username = '机器人'
        robot_groupname = '机器人组'
        robot_role = 'sale'
        robot_phoneservice = ''
        robot_max_reception = 500
        robot_xbot_versionid = robottype
        robot_noanscon = '对不起啦，我会改正的，我还在不断的学习怎么能更好的回答^_^~！您可以输入【转人工】由人工客服为您服务。'
        robot_tagentid = ''
        reply1 = '我是今天的值班客服，很高兴为您服务。请问您需要咨询哪方面的问题？为了更好的跟踪服务效果，请在对话结束后对我的服务满意度进行评价，非常感谢您的支持。'
        reply2 = '已经很久没有收到您的消息了，请问您还在电脑前吗？如果没有其他的问题我将主动关闭该对话。随时欢迎您再次向我咨询，祝您今天好心情。'
        reply3 = '我现在临时有事需要离开电脑前，您可以先浏览一下网站看看产品的详细介绍，或者留下您的联系方式等我回复，给您带来的不便请多谅解。'
        reply2time = 5
        reply3time = 1
        groupid = siteid + '_ISME9754_GT2D_link_' + siteid + '_9999_icon'
        modeid = siteid + '_9999_icon'
        settingid = siteid + '_9999'
        chosenuserid = siteid + '_ISME9754_GT2D_link_' + siteid + '_9999_icon'
        iconid = settingid + '_icon'
        listid = settingid + '_list'
        toolbarid = settingid + '_toolbar'
        settingname = '默认代码'
        invitetitle = '在线客服'
        invitecontent = '尊敬的客户您好，欢迎光临本公司网站！我是今天的在线值班客服，点击“开始交谈”即可与我对话。'

        # 机器人配置表
        sql_robot_config = "REPLACE INTO t2d_robot_config (siteid,robotid,secret,robotversionid) values ('%s','%s','%s','%s')" % \
                           (siteid, robotid, secret, robot_xbot_versionid)
        data_robot_config = self.dbcon.add_up_de_commit(sql_robot_config)
        if data_robot_config == False:
            logger.info('【开通机器人失败】t2d_robot_config写入失败')
            return False
        # 企业表-修改机器人是否开通字段
        enterpriseinfosql = "update t2d_enterpriseinfo set coop=9,robot=2 where siteid='%s'" % \
                            (siteid)
        data = self.dbcon.add_up_de(enterpriseinfosql)
        if data == False:
            logger.info('【开通机器人失败】t2d_enterpriseinfo写入失败')
            return False
        # 行政组表-查询机器人组是否存在不存在则新建机器人组

        groupsql = "select id,siteid,groupname from t2d_group where siteid='%s' and groupname='%s' limit 1" % \
                   (siteid, robot_groupname)
        curgroup = self.dbcon.select(groupsql)
        if curgroup == True:
            robot_group_gid = curgroup['id']
        else:
            group_sql = "insert into t2d_group(siteid,groupname) values ('%s','%s')" % \
                        (siteid, robot_groupname)
            group_data = self.dbcon.add_up_de_commit(group_sql)
            if group_data == True:
                robot_group_gid = self.dbcon.lastrowid()
            else:
                logger.info('【开通机器人失败】t2d_group写入失败')
                traceback.print_exc()
                return False
        # 如果是xbot机器人到这步就返回
        if robottype == 'xbot1.0':
            # 开通成功
            dbcommit = self.dbcon.commit()
            if dbcommit == True:
                logger.info('【开通机器人成功】')
                return True
            else:
                logger.info('【开通机器人失败】机器人开站所执行的sql提交到kf库失败')
                return False
        # 客服用户表-查询机器人是否创建
        user_sql = "select id,siteid,userid from t2d_user where siteid='%s' and max_reception='%d' and (nickname='%s' or externalname='%s') limit 1" % \
                   (siteid, robot_max_reception, robot_username, robot_username)
        user_data = self.dbcon.select(user_sql)
        if user_data == True:
            robot_userid = user_data['userid']
            robot_sql_user = "update t2d_user set name='%s',gid='%d',password='%s',role='%s',phoneservice='%s',max_reception='%d' where userid='%s'" % \
                             (robot_username, robot_group_gid, robot_password, robot_role, robot_phoneservice,
                              robot_max_reception, robot_userid)
            user_data = self.dbcon.add_up_de_commit(robot_sql_user)
            if user_data == False:
                logger.info('【开通机器人失败】t2d_user修改失败')
                return False
        else:
            robot_sql_user = "insert into t2d_user(name,gid,siteid,password,userid,nickname,role,externalname,createtime,phoneservice,max_reception,usertype,active) values ('%s','%d','%s','%s','%s','%s','%s','%s','%d','%s','%d',%d,%d)" % \
                             (robot_name, robot_group_gid, siteid, robot_password, robot_userid, robot_username,
                              robot_role, robot_username, robot_createtime, robot_phoneservice,
                              int(robot_max_reception), 1, 1)
            user_data = self.dbcon.add_up_de_commit(robot_sql_user)
            if user_data == False:
                logger.info('【开通机器人失败】t2d_user写入失败')
                return False

        # 查询机器人用户表
        robot_user_sql = "select siteid,userid from t2d_robot_user where siteid='%s' and userid='%s' limit 1" % \
                         (siteid, robot_userid)
        robot_user_data = self.dbcon.select(robot_user_sql)
        if robot_user_data == True:
            sql_robot_user = "update t2d_robot_user set noanscon='%s', nodeid='%s',robotagentid='%s' where userid='%s'" % \
                             (robot_noanscon, robot_userid, robot_tagentid, robot_userid)
            robot_user_data = self.dbcon.add_up_de_commit(sql_robot_user)
            if robot_user_data == False:
                logger.info('【开通机器人失败】t2d_robot_user修改失败')
                return False
        else:
            sql_robot_user = "insert into t2d_robot_user(siteid,userid,noanscon,nodeid,robotagentid) values ('%s','%s','%s','%s','%s')" % \
                             (siteid, robot_userid, robot_noanscon, robot_userid, robot_tagentid)
            robot_user_data = self.dbcon.add_up_de_commit(sql_robot_user)
            if robot_user_data == False:
                logger.info('【开通机器人失败】t2d_robot_user写入失败')
                return False
        # 查询客服信息扩展表
        sql_robot_usersetting = "select userid,autoreply from t2d_usersetting where userid='%s' limit 1" % \
                                (robot_userid)
        usersetting_data = self.dbcon.select(sql_robot_usersetting)
        if usersetting_data == True:
            sql_robot_usersetting = "update t2d_usersetting set autoreply='%d' where userid='%s'" % \
                                    (1, robot_userid)
            usersetting_data = self.dbcon.add_up_de_commit(sql_robot_usersetting)
            if usersetting_data == False:
                logger.info('【开通机器人失败】t2d_usersetting修改失败')
                return False
        else:
            sql_robot_usersetting = "insert into t2d_usersetting (userid,autoreply) values ('%s',%d)" % (robot_userid, 1)
            usersetting_data = self.dbcon.add_up_de_commit(sql_robot_usersetting)
            if usersetting_data == False:
                logger.error('【开通机器人失败】t2d_usersetting新增失败')
                return False
        # 自动应答表
        sql_autoreply = "select userid from t2d_autoreply where userid='%s' limit 1" % \
                        (robot_userid)
        autoreply_data = self.dbcon.select(sql_autoreply)
        if autoreply_data == True:
            sql_autoreply = "update t2d_autoreply set reply1='%s',reply2='%s',reply3='%s',reply2time=%d,reply3time=%d where userid='%s'" % \
                            (reply1, reply2, reply3, reply2time, reply3time, robot_userid)
            autoreply_data = self.dbcon.add_up_de_commit(sql_autoreply)
            if autoreply_data == False:
                logger.info('【开通机器人失败】t2d_autoreply修改失败')
                return False
        else:
            sql_autoreply = "insert into t2d_autoreply(userid,reply1,reply2,reply3,reply2time,reply3time)values('%s','%s','%s','%s',%d,%d)" % \
                            (robot_userid, reply1, reply2, reply3, reply2time, reply3time)
            autoreply_data = self.dbcon.add_up_de_commit(sql_autoreply)
            if autoreply_data == False:
                logger.info('【开通机器人失败】t2d_autoreply新增失败')
                return False
        # 客服，接待组绑定关系表
        sql_chosenuser = "select * from t2d_chosenuser where userid='%s' and groupid='%s' and settingid='%s' limit 1" % \
                         (robot_userid, groupid, settingid)
        chosenuser_data = self.dbcon.select(sql_chosenuser)
        if chosenuser_data == False:
            sql_chosenuser = "insert into t2d_chosenuser(settingid,modeid,userid,username,groupid) select '%s','%s',userid,externalname,'%s' from t2d_user where userid='%s'" % \
                             (settingid, modeid, chosenuserid, robot_userid)
            chosenuser_data = self.dbcon.add_up_de_commit(sql_chosenuser)
            if chosenuser_data == False:
                logger.info('【开通机器人失败】t2d_chosenuser新增失败')
                return False
        # user_binding_pri
        user_binding_pri = "select * from t2d_user_binding_pri where userid='%s' limit 1" % \
                           (robot_userid)
        user_binding_pri_data = self.dbcon.select(user_binding_pri)
        if user_binding_pri_data == False:
            user_binding_pri = "insert into t2d_user_binding_pri(account,advice,kpi,message,monitoring,manual,userid,siteid)value(0,0,0,0,0,0,'%s','%s')" % \
                               (robot_userid, siteid)
            user_binding_pri_data = self.dbcon.add_up_de_commit(user_binding_pri)
            if user_binding_pri_data == False:
                logger.info('【开通机器人失败】t2d_user_binding_pri新增失败')
                return False
        # syssetting
        if "kf_" in siteid:
            settingid = siteid + '_9999'
        else:
            settingid = siteid + '_' + time.time()[-3:]
        syssetting_sql = "select * from t2d_syssetting where id='%s' and siteid='%s' limit 1" % \
                         (settingid, siteid)
        syssetting_data = self.dbcon.select(syssetting_sql)
        if syssetting_data == False:
            sql_syssetting = "insert into t2d_syssetting(id,name,siteid,createtime,autoinvite,invitedelay,invitetitle,invitecontent,mode) values ('%s','%s','%s',%d,%d,%d,'%s','%s','%s')" % \
                             (settingid, settingname, siteid, robot_createtime, 0, 1500, invitetitle, invitecontent,
                              'embed')
            syssetting_data = self.dbcon.add_up_de_commit(sql_syssetting)
            if syssetting_data == False:
                logger.info('【开通机器人失败】t2d_syssetting新增失败')
                return False
        # syssetting_mode
        syssetting_mode_sql = "select * from t2d_syssetting_mode where modeid='%s' and settingid='%s' limit 1" % \
                              (iconid, settingid)
        syssetting_mode_data = self.dbcon.select(syssetting_mode_sql)
        if syssetting_mode_data == False:
            syssetting_mode_sql = "insert into t2d_syssetting_mode(modeid,settingid,mode,siteid,enabled) values ('%s','%s','%s','%s',%d)" % \
                                  (iconid, settingid, 'icon', siteid, 1)
            syssetting_mode_data = self.dbcon.add_up_de_commit(syssetting_mode_sql)
            if syssetting_mode_data == False:
                return False
        syssetting_mode_sql = "select * from t2d_syssetting_mode where modeid='%s' and settingid='%s' limit 1" % \
                              (listid, settingid)
        syssetting_mode_data = self.dbcon.select(syssetting_mode_sql)
        if syssetting_mode_data == False:
            syssetting_mode_sql = "insert into t2d_syssetting_mode(modeid,settingid,mode,siteid,enabled) values ('%s','%s','%s','%s',%d)" % \
                                  (listid, settingid, 'list', siteid, 0)
            syssetting_mode_data = self.dbcon.add_up_de_commit(syssetting_mode_sql)
            if syssetting_mode_data == False:
                return False
        syssetting_mode_sql = "select * from t2d_syssetting_mode where modeid='%s' and settingid='%s' limit 1" % \
                              (toolbarid, settingid)
        syssetting_mode_data = self.dbcon.add_up_de_commit(syssetting_mode_sql)
        if syssetting_mode_data == False:
            syssetting_mode_sql = "insert into t2d_syssetting_mode(modeid,settingid,mode,siteid,enabled,enablemap,enablecall) values ('%s','%s','%s','%s',%d)" % \
                                  (toolbarid, settingid, 'toolbar', siteid, 0, 0, 0)
            syssetting_mode_data = self.dbcon.add_up_de_commit(syssetting_mode_sql)
            if syssetting_mode_data == False:
                return False
        # 开通成功
        dbcommit = self.dbcon.commit()
        if dbcommit == True:
            status = {"code": "True", "msg": "操作成功", "error": "null"}
            return True
        else:
            return False
