"""
function：Functionset 功能开关
describe：功能开关操作类封装
date：20171127
author：gjf
version:1.09
"""
# coding=utf-8
from libs.push_service.robot import Robot
class Functionset:
    """
    function:__init__
    describe:构造函数初始连接数据库kf库
    param: pymysql.cursors.Cursor @dbcon kf库
    """
    def __init__(self, dbcon):
        self.dbcon = dbcon

    """
    function:erpserver
    describe:erp显示功能开通和关闭 关闭:0,开通:1
    param: string @siteid 企业id
    switch: string @switch 开关
    """
    def erpserver(self, siteid, switch):
        sql = "update t2d_enterpriseinfo set erpserver='%s' where siteid='%s'" % (switch, siteid)
        data = self.dbcon.add_up_de(sql)
        if data == False:
            return False
        else:
            return True
    """
    function:iscommodity
    describe:商品接口设置功能开通和关闭 关闭:0,开通:1
    param: string @siteid 企业id
    switch: string @switch 开关
    """
    def iscommodity(self, siteid, switch):
        sql = "update t2d_enterpriseinfo set iscommodity='%s' where siteid='%s'" % (switch, siteid)
        data = self.dbcon.add_up_de(sql)
        if data == False:
            return False
        else:
            return True
    """
    function:isweixin
    describe:微信设置功能开通和关闭 关闭:0,开通:1
    param: string @siteid 企业id
    switch: string @switch 开关
    """
    def isweixin(self, siteid, switch):
        sql = "update t2d_enterpriseinfo set isweixin='%s' where siteid='%s'" % (switch, siteid)
        data = self.dbcon.add_up_de(sql)
        if data == False:
            return False
        else:
            return True
    """
    function:autoconnect
    describe:连接客服逻辑功能开通和关闭 直接连接:1,输入信息后连接:0
    param: string @siteid 企业id
    switch: string @switch 开关
    """
    def autoconnect(self, siteid, switch):
        sql = "update t2d_enterpriseinfo set autoconnect='%s' where siteid='%s'" % (switch, siteid)
        data = self.dbcon.add_up_de(sql)
        if data == False:
            return False
        else:
            return True
    """
    function:iserp
    describe:开启erp功能开通和关闭 关闭:0,开通:1
    param: string @siteid 企业id
    switch: string @switch 开关
    """
    def iserp(self, siteid, switch):
        sql = "update t2d_enterpriseinfo set iserp='%s' where siteid='%s'" % (switch, siteid)
        data = self.dbcon.add_up_de(sql)
        if data == False:
            return False
        else:
            return True
    """
    function:ticket
    describe:工单设置功能开通和关闭 关闭:0,开通:1
    param: string @siteid 企业id
    switch: string @switch 开关
    """
    def ticket(self, siteid, switch):
        sql = "update t2d_enterpriseinfo set ticket='%s' where siteid='%s'" % (switch, siteid)
        data = self.dbcon.add_up_de(sql)
        if data == False:
            return False
        else:
            return True
    """
    function:smarteye
    describe:帮助中心设置功能开通和关闭 关闭:0,开通:1
    param: string @siteid 企业id
    switch: string @switch 开关
    """
    def smarteye(self, siteid:str, switch:str) -> bool:
        sql = "update t2d_enterpriseinfo set smarteye='%s' where siteid='%s'" % (switch, siteid)
        data = self.dbcon.add_up_de(sql)
        if data == False:
            return False
        else:
            return True
    """
    function:enable_artificialgreeting
    describe:默认欢迎语功能开通和关闭 关闭:0,开通:1
    param: string @siteid 企业id
    switch: string @switch 开关
    """
    def enable_artificialgreeting(self, siteid, switch):
        sql = "update t2d_enterpriseinfo set enable_artificialgreeting='%s' where siteid='%s'" % (switch, siteid)
        data = self.dbcon.add_up_de(sql)
        if data:
            return True
        else:
            return False
    """
    function:changecsr
    describe:更换客服功能开通和关闭 关闭:0,开通:1
    param: string @siteid 企业id
    switch: string @switch 开关
    """
    def changecsr(self, siteid, switch):
        sql = "update t2d_enterpriseinfo set changecsr='%s' where siteid='%s'" % (switch, siteid)
        data = self.dbcon.add_up_de(sql)
        if data == False:
            return False
        else:
            return True
    """
    function:xiaonengver
    describe:小能版权信息功能开通和关闭 关闭:0,开通:1
    param: string @siteid 企业id
    switch: string @switch 开关
    """
    def xiaonengver(self, siteid, switch):
        sql = "update t2d_enterpriseinfo set xiaonengver='%s' where siteid='%s'" % (switch, siteid)
        data = self.dbcon.add_up_de(sql)
        if data == False:
            return False
        else:
            return True
    """
    function:watchqueue
    describe:客户端查看排队信息功能开通和关闭 关闭:0,开通:1
    param: string @siteid 企业id
    switch: string @switch 开关
    """
    def watchqueue(self, siteid, switch):
        sql = "update t2d_enterpriseinfo set watchqueue='%s' where siteid='%s'" % (switch, siteid)
        data = self.dbcon.add_up_de(sql)
        if data == False:
            return False
        else:
            return True
    """
    function:linechannel
    describe:二维码功能开通和关闭 关闭:0,开通:1
    param: string @siteid 企业id
    switch: string @switch 开关
    """
    def linechannel(self, siteid, switch):
        sql = "update t2d_enterpriseinfo_extend set linechannel='%s' where siteid='%s'" % (switch, siteid)
        data = self.dbcon.add_up_de(sql)
        if data == False:
            return False
        else:
            return True
    """
    function:autoexpansion
    describe:是否展开侧边栏功能开通和关闭 关闭:0,开通:1
    param: string @siteid 企业id
    switch: string @switch 开关
    """
    def autoexpansion(self, siteid, switch):
        sql = "update t2d_enterpriseinfo set autoexpansion='%s' where siteid='%s'" % (switch, siteid)
        data = self.dbcon.add_up_de(sql)
        if data == False:
            return False
        else:
            return True
    """
    function:isnoim
    describe:更改IM连接级别功能开通和关闭
             进入网页就加载im服务,访客关闭聊窗,收到客服发送消息后,弹tip:0,
             关闭im服务,访客关闭聊窗,收不到客服发送的消息:1,
             打开聊窗后,再加载im服务,访客关闭聊窗,收到客服发送消息后,弹tip:2,
             进入网页就加载im服务,访客关闭聊窗,收到客服发送消息后,直接打开聊窗:3
    param: string @siteid 企业id
    switch: string @switch 开关
    """
    def isnoim(self, siteid, switch):
        sql = "update t2d_enterpriseinfo set isnoim='%s' where siteid='%s'" % (switch, siteid)
        data = self.dbcon.add_up_de(sql)
        if data == False:
            return False
        else:
            return True
    """
    function:transferfiles
    describe:访客端是否显示上传文件按钮功能开通和关闭 关闭:0,开通:1
    param: string @siteid 企业id
    switch: string @switch 开关
    """
    def transferfiles(self, siteid, switch):
        sql = "update t2d_enterpriseinfo set transferfiles='%s' where siteid='%s'" % (switch, siteid)
        data = self.dbcon.add_up_de(sql)
        if data == False:
            return False
        else:
            return True

    """
    function:close_im_flash
    describe:IM的flash连接功能开通和关闭 关闭:0,开通:1
    param: string @siteid 企业id
    switch: string @switch 开关
    """
    def close_im_flash(self, siteid, switch):
        sql = "update t2d_enterpriseinfo set close_im_flash='%s' where siteid='%s'" % (switch, siteid)
        data = self.dbcon.add_up_de(sql)
        if data == False:
            return False
        else:
            return True
    """
    function:close_tchat_flash
    describe:tchat的flash连接功能开通和关闭 关闭:0,开通:1
    param: string @siteid 企业id
    switch: string @switch 开关
    """
    def close_tchat_flash(self, siteid, switch):
        sql = "update t2d_enterpriseinfo set close_tchat_flash='%s' where siteid='%s'" % (switch, siteid)
        data = self.dbcon.add_up_de(sql)
        if data == False:
            return False
        else:
            return True
    """
    function:resize_chat
    describe:聊天窗口是否可变换大小功能开通和关闭 关闭:0,开通:1
    param: string @siteid 企业id
    switch: string @switch 开关
    """
    def resize_chat(self, siteid, switch):
        sql = "update t2d_enterpriseinfo set resize_chat='%s' where siteid='%s'" % (switch, siteid)
        data = self.dbcon.add_up_de(sql)
        if data == False:
            return False
        else:
            return True
    """
    function:drag_chat
    describe:聊天窗口是否可拖动功能开通和关闭 关闭:0,开通:1
    param: string @siteid 企业id
    switch: string @switch 开关
    """
    def drag_chat(self, siteid, switch):
        sql = "update t2d_enterpriseinfo set drag_chat='%s' where siteid='%s'" % (switch, siteid)
        data = self.dbcon.add_up_de(sql)
        if data == False:
            return False
        else:
            return True
    """
    function:enable_robotgreeting
    describe:是否启用机器人1.0欢迎语开通和关闭 关闭:0,开通:1
    param: string @siteid 企业id
    switch: string @switch 开关
    """
    def enable_robotgreeting(self, siteid, switch):
        sql = "update t2d_enterpriseinfo set enable_robotgreeting='%s' where siteid='%s'" % (switch, siteid)
        data = self.dbcon.add_up_de(sql)
        if data == False:
            return False
        else:
            return True
    """
    function:notrail
    describe:轨迹调用开通和关闭 进入网页就加载轨迹服务:0,关闭轨迹服务:1,打开聊窗后,再加载轨迹服务:2
    param: string @siteid 企业id
    switch: string @switch 开关
    """
    def notrail(self, siteid, switch):
        sql = "update t2d_enterpriseinfo set notrail='%s' where siteid='%s'" % (switch, siteid)
        data = self.dbcon.add_up_de(sql)
        if data == False:
            return False
        else:
            return True
    """
    function:captureimage
    describe:访客端截图插件功能开通和关闭 关闭:0,开通:1
    param: string @siteid 企业id
    switch: string @switch 开关
    """
    def captureimage(self, siteid, switch):
        sql = "update t2d_enterpriseinfo set captureimage='%s' where siteid='%s'" % (switch, siteid)
        data = self.dbcon.add_up_de(sql)
        if data == False:
            return False
        else:
            return True
    """
    function:sessioncarry
    describe:会话携带功能开通和关闭 关闭:0,开通:1
    param: string @siteid 企业id
    switch: string @switch 开关
    """
    def sessioncarry(self, siteid, switch):
        sql = "update t2d_enterpriseinfo set sessioncarry='%s' where siteid='%s'" % (switch, siteid)
        data = self.dbcon.add_up_de(sql)
        if data == False:
            return False
        else:
            return True
    """
    function:viewchatrecord
    describe:前端查看聊天记录功能开通和关闭 关闭:0,开通:1
    param: string @siteid 企业id
    switch: string @switch 开关
    """
    def viewchatrecord(self, siteid, switch):
        sql = "update t2d_enterpriseinfo set viewchatrecord='%s' where siteid='%s'" % (switch, siteid)
        data = self.dbcon.add_up_de(sql)
        if data == False:
            return False
        else:
            return True
    """
    function:enable_entrance
    describe:新版邀请功能开通和关闭 关闭:0,开通:1
    param: string @siteid 企业id
    switch: string @switch 开关
    """
    def enable_entrance(self, siteid, switch):
        sql = "update t2d_enterpriseinfo set enable_entrance='%s' where siteid='%s'" % (switch, siteid)
        data = self.dbcon.add_up_de(sql)
        if data == False:
            return False
        else:
            return True
    """
    function:androidtransf
    describe:WAP图片上传功能（安卓）功能开通和关闭 关闭:0,开通:1
    param: string @siteid 企业id
    switch: string @switch 开关
    """
    def androidtransf(self, siteid, switch):
        sql = "update t2d_enterpriseinfo set androidtransf='%s' where siteid='%s'" % (switch, siteid)
        data = self.dbcon.add_up_de(sql)
        if data == False:
            return False
        else:
            return True
    """
    function:othertransf
    describe:WAP图片上传功能（非安卓）功能开通和关闭 关闭:0,开通:1
    param: string @siteid 企业id
    switch: string @switch 开关
    """
    def othertransf(self, siteid, switch):
        sql = "update t2d_enterpriseinfo set othertransf='%s' where siteid='%s'" % (switch, siteid)
        data = self.dbcon.add_up_de(sql)
        if data == False:
            return False
        else:
            return True
    """
    function:sessionmode
    describe:是否开通公平模式功能开通和关闭 关闭:0,开通:1
    param: string @siteid 企业id
    switch: string @switch 开关
    """
    def sessionmode(self, siteid, switch):
        sql = "update t2d_enterpriseinfo set sessionmode='%s' where siteid='%s'" % (switch, siteid)
        data = self.dbcon.add_up_de(sql)
        if data == False:
            return False
        else:
            return True

    # 小能使用模式
    def mode(self, siteid, switch):
        sql = "update t2d_enterpriseinfo set mode='%s' where siteid='%s'" % (switch, siteid)
        data = self.dbcon.add_up_de(sql)
        if data == False:
            return False
        else:
            return True

    def sessionhelp(self, siteid, switch):
        sql = "update t2d_enterpriseinfo set sessionhelp='%s' where siteid='%s'" % (switch, siteid)
        data = self.dbcon.add_up_de(sql)
        if data == False:
            return False
        else:
            return True

    # WAP聊窗功能开关功能开通和关闭 关闭:0,开通:1
    def wap(self, siteid, switch):
        sql = "update t2d_enterpriseinfo set wap='%s' where siteid='%s'" % (switch, siteid)
        data = self.dbcon.add_up_de(sql)
        if data == False:
            return False
        else:
            return True

    # 打开链接方式功能开通和关闭 关闭:0,开通:1
    def waphref(self, siteid, switch):
        sql = "update t2d_enterpriseinfo set waphref='%s' where siteid='%s'" % (switch, siteid)
        data = self.dbcon.add_up_de(sql)
        if data == False:
            return False
        else:
            return True

    # 聊天记录是否可导出功能开通和关闭 关闭:0,开通:1
    def chatingrecord(self, siteid, switch):
        sql = "update t2d_enterpriseinfo set chatingrecord='%s' where siteid='%s'" % (switch, siteid)
        data = self.dbcon.add_up_de(sql)
        if data == False:
            return False
        else:
            return True

    # 敏感词开关功能开通和关闭 关闭:0,开通:1
    def filter(self, siteid, switch):
        sql = "update t2d_enterpriseinfo set filter='%s' where siteid='%s'" % (switch, siteid)
        data = self.dbcon.add_up_de(sql)
        if data == False:
            return False
        else:
            return True

    # 会话接管功能开通和关闭 关闭:0,开通:1
    def sessiontakeover(self, siteid, switch):
        sql = "update t2d_enterpriseinfo set sessiontakeover='%s' where siteid='%s'" % (switch, siteid)
        data = self.dbcon.add_up_de(sql)
        if data == False:
            return False
        else:
            return True

    # 接待时间功能开通和关闭 关闭:0,开通:1
    def isrecep_time(self, siteid, switch):
        sql = "update t2d_enterpriseinfo set isrecep_time='%s' where siteid='%s'" % (switch, siteid)
        data = self.dbcon.add_up_de(sql)
        if data == False:
            return False
        else:
            return True

    # 会话断开时间功能 单位秒
    def contime(self, siteid, switch):
        sql = "update t2d_enterpriseinfo set contime='%s' where siteid='%s'" % (switch, siteid)
        data = self.dbcon.add_up_de(sql)
        if data == False:
            return False
        else:
            return True

    # 客服坐席数功能 单位/人
    def kfsum(self, siteid, switch):
        sql = "update t2d_enterpriseinfo set kfsum='%s' where siteid='%s'" % (switch, siteid)
        data = self.dbcon.add_up_de(sql)
        if data == False:
            return False
        else:
            return True

    # qq功能开通和关闭 关闭:0,开通:1
    def is_qq(self, siteid, switch):
        sql = "update t2d_enterpriseinfo_extend set is_qq='%s' where siteid='%s'" % (switch, siteid)
        data = self.dbcon.add_up_de(sql)
        if data == False:
            return False
        else:
            return True

    # 微博功能开通和关闭 关闭:0,开通:1
    def is_weibo(self, siteid, switch):
        sql = "update t2d_enterpriseinfo_extend set is_weibo='%s' where siteid='%s'" % (switch, siteid)
        data = self.dbcon.add_up_de(sql)
        if data == False:
            return False
        else:
            return True

    # （教育版）咨询接待-邀请会话功能开通和关闭 关闭:0,开通:1
    def reversechat(self, siteid, switch):
        sql = "update t2d_enterpriseinfo_extend set reversechat='%s' where siteid='%s'" % (switch, siteid)
        data = self.dbcon.add_up_de(sql)
        if data == False:
            return False
        else:
            return True

    # （（教育版）KPI-邀请会话功能开通和关闭 关闭:0,开通:1
    def isyqhh(self, siteid, switch):
        sql = "update t2d_enterpriseinfo_extend set isyqhh='%s' where siteid='%s'" % (switch, siteid)
        data = self.dbcon.add_up_de(sql)
        if data == False:
            return False
        else:
            return True

    # （教育版）数据分析 - 运营报表功能开通和关闭 关闭:0,开通:1
    def ishhlx(self, siteid, switch):
        sql = "update t2d_enterpriseinfo_extend set ishhlx='%s' where siteid='%s'" % (switch, siteid)
        data = self.dbcon.add_up_de(sql)
        if data == False:
            return False
        else:
            return True

    # 机器人开关 关闭:0,开通:1
    def xbot(self, siteid, switch):
        if int(switch)==1:
            robot = Robot(self.dbcon)
            robot_re=robot.createrobot_xbot(siteid)
            if robot_re==False:
                return False
            else:
                return True
        else:
            return True
    def yunwen(self,siteid,switch):
        if int(switch)==1:
            robot = Robot(self.dbcon)
            robot_re=robot.createrobot_yunwen(siteid)
            if robot_re==False:
                return False
            else:
                return True
        else:
            return True
    def coop(self,siteid,switch):
        return True