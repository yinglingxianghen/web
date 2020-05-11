# coding=utf-8
import os
from sklearn import svm
from sklearn.externals import joblib
from hiveConn import HiveConn

import numpy as np
import math


def hiveData(var, starttime, endtime):
    hc = HiveConn()
    # sql = 'SELECT ' + vars + ' FROM hd_kblffz_mblmean where gettime >= "' + starttime + '" and gettime < "' + endtime + '"'
    sql = 'SELECT ' + var + ' FROM hd_kblffz_mblmean where dt = "2017-07-16" limit 2000'
    print sql
    datalist = []
    for fields in hc.select(sql):
        datalist.append(map(eval, fields))
    return np.array(datalist)

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

def getThreshold(shangx):
    # 均值
    mean = np.mean(shangx)
    # 无偏标准差
    std = np.std(shangx, ddof=1)
    threshold = [mean - 3 * std, mean + 3 * std]
    return threshold


def isIn(x, xt):
    if x >= xt[0] and x < xt[1]:
        return True
    return False

def filterDataMultiVar(rawData,fieldCom,multiFieldsIdx):#多变量数据过滤,rawdata原始数据，fieldcom变量组合，multiFieldsIdx变量对应在rawdata序号
    fieldDatas = []
    fieldDatas = np.array(fieldDatas)
    fieldDataThre = [] #阈值
    trainSamples = []
    outlierSamples = []
    
    for i in range(len(fieldCom)):
        fieldIdx = multiFieldsIdx[fieldCom[i]]
        fieldData = rawData[:,fieldIdx]
        if len(fieldDatas) == 0:
            fieldDatas = fieldData
        else:
             fieldDatas = np.c_[fieldDatas,fieldData]
        thre = getThreshold(fieldData)
        fieldDataThre.append(thre)
    if len(fieldDatas) == 0:
        return np.array(trainSamples),np.array(outlierSamples)
    
    for i in range(len(fieldDatas)):
        isInRange = 1
        for j in range(len(fieldDatas[i])):#判断这一行是否超过阈值
            if isIn(fieldDatas[i][j],fieldDataThre[j]) == False:
                isInRange = 0
                break
        if isInRange == 0: #说明这一行超过阈值
            outlierSamples.append(fieldDatas[i,:])
        else:
            trainSamples.append(fieldDatas[i,:])
        
    # for j in range(len(fieldDatas[0])):  # 判断该行是否超过阈值
    #     isInRange = 1
    #     outlierSample = []
    #     trainSample = []
    #     for i in range(len(fieldDatas)):#遍历每行
    #         if isIn(fieldDatas[i][j],fieldDataThre[i]) == False:
    #             isInRange = 0
    #             break
    #     # if isInRange == 0:#这一行超过阈值，保存在outliesamle中
    #     #     for i in range(len(fieldDatas)):  # 遍历每行
    #     #         outlierSample.append(fieldDatas[i][j])
    #     #     outlierSamples.append(outlierSample)
    #     # for i in range(len(fieldDatas)):  # 遍历每行
    #     #     trainSample.append(fieldDatas[i][j])
    #     # trainSamples.append(trainSample)
    #     if isInRange == 0:
    #         outlierSamples.append()
    #     else:
    #         trainSamples.append()
    return np.array(trainSamples),np.array(outlierSamples)
def filterData(x, y):#获取mean - 3 * std, mean + 3 * std区间中的值作为outlierSample，把x，y合并到一起成xy
    ll = len(x)
    xt = getThreshold(x)
    yt = getThreshold(y)
    trainSample = []
    outlierSample = []
    for i in range(ll):
        if isIn(x[i], xt) and isIn(y[i], yt):
            trainSample.append([x[i], y[i]])
        else:
            outlierSample.append([x[i], y[i]])
    xy = np.vstack([trainSample, outlierSample])
    return np.array(xy), np.array(outlierSample)
    return np.array(trainSample), np.array(outlierSample)

def getSvmMultiVar(trainSamples, outlierSamples,modelName):
    nu = float(len(outlierSamples)) /float(len(trainSamples))
    smax = []#每个维度的最大值和最小值
    smin = []
    if len(trainSamples) ==0:
        return smax,smin
    for i in range(len(trainSamples[0])):
        smax.append(np.max(trainSamples[:,i]))
        smin.append(np.min(trainSamples[:,i]))
    gamma = 0.0001
    if nu <= 0:
        nu = 0.00001
    if nu >= 1:
        nu = 0.99999
    clf = svm.OneClassSVM(nu=nu, kernel="rbf", gamma=gamma)
    clf.fit(trainSamples)
    joblib.dump(clf, modelName)  # modelName
    return smax,smin
def getSvm(trainSample, outlierSample,modelName):
    nu = float(len(outlierSample)) / float(len(trainSample))

    # xmax = np.max(trainSample[:,0])
    # xmin = np.min(trainSample[:,0])
    # ymax = np.max(trainSample[:,1])
    # ymin = np.min(trainSample[:,1])

    xmax = np.max(trainSample[:,0])
    xmin = np.min(trainSample[:,0])
    ymax = np.max(trainSample[:,1])
    ymin = np.min(trainSample[:,1])

    gamma = 0.0001
    clf = svm.OneClassSVM(nu=nu, kernel="rbf", gamma=gamma)
    clf.fit(trainSample)
    joblib.dump(clf, modelName)#
    clf = joblib.load(modelName)

    num = 20
    xx, yy = np.meshgrid(np.linspace(0, trainSample[:, 0].max(), num), \
                         np.linspace(0, trainSample[:, 1].max(), num))

    Z = clf.decision_function(np.c_[xx.ravel(), yy.ravel()])
    Z = Z.reshape(xx.shape)
    data = np.c_[xx.ravel(), yy.ravel(), Z.ravel()].tolist()
    return data, num, xmax, xmin, ymax, ymin


def sigmoid(samples):
    y = [(1 if x > 0 else round(2 / (1 + 2 * math.exp(-x)), 4)) for x in samples]
    return np.array(y)

def score(samples,modelName):#modelName = "train_model.m"
    clf = joblib.load(modelName)
    Z = clf.decision_function(samples)
    return 100*sigmoid(Z)#z大于0时，大于50

def getHealthIndex(samples):
    clf = joblib.load("train_model.m")
    clf.decision_function(samples)
    indexVal = sigmoid(samples)
    return 100*sum(indexVal)/len(indexVal)
    
if __name__ == '__main__':
    # m = 'xx'
    # f = ['1', '2']
    # s = [[m, i] for i in f]
    # print s
    initial_fields = ["shangx", "shangy"]
    var = ','.join(initial_fields)
    rawdata = hiveData(var, '', '')
    trainSample, outlierSample = filterData(rawdata[:, 0], rawdata[:, 1])
    getSvm(trainSample, outlierSample)
    print getHealthIndex([275,345])



