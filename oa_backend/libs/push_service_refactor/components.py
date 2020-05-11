# __author__ = itsneo1990

from libs.push_service_refactor import resource
from libs.push_service_refactor.base import BaseComponent


class NoticeAccountCenter1st(BaseComponent):
    """1.开站前通知账号中心"""

    def __init__(self, *args, **kwargs):
        super(NoticeAccountCenter1st, self).__init__(*args, **kwargs)
        self.title = "开站前通知账号中心"
        self.post_sources = (
            (f"{self.user_center_url}/usercenter/enterprise/{self.site_id}/productFeature", {}),
        )


class NoticeAccountCenter2nd(BaseComponent):
    """2.开站后通知账号中心"""

    def __init__(self, *args, **kwargs):
        super(NoticeAccountCenter2nd, self).__init__(*args, **kwargs)
        self.title = "开站后通知账号中心"
        self.post_sources = (
            (f"{self.user_center_url}/usercenter/enterprise/{self.site_id}/productFunction", {}),
        )


class CreateSite(BaseComponent):
    """3.创建企业"""

    def __init__(self, *args, **kwargs):
        super(CreateSite, self).__init__(*args, **kwargs)
        self.title = "创建企业"
        self.exists_url = f"{self.user_center_url}/enterprise/{self.site_id}"
        self.post_sources = (
            (f"{self.user_center_url}/enterprise/{self.site_id}",
             resource.create_site(self.site_id, self.name)),
        )
        self.delete_sources = [
            f"{self.user_center_url}/enterprise/{self.site_id}"
        ]


class CreateGroup(BaseComponent):
    """4.创建行政组"""

    def __init__(self, *args, **kwargs):
        super(CreateGroup, self).__init__(*args, **kwargs)
        self.title = "创建行政组"
        self.exists_url = f"{self.user_center_url}/enterprise/{self.site_id}/group/{self.site_id}_9999"
        self.post_sources = (
            (f"{self.user_center_url}/enterprise/{self.site_id}/group", resource.create_group(self.site_id)),
        )
        self.delete_sources = [
            f"{self.user_center_url}/enterprise/{self.site_id}/group/{self.site_id}_9999",
        ]


class CreateRole(BaseComponent):
    """5.创建角色"""

    def __init__(self, *args, **kwargs):
        super(CreateRole, self).__init__(*args, **kwargs)
        self.title = "创建角色"
        self.exists_url = (
            f"{self.user_center_url}/enterprise/{self.site_id}/role/admin",
            f"{self.user_center_url}/enterprise/{self.site_id}/role/kf",
            f"{self.user_center_url}/enterprise/{self.site_id}/role/groupleader"
        )
        self.post_sources = (
            (f"{self.user_center_url}/enterprise/{self.site_id}/role", resource.create_role_admin(self.site_id)),
            (f"{self.user_center_url}/enterprise/{self.site_id}/role", resource.create_role_kf(self.site_id)),
            (f"{self.user_center_url}/enterprise/{self.site_id}/role", resource.create_role_group_leader(self.site_id))
        )
        self.delete_sources = (
            f"{self.user_center_url}/enterprise/{self.site_id}/role/admin",
            f"{self.user_center_url}/enterprise/{self.site_id}/role/kf",
            f"{self.user_center_url}/enterprise/{self.site_id}/role/groupleader",
        )


class CreateTag(BaseComponent):
    """6.创建默认标签"""

    def __init__(self, *args, **kwargs):
        super(CreateTag, self).__init__(*args, **kwargs)
        self.title = "创建个性化功能"
        self.post_sources = (
            (f"{self.user_center_url}/enterprise/{self.site_id}/tag", resource.create_tag(self.site_id)),
        )
        self.delete_sources = [
            f"{self.user_center_url}/enterprise/{self.site_id}/tag/{self.site_id}_default",
        ]


class CreateUser(BaseComponent):
    """7.创建超级管理员"""

    def __init__(self, *args, **kwargs):
        super(CreateUser, self).__init__(*args, **kwargs)
        self.title = "创建超级管理员"
        self.exists_url = f"{self.user_center_url}/enterprise/{self.site_id}/user/{self.site_id}_admin"
        self.post_sources = (
            (f"{self.user_center_url}/enterprise/{self.site_id}/user", resource.create_user(site_id=self.site_id)),
        )
        self.delete_sources = [
            f"{self.user_center_url}/enterprise/{self.site_id}/user/{self.site_id}_admin",
        ]


