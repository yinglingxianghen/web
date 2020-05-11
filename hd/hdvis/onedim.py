# coding:utf-8

import csv
import numpy as np
from hiveConn import HiveConn
from datetime import datetime
from datetime import timedelta

def hiveData(var):
	hc = HiveConn()
	vars = ','.join(var)
	sql = 'SELECT ' + vars + ' FROM hd_kblffz_mblmean where dt = "2017-07-16" limit 2000'
	# sql = 'SELECT ' + vars + ' FROM kbl'
	print sql
	datalist = []
	for fields in hc.select(sql):
		datalist.append(map(eval, fields))
	return np.array(datalist)
def hiveDataNoTime(var,startTime,endTime,datanum):
    hc = HiveConn()
    vars = ','.join(var)
    datalist = []
    dataTime = ''
    sql = ''
    if endTime == '':  # 如果终点时刻没有值，直接返回空
        return datalist
    if startTime == '':  # 获取时刻值
        sql = 'SELECT ' + vars + ' FROM hd_kblffz_mblmean where gettime = ' + '"' + endTime + '"'
    else:
        sql = 'SELECT ' + vars + ' FROM hd_kblffz_mblmean where gettime between ' + '"' + startTime + '"' + ' and ' + '"' + endTime + '" limit ' + str(
            datanum)
    print sql
    datalist = []
    for fields in hc.select(sql):
		datalist.append(map(eval, fields))
    return np.array(datalist)
#选择时间,变量,机组
def hiveDataEndTime(var,endTime):
	hc = HiveConn()
	vars = ','.join(var)
	datalist = []
	dataTime = ''
	sql = ''
	if endTime == '':  # 如果终点时刻没有值，直接返回空
		return datalist
	sql = 'SELECT ' + vars + ' FROM hd_kblffz_mblmean where gettime = ' + '"' + endTime + '"'
	print sql

	for fields in hc.select(sql):
		datalist.append(map(eval, fields))
	return datalist

def hiveDataTime(var,startTime,endTime,datanum):

	hc = HiveConn()
	vars = ','.join(var)
	datalist = []
	dataTime = ''
	sql = ''
	if endTime == '':#如果终点时刻没有值，直接返回空
		return datalist
	if startTime == '':#获取时刻值
		sql = 'SELECT gettime,' + vars + ' FROM hd_kblffz_mblmean where gettime = '+ '"' + endTime + '"'
	else:
		sql = 'SELECT gettime,' + vars + ' FROM hd_kblffz_mblmean where gettime between ' + '"' + startTime + '"' + ' and ' + '"' + endTime + '" limit '+str(datanum)
	print sql

	for fields in hc.select(sql):
		datalist.append(fields)
	return np.array(datalist)
def str2Dt(str):
    dt = datetime.strptime(str, '%Y-%m-%d %H:%M:%S')
    return dt
def hiveDataTimeNew(var,startTime,endTime,datanum):#从新表获取数据
	hc = HiveConn()
	vars = ','.join(var)
	datalist = []
	dataTime = ''
	sql = ''
	if endTime == '':
		return datalist
	if startTime != '':
		startTimeDt = str2Dt(startTime)
	
	endTimeDt = str2Dt(endTime)
	endTimeYear = str(endTimeDt.year)
	endTimeMonth = str(endTimeDt.month)
	if len(endTimeMonth) == 1:
		endTimeMonth = "0" + endTimeMonth
	endTimeDay = str(endTimeDt.day)
	if len(endTimeDay) == 1:
		endTimeDay = "0" + endTimeDay
	if startTime == '':  # 获取end时刻值,startTime不为空，则获取一段时间的值
		sql = 'SELECT gettime,' + vars + ' FROM hd_middledata_all_tmp where y="' + endTimeYear + '" and m="' + endTimeMonth + '" and d="' + endTimeDay + '" limit ' + str(datanum)
	else:
		sql = 'SELECT gettime,' + vars + ' FROM hd_middledata_all_tmp where y="' + endTimeYear + '" and m="' + endTimeMonth + '" and d="' + endTimeDay + '" and gettime between ' + '"' + startTime + '"' + ' and ' + '"' + endTime + '" limit ' + str(datanum)
	print sql
	datalist = []
	#print hc.select(sql)
	for fields in hc.select(sql):
		datalist.append(fields)
	return np.array(datalist)


