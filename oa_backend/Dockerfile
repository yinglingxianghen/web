FROM reg.xiaoneng.cn/oa/backend_base:latest

MAINTAINER itsneo1990 <itsneo1990@gmail.com>

WORKDIR /src

COPY . .

ENV TZ "Asia/Shanghai"

CMD ["gunicorn", "ldap_server.wsgi", "--workers=5", "--bind=0.0.0.0:8000", "--reload"]
