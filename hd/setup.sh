#!/bin/bash

APACHE_RUN_USER="www-data"
PROJECT_NAME="hd"
PROJECT_DIR="/usr/src/app"
MYSQL_HOST="mysql"
MYSQL_PORT=3306
MYSQL_USER="root"
MYSQL_PASSWORD="abc123"
MYSQL_DATA_DIR=${PROJECT_DIR}"/hdMysqlData"

APACHE2_PROJECT_CONF="/etc/apache2/sites-available/${PROJECT_NAME}.conf"

chown -Rf ${APACHE_RUN_USER}:${APACHE_RUN_GROUP} ${PROJECT_DIR}
chsh -s /bin/sh ${APACHE_RUN_USER}


if [ ! -f "${APACHE2_PROJECT_CONF}" ]; then
	cp -f ${PROJECT_DIR}/conf/wsgi.apache ${APACHE2_PROJECT_CONF}
	sed -i "s#__INSERT_ADMIN_EMAIL__#${PROJECT_NAME}.com#" ${APACHE2_PROJECT_CONF}
	sed -i "s#__WSGI_FULLPATH__#${PROJECT_DIR}/${PROJECT_NAME}/wsgi.py#" ${APACHE2_PROJECT_CONF}
	sed -i "s#__PROJECT_NAME__#${PROJECT_NAME}#" ${APACHE2_PROJECT_CONF}
	sed -i "s#__WEB_PATH__#${PROJECT_DIR}#" ${APACHE2_PROJECT_CONF}

fi
a2ensite ${PROJECT_NAME}


if [ -f "/etc/apache2/sites-enabled/000-default.conf" ]; then
	a2dissite 000-default
fi

if [ ! -f "${PROJECT_DIR}/hd/settings.py" ]; then
	cp -f ${PROJECT_DIR}/hd/settings.py.default ${PROJECT_DIR}/hd/settings.py
fi

supervisorctl reload

cd ${PROJECT_DIR} && \
./manage.py migrate && \
./manage.py collectstatic --noinput

chown -Rf ${APACHE_RUN_USER}:${APACHE_RUN_GROUP} ${PROJECT_DIR}

for file in ${MYSQL_DATA_DIR}/*
do
    if test -f $file -a "${file##*.}" = "sql"
    then
    	mysql -h ${MYSQL_HOST} -P ${MYSQL_PORT} -u ${MYSQL_USER} -p${MYSQL_PASSWORD} < $file
        echo "加载数据文件"$file
    fi
done