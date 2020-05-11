# coding=utf-8
"""
    03/08/17,11:53,2017
    BY DoraZhang
"""
import sys

reload(sys)
sys.setdefaultencoding('utf-8')

import numpy as np
from minepy import MINE
from hiveConn import HiveConn
from scipy.stats import gaussian_kde
from sklearn import linear_model
from datetime import datetime
from datetime import timedelta

# import pylab as pl
# import matplotlib.pyplot as plt
import math


def getCorr(mainfield, fields, starttime, endtime):
    pass
def hiveRawDataSecond(var, starttime, endtime):#2017-7-16每秒进行采样
    hc = HiveConn()

    # sql = 'SELECT ' + vars + ' FROM hd_kblffz_mblmean where gettime >= "' + starttime + '" and gettime < "' + endtime + '"'
    sql = 'SELECT ' + var + ' FROM hd24_hadoop limit 2000'
    print sql
    datalist = []
    for fields in hc.select(sql):
        datalist.append(fields)
    return np.array(datalist)
def hiveRawData(var, starttime, endtime,datanum):#目前还不能设置时间
    hc = HiveConn()
    # sql = 'SELECT ' + vars + ' FROM hd_kblffz_mblmean where gettime >= "' + starttime + '" and gettime < "' + endtime + '"'
    sql = ''
    if starttime == '':
        sql = 'SELECT ' + var + ' FROM hd24_hadoop limit '+str(datanum)
    else:
        sql = 'SELECT ' + var + ' FROM hd24_hadoop where gettime between "'+ starttime + '" and "'+ endtime+'" limit ' + str(datanum)
    print sql
    datalist = []
    for fields in hc.select(sql):
        datalist.append(fields)
    return np.array(datalist)

def str2Dt(str):
    dt = datetime.strptime(str, '%Y-%m-%d %H:%M:%S')
    return dt
def hiveRawDataTimeNew(BivarFields, startTime, endTime, datanum):  # 从新表获取原始数据
    #去掉var中的
    bivarRawFields = []
    for bf in BivarFields:
        pos = bf.find('_')
        #bf = str(bf)
        if pos != -1:
            bf = bf[0:pos]
        bivarRawFields.append(bf)
    hc = HiveConn()
    vars = ','.join(bivarRawFields)
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
        sql = 'SELECT gettime,' + vars + ' FROM hd_rawdata_tmp where y="' + endTimeYear + '" and m="' + endTimeMonth + '" and d="' + endTimeDay + '" limit ' + str(
            datanum)
    else:
        sql = 'SELECT gettime,' + vars + ' FROM hd_rawdata_tmp where y="' + endTimeYear + '" and m="' + endTimeMonth + '" and d="' + endTimeDay + '" and gettime between ' + '"' + startTime + '"' + ' and ' + '"' + endTime + '" limit ' + str(
            datanum)
    print sql
    datalist = []
    # print hc.select(sql)
    for fields in hc.select(sql):
        datalist.append(fields)
    return np.array(datalist)


def hiveDataNum(var, starttime, endtime,datanum):
    hc = HiveConn()
    # sql = 'SELECT ' + vars + ' FROM hd_kblffz_mblmean where gettime >= "' + starttime + '" and gettime < "' + endtime + '"'
    sql = 'SELECT ' + var + ' FROM hd_kblffz_mblmean where dt = "2017-07-16" limit '+ str(datanum)
    print sql
    datalist = []
    for fields in hc.select(sql):
        datalist.append(map(eval, fields))
    return np.array(datalist)
def hiveData(var, starttime, endtime):
    hc = HiveConn()
    sql = 'SELECT ' + vars + ' FROM hd_kblffz_mblmean where gettime >= "' + starttime + '" and gettime < "' + endtime + '"'
    #sql = 'SELECT ' + var + ' FROM hd24_hadoop limit 2000'
    print sql
    datalist = []
    for fields in hc.select(sql):
    #    datalist.append(map(eval, fields))
        datalist.append(fields)
    return np.array(datalist)

def partition(lst, partition_size):
    if partition_size < 1:
        partition_size = 1
    return [
        lst[i:i + partition_size]
        for i in range(0, len(lst), partition_size)
    ]

def linearScore(x,y):# 输入两列数据x,y，返回拟合评分
    clf = linear_model.LinearRegression()
    px = partition(x, 1)  # 转置
    score = clf.score(px,y)
    return score
def linearRegression(x,y):  # 输入两列数据x,y，返回y = kx+b,coef对应k，intercept对应b,score对应分数
    #如果x=[[x1,x2]...]，y=kx1+kx2+b
    px = partition(x,1) #转置
    clf = linear_model.LinearRegression()
    clf.fit(px, y)
    score = clf.score(px,y)
    return clf.coef_[0],clf.intercept_,score
