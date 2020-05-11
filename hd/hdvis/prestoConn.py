# coding=utf-8
"""
    08/08/17,12:43,2017
    BY DoraZhang
"""

import sys

reload(sys)
sys.setdefaultencoding('utf-8')

from pyhive import presto
from django.conf import settings


class PrestoConn():
	def getConn(self):
		try:
			conn = presto.connect(host=settings.PRESTO_CONF['HOST'], \
								  port=settings.PRESTO_CONF['PORT'], \
								  username=settings.PRESTO_CONF['USERNAME'])
			return conn
		except presto.Error, e:
			print "presto Error:%s" % e

	def select(self, sql):
		try:
			con = self.getConn()
			cur = con.cursor()
			cur.execute(sql)
			fc = cur.fetchall()
			return fc
		except presto.Error, e:
			print "presto Error:%s" % e
		finally:
			# cur.close()
			con.close()


if __name__ == '__main__':
	import datetime

	begin = datetime.datetime.now()
	sql = "select gettime,shangx_xfs,shangy_xfs,xiax_xfs,xiay_xfs,shuix_xfs,shuiy_xfs,shangjjx_xfs,shangjjy_xfs,shangjjz_xfs,dingjjx_xfs,dingjjy_xfs,xiajjx_xfs,xiajjy_xfs,xiajjz_xfs,dinggx_xfs,dinggy_xfs,dinggz_xfs,dingzh1_xfs,dingzh2_xfs,dingzh3_xfs,dingzv1_xfs,dingzv2_xfs,dingzv3_xfs,ylmddg_xfs,ylmdwy_xfs,ylmdwk_xfs,ylmdshang_xfs,ylmdxia_xfs from hd_middledata_all_xfs_tmp where y='2017' and m='05' and d='06' and h='00' limit 100"
	# sql = 'select gettime,shangx_xfs,shangy_xfs,xiax_xfs,xiay_xfs,shuix_xfs,shuiy_xfs,shangjjx_xfs,shangjjy_xfs,shangjjz_xfs,dingjjx_xfs,dingjjy_xfs,xiajjx_xfs,xiajjy_xfs,xiajjz_xfs,dinggx_xfs,dinggy_xfs,dinggz_xfs,dingzh1_xfs,dingzh2_xfs,dingzh3_xfs,dingzv1_xfs,dingzv2_xfs,dingzv3_xfs,ylmddg_xfs,ylmdwy_xfs,ylmdwk_xfs,ylmdshang_xfs,ylmdxia_xfs from hd_middledata_all_xfs_tmp limit 10'

	hc = PrestoConn()
	hc.getConn()
	datalist = []
	for i in hc.select(sql):
		datalist.append(i)

	end = datetime.datetime.now()
	print end - begin
