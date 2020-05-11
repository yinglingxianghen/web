# coding=utf-8
import os
from sklearn import linear_model
import numpy as np
import csv
import time
from datetime import datetime
from datetime import timedelta
from hiveConn import HiveConn
import copy
# import matplotlib
# import matplotlib.pyplot as plt
# from sklearn.externals import joblib
# from scipy import stats
# import math
# 
# import matplotlib.dates as mdates
# import matplotlib.ticker as mtick
# import pandas as pd
# # hive connection
# from hiveConn import HiveConn
# # hbase connection
# from hbase import Hbase
# from hbase import ttypes
# from thrift.transport import TSocket
# from thrift.transport import TTransport
# from thrift.protocol import TBinaryProtocol

def getFeature(x) :
    positive = True
    # 以后可以替换成我们的个性化阈值
    threshold = 300
    vpp = x.max() - x.min()
    if (vpp > threshold):
        positive = False
    return positive,vpp

# def hiveData(var):
#     hc = HiveConn()
#     # vars = ','.join(var)
#     vars = 'gettime,shangx'
#     sql = 'SELECT ' + vars + ' FROM hd_kblffz_mblmean limit 2'
#     # sql = 'SELECT ' + vars + ' FROM kbl'
#     print sql
#     datalist = []
#     for fields in hc.select(sql):
#         datalist.append(map(eval, fields))
#     return np.array(datalist)    

# def hbaseData():
#     transport = TSocket.TSocket('hd',9090)
#     transport = TTransport.TBufferedTransport(transport)
#     protocol = TBinaryProtocol.TBinaryProtocol(transport)
#     client = Hbase.Client(protocol)
#     transport.open()
#     print client.getTableNames()
#     return 


def readfile(file_name) :
    csvfile = open(file_name)
    csv_reader = csv.reader(csvfile)
    x = []
    for row in csv_reader:
        x.append(float(row[0]))
    csvfile.close()
    return x

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
def strToFloat(rawdata):
	floatdata = []
	for i in range(len(rawdata)):
		floatdata.append(map(eval,rawdata[i]))
	return floatdata
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
def dt2Str(timedata):
    return timedata.strftime('%Y-%m-%d %H:%M:%S')
def str2Dt(timedata):
    times = []
    for t in timedata:
        dt = datetime.strptime(t, '%Y-%m-%d %H:%M:%S.%f')
        #dt = dt2millisectimestamp(dt)
        times.append(dt)
    return times
def dt2millisectime(timedata):
    times = []
    for t in timedata:
        #dt = datetime.strptime(t, '%Y-%m-%d %H:%M:%S')
        dt = dt2millisectimestamp(t)
        times.append(dt)
    return times
def getSamples(var):
    num_one_circle = 256
    # path = '../decomp_417'
    path = os.getcwd()
    
    path = os.path.join(path,"data/decomp_417") #数据文件夹
    time_file = open(os.path.join(path,'times.txt'),'r')
    timef_file = open(os.path.join(path,'times1.txt'),'r')

    X_train = []
    # X_outliers = []
    X_time = []

    j = 0
    while True:
    	# j = j+1
    	# if j>5:
    	# 	break
        time_str = time_file.readline().strip()
        timef_str = timef_file.readline().strip()
        if not time_str:
            break
        x = readfile(os.path.join(path, var + time_str + ".csv"))
       #这个x读取的csv数据是什么意思
        n_samples = len(x) // num_one_circle
        x = np.array(x)

        # 给每个峰峰值的数据间隔设为0.8s
        dt = datetime.strptime(timef_str,'%Y-%m-%d %H:%M:%S')
        for i in range(n_samples):
            positive,sample = getFeature(x[i*num_one_circle : (i+1)*num_one_circle-1])    
            if positive:
                X_train.append(sample)
                # X_time.append(dt.strftime('%Y-%m-%d %H:%M:%S'))
                X_time.append(dt)
            # else:
            #     X_outliers.append(sample)
            dt = dt + timedelta(seconds = 0.8)    

    time_file.close()
    timef_file.close()

    X_train = np.array(X_train)
    X_time = np.array(X_time)
    # X_outliers = np.array(X_outliers)
    X_millisecond = np.array([dt2millisectimestamp(t_smaple) for t_smaple in X_time])
    #什么意思
    data = np.c_[X_millisecond.ravel(),X_train.ravel()].tolist()
    return data,X_millisecond,X_train


    # return X_millisecond,X_train

