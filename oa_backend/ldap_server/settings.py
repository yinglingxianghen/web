import djcelery
import ldap
import os
from django_auth_ldap.config import LDAPSearch, NestedOrganizationalRoleGroupType, GroupOfUniqueNamesType

from libs.environment import ENV

current_env = ENV()

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
BASE_URL = current_env.get_config("BASE_URL")
SECRET_KEY = current_env.get_config("SECRET_KEY")
DEBUG = current_env.get_config("DEBUG")

ALLOWED_HOSTS = ['*']

# Application definition
INSTALLED_APPS = [
    # 'django.contrib.sites',
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',

    # applications
    'applications.backend',
    'applications.permission_and_staff_manage',
    'applications.production_manage',
    'applications.log_manage',
    'applications.workorder_manage',
    'applications.data_manage',
    'applications.setup',

    # Third part
    'rest_framework',
    'raven.contrib.django.raven_compat',  # Sentry
    'djcelery'
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'libs.middlewares.query_count.QueryCountMiddleware',
]

ROOT_URLCONF = 'ldap_server.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [os.path.join(BASE_DIR, "templates")],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'ldap_server.wsgi.application'

DATABASES = {
    'ldap': {
        'ENGINE': 'ldapdb.backends.ldap',
        'NAME': current_env.get_config("LDAP_SERVER_URL"),
        'USER': 'cn=admin,dc=xiaoneng,dc=cn',
        'PASSWORD': '8ql6,yhY',
    },
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'HOST': current_env.get_config("DB_HOST"),
        'NAME': current_env.get_config("DB_NAME"),
        'USER': current_env.get_config("DB_USER"),
        'PASSWORD': current_env.get_config("DB_PASSWORD"),
        'PORT': current_env.get_config("DB_PORT")
    }
}

DATABASE_ROUTERS = ['ldapdb.router.Router']

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'Asia/Shanghai'

USE_I18N = True

USE_L10N = True

USE_TZ = True

STATIC_URL = '/backend_static/'
# STATIC_ROOT = os.path.join(BASE_DIR, "static")
STATICFILES_DIRS = [os.path.join(BASE_DIR, "static")]


REST_FRAMEWORK = {
    'DEFAULT_PAGINATION_CLASS': 'libs.pagination.CustomPagination',
    'PAGE_SIZE': 10
}

SESSION_EXPIRE_AT_BROWSER_CLOSE = True

AUTHENTICATION_BACKENDS = (
    'django_auth_ldap.backend.LDAPBackend',
    'django.contrib.auth.backends.ModelBackend',
)

AUTH_LDAP_SERVER_URI = "ldap://ldap.xiaoneng.cn"
# 默认用户DN模板
# AUTH_LDAP_USER_DN_TEMPLATE = "cn=%(user)s,ou=Users,dc=xiaoneng,dc=cn"

# 搜索组织架构树
AUTH_LDAP_BIND_DN = "cn=admin,dc=xiaoneng,dc=cn"
AUTH_LDAP_BIND_PASSWORD = "8ql6,yhY"
AUTH_LDAP_USER_SEARCH = LDAPSearch("ou=Users,dc=xiaoneng,dc=cn", ldap.SCOPE_SUBTREE, "(cn=%(user)s)")

AUTH_LDAP_GROUP_SEARCH = LDAPSearch("cn=LDAP,ou=Roles,dc=xiaoneng,dc=cn", ldap.SCOPE_SUBTREE,
                                    "(objectClass=groupOfUniqueNames)")
AUTH_LDAP_GROUP_TYPE = GroupOfUniqueNamesType()

# LDAP和django user model列对应, 方便admin页面管理查看
AUTH_LDAP_USER_ATTR_MAP = {
    "first_name": "givenName",
    "last_name": "sn",
    "email": "mail"
}

AUTH_LDAP_USER_FLAGS_BY_GROUP = {
    "is_active": "cn=users,cn=LDAP,ou=Roles,dc=xiaoneng,dc=cn",
    "is_staff": "cn=ldap-admin,cn=LDAP,ou=Roles,dc=xiaoneng,dc=cn",
    "is_superuser": "cn=ldap-admin,cn=LDAP,ou=Roles,dc=xiaoneng,dc=cn"
}

LOG_DIR = os.path.join(BASE_DIR, 'log')

if not os.path.exists(LOG_DIR):
    os.makedirs(LOG_DIR)