class CreateTemplate(BaseComponent):
    """8.创建用户群"""

    def __init__(self, *args, **kwargs):
        super(CreateTemplate, self).__init__(*args, **kwargs)
        self.title = "创建用户群"
        self.post_sources = (
            (f"{self.setting_url}/template/{self.site_id}", resource.create_template(self.site_id)),
        )
        self.delete_sources = [
            f"{self.setting_url}/template/{self.site_id}/{self.site_id}_template_9999"
        ]


class CreateConfigItems(BaseComponent):
    """9.创建企业级配置项"""

    def __init__(self, *args, **kwargs):
        super(CreateConfigItems, self).__init__(*args, **kwargs)
        self.title = "创建企业级配置项"
        self.post_sources = (
            (f"{self.setting_url}/configItems/{self.site_id}",
             {"item": num, "level": 0, "siteid": "zl_1006"}) for num in range(1, 9)
        )
        self.delete_sources = [
            f"{self.setting_url}/configItems/{self.site_id}"
        ]


class CreateGreetings(BaseComponent):
    """10.创建问候语"""

    def __init__(self, *args, **kwargs):
        super(CreateGreetings, self).__init__(*args, **kwargs)
        self.title = "创建问候语"
        self.post_sources = (
            (f"{self.setting_url}/auto/welcome/{self.site_id}", resource.create_greetings(self.site_id, self.name)),
        )
        self.delete_sources = [
            f"{self.setting_url}/auto/welcome/{self.site_id}"
        ]


class CreateAutoReply(BaseComponent):
    """11.创建自动应答"""

    def __init__(self, *args, **kwargs):
        super(CreateAutoReply, self).__init__(*args, **kwargs)
        self.title = "创建自动应答"
        self.post_sources = (
            (f"{self.setting_url}/auto/reply/{self.site_id}", resource.create_auto_reply(self.site_id)),
        )
        self.delete_sources = [
            f"{self.setting_url}/auto/reply/{self.site_id}"
        ]


class CreateLoca(BaseComponent):
    """12.创建个性化功能"""

    def __init__(self, *args, **kwargs):
        super(CreateLoca, self).__init__(*args, **kwargs)
        self.title = "创建个性化功能"
        self.post_sources = (
            (f"{self.setting_url}/settings/{self.site_id}/{self.site_id}/configChatset",
             resource.create_config_chatset(self.site_id)),
            (f"{self.setting_url}/settings/{self.site_id}/{self.site_id}/configIntelligent",
             resource.create_config_intelligent(self.site_id)),
            (f"{self.setting_url}/settings/{self.site_id}/{self.site_id}/configReply",
             resource.create_config_reply(self.site_id)),
            (f"{self.setting_url}/settings/{self.site_id}/{self.site_id}/configSkin",
             resource.create_config_skin(self.site_id)),
            (f"{self.setting_url}/settings/{self.site_id}/{self.site_id}/configTabmanager",
             resource.create_config_tab_manager(self.site_id)),
            (f"{self.setting_url}/settings/{self.site_id}/{self.site_id}/defaultWordbench",
             resource.create_default_word_bench(self.site_id))
        )
        self.delete_sources = [
            f"{self.setting_url}/settings/{self.site_id}/{self.site_id}/configChatset",
            f"{self.setting_url}/settings/{self.site_id}/{self.site_id}/configIntelligent",
            f"{self.setting_url}/settings/{self.site_id}/{self.site_id}/configReply",
            f"{self.setting_url}/settings/{self.site_id}/{self.site_id}/configSkin",
            f"{self.setting_url}/settings/{self.site_id}/{self.site_id}/configTabmanager",
            f"{self.setting_url}/settings/{self.site_id}/{self.site_id}/defaultWordbench",
        ]


class CreateQueue(BaseComponent):
    """13.创建排队"""

    def __init__(self, *args, **kwargs):
        super(CreateQueue, self).__init__(*args, **kwargs)
        self.title = "创建排队"
        self.post_sources = (
            (f"{self.setting_url}/queue/{self.site_id}", resource.create_queue()),
        )
        self.delete_sources = [
            f"{self.setting_url}/queue/{self.site_id}"
        ]