def dt2sectimestamp(dttime):
    t = dttime.timetuple()
    timestamp = time.mktime(t)
    timestamp = timestamp + float(dttime.microsecond)/1000000
    return timestamp

# highchart支持到milliseconds
def dt2millisectimestamp(dttime):
    t = dttime.timetuple()
    timestamp = time.mktime(t)
    timestamp = timestamp*1000 + dttime.microsecond/1000
    return timestamp
def judgeSlope(datetimedata,univarExceThrehold,rawdata,monitXSlope,monitXIntercept,thre_slope):#判断这一列数据的斜率值是否超标
    R_slope = []
    isExce = 0 #1为这一列可能越界，0为没有越界
    for i in range(len(monitXSlope)):
        datetimestr = dt2Str(datetimedata[i])
        if monitXSlope[i] > thre_slope:#斜率越界
            R_slope.append([datetimestr,univarExceThrehold[i]+3,thre_slope,monitXSlope[i]])
            #print(str(i)+"\n")
            isExce = 1
        else:
            if univarExceThrehold[i] > 0:#1为阈值越界
                R_slope.append([datetimestr,univarExceThrehold[i],thre_slope,monitXSlope[i]])
                isExce = 1
            else:
                R_slope.append([datetimestr,0,thre_slope,monitXSlope[i]]) #2为变量和斜率都没有超阈值
    millisectimedata = dt2millisectime(datetimedata)
    millisectimedata = np.array(millisectimedata)
    # data做滑动平均
    data = np.c_[millisectimedata.ravel(), rawdata.ravel()].tolist()
    slideData = copy.deepcopy(data)
    datalen = len(data)
    step = 10
    for i in range(datalen):
        sum = 0
        num = 0
        for j in range(i-step,i+step):
            if j < 0:
                continue
            if j >= datalen:
                continue
            sum += data[j][1]
            num = num + 1
        slideData[i][1] = sum/num
    # slope做滑动平均
    slope = np.c_[millisectimedata.ravel(), monitXSlope.ravel() * 1].tolist()
    slideSlope = copy.deepcopy(slope)
    slopelen = len(slope)
    for i in range(slopelen):
        sum = 0
        num = 0
        for j in range(i-step,i+step):
            if j < 0:
                continue
            if j >= slopelen:
                continue
            sum += slope[j][1]
            num = num + 1
        slideSlope[i][1] = sum/num
    intercept = np.c_[millisectimedata.ravel(), monitXIntercept.ravel() * 1].tolist()
    return R_slope, isExce, slideData, slideSlope, intercept #返回滑动窗口
    #return R_slope,isExce,data,slope,intercept
