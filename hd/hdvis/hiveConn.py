# coding=utf-8
"""
    08/08/17,12:43,2017
    BY DoraZhang
"""

import sys

reload(sys)
sys.setdefaultencoding('utf-8')

from pyhive import hive
from django.conf import settings


class HiveConn():
	def getConn(self):
		try:
			conn = hive.connect(host=settings.HIVE_CONF['HOST'], \
								port=settings.HIVE_CONF['PORT'], \
								database=settings.HIVE_CONF['DATABASE'], \
								username=settings.HIVE_CONF['USERNAME'])
			#conn = hive.connect(host="218.247.237.29",port=10000,database='default',username='hadoop')
			return conn
		except hive.Error, e:
			print "hive Error:%s" % e

	def select(self, sql):
		try:
			con = self.getConn()
			cur = con.cursor()
			cur.execute(sql)
			fc = cur.fetchall()
			return fc
		except hive.Error, e:
			print "hive Error:%s" % e
		finally:
			# cur.close()
			con.close()


if __name__ == '__main__':
	sql = 'SELECT * FROM hd_kblffz_mblmean LIMIT 10'
	hc = HiveConn()
	hc.getConn()
	datalist = []
	for i in hc.select(sql):
		datalist.append(i[0])
	print datalist