class CreateSensitive(BaseComponent):
    """14.创建敏感词"""

    def __init__(self, *args, **kwargs):
        super(CreateSensitive, self).__init__(*args, **kwargs)
        self.title = "创建敏感词"
        self.post_sources = (
            (f"{self.setting_url}/sensitiveWords/{self.site_id}", resource.create_sensitive(self.site_id)),
        )
        self.delete_sources = [
            f"{self.setting_url}/sensitiveWords/{self.site_id}"
        ]


class CreateWebChatData(BaseComponent):
    """15.创建web聊窗"""

    def __init__(self, *args, **kwargs):
        super(CreateWebChatData, self).__init__(*args, **kwargs)
        self.title = "创建web聊窗"
        self.post_sources = (
            (f"{self.setting_url}/webChat/{self.site_id}", resource.create_web_chat_data(self.site_id)),
        )
        self.delete_sources = [
            f"{self.setting_url}/webChat/{self.site_id}"
        ]


class CreateEvaluation(BaseComponent):
    """16.创建企业评价"""

    def __init__(self, *args, **kwargs):
        super(CreateEvaluation, self).__init__(*args, **kwargs)
        self.title = "创建企业评价"
        self.post_sources = (
            (f"{self.setting_url}/evaluation/{self.site_id}", resource.create_evaluation(self.site_id)),
        )
        self.delete_sources = [
            f"{self.setting_url}/evaluation/{self.site_id}"
        ]


class CreateLeavemsg(BaseComponent):
    """17.创建留言"""

    def __init__(self, *args, **kwargs):
        super(CreateLeavemsg, self).__init__(*args, **kwargs)
        self.title = "创建留言"
        self.post_sources = (
            (f"{self.setting_url}/leaveMsg/{self.site_id}", resource.create_leave_msg(self.site_id)),
        )
        self.delete_sources = [
            f"{self.setting_url}/leaveMsg/{self.site_id}"
        ]


class CreateSource(BaseComponent):
    """18.创建访客来源"""

    def __init__(self, *args, **kwargs):
        super(CreateSource, self).__init__(*args, **kwargs)
        self.title = "创建访客来源"

    def process(self):
        type_id_map = {}
        for data in resource.create_source_type(self.site_id):
            resp = self.post_remote_data(url=f"{self.setting_url}/source/{self.site_id}", data=data)
            code = resp.get("code", None) or resp.get("status", None)
            if not code == 200:
                return False, ""
            type_id_map[resp['data']['typename']] = resp['data']['source_type_id']

        for data in resource.create_source_sousuo(self.site_id, type_id_map['搜索引擎']):
            resp = self.post_remote_data(url=f"{self.setting_url}/source/{self.site_id}/item", data=data)
            code = resp.get("code", None) or resp.get("status", None)
            if not code == 200:
                return False, ""

        for data in resource.create_source_youqing(self.site_id, type_id_map['友情链接']):
            resp = self.post_remote_data(url=f"{self.setting_url}/source/{self.site_id}/item", data=data)
            code = resp.get("code", None) or resp.get("status", None)
            if not code == 200:
                return False, ""

        for data in resource.create_source_zhijie(self.site_id, type_id_map['直接访问']):
            resp = self.post_remote_data(url=f"{self.setting_url}/source/{self.site_id}/item", data=data)
            code = resp.get("code", None) or resp.get("status", None)
            if not code == 200:
                return False, ""
        return True, ""


class CreateToolbar(BaseComponent):
    """19.创建咨询接待工具栏"""

    def __init__(self, *args, **kwargs):
        super(CreateToolbar, self).__init__(*args, **kwargs)
        self.title = "创建咨询接待工具栏"
        self.delete_sources = [
            f"{self.setting_url}/toolbar/{self.site_id}"
        ]

    def process(self):
        resp = self.post_remote_data(url=f"{self.setting_url}/toolbar/{self.site_id}",
                                     data=resource.create_tool_bar(self.site_id))
        code = resp.get("code", None) or resp.get("status", None)
        if not code == 200:
            return False, ""
        return True, ""


class CreateMenuConfig(BaseComponent):
    """20.创建窗口主菜单"""

    def __init__(self, *args, **kwargs):
        super(CreateMenuConfig, self).__init__(*args, **kwargs)
        self.title = "创建窗口主菜单"
        self.post_sources = (
            (f"{self.setting_url}/menuconfig/{self.site_id}", resource.create_menu_config(self.site_id)),
        )
        self.delete_sources = [
            f"{self.setting_url}/menuconfig/{self.site_id}"
        ]
