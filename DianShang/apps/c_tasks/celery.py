
from celery import Celery

# 创建celery实例
app = Celery('c_tasks')
app.config_from_object('c_tasks.c_config')

# 搜索任务
app.autodiscover_tasks(['c_tasks'])