def hiveRawDataTime(var,startTime,endTime,datanum):
    hc = HiveConn()
    vars = var
    datalist = []
    timelist = []
    dataTime = ''
    sql = ''
    if startTime == '':#获取时刻值
        sql = 'SELECT gettime,' + vars + ' FROM hd24_hadoop limit ' + str(datanum)
    else:
        sql = 'SELECT gettime,' + vars + ' FROM hd24_hadoop where gettime between ' + '"' + startTime + '"' + ' and ' + '"' + endTime + '" limit '+str(datanum)
    print sql

    for fields in hc.select(sql):
        datalist.append(fields)
    return np.array(datalist)
def hiveDataTime(var,startTime,endTime,datanum):
    hc = HiveConn()
    vars = var
    datalist = []
    timelist = []
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


def hiveDataTimeNew(var, startTime, endTime, datanum):  # 从新表获取数据
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
def strToFloat(rawdata):
    floatdata = []
    for i in range(len(rawdata)):
        floatdata.append(map(eval,rawdata[i]))
    return floatdata
def isSameValue(x):
    isSame = True
    for i in x:
        if i != x[0]:
            isSame = False
            break
    return isSame
def computerZZ(x,y):#如果有重复的话,
    isRepeatX = 1
    isRepeatY = 1
    for i in range(1,len(x)):
        if x[i] != x[0]:
            isRepeatX = 0
            break
    for i in range(1,len(y)):
        if y[i] != y[0]:
            isRepeatY = 0
            break
    if isRepeatX == 1 or isRepeatY == 1:
        return 1
    else:
        return 0
def computeCorr(x, y):
    # Calculate the point density
    xy = np.vstack([x, y])
    r = 0
    if isSameValue(x)==True or isSameValue(y)==True:#有一列数据重复
        zz = x
        for i in zz:
            i = 50
        r = 0
    else:
        z = gaussian_kde(xy)(xy)  # 用来画峰峰值的颜色情况
        zz = np.floor(z * 500000)
        r = np.corrcoef(x, y)[0, 1]
    mine = MINE(alpha=0.6, c=15, est="mic_approx")
    mine.compute_score(x, y)

    # print zz
    # pl.hist(zz)
    # pl.show()
    # ll = len(x)
    # xyz = []
    # for i in range(ll):
    #     xyz.append({'x': x[i], 'y': y[i], 'color': setColor(zz[i])})
    # 
    # return xyz, mine.mic(), r


    # print_stats(mine) 最大 pearson
    return x.tolist(), y.tolist(), zz.tolist(), round(mine.mic(), 5), round(r,5)
def computeCorrScale(x, y,scaleRatio):
    for i in range(len(y)):
        y[i] = y[i]*scaleRatio;
    # Calculate the point density
    xy = np.vstack([x, y])
    if isSameValue(x)==True or isSameValue(y):#有一列数据重复
        zz = x
        for i in zz:
            i = 50
        r = 0
    else:
        z = gaussian_kde(xy)(xy)  # 用来画峰峰值的颜色情况
        zz = np.floor(z * 500000)
        r = np.corrcoef(x, y)[0, 1]
    
    # z = gaussian_kde(xy)(xy)
    # zz = np.floor(z * 500000)
    # r = np.corrcoef(x, y)[0, 1]
    
    mine = MINE(alpha=0.6, c=15, est="mic_approx")
    mine.compute_score(x, y)
    

    # print zz
    # pl.hist(zz)
    # pl.show()
    # ll = len(x)
    # xyz = []
    # for i in range(ll):
    #     xyz.append({'x': x[i], 'y': y[i], 'color': setColor(zz[i])})
    #
    # return xyz, mine.mic(), r


    # print_stats(mine) 最大 pearson
    return x.tolist(), y.tolist(), zz.tolist(), round(mine.mic(), 3), r


def setColor(z):
    colorstep = ['#3060cf', '#fffbbc', '#c4463a', '#c4463a', '#018796']
    color = colorstep[int(math.floor(z / 2))]
    return color


# fig, ax = plt.subplots()
# ax.scatter(x, y, c=z, s=100, edgecolor='')
# plt.show()

# xyl = x.shape[0]
# xmax = int(math.floor(np.max(x)))
# xmin = int(math.ceil(np.min(x)))
# 
# ymax = int(math.floor(np.max(y)))
# ymin = int(math.ceil(np.min(y)))
# xl = xmax-xmin
# yl = ymax-ymin
# xstep = xyl/xl if xyl > xl else xl/xyl
# ystep = xyl/yl if xyl > yl else yl/xyl


def print_stats(mine):
    print "MIC", mine.mic()
    print "MAS", mine.mas()
    print "MEV", mine.mev()
    print "MCN (eps=0)", mine.mcn(0)
    print "MCN (eps=1-MIC)", mine.mcn_general()
    print "GMIC", mine.gmic()
    print "TIC", mine.tic()


if __name__ == '__main__':
    # m = 'xx'
    # f = ['1', '2']
    # s = [[m, i] for i in f]
    # print s
    initial_fields = ["shangx", "shangy"]
    var = ','.join(initial_fields)
    rawdata = hiveData(var, '', '')
    x, y, z, mic, r = computeCorr(rawdata[:, 0], rawdata[:, 1])