LOGGING = {
    'version': 1,
    'disable_existing_loggers': True,
    'formatters': {
        'standard_bak': {
            'format': '%(asctime)s [%(threadName)s:%(thread)d] [%(name)s:%(lineno)d] [%(levelname)s]- %(message)s'
        },
        'standard': {
            'format': '[%(asctime)s] [%(threadName)s:%(thread)d:%(name)s] '
                      '[%(levelname)s] [%(module)s.%(funcName)s Line:%(lineno)d]- %(message)s'
        },
    },
    'filters': {
    },
    'handlers': {
        'default': {
            'level': 'INFO',
            'class': 'logging.handlers.TimedRotatingFileHandler',
            'filename': os.path.join(LOG_DIR, 'default.log'),  # 或者直接写路径：'c:\logs\all.log',
            #'maxBytes': 1024 * 1024 * 5,  # 5 MB
            'backupCount': 5,
            'formatter': 'standard',
            'interval':1,
            'when':'D',
            'delay':True
        },
        'worker': {
            'level': 'INFO',
            'class': 'logging.handlers.TimedRotatingFileHandler',
            'filename': os.path.join(LOG_DIR, 'work.log'),  # 或者直接写路径：'c:\logs\all.log',
            #'maxBytes': 1024 * 1024 * 5,  # 5 MB
            'backupCount': 5,
            'formatter': 'standard',
            'interval':1,
            'when':'D',
            'delay':True
        },
        'error': {
            'level': 'ERROR',
            'class': 'logging.handlers.TimedRotatingFileHandler',
            'filename': os.path.join(LOG_DIR, 'error.log'),  # 或者直接写路径：'c:\logs\all.log',
            #'maxBytes': 1024 * 1024 * 5,  # 5 MB
            'backupCount': 5,
            'formatter': 'standard',
            'interval':1,
            'when':'D',
            'delay':True
        },
        'console': {
            'level': 'INFO',
            'class': 'logging.StreamHandler',
            'formatter': 'standard'
        },
    },
    'loggers': {
        'django': {
            'handlers': ['default', 'console', 'error'],
            'level': 'DEBUG',
            'propagate': False
        },
        'worker': {
            'handlers': ['worker', 'console', 'error'],
            'level': 'INFO',
            'propagate': False
        },
    }
}

REDIS_URL = 'redis://:%s@%s:%s/%s' % (current_env.get_config("REDIS_PASSWORD"),
                                      current_env.get_config("REDIS_SERVER"),
                                      current_env.get_config("REDIS_PORT"),
                                      current_env.get_config("REDIS_DBNUM"))

if DEBUG:
    REST_FRAMEWORK.update(dict(DEFAULT_PERMISSION_CLASSES=['rest_framework.permissions.AllowAny', ]))
else:
    REST_FRAMEWORK.update(dict(DEFAULT_PERMISSION_CLASSES=['rest_framework.permissions.DjangoModelPermissions', ]))
    RAVEN_CONFIG = {
        'dsn': 'https://dee3b85a296e48f7afda377f3e6b1c95:3e31e6a523b74470944e6b87198f47c0@sentry.io/217378',
        'release': 'de49621e99c011e7b21a4201c0a8d03b'
    }

# celery任务相关配置
djcelery.setup_loader()
CELERYBEAT_SCHEDULER = 'djcelery.schedulers.DatabaseScheduler'
CELERY_ACCEPT_CONTENT = ['json']
CELERY_TASK_SERIALIZER = 'json'
CELERY_RESULT_SERIALIZER = 'json'

# 定时数据库备份目录
BACKUP_PATH = "/db_backup"

# db_info数据库密码加密秘钥
CRYPT_SECRET = "_w;*w0&^u;n8}:c+|ongbo1-{b!*d()+"

# 白山云文件存储账户信息，（帮助中心头像图片）
BAISHANYUN_CONFIGS = {
    "service_name": "s3",
    "aws_access_key_id": "70sqinux2yp3fdet14bk",
    "aws_secret_access_key": "uYkqsdAwTcUgMYBxbrrl+M4U5aMh9S26or47s4jW",
    "endpoint_url": "http://s2.i.qingcdn.com",
}

# 帮助中心上传头像size，宽， 高
AVATAR_SIZE = (280, 280)

# DEBUG时开启的query_count中间件配置
QC_SETTINGS = {
    'THRESHOLDS': {
        'MEDIUM': 20,
        'HIGH': 50,
        'MIN_TIME_TO_LOG': 0,
        'MIN_QUERY_COUNT_TO_LOG': 0
    },
    'IGNORE_REQUEST_PATTERNS': [],
    'IGNORE_SQL_PATTERNS': [
        r"^/admin/",
    ],
    'DISPLAY_DUPLICATES': 10,
    'RESPONSE_HEADER': 'X-DjangoQueryCount-Count'
}

try:
    from .configs import *
except ImportError:
    pass
