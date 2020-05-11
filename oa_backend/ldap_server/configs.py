# xbot机器人域名
ROBOT_XBOT_URL = 'http://bj-v100.ntalker.com/'
ROBOT_YUNWEN_URL = 'http://hz-xnfaq.ntalker.com/'
MONTH_KEY = {
    "01": '!@*',
    "02": '%_@',
    "03": '#*@',
    "04": '%$！',
    "05": '%#*',
    "06": '*^+',
    "07": '&#%',
    "08": '*$#',
    "09": '@^*',
    "10": '!*$',
    "11": '_#@',
    "12": '%!&'
}

# 部署方式
DEPLOY_STANDARD = 1
DEPLOY_VIP = 2
DEPLOY_VPC = 3
DEPLOY_OEM = 4
DEPLOY_WAYS = (
    (DEPLOY_STANDARD, "标准版"),
    (DEPLOY_VIP, "VIP版"),
    (DEPLOY_VPC, "VPC版"),
    (DEPLOY_OEM, "企业版"),
)

# 客户版本
CLI_B2B = 1
CLI_B2C = 2
CLI_UNLIMITED = 3
CLI_CHOICES = (
    (CLI_B2B, "B2B"),
    (CLI_B2C, "B2C"),
    (CLI_UNLIMITED, "不限"),
)

# 站点类型
STATION_TRIAL = 1
STATION_OFFICAL = 2
STATION_MARKET = 3
STATION_BUSINESS = 4
STATION_PERSONAL = 5
STATION_CHOICES = (
    (STATION_TRIAL, "试用客户"),
    (STATION_OFFICAL, "正式客户"),
    (STATION_MARKET, "市场渠道客户"),
    (STATION_BUSINESS, "商务渠道客户"),
    (STATION_PERSONAL, "自用站点"),
)

# 客户类型
CUSTOM_NEW = False
CUSTOM_OLD = True
CUSTOM_TYPES = (
    (CUSTOM_NEW, "新客户"),
    (CUSTOM_OLD, "老客户"),
)

# 咨询渠道
CHANNEL_UNKNOWN = -1
CHANNEL_PC = 6
CHANNEL_WECHAT = 1
CHANNEL_APP = 2
CHANNEL_WAP = 3
CHANNEL_IOS = 4
CHANNEL_ANDROID = 5
CHANNEL_WEIBO = 7
CHANNEL_QQ = 8

CHANNEL_CHOICES = (
    (CHANNEL_PC, "PC"),
    (CHANNEL_WECHAT, "微信"),
    (CHANNEL_APP, "APP"),
    (CHANNEL_WAP, "WAP"),
    (CHANNEL_IOS, "IOS"),
    (CHANNEL_ANDROID, "Android"),
    (CHANNEL_UNKNOWN, "未知"),
    (CHANNEL_WEIBO, "微博"),
    (CHANNEL_QQ, "QQ"),
)

CHANNEL_TYPES = (
    (CHANNEL_PC, 'CHANNEL_PC'),
    (CHANNEL_WECHAT, 'CHANNEL_WECHAT'),
    (CHANNEL_APP, 'CHANNEL_APP'),
    (CHANNEL_WAP, 'CHANNEL_WAP'),
    (CHANNEL_IOS, 'CHANNEL_IOS'),
    (CHANNEL_ANDROID, 'CHANNEL_ANDROID'),
    (CHANNEL_UNKNOWN, 'CHANNEL_UNKNOWN'),
    (CHANNEL_WEIBO, 'CHANNEL_WEIBO'),
    (CHANNEL_QQ, 'CHANNEL_QQ'),
)

# 日志模块
MODULES_MAP = {
    "openstationmanage-detail": "工单管理-开站管理",
    "openstationmanage-list": "工单管理-开站管理",
    "industry-list": "设置-客户行业",
    "industry-detail": "设置-客户行业",
    "openstationmanage-modify-status": "工单管理-修改状态",
    "server-detail": "产品管理-运维配置-服务器",
    "server-list": "产品管理-运维配置-服务器",
    "servergroup-detail": "产品管理-运维配置-服务组",
    "servergroup-list": "产品管理-运维配置-服务组",
    "grid-detail": "产品管理-运维配置-节点",
    "grid-list": "产品管理-运维配置-节点",
    "sertype-detail": "产品管理-运维配置-产品关联",
    "sertype-list": "产品管理-运维配置-产品关联",
    "product-detail": "产品管理-产品配置",
    "product-list": "产品管理-产品配置",
    "versioninfo-list": "产品管理-版本",
    "versioninfo-detail": "产品管理-版本",
    "functioninfo-list": "产品管理-功能开关",
    "functioninfo-detail": "产品管理-功能开关",
    "singleselection-modify-default": "产品管理-功能开关-更改默认选项",
    "group-detail": "权限和人员管理-角色权限",
    "group-list": "权限和人员管理-角色权限",
    "user-detail": "权限和人员管理-人员配置",
    "user-list": "权限和人员管理-人员配置",
}

# 日志类型
TYPE_POST = 1
TYPE_DELETE = 2
TYPE_PUT = 3
TYPE_LOGIN = 4
TYPE_LOGOUT = 5
TYPE_ELSE = 500
LOG_TYPE_CHOICES = (
    (TYPE_POST, "新增"),
    (TYPE_DELETE, "删除"),
    (TYPE_PUT, "修改"),
    (TYPE_LOGIN, "登录"),
    (TYPE_LOGOUT, "退出"),
    (TYPE_ELSE, "其他"),
)

ACTION_MAP = {
    "POST": TYPE_POST,
    "PUT": TYPE_PUT,
    "DELETE": TYPE_DELETE,
}

# 运营记录统计
OPERATE_CREATE = 1
OPERATE_RENEWAL = 2
OPERATE_ADD_PRODUCT = 3
OPERATE_ONLINE = 4
OPERATE_OFFLINE = 5
OPERATE_ACTION_CHOICES = (
    (OPERATE_CREATE, "新增客户"),
    (OPERATE_RENEWAL, "续费客户"),
    (OPERATE_ADD_PRODUCT, "新增产品"),
    (OPERATE_ONLINE, "上线客户"),
    (OPERATE_OFFLINE, "下线客户"),
)

# 产品—服务分类
CLASSIC_VERSION = 1
REFACTOR_VERSION = 2
PROD_SERV_VERSIONS = (
    (REFACTOR_VERSION, '重构版'),
    (CLASSIC_VERSION, '经典版')
)