def timeSlope(datetimedata,univarExceThrehold,rawdata,timeInterval,thre_slope,jzname,zname,field,monitSegmentDatas,alert_slope,factor):#第i列是否超过阈值，并且对rawdata数据进行斜率判断
    #保存斜率异常或者的一段时间数据
    regr = linear_model.LinearRegression()
    X_slope = univarExceThrehold.copy()#返回rawdata这一列的斜率
    X_intercept = univarExceThrehold.copy()
    timedataLen = len(datetimedata)-1
    monitSlopeCount = 0

    max_slope = 0
    for i in range(timedataLen,-1,-1):
        #每个datetimedata[i],往前找时间间隔timeInterval的数据作为斜率
        timestart = datetimedata[i]
        timeend = datetimedata[i] - timedelta(minutes=int(timeInterval))
        for j in range(i,-1,-1):
            if(datetimedata[j] < timeend):
                break
        if j == i -1:#前面一分钟都没有数据
            X_slope[i] = 0
            continue
        if j == 0:#往前编列到头
            for t in range(i,-1,-1):
                k = min(i+1,len(datetimedata))
                #X_slope[t] = X_slope[k]#注意这儿i可能越界
                X_slope[t] = 0
            break
        T_samples = datetimedata[j+1:i+1]
        T_samplesCopy = copy.deepcopy(T_samples)
        T_samples = dt2millisectime(T_samples)
        T_samples = np.array(T_samples)
        T_samples = T_samples[:, np.newaxis]
        X_samples = rawdata[j+1:i+1]
        regr.fit(T_samples, X_samples)
        k = float(regr.coef_[0])
        b = regr.intercept_
        t1 = dt2millisectimestamp(timeend)
        p1 = (k*t1 + b)
        t2 = dt2millisectimestamp(timestart)
        p2 = float(rawdata[i])
        fitLine = []  # 拟合直线
        fitLine.append([t1,p1])
        fitLine.append([t2,p2])

        X_slope[i] = (abs(regr.coef_))*factor
        X_intercept[i] = regr.intercept_  # rawdata现在是单列，所以返回是一个数，原来rawdata是一个数组，返回是一个数组
        segmentData = []
        if (univarExceThrehold[i] > 0 or X_slope[i] > thre_slope) and X_slope[i] > max_slope:  # 如果变量阈值超标，斜率超标,保存数据，斜率
            max_slope = X_slope[i]
            monitSlopeCount = monitSlopeCount + 1
            millisectimedata = dt2millisectime(T_samplesCopy)
            millisectimedata = np.array(millisectimedata)
            dataTime = np.c_[millisectimedata.ravel(), X_samples.ravel()].tolist()
            curDatetime =  dt2Str(datetimedata[i])#当前时刻
            segmentData = [jzname,zname,field,curDatetime,X_slope[i],X_intercept[i],dataTime,thre_slope,alert_slope,fitLine,i]#斜率乘以1000
            jzfieldtime = jzname+field
            monitSegmentDatas[jzfieldtime] = segmentData
    return X_slope,X_intercept
def timeIntervalSlope(datetimedata,rawdatas,timeInterval,factor):#timeInterval间隔采样,datetimedata时间数据，rawdata峰峰值数据
    datetimedata = np.array(datetimedata)  # datatime 结构
    rawdatas = np.array(rawdatas)  # datatime 结构
    regr = linear_model.LinearRegression()
    X_slope = []
    X_intercept = []
    X_millisectime = []
    j = 0#记录已有数据的时间点终点
    for i in range(len(datetimedata)):
        if i < j:
            continue
        timestart = datetimedata[i]
        timeend = datetimedata[i] + timedelta(minutes=int(timeInterval))
        for j in range(i,len(datetimedata)):
            if(datetimedata[j] > timeend):#超出时间点，将这段时间的数据保存下来
                break
        #datetimedata[i,j]之间是该区间的数据
        if i == j:
            break
        if (datetimedata[j] < timeend):  # j访问到最后一个数据，但是时间没有超过设定值，舍去最后一个时间值
            break
        T_samples = datetimedata[i:j]
        T_samples =  dt2millisectime(T_samples)
        T_samples = np.array(T_samples)
        T_samples = T_samples[:, np.newaxis]
        X_samples = rawdatas[i:j]
        regr.fit(T_samples, X_samples)
        X_slope.append(abs(regr.coef_)*factor)
        X_intercept.append(regr.intercept_)#rawdata现在是单列，所以返回是一个数，原来rawdata是一个数组，返回是一个数组
        X_millisectime.append(T_samples[len(T_samples)-1])
        i = j
    X_slope = np.array(X_slope)
    X_millisectime = np.array(X_millisectime)
    X_intercept = np.array(X_intercept)
    millisectimedata= dt2millisectime(datetimedata)
    millisectimedata = np.array(millisectimedata)
    data = np.c_[millisectimedata.ravel(), rawdatas.ravel()].tolist()
    slope = np.c_[X_millisectime.ravel(), X_slope.ravel() * 1].tolist()
    return data,X_slope,slope
