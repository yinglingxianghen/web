# __author__ = itsneo1990
import logging
from queue import LifoQueue

from libs.push_service_refactor.components import CreateSite, \
    CreateGroup, CreateRole, CreateTag, CreateUser, CreateTemplate, CreateConfigItems, CreateGreetings, CreateAutoReply, \
    CreateLoca, CreateQueue, CreateSensitive, CreateWebChatData, CreateEvaluation, CreateLeavemsg, CreateSource, \
    CreateToolbar, CreateMenuConfig, NoticeAccountCenter1st, NoticeAccountCenter2nd

logger = logging.getLogger(__name__)


class SitePush:
    def __init__(self, site_id, name):

        self.site_id = site_id
        self.name = name

        self.user_center = "http://usercenter-devdebug.ntalker.com"
        self.setting_center = "http://dolphinsetting-devdebug.ntalker.com"

        self.steps = [
            NoticeAccountCenter1st,
            NoticeAccountCenter2nd,
            CreateSite,
            CreateGroup,
            CreateRole,
            CreateTag,
            CreateUser,
            CreateTemplate,
            CreateConfigItems,
            CreateGreetings,
            CreateAutoReply,
            CreateLoca,
            CreateQueue,
            CreateSensitive,
            CreateWebChatData,
            CreateEvaluation,
            CreateLeavemsg,
            CreateSource,
            CreateToolbar,
            CreateMenuConfig
        ]

        self.processed_steps = LifoQueue()  # 先进后出，堆结构

    def push(self):
        for step in self.steps:
            step_obj = step(**self.get_params())
            is_success, msg = step_obj.process()
            if is_success:
                self.processed_steps.put(step_obj)
            else:
                while not self.processed_steps.empty():
                    self.processed_steps.get().rollback()
                break

    def get_params(self):
        return {
            "site_id": self.site_id,
            "name": self.name,
            "setting_url": self.setting_center,
            "user_center_url": self.user_center
        }
