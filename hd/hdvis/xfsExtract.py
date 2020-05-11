# coding=utf-8
"""
    20/11/2017,16:29,2017
    BY DoraZhang
"""
import models
import sys

reload(sys)
sys.setdefaultencoding('utf-8')
import numpy as np


from prestoConn import *

def hiveData(sql):
	hc = PrestoConn()
	hc.getConn()
	return hc.select(sql)

def getXFs():
	slide_window = 512 * 8
	xf_len = 2049  # slide_window / 2 + 1
	__fs = 640 | 54
	__circleNo = 512
	f_step = float(__fs) / float(slide_window)
	f_data = float(__fs) / float(__circleNo)
	xf_index = float(f_data / f_step)

	x_index = []
	for i in range(xf_len):
		x_index.append(i / xf_index)

	# 获取查询字段
	vcs = models.Allxfsvariable.objects.all()
	fieldname_meaning = {}
	for vc in vcs:
		fieldname_meaning[vc.fieldname] = vc.comments
	fields2line = fieldname_meaning.keys()[:2]
	if 'gettime' in fields2line:
		fields2line.remove('gettime')
	basicfield = ['gettime']
	fields2query = basicfield + fields2line
	sql_fields = ','.join(fields2query)

	fieldChar = []
	for f in fields2line:
		fieldChar.append(fieldname_meaning[f])

	sql = "select " + sql_fields + " from hd_middledata_all_xfs_tmp where y='2017' and m='05' and d='06' and h='00' limit 20"
	# print sql
	sqldata = hiveData(sql)
	gettime = []
	dataResults = []
	for dataFrame in sqldata:
		gettime.append(dataFrame[0])
		dataResult = []
		for df in dataFrame[1:]:
			dr = [float(d) for d in df.split('/')]
			dataResult.append(dr)
		dataResults.append(dataResult)
	da = np.array(dataResults)

	return da, x_index, gettime, fieldChar


if __name__ == '__main__':
	getXFs()