def hiveRawDataTimeNew(var, startTime, endTime, datanum):  # 从新表获取数据
	hc = HiveConn()
	vars = ','.join(var)
	datalist = []
	dataTime = ''
	sql = ''
	if endTime == '':
		return datalist
	if startTime != '':
		startTimeDt = str2Dt(startTime)
	
	endTimeDt = str2Dt(endTime)
	endTimeYear = str(endTimeDt.year)
	endTimeMonth = str(endTimeDt.month)
	if len(endTimeMonth) == 1:
		endTimeMonth = "0" + endTimeMonth
	endTimeDay = str(endTimeDt.day)
	if len(endTimeDay) == 1:
		endTimeDay = "0" + endTimeDay
	if startTime == '':  # 获取end时刻值,startTime不为空，则获取一段时间的值
		sql = 'SELECT gettime,' + vars + ' FROM hd_middledata_all_tmp where y="' + endTimeYear + '" and m="' + endTimeMonth + '" and d="' + endTimeDay + '" limit ' + str(
			datanum)
	else:
		sql = 'SELECT gettime,' + vars + ' FROM hd_middledata_all_tmp where y="' + endTimeYear + '" and m="' + endTimeMonth + '" and d="' + endTimeDay + '" and gettime between ' + '"' + startTime + '"' + ' and ' + '"' + endTime + '" limit ' + str(
			datanum)
	print sql
	datalist = []
	# print hc.select(sql)
	for fields in hc.select(sql):
		datalist.append(fields)
	return np.array(datalist)
def allthreholdTime(var, startTime, endTime, datanum):
	vars = hiveDataNoTime(var, startTime, endTime, datanum)#不要第一行时间数据

	thres = []
	for i in range(vars.shape[1]):
		shangx = vars[:, i]
		# 均值
		mean = np.mean(shangx)

		# 无偏标准差
		std = np.std(shangx, ddof=1)
		sigma = []
		# 实际分布比例
		for i in range(3):
			xp = mean + std * (i + 1)
			xl = mean - std * (i + 1)
			k = 0
			for j in shangx:
				if j < xp and j > xl:
					k = k + 1
			sigma.append(k / len(shangx))
		threshol = mean + 3 * std
		thres.append(threshol)
	return thres

#计算全部快变量阈值
def strToFloat(rawdata):
	floatdata = []
	for i in range(len(rawdata)):
		floatdata.append(map(eval,rawdata[i]))
	return np.array(floatdata)
def allthreholdMiddle(datamiddle):
	thres = []
	for i in range(datamiddle.shape[1]):
		shangx = datamiddle[:, i]
		# 均值
		
		mean = np.mean(shangx)
		
		# 无偏标准差
		std = np.std(shangx, ddof=1)
		sigma = []
		# 实际分布比例
		for i in range(3):
			xp = mean + std * (i + 1)
			xl = mean - std * (i + 1)
			k = 0
			for j in shangx:
				if j < xp and j > xl:
					k = k + 1
			sigma.append(k / len(shangx))
		threshol = mean + 3 * std
		thres.append(threshol)
	return thres
def allthrehold(var):
	vars = hiveData(var)

	thres = []
	for i in range(vars.shape[1]):
		shangx = vars[:, i]
		# 均值
		mean = np.mean(shangx)

		# 无偏标准差
		std = np.std(shangx, ddof=1)
		sigma = []
		# 实际分布比例
		for i in range(3):
			xp = mean + std * (i + 1)
			xl = mean - std * (i + 1)
			k = 0
			for j in shangx:
				if j < xp and j > xl:
					k = k + 1
			sigma.append(k / len(shangx))
		threshol = mean + 3 * std
		thres.append(threshol)
	return thres


def threshold(var):
	shangx = hiveData(var)

	# 均值
	mean = np.mean(shangx)

	# 无偏标准差
	std = np.std(shangx, ddof=1)

	sigma = []
	# 实际分布比例
	for i in range(3):
		xp = mean + std * (i + 1)
		xl = mean - std * (i + 1)
		k = 0
		for j in shangx:
			if j < xp and j > xl:
				k = k + 1
		sigma.append(k / len(shangx))

	data = [1, 2]

	# return (data, ("%.2f" % mean), ("%.2f" % std), sigma)
	threshold = mean + 3 * std
	return threshold