def pdtSlope(timedata,rawdata,timeInterval):
    #输入时间，数据，返回每个时间点的斜率,t代表时间，x代表数据
    regr = linear_model.LinearRegression()
    space = 40
    n_iter = len(rawdata) / space
    slopedata = []
    X_slope = []
    X_intercept = []
    timedata = np.array(timedata) #datatime 结构
    for i in range(len(rawdata)):#每个点跟前space点进行线段拟合表示劣化速度
        timeTmp = rawdata[i][0]
        dt = datetime.strptime(timeTmp,'%Y-%m-%d %H:%M:%S.%f')
        if i < space:#前space个不考虑
            X_slope.append(np.array(0))
            X_intercept.append(np.array(0))
            continue
        else:
            x_samples = rawdata[i-space:i+1]
            t_samples = timedata[i-space:i+1]
            t_samples = t_samples[:,np.newaxis]
            regr.fit(t_samples,x_samples)
            X_slope.append(abs(regr.coef_))
            X_intercept.append(regr.intercept_)
    for i in range(space):
        X_slope[i] = X_slope[space]
        X_intercept[i] = X_intercept[space]

    #X_slope = np.array(np.abs(X_slope))
   # X_slope_time = timedata
    X_slope = np.array(X_slope)
    X_intercept = np.array(X_intercept)
    X_slope_time = timedata[:, np.newaxis]
    T_slope = np.c_[X_slope_time.ravel(), X_slope.ravel() * 1000].tolist()
    timerawdata = np.c_[timedata.ravel(), rawdata.ravel()].tolist()
    return T_slope,X_slope,timerawdata
def slope(t,x):
    regr = linear_model.LinearRegression()
	# 每分钟8个数据，那么1hour就有8*60个数据
    # space = 480
    # 每分钟8个数据，5分钟就有8*5个数据
    space = 40
    n_iter = len(x) / space
    X_slope = []
    X_intercept = []

    # 趋势预测
    trend_t = []
    for i in range(n_iter+1):
        if i == n_iter:
            x_samples = x[i * space :]
            t_samples = t[i * space :]
            trend_t.append(t[i * space])
            trend_t.append(t[-1])
            trend_t.append(t[-1] + 1*60*60*1000)
        else:
            x_samples = x[i * space : (i + 1) * space - 1]
            t_samples = t[i * space : (i + 1) * space - 1]
        t_samples = t_samples[:,np.newaxis]
        regr.fit(t_samples,x_samples)
        X_slope.append(regr.coef_)
        X_intercept.append(regr.intercept_)
    #选一段时间，
	X_slope_time = t[0:-1:space]
    X_slope_time = X_slope_time[:,np.newaxis]
    X_slope = np.array(np.abs(X_slope))
    slope = np.c_[X_slope_time.ravel(),X_slope.ravel()*1000].tolist()

    # 计算趋势y
    a = X_slope[-1]
    b = X_intercept[-1]
    trend_y = [a * t + b for t in trend_t]
    trend_t = np.array(trend_t)
    trend_y = np.array(trend_y)
    trend = np.c_[trend_t.ravel(),trend_y.ravel()].tolist()
    return slope,trend,X_slope
def meanstd(X_slope):
    # 均值
    mean = np.mean(X_slope)
    
    std = np.std(X_slope, ddof=1)
    max_val = np.max(X_slope)
    min_val = np.min(X_slope)
    mid_val = mean + 2 * std
    
    # mid_val = np.median(X_slope)
    
    #min_val = mean
    
    #max_val = mean + 3 * std
    alert_val = mean + 3 * std

    return round(min_val,5),round(mid_val,5),round(max_val,5),round(alert_val,5),round(mean,5),round(std,5)




