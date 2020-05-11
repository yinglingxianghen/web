# coding=utf-8

"""
    20/07/2017,23:33,2017
    BY DoraZhang
"""

from __future__ import unicode_literals

from django.shortcuts import render
from django.shortcuts import redirect
from django.http import HttpResponse
from django.http import JsonResponse
from json import loads, dumps
from datetime import datetime

import models
import onedim as od
import onesvm as osvm
import monitor as mo
import bicorr as co
import hbaseConn as hc
import report as rpt

import itertools as it
import predict as pdt
import numpy as np
from docx import Document
from docx.shared import Inches
import os
import time
import random
import json
# import the logging library
import logging
from scipy.stats import kstest

from xfsExtract import *

import healthIndex as hi
import isolationForest as isof
import copy

from hiveConn import HiveConn

import healthIndex as hi
# Get an instance of a logger
logger = logging.getLogger("hdvis.views")
timeStamp = 0


# Bootstrap 测试
def frame(request):
    return render(request, 'signin.html')


def realtime(request):
    global timeStamp
    # highchart使用ms_timestamp,python使用s_timestamp
    # api参数,tablename,timeStamp,columns
    columns = 'bd:shangx'
    gk = 'mbl:zs'
    tablename = 'hd24'
    conn = hc.HbaseConnection()
    if request.is_ajax():
        interval = 800.0 / 512  # 采样间隔，单位ms,0.8s
        interval = 60 * 1000  # 1hour

        timeStamp = timeStamp + interval
        x, y = conn.get_next_data(tablename, columns, timeStamp)
        gkx, gky = conn.get_next_data(tablename, gk, timeStamp)
        return JsonResponse({'x': x, 'y': y, 'gkx': gkx, 'gky': gky})
    else:
        data = conn.get_init_data(tablename, columns, 20)
        gk = conn.get_init_data(tablename, gk, 20)
        timeStamp = data[-1][0]
        return render(request, 'realtime.html', {'data': data, 'gk': gk})


# signin
def signin(request):
    if request.method == 'POST':
        input_name = request.POST['username']
        input_pwd = request.POST['password']
        x = models.User.objects.filter(uname=input_name, password=input_pwd)
        if len(x) == 1:
            return redirect('../univar/')
        else:
            return render(request, "signin.html", {"msg": "用户名密码错误"})
    return render(request, 'signin.html')


# signin ajax
def login(request):
    if request.method == 'POST':
        input_name = request.POST['username']
        input_pwd = request.POST['password']
        x = models.User.objects.filter(uname=input_name, password=input_pwd)
        if len(x) == 1:
            return HttpResponse(dumps({'data': 1}), content_type='application/json')
        else:
            return HttpResponse(dumps({'data': 0}), content_type='application/json')
    return HttpResponse(dumps({'data': -1}), content_type='application/json')

num_progress = 0
res = ''
logInfo = ''#记录建模模块的输出信息

def processdata(request):
    global num_progress, logInfo
    if num_progress == 1:
        return JsonResponse({'status': 1, 'logInfo': logInfo})
    # for i in range(num_progress, 12334):
    #     num_progress = i  # 更新后台进度值，因为想返回百分数所以乘100
    #     res += str(num_progress) + '\n'
 
    return JsonResponse({'status': 0, 'logInfo': logInfo})


def realtimemonitor(request):
    return
# 单一维度阈值对比 及 不同阈值间不同机组对比
def univar(request):
    logger.info("request univar view")
    if request.is_ajax() and request.method == 'POST':  # 是否为post请求
        # for key in request.POST.keys():
        #    print key
        # print type(request.POST.get('jz'))

        jznames = eval(request.POST.get('jz'))
        fields = eval(request.POST.get('field'))
        params = eval(request.POST.get('param'))
        param = {}
        for x in params:
            param[x['name']] = x['value']
        # print fields

        # 连接HBase筛选
        # to do
        fuhe_start = param['fuhe_start']
        fuhe_end = param['fuhe_end']
        shuitou_start = param['shuitou_start']
        shuitou_end = param['shuitou_end']
        startTime = param['startTime']
        endTime = param['endTime']

        #机组,机组有功功率，转速1，转速2，转速3 影响个性化阈值的因变量
        activepower = 0
        rotatespeed1 = 0
        rotatespeed2 = 0
        rotatespeed3 = 0
        categories = []
        thre_ground = []
        #jznames = ["23","24"]
        startTime = "2017-07-16 12:00:00"
        endTime = "2017-07-16 13:00:00"
        while '' in fields:
            fields.remove('')
        for field in fields:
            if field != '':
                categories.append(models.Variable.objects.filter(aliasname=field)[0].zname)
                thre_ground.append(models.Threshold.objects.filter(aliasname=field)[0].HECH)
        datanum = 2000
        #thre = od.allthrehold(fields)#生成个性化阈值
        thre = od.allthreholdTime(fields,startTime,endTime,datanum)#
        # 机组,机组有功功率，转速1，转速2，转速3 影响个性化阈值的因变量
        jzFactor = {}
        jzCompare = {}
        for jzname in jznames:
            jzf = jzname+"-"+str(activepower)+"-"+str(rotatespeed1)+"-"+str(rotatespeed2)+"-"+str(rotatespeed3)
            jzCompare[jzname] = thre
            jzFactor[jzf] = thre
        #将个性化阈值插入到models中
        #models.PersonalizedThreshold.objects.all().delete()
        for jzname in jznames:
            for i in range(len(fields)):
                aliasname = fields[i]
                zname = categories[i]
                threshold = jzCompare[jzname][i]
                md = models.PersonalizedThreshold.objects.filter(jzname=jzname, zname=zname, aliasname=aliasname,activepower = activepower,
                    rotatespeed1=rotatespeed1,rotatespeed2=rotatespeed2,rotatespeed3=rotatespeed3)
                if md.count()!=0:
                    models.PersonalizedThreshold.objects.filter(jzname=jzname, zname=zname, aliasname=aliasname,activepower = activepower,
                    rotatespeed1=rotatespeed1,rotatespeed2=rotatespeed2,rotatespeed3=rotatespeed3).update(threshold=threshold)
                else:
                    models.PersonalizedThreshold.objects.create(jzname=jzname, zname=zname, aliasname=aliasname,activepower = activepower,
                    rotatespeed1=rotatespeed1,rotatespeed2=rotatespeed2,rotatespeed3=rotatespeed3,threshold=threshold)

        #jzCompare = {}
        #for jz in jzCompare:
            #models.PersonalizedThreshold.objects.create(jzname=,zname =,aliasname=,threshold=)
        return HttpResponse(
            dumps({"jzcompare": jzCompare, "categories": categories, "threshold_ground": thre_ground}))

    else:
        # 获取变量树
        treeData, jzData = formInitNew()
        # td应该是变量树，描述不同维度，jzData是所有机组编号
        initial_fields = ["shangx", "shangy", "xiax", "xiay", "shuix", "shuiy"]#变量种类，英文表示
        # initial_fields = ["shangx"]

        categories = []#变量种类,中文表示
        thre_ground = []#标准阈值，对于每个变量早定好了
        startTime = "2017-07-16 12:00:00"
        endTime = "2017-07-16 13:00:00"
        datanum = 2000
        for field in initial_fields:
            if field != '':
                categories.append(models.Middlevariable.objects.filter(fieldname=field+'_ffz')[0].comments)
                thre_ground.append(models.Threshold.objects.filter(aliasname=field)[0].hech)

        #thre = od.allthrehold(initial_fields)#均值加3个标准差作为阈值，得到这六个变量的阈值，四个机组的阈值都是一样的
        thre = od.allthreholdTime(initial_fields,startTime, endTime, datanum)
        #插入个性化阈值
        # 标准阈值
        # thre_ground = [1216.0] * len(initial_fields)
        jzNo = ['23', '24', '25', '26']
        jzcompare = {}
        for j in jzNo:
            jzcompare[j] = thre
        # data = od.readfile('data/decomp_417/shangx2016-12-03 235838.csv')

        return render(request, "univar.html",
                      {'td': dumps(treeData), 'jznames': dumps(jzData), "jzno": jzNo, "jzcompare": dumps(jzcompare),
                       "categories": dumps(categories), "threshold_ground": dumps(thre_ground)})

    # 生成报告

# 相关性分析 1 v n
def bivar(request):
    if request.is_ajax() and request.method == 'POST':  # 是否为post请求

        jznames = eval(request.POST.get('jz'))
        bivarFields = eval(request.POST.get('field'))
        params = eval(request.POST.get('param'))
        param = {}
        for x in params:
            param[x['name']] = x['value']
        # to do
        fuhe_start = param['fuhe_start']
        fuhe_end = param['fuhe_end']
        shuitou_start = param['shuitou_start']
        shuitou_end = param['shuitou_end']
        startTime = param['startTime']
        endTime = param['endTime']
        thre_bivar = param['thre_bivar']
        while '' in bivarFields:
            bivarFields.remove('')
        mainfield = param['mainfieldcontent']
        jznames = ["23"]
        startTime = "2017-07-16 12:00:00"
        endTime = "2017-07-16 13:00:00"

        if thre_bivar == '':
            thre_bivar = 0.8
        bivarFields = case_insensitive_sort(bivarFields)#进行排序
        jznames = ["23"]
        #models.bivarVariable.objects.all().delete()
        datanum = 2000
        if mainfield == '':
            # 全变量交叉测试 测试对比
            mainCom = [x for x in it.combinations(bivarFields, 2)]
            var = ','.join(bivarFields)
            bivarRawData = co.hiveRawData(var,'','',datanum)
            bivarData = co.hiveDataNum(var, '', '',datanum)#峰峰
            fieldsDict = dict(zip(bivarFields, range(len(bivarFields))))

            bivarRawDataPairs = {}
            bivarRawFieldPairs = {}
            bivarDataPairs = {}
            bivarFieldPairs = {}
            fields_no = len(mainCom)
            #这里默认为23

            for jzname in jznames:
                rotatespeed = 0
                load = 0
                activepower = 0
                for i in range(fields_no):
                    fieldpair = ''.join(mainCom[i])
                    fieldpair = jzname + fieldpair
                    rawx, rawy, rawz, rawmic, rawr = co.computeCorr(bivarRawData[:, fieldsDict[mainCom[i][0]]],
                                                                    bivarRawData[:, fieldsDict[mainCom[i][1]]])
                    x, y, z, mic, r = co.computeCorr(bivarData[:, fieldsDict[mainCom[i][0]]],
                                                                    bivarData[:, fieldsDict[mainCom[i][1]]])
                    coef, intercept, score = co.linearRegression(rawx, rawy)  # 获取两列数据拟合值
                    k = coef
                    b = intercept
                    coef1 = 1/coef
                    intercept1 = -1*intercept/coef
                    dists = []
                    for j in range(len(x)):
                        dist = abs(k*rawx[j]-rawy[j]+b)/((k*k+1)**0.5)
                        dists.append(dist)
                    mean = np.mean(dists)#均值
                    std = np.std(dists, ddof=1)# 无偏标准差
                    stat = kstest(dists,'norm')
                    distthre  = mean + std
                    #保存相关性过程的系数，jz,rotatespeed,load,activepower,mainfield,mainCom[i-1],,mic,r
                    md = models.bivarVariable.objects.filter(jzname=jzname,rotatespeed = rotatespeed,load = load,
                                                             activepower = activepower,aliasname1 = mainCom[i][0],
                                                             aliasname2 = mainCom[i][1],mic = rawmic, bivarr = rawr,coef = coef,intercept = intercept,distthre = distthre)
                    if md.count()!=0:
                        models.bivarVariable.objects.filter(jzname=jzname,rotatespeed = rotatespeed,load = load,
                                                             activepower = activepower,aliasname1 = mainCom[i][0],
                                                             aliasname2 = mainCom[i][1]).update(mic = rawmic, bivarr = rawr,coef = coef,intercept = intercept,score = score,distthre = distthre)
                        models.bivarVariable.objects.filter(jzname=jzname, rotatespeed=rotatespeed, load=load,
                                                            activepower=activepower, aliasname2 = mainCom[i][0],
                                                            aliasname1=mainCom[i][1]).update(mic=rawmic, bivarr=rawr, coef=coef1,
                                                                                              intercept=intercept1,score = score,distthre = distthre)#变量顺序反过来也可以，不过直线方程要变一下
                    else:
                        models.bivarVariable.objects.create(jzname=jzname, rotatespeed=rotatespeed, load=load,
                                                            activepower=activepower, aliasname1=mainCom[i][0],
                                                            aliasname2=mainCom[i][1], mic=rawmic, bivarr=rawr,coef = coef,intercept = intercept,score = score,distthre = distthre)
                        models.bivarVariable.objects.create(jzname=jzname, rotatespeed=rotatespeed, load=load,
                                                        activepower=activepower, aliasname2=mainCom[i][0],
                                                        aliasname1=mainCom[i][1], mic=rawmic, bivarr=rawr, coef=coef1,
                                                        intercept=intercept1,score = score,distthre = distthre)#变量顺序反过来也可以，不过直线方程要变一下
                    if abs(rawr) < thre_bivar:
                        continue

                    bivarRawDataPairs[fieldpair] = [rawx, rawy, rawz]
                    bivarDataPairs[fieldpair] = [x,y,z]
                    rawnamepair = [models.Variable.objects.filter(aliasname=mainCom[i][0])[0].zname,
                                models.Variable.objects.filter(aliasname=mainCom[i][1])[0].zname, rawmic, rawr]
                    namepair = [models.Variable.objects.filter(aliasname=mainCom[i][0])[0].zname,
                                   models.Variable.objects.filter(aliasname=mainCom[i][1])[0].zname, mic, r,jzname]
                    bivarRawFieldPairs[fieldpair] = rawnamepair
                    bivarFieldPairs[fieldpair] = namepair
            return HttpResponse(dumps({'bivarRawFieldPairs': bivarRawFieldPairs, 'bivarRawDataPairs': bivarRawDataPairs,
                                       'bivarDataPairs': bivarDataPairs, 'bivarFieldPairs': bivarFieldPairs}))
        else:
            # 主变量交叉 线上版本
            # if mainfield == '':
            #     mainfield = "shangx"
            # mainfield = "shangx"
            # fields = ["shangy"]
            if mainfield in bivarFields:
                bivarFields.remove(mainfield)

            mainCom = [[mainfield, f] for f in bivarFields]
            bivarFields.insert(0,mainfield)
            var = ','.join(bivarFields)
            #var = ','.join([mainfield, ','.join(bivarFields)])#将mainField加入
            bivarRawData = co.hiveRawData(var, '', '', 2000)
            bivarData = co.hiveDataNum(var, '', '',datanum)
            fieldsDict = dict(zip(bivarFields, range(len(bivarFields))))

            bivarRawDataPairs = {}
            bivarRawFieldPairs = {}
            bivarDataPairs = {}
            bivarFieldPairs = {}
            fields_no = len(mainCom)
            # 这里默认为23

            for jzname in jznames:
                rotatespeed = 0
                load = 0
                activepower = 0
                for i in range(fields_no):
                    fieldpair = ''.join(mainCom[i])
                    fieldpair = jzname + fieldpair
                    rawx, rawy, rawz, rawmic, rawr = co.computeCorr(bivarRawData[:, fieldsDict[mainCom[i][0]]],
                                                                    bivarRawData[:, fieldsDict[mainCom[i][1]]])
                    x, y, z, mic, r = co.computeCorr(bivarData[:, fieldsDict[mainCom[i][0]]],
                                                     bivarData[:, fieldsDict[mainCom[i][1]]])
                    coef, intercept, score = co.linearRegression(rawx, rawy)  # 获取两列数据拟合值
                    k = coef
                    b = intercept
                    coef1 = 1 / coef
                    intercept1 = -1 * intercept / coef
                    dists = []
                    for j in range(len(x)):
                        dist = abs(k * rawx[j] - rawy[j] + b) / ((k * k + 1) ** 0.5)
                        dists.append(dist)
                    mean = np.mean(dists)  # 均值
                    std = np.std(dists, ddof=1)  # 无偏标准差
                    stat = kstest(dists, 'norm')
                    distthre = mean + std
                    # 保存相关性过程的系数，jz,rotatespeed,load,activepower,mainfield,mainCom[i-1],,mic,r
                    md = models.bivarVariable.objects.filter(jzname=jzname, rotatespeed=rotatespeed, load=load,
                                                             activepower=activepower, aliasname1=mainCom[i][0],
                                                             aliasname2=mainCom[i][1], mic=rawmic, bivarr=rawr,
                                                             coef=coef, intercept=intercept, distthre=distthre)
                    if md.count() != 0:
                        models.bivarVariable.objects.filter(jzname=jzname, rotatespeed=rotatespeed, load=load,
                                                            activepower=activepower, aliasname1=mainCom[i][0],
                                                            aliasname2=mainCom[i][1]).update(mic=rawmic, bivarr=rawr,
                                                                                             coef=coef,
                                                                                             intercept=intercept,
                                                                                             score=score,
                                                                                             distthre=distthre)
                        models.bivarVariable.objects.filter(jzname=jzname, rotatespeed=rotatespeed, load=load,
                                                            activepower=activepower, aliasname2=mainCom[i][0],
                                                            aliasname1=mainCom[i][1]).update(mic=rawmic, bivarr=rawr,
                                                                                             coef=coef1,
                                                                                             intercept=intercept1,
                                                                                             score=score,
                                                                                             distthre=distthre)  # 变量顺序反过来也可以，不过直线方程要变一下
                    else:
                        models.bivarVariable.objects.create(jzname=jzname, rotatespeed=rotatespeed, load=load,
                                                            activepower=activepower, aliasname1=mainCom[i][0],
                                                            aliasname2=mainCom[i][1], mic=rawmic, bivarr=rawr,
                                                            coef=coef, intercept=intercept, score=score,
                                                            distthre=distthre)
                        models.bivarVariable.objects.create(jzname=jzname, rotatespeed=rotatespeed, load=load,
                                                        activepower=activepower, aliasname2=mainCom[i][0],
                                                        aliasname1=mainCom[i][1], mic=rawmic, bivarr=rawr, coef=coef1,
                                                        intercept=intercept1, score=score,
                                                        distthre=distthre)  # 变量顺序反过来也可以，不过直线方程要变一下
                    if abs(rawr) < thre_bivar:
                        continue

                    bivarRawDataPairs[fieldpair] = [rawx, rawy, rawz]
                    bivarDataPairs[fieldpair] = [x, y, z]
                    rawnamepair = [models.Variable.objects.filter(aliasname=mainCom[i][0])[0].zname,
                                   models.Variable.objects.filter(aliasname=mainCom[i][1])[0].zname, rawmic, rawr]
                    namepair = [models.Variable.objects.filter(aliasname=mainCom[i][0])[0].zname,
                                models.Variable.objects.filter(aliasname=mainCom[i][1])[0].zname, mic, r]
                    bivarRawFieldPairs[fieldpair] = rawnamepair
                    bivarFieldPairs[fieldpair] = namepair
            return HttpResponse(dumps({'bivarRawFieldPairs': bivarRawFieldPairs, 'bivarRawDataPairs': bivarRawDataPairs,
                                       'bivarDataPairs': bivarDataPairs, 'bivarFieldPairs': bivarFieldPairs}))

    else:
        # 获取变量树
        treeData, jzData = formInit()

        # 主变量下拉框渲染
        childArray = []
        childVariable = models.Variable.objects.exclude(parentid=0)
        for t in childVariable:
            # cNode = {'id': t.nid, 'name': t.zname, 'aliasname': t.aliasname}
            cNode = {'id': t.aliasname, 'name': t.zname}
            childArray.append(cNode)


        # 相关性分析 C n 2
        # initial_fields = ["shangx", "shangy", "xiax", "xiay", "shuix", "shuiy"]
        jznames = ["23"]
        jzname = "23"
        startTime = "2017-07-16 12:00:00"
        endTime = "2017-07-16 13:00:00"
        bivarRawDataNum = 2000
        BivarFields = ["shuix", "shuiy", "shangy", "xiay"]
        BivarFields = case_insensitive_sort(BivarFields)#对变量按照英文字母进行排序
        multiFieldsIdx = {}  # 变量对应在rawdata中的序号
        for i in range(len(BivarFields)):
            multiFieldsIdx[BivarFields[i]] = i
        var = ','.join(BivarFields)
        mainCom = [x for x in it.combinations(BivarFields, 2)]#进行22组合
        lenCom = len(mainCom)

        #处理峰峰值数据
        # 处理原始数据,保留原始数据中相关系数大于0.8的情况
        datanum = 2000
        bivarData = co.hiveDataNum(var, '', '',datanum)
        bivarRawData = co.hiveRawData(var, '', '', bivarRawDataNum)  # raw表示是原始数据

        bivarDataPairs = {}
        bivarRawDataPairs = {}
        bivarFieldPairs = {}
        bivarRawFieldPairs = {}
        fields_no = bivarData.shape[1]
        thre_r = 0.8
        numNoBicorr = 0
        for i in range(1, lenCom):
            fieldpair = ''.join(mainCom[i - 1])
            fieldpair = jzname + fieldpair
            idx1 = multiFieldsIdx[mainCom[i - 1][0]]
            idx2 = multiFieldsIdx[mainCom[i - 1][1]]

            rawx,rawy,rawz,rawmic,rawr = co.computeCorr(bivarRawData[:, idx1], bivarRawData[:, idx2])
            if abs(rawr) < thre_r and numNoBicorr == 1:#如果没有相关性不展示
                continue;
            if numNoBicorr == 0:
                numNoBicorr = 1
            bivarRawDataPairs[fieldpair] = [rawx,rawy,rawz]
            rawNamePair = [models.Variable.objects.filter(aliasname=mainCom[i - 1][0])[0].zname,
                        models.Variable.objects.filter(aliasname=mainCom[i - 1][1])[0].zname, rawmic, rawr]
            bivarRawFieldPairs[fieldpair] = rawNamePair

            x, y, z, mic, r = co.computeCorr(bivarData[:, idx1],
                                             bivarData[:, idx2])  # x第一列数据，y第二列数据，z是gaussian_kde列数据，mic信息系数，r线性相关系数
            bivarDataPairs[fieldpair] = [x, y, z]
            coef, intercept, score = co.linearRegression(x, y)  # 获取两列数据拟合值
            # xyz, mic, r = co.computeCorr(rawdata[:, 0], rawdata[:, i])
            # datapair[fieldpair] = xyz
            namepair = [models.Variable.objects.filter(aliasname=mainCom[i - 1][0])[0].zname,
                        models.Variable.objects.filter(aliasname=mainCom[i - 1][1])[0].zname, mic, r]
            bivarFieldPairs[fieldpair] = namepair

        return render(request, 'bivar.html',
                      {'td': dumps(treeData), 'jznames': dumps(jzData), 'childArray': dumps(childArray),
                       'bivarRawDataPairs': dumps(bivarRawDataPairs), 'bivarRawFieldPair': bivarRawFieldPairs, 'bivarRawFieldPairs': dumps(bivarRawFieldPairs),
                       'bivarDataPairs': dumps(bivarDataPairs), 'bivarFieldPair': bivarRawFieldPairs,'bivarFieldPairs': dumps(bivarRawFieldPairs)})


# 全维度分析 c n 2
def case_insensitive_sort(liststring):
    listtemp = [(x.lower(), x) for x in liststring]  # 将字符串列表，生成元组，（忽略大小写的字符串，字符串）
    listtemp.sort()  # 对元组排序，因为元组为：（忽略大小写的字符串，字符串），就是按忽略大小写的字符串排序

    return [x[1] for x in listtemp]  # 排序完成后，返回原字符串的列表


def multivar(request):
    if request.is_ajax() and request.method == 'POST':  # 是否为post请求

        jznames = eval(request.POST.get('jz'))
        fields = eval(request.POST.get('field'))
        params = eval(request.POST.get('param'))
        param = {}
        for x in params:
            param[x['name']] = x['value']
        # to do
        fuhe_start = param['fuhe_start']
        fuhe_end = param['fuhe_end']
        shuitou_start = param['shuitou_start']
        shuitou_end = param['shuitou_end']
        startTime = param['startTime']
        endTime = param['endTime']
        multiVarNum = param['multi_num']
        # 全维度分析 C n 2
        # fields = ["shangx", "shangy", "xiax", "xiay", "shuix", "shuiy"]
        while '' in fields:
            fields.remove('')
        var = ','.join(fields)
        #rawdata = osvm.hiveData(var, '', '')
        jznames = ["23"]
        datanum = 2000
        startTime = "2017-07-16 12:00:00"#记得删除
        endTime = "2017-07-16 13:00:00"
        if multiVarNum == '':
            multiVarNum = 2#2个维度之间的svmm

        multiFields = fields
        multiFields = case_insensitive_sort(multiFields)  # 先排序
        rawdatas = osvm.hiveDataTime(multiFields, startTime, endTime, datanum)  # 直接获取原始表中的数据
        timedata = rawdatas[:, 0]
        datatimedata = pdt.str2Dt(timedata)
        rawdatas = rawdatas[:, 1:len(rawdatas)]
        rawdatas = pdt.strToFloat(rawdatas)  # 转成数字
        rawdatas = np.array(rawdatas)
        multiFieldsIdx = {}  # 变量对应在rawdata中的序号
        for i in range(len(multiFields)):
            multiFieldsIdx[multiFields[i]] = i
        #  比对字段数组
        field_data = dict(zip(fields, rawdatas.transpose().tolist()))
        mainCom = [x for x in it.combinations(fields, multiVarNum)]
        datapair = {}
        fieldpairs = {}

        rotatespeed = 0
        load = 0
        activepower = 0
        pathName = "data/"  # model保存路径名称
        for jzname in jznames:
            for fieldCom in mainCom:
                fieldpair = ''.join(fieldCom)
                modelName = pathName + "train_model_" + jzname
                for fiTmp in fieldCom:
                    modelName += "_" + fiTmp
                modelName += ".m"


                trainSample, outlierSample = osvm.filterData(field_data[fieldCom[0]], field_data[fieldCom[1]])
                data, num, xmax, xmin, ymax, ymin = osvm.getSvm(trainSample, outlierSample,modelName)
                datapair[fieldpair] = [trainSample.tolist(), data, num, xmax, xmin, ymax, ymin]
                namepair = [models.Variable.objects.filter(aliasname=fieldCom[0])[0].zname,
                            models.Variable.objects.filter(aliasname=fieldCom[1])[0].zname]
                fieldpairs[fieldpair] = namepair
                # 保存到数据中

                #多维度
                multiFieldpair = '_'.join(fieldCom)  # 用空格隔开，存放在数据库中
                modelName = pathName + "train_model_"+jzname+"_" + multiFieldpair + ".m"
                trainSamples, outlierSamples = osvm.filterDataMultiVar(rawdatas, fieldCom, multiFieldsIdx)  # 过滤mean-+std的数据
                smax, smin = osvm.getSvmMultiVar(trainSamples, outlierSamples, modelName)  # 多维度svm生成clf，存入modelName
                multiScore = osvm.score(outlierSamples, modelName)  # z大于0时，大于50,为类中的点
                md = models.multivarVariable.objects.filter(jzname=jzname, rotatespeed=rotatespeed, load=load,
                                                            activepower=activepower, fieldpair=multiFieldpair)
                if md.count() != 0:
                    md.update(modelName=modelName)
                else:
                    models.multivarVariable.objects.create(jzname=jzname, rotatespeed=rotatespeed, load=load,
                                                           activepower=activepower, fieldpair=fieldpair,
                                                           modelName=modelName)
        return HttpResponse(dumps({'allpoint': datapair, 'fieldpairs': fieldpairs}))

    else:
        # 获取变量树
        treeData, jzData = formInit()
        jznames = ["23"]
        # 全维度分析 C n 2
        # initial_fields = ["shangx", "shangy", "xiax", "xiay", "shuix", "shuiy"]
        #参数区域
        multiFields = ["shangx", "shangy", "xiax", "xiay"]
        startTime = "2017-07-16 12:00:00"
        endTime = "2017-07-16 13:00:00"
        datanum = 2000
        multiFields = case_insensitive_sort(multiFields)#先排序
        multiVarNum  = 2#默认三个变量之间相关性
        multiFieldsIdx = {}#变量对应在rawdata中的序号
        for i in range(len(multiFields)):
            multiFieldsIdx[multiFields[i]] = i

        rawdatas = osvm.hiveDataTime(multiFields, startTime, endTime, datanum)  # 直接获取原始表中的数据
        timedata = rawdatas[:, 0]
        datatimedata = pdt.str2Dt(timedata)
        rawdatas = rawdatas[:, 1:len(rawdatas)]
        rawdatas = pdt.strToFloat(rawdatas)  # 转成数字
        rawdatas = np.array(rawdatas)

        #rawdata = osvm.hiveData(var, '', '')
        #  比对字段数组
        field_data = dict(zip(multiFields, rawdatas.transpose().tolist()))
        mainCom = [x for x in it.combinations(multiFields,multiVarNum)]
        datapair = {}
        fieldpairs = {}
        pathName = "data/"#model保存路径名称
        rotatespeed = 0
        load = 0
        activepower = 0
        for jzname in jznames:
            for fieldCom in mainCom:
                fieldpair = ''.join(fieldCom)#用空格隔开，存放在数据库中
                multiFieldpair = '_'.join(fieldCom)  # 用空格隔开，存放在数据库中
                #多维度
                modelName = pathName + "train_model_"+jzname+"_"+multiFieldpair+".m"

                trainSamples, outlierSamples = osvm.filterDataMultiVar(rawdatas, fieldCom, multiFieldsIdx)  # 过滤mean-+std的数据
                smax, smin = osvm.getSvmMultiVar(trainSamples, outlierSamples, modelName)  # 多维度svm生成clf，存入modelName
                multiScore = osvm.score(outlierSamples, modelName)  # z大于0时，大于50,为类中的点
                md = models.multivarVariable.objects.filter(jzname=jzname, rotatespeed=rotatespeed, load=load,
                                                         activepower=activepower,fieldpair = multiFieldpair)
                if md.count() != 0:
                    md.update(modelName = modelName)
                else:
                    models.multivarVariable.objects.create(jzname=jzname, rotatespeed=rotatespeed, load=load,
                                                           activepower=activepower, fieldpair=fieldpair,modelName = modelName)
                trainSample, outlierSample = osvm.filterData(field_data[fieldCom[0]], field_data[fieldCom[1]])
                modelName =  "train_model.m"
                data, num, xmax, xmin, ymax, ymin = osvm.getSvm(trainSample, outlierSample,modelName)#
                osvm.score(outlierSample,modelName)#z大于0时，大于50

                datapair[fieldpair] = [trainSample.tolist(), data, num, xmax, xmin, ymax, ymin]
                #trainSample是训练点，data是边界点，后面对应轴的最大值最小值
                namepair = [models.Variable.objects.filter(aliasname=fieldCom[0])[0].zname,
                            models.Variable.objects.filter(aliasname=fieldCom[1])[0].zname]
                fieldpairs[fieldpair] = namepair
        return render(request, 'multivar.html', {'td': dumps(treeData), 'jznames': dumps(jzData),
                                                 'allpoint': dumps(datapair), 'fieldpair': fieldpairs,
                                                 'fieldpairs': dumps(fieldpairs)})

# 健康度计算
def analysis(request):
    if request.is_ajax() and request.method == 'POST':  # 是否为post请求
        params = eval(request.POST.get('param'))
        param = {}
        for x in params:
            param[x['name']] = x['value']
        x = param['xffz']
        y = param['yffz']
        # healthIndex = osvm.getHealthIndex([x, y])
        healthIndex = osvm.score(np.array([x, y]).reshape(1, -1))

        return HttpResponse(healthIndex)

    else:
        # 获取变量树
        treeData, jzData = formInit()

        return render(request, 'analysis.html', {'td': dumps(treeData),
                                                 'jznames': dumps(jzData)})


# 劣化速度
def monitor(request):

    if request.is_ajax() and request.method == 'POST':  # 是否为post请求

        jznames = eval(request.POST.get('jz'))
        fields = eval(request.POST.get('field'))
        params = eval(request.POST.get('param'))
        param = {}
        for x in params:
            param[x['name']] = x['value']
        # to do
        fuhe_start = param['fuhe_start']
        fuhe_end = param['fuhe_end']
        shuitou_start = param['shuitou_start']
        shuitou_end = param['shuitou_end']
        startTime = param['startTime']
        endTime = param['endTime']
        while '' in fields:
            fields.remove('')
        # 数据第一来自数据库，如果这个维度阈值超标,必须进行趋势分析，如果这个维度劣化速度过快，也必须进行分析
        # 先根据维度,从数据库中读取数据，然后在report需要考虑到阈值超标的情况，
        if len(jznames) == 0:
            jznames = ["23"]
        single_fields = fields#["shangx", "shangy"]
        jznames = ["23"]
        startTime = "2017-07-16 12:00:00"
        endTime = "2017-07-16 13:00:00"
        datanum = 2000
        rawdatas = pdt.hiveDataTime(single_fields, startTime, endTime, datanum)  # 直接获取原始表中的数据
        # rawdatas = rawdatas.sort(lambda x,y:cmp(x[0],y[0]))
        # 如果读取时间段数据为空如何处理
        timedata = rawdatas[:, 0]
        datatimedata = pdt.str2Dt(timedata)
        rawdatas = rawdatas[:, 1:len(rawdatas)]
        rawdatas = pdt.strToFloat(rawdatas)  # 转成数字
        rawdatas = np.array(rawdatas)

        # 在report中先要进行阈值判断
        rotatespeed = 0  # 转速
        load = 0  # 负荷
        activepower = 0  # 有功功率
        exceThreholds = {}  # 是否超过阈值，或者劣化过快
        datajz = {}
        slopejz = {}
        timeInterval = 1  # 时间间隔 1min
        namepairs = {}
        thre_slope = 0
        factor = 1000  # 斜率值太小，乘以1000,
        for jzname in jznames:
            slopedbs = []
            X_slopedbs = []
            isExce = 0
            for i in range(len(single_fields)):
                datadb, X_slopedb, slopedb= pdt.timeIntervalSlope(datatimedata,rawdatas[:,i],timeInterval,factor)
                 # slopedb,X_slopedb,timerawdata = pdt.pdtSlope(datatimedata,rawdatas[:,i],timeInterval)
                min_val, mid_val, max_val, alert_val,mean,std = pdt.meanstd(X_slopedb)
                jzfield = jzname + single_fields[i]
                zname = models.Variable.objects.filter(aliasname=single_fields[i])[0].zname
                namepair = [jzname, single_fields[i], zname, min_val, mid_val, max_val, alert_val, mean, std,thre_slope]
                namepairs[jzfield] = namepair
                datajz[jzfield] = datadb
                slopejz[jzfield] = slopedb
                md = models.monitorVariable.objects.filter(jzname=jzname, rotatespeed=rotatespeed, load=load,
                                                         activepower=activepower, aliasname=single_fields[i],timeInterval = timeInterval)
                if md.count()!=0:
                    md.update(min_val=min_val,mid_val=mid_val, max_val=max_val, alert_val=alert_val,std = std)
                else:
                    models.monitorVariable.objects.create(jzname=jzname, rotatespeed=rotatespeed, load=load,
                                                         activepower=activepower, aliasname=single_fields[i],timeInterval = timeInterval,
                                                          min_val=min_val, mid_val=mid_val, max_val=max_val,
                                                          alert_val=alert_val, std=std)
        return HttpResponse(dumps({'data': datajz,'slope': slopejz,'namepairs': namepairs
        }))
        # return HttpResponse(dumps(
        #     {'data': data, 'slope': slope, 'trend': trend, 'min': min_val, 'mid': mid_val, 'max': max_val,
        #      'alert1': alert_val}))

    else:
        # 获取变量树
        treeData, jzData = formInit()

        # var = "shangx"
        # data, X_millisecond, X_train = pdt.getSamples(var)#data <type 'list'>: [[1480809518000.0, 118.59999999999991]...]
        # slope, trend, X_slope = pdt.slope(X_millisecond, X_train)#data，list,list,mill时间,原始数据,slope,list,list,mill时间,斜率×1000，X_slope ndarray,ndarray
        # min_val, mid_val, max_val, alert_val,mean,std = pdt.meanstd(X_slope)
        # data 时间，原始数据 ,trend没用到，第一个时间，算出来时间点在直线上的值,没怎么用到，x_slope是斜率，只有一列

        # 数据第一来自数据库，如果这个维度阈值超标,必须进行趋势分析，如果这个维度劣化速度过快，也必须进行分析
        # 先根据维度,从数据库中读取数据，然后在需要考虑到阈值超标的情况，
        jznames = ["23"]
        single_fields = ["xiax","xiay"]
        startTime = "2017-07-16 12:00:00"
        endTime = "2017-07-16 13:00:00"
        datanum = 2000
        rawdatas = pdt.hiveDataTime(single_fields, startTime, endTime, datanum)#直接获取原始表中的数据
        #rawdatas = rawdatas.sort(lambda x,y:cmp(x[0],y[0]))
        #如果读取时间段数据为空如何处理
        timedata = rawdatas[:,0]
        datatimedata = pdt.str2Dt(timedata)
        rawdatas = rawdatas[:,1:len(rawdatas)]
        rawdatas = pdt.strToFloat(rawdatas)#转成数字
        rawdatas = np.array(rawdatas)

    
        exceThreholds = {}#是否超过阈值，或者劣化过快
        datajz = {}
        slopejz = {}
        timeInterval = 1#时间间隔 1min
        namepairs = {}
        thre_slope = 0
        factor = 1000#斜率值太小，乘以1000,
        for jzname in jznames:
            slopedbs = []
            X_slopedbs = []
            isExce = 0
            for i in range(len(single_fields)):
                datadb, X_slopedb, slopedb= pdt.timeIntervalSlope(datatimedata,rawdatas[:,i],timeInterval,factor)
                 # slopedb,X_slopedb,timerawdata = pdt.pdtSlope(datatimedata,rawdatas[:,i],timeInterval)
                min_val, mid_val, max_val, alert_val,mean,std = pdt.meanstd(X_slopedb)
                jzfield = jzname + single_fields[i]
                zname = models.Variable.objects.filter(aliasname=single_fields[i])[0].zname
                namepair = [jzname,single_fields[i],zname,min_val,mid_val,max_val,alert_val,mean,std,thre_slope]
                namepairs[jzfield] = namepair#相关信息
                datajz[jzfield] = datadb#原始数据
                slopejz[jzfield] = slopedb#斜率变化
        return render(request, 'monitor.html',{'td': dumps(treeData), 'jznames': dumps(jzData), 'data': dumps(datajz), 'slope': dumps(slopejz),
                       'jznos':dumps(jznames),'namepairs':dumps(namepairs),'namepair':namepairs})
        # return render(request, 'monitor.html',
        #           {'td': dumps(treeData), 'jznames': dumps(jzData), 'data': datajz, 'slope': slopejz,
        #            'jznames': jznames, 'znames':znames, 'single_fields': single_fields, 'trend': trend, 'min': min_val, 'mid': mid_val,
        #            'max': max_val, 'alert1': alert_val})



# interactive

def monitor_bac(request):
    # 获取变量树
    treeData, jzData = formInit()

    initial_fields = ["shangx", "shangy", "xiax", "xiay", "shuix", "shuiy"]
    datapair = []
    timeseries = []

    for t in ts.gettime():
        timeseries.append(t[0:13] + ':' + t[13:15] + ':' + t[15:17])

    # print timeseries
    categories = []
    for field in initial_fields:
        models.Variable.objects.filter(aliasname=field)
        datapair.append(ts.getdata(field)[:500])
        categories.append(models.Variable.objects.filter(aliasname=field)[0].zname)

    return render(request, 'monitor.html',
                  {'td': dumps(treeData), 'jznames': dumps(jzData)})


# 数据接口  健康度 劣化速度 趋势
def vis(request):
    X_train, X_outliers, X_all, time_series = mo.getSamples('shangx', 'shangy')
    nu = float(len(X_outliers)) / float(len(X_train))
    gamma = 0.0001
    mo.train(X_train, nu, gamma)
    xx, yy, z, sc = mo.gettridata(X_train)

    jsondata = {'xData': time_series,
                'datasets': [
                    {'name': '上导X摆度峰峰值', 'data': xx.tolist(), 'unit': 'um', 'type': 'line', 'valueDecimals': 1},
                    {'name': '上导Y摆度峰峰值', 'data': yy.tolist(), 'unit': 'um', 'type': 'line', 'valueDecimals': 1},
                    {'name': '健康度', 'data': sc.tolist(), 'unit': '1', 'type': 'line', 'valueDecimals': 2},
                    {'name': '劣化速度', 'data': z.tolist(), 'unit': '/s', 'type': 'line', 'valueDecimals': 1}]}

    return HttpResponse(dumps(jsondata), content_type='application/json')

# 机组复选框 初始化
def formInit():
    # 获取变量树
    treeArray = []

    def getChildren(id=0):
        jsonArray = []
        for obj in treeArray:
            if obj["parentid"] == id:
                x = getChildren(obj["id"])
                if len(x) != 0:
                    jsonArray.append({"nodeid": obj["id"], "text": obj["name"], "alias": obj["aliasn"], "nodes": x})
                else:
                    jsonArray.append({"nodeid": obj["id"], "text": obj["name"], "alias": obj["aliasn"]})

        return jsonArray

    treeview = models.Variable.objects.all()
    for t in treeview:
        treeNode = {'id': t.nid, 'parentid': t.parentid, 'name': t.zname, 'aliasn': t.aliasname}
        treeArray.append(treeNode)
    treeData = getChildren()
    #   treeData = [{"text": "Node 1"}]

    # 获取机组列表
    jzArray = []

    def getJzChildren(id=0):
        jArray = []
        for obj in jzArray:
            if obj["parentid"] == id:
                x = getJzChildren(obj["id"])
                if len(x) != 0:
                    jArray.append({"nodeid": obj["id"], "text": obj["name"], "alias": obj["aliasn"], "nodes": x})
                else:
                    jArray.append({"nodeid": obj["id"], "text": obj["name"], "alias": obj["aliasn"]})

        return jArray

    #   获取机组名称
    jz = models.Jzvariable.objects.all()
    for t in jz:
        jnode = {'id': t.jid, 'parentid': t.parentid, 'name': t.jzname, 'aliasn': t.aliasname}
        jzArray.append(jnode)
    jzData = getJzChildren()

    return treeData, jzData

# 机组复选框 初始化
def formInitNew():
    # 获取变量树
    treeArray = []

    def getChildren(id=0):
        jsonArray = []
        for obj in treeArray:
            if obj["parentid"] == id:
                x = getChildren(obj["id"])
                if len(x) != 0:
                    jsonArray.append({"nodeid": obj["id"], "text": obj["name"], "alias": obj["aliasn"], "nodes": x})
                else:
                    jsonArray.append({"nodeid": obj["id"], "text": obj["name"], "alias": obj["aliasn"]})

        return jsonArray

    treeview = models.Middlevariable.objects.all()
    
    for t in treeview:
        comments = t.comments
        if t.fieldname == 'gettime':
            continue
        #comments = comments[:-2]
        # comments = comments.replace('_','')
        treeNode = {'id': t.id, 'parentid': t.parentid, 'name': comments, 'aliasn': t.fieldname}
        treeArray.append(treeNode)
    treeData = getChildren()
    #   treeData = [{"text": "Node 1"}]

    # 获取机组列表
    jzArray = []

    def getJzChildren(id=0):
        jArray = []
        for obj in jzArray:
            if obj["parentid"] == id:
                x = getJzChildren(obj["id"])
                if len(x) != 0:
                    jArray.append({"nodeid": obj["id"], "text": obj["name"], "alias": obj["aliasn"], "nodes": x})
                else:
                    jArray.append({"nodeid": obj["id"], "text": obj["name"], "alias": obj["aliasn"]})

        return jArray

    #   获取机组名称
    jz = models.Jzvariable.objects.all()
    for t in jz:
        jnode = {'id': t.jid, 'parentid': t.parentid, 'name': t.jzname, 'aliasn': t.aliasname}
        jzArray.append(jnode)
    jzData = getJzChildren()

    return treeData, jzData



def configuration(request):

    return render(request, 'configuration.html')

def getDataJson(request):
    # print request.method,request.GET
    # print u'field' in request.GET
    # print request.GET['field']
    data = []
    if request.method == 'GET' and 'field' in request.GET:
        try:
            fields2line = request.GET['field']
            # print fields2line
            vcs = models.Xfsvariable.objects.all()
            # vcs = models.Middlevariable.objects.all()

            fieldname_meaning = {}
            fieldmeaning_name = {}

            for vc in vcs:
                fieldname_meaning[vc.fieldname] = vc.comments
                fieldmeaning_name[vc.comments] = vc.fieldname

            basicfield = ['获取时间']
            fields2query = basicfield + [fields2line]

            sql_fields = ','.join([fieldmeaning_name[f] for f in fields2query])
            # sql = "SELECT " + sql_fields + " FROM hd_middledata_all_xfs_ffz_mean_tmp where y='2017' and m between '05' and '07'"
            # sql = "SELECT " + sql_fields + " FROM hd_middledata_all_xfs_ffz_mean_tmp where y='2017' and m='05' and d between '06' and '31'"
            sql = "SELECT " + sql_fields + " FROM hd_middledata_all_xfs_ffz_mean_tmp where y='2017' and m='05' and d='06'"
            # sql = "SELECT " + sql_fields + " FROM hd_premiddledata_ffz_mean_ext_orc where y='2017' and m='05' and d='06' limit 100"

            hc = HiveConn()
            hc.getConn()
            for i in hc.select(sql):
                # gettime.append(time.mktime(time.strptime(i[0], '%Y-%m-%d %H:%M:%S')) * 1000 - 8 * 60 * 60 * 1000)
                data.append([time.mktime(time.strptime(i[0], '%Y-%m-%d %H:%M:%S.%f')) * 1000 - 8 * 60 * 60 * 1000, i[1]])
        finally:
            pass
    return HttpResponse(dumps(data), content_type='application/json')



def realtimemonitor(request):
    vcs = models.Xfsvariable.objects.all()
    fieldname_meaning = {}
    fieldmeaning_name = {}
    for vc in vcs:
        fieldname_meaning[vc.fieldname] = vc.comments
        fieldmeaning_name[vc.comments] = vc.fieldname
    # fields2line = ['上导X摆度峰峰值均值', '上导Y摆度峰峰值最大值', '上导Y摆度峰峰值均值', '上导X摆度一倍频']
    fields2line = fieldname_meaning.values()[:4]
    # fields2line = ['上导X摆度峰峰值均值', '上导Y摆度峰峰值最大值', '上导Y摆度峰峰值均值', '上导X摆度一倍频']
    # fields2line = ['上导X摆度峰峰值均值']
    return render(request, 'scaleRealtime.html', {'fields': dumps(fields2line)})

def lines(request):
    # vcs = models.Xfsvariable.objects.all()
    vcs = models.Middlevariable.objects.all()

    fieldname_meaning = {}
    fieldmeaning_name = {}

    for vc in vcs:
        fieldname_meaning[vc.fieldname] = vc.comments
        fieldmeaning_name[vc.comments] = vc.fieldname
    # fields2line = ['上导X摆度峰峰值均值', '上导Y摆度峰峰值最大值', '上导Y摆度峰峰值均值', '上导X摆度一倍频']
    fields2line = fieldname_meaning.values()[:8]
    # print fields2line
    if '获取时间' in fields2line:
        fields2line.remove('获取时间')

    basicfield = ['获取时间']
    fields2query = basicfield + fields2line

    sql_fields = ','.join([fieldmeaning_name[f] for f in fields2query])
    # sql = "SELECT " + sql_fields + " FROM hd_middledata_all_xfs_ffz_mean_tmp where y='2017' and m='05' and d='06' limit 2000"
    sql = "SELECT " + sql_fields + " FROM hd_premiddledata_ffz_mean_ext_orc where y='2017' and m='05' and d='06'"

    hc = HiveConn()
    hc.getConn()
    gettime = []
    datalist = []
    for i in hc.select(sql):
        # print i
        # gettime.append(time.mktime(time.strptime(i[0], '%Y-%m-%d %H:%M:%S')) * 1000 - 8 * 60 * 60 * 1000)
        gettime.append(time.mktime(time.strptime(i[0], '%Y-%m-%d %H:%M:%S.%f')) * 1000 - 8 * 60 * 60 * 1000)
        # gettime.append(i[0])
        datalist.append(i[1:])
    dataarray = np.array(datalist)

    # titletext = '-'.join([f for f in fields2line])
    titletext = '实时监控'
    legenddata = fields2line
    xAxisdata = gettime
    seriesdata = []
    ll = len(fields2line)
    for i in range(ll):
        seriesdata.append(dataarray[:, i].tolist())
    # seriesdata.append({'name': fields2line[i], 'type': 'line', 'visible': 'true', 'data': dataarray[:, i].tolist()})
    # seriesdata = [{'name':'邮件营销','type':'line','stack': '总量','data': [120, 132, 101, 134, 90, 230, 210]},{'name':'联盟广告','type':'line','stack': '总量','data': [120, 132, 101, 134, 90, 230, 210]}]

    return render(request, 'realtimemonitor.html',
                  {'titletext': dumps(titletext), 'legenddata': dumps(legenddata), 'xAxisdata': dumps(xAxisdata),
                   'seriesdata': dumps(seriesdata)})

def monitor_realtime(request):

    # 获取变量树
    treeData, jzData = formInitNew()

    # vcs = models.Xfsvariable.objects.all()
    vcs = models.Middlevariable.objects.all()

    fieldname_meaning = {}
    fieldmeaning_name = {}

    for vc in vcs:
        fieldname_meaning[vc.fieldname] = vc.comments
        fieldmeaning_name[vc.comments] = vc.fieldname
    # fields2line = ['上导X摆度峰峰值均值', '上导Y摆度峰峰值最大值', '上导Y摆度峰峰值均值', '上导X摆度一倍频']
    fields2line1 = fieldname_meaning.values()[:8]
    # print fields2line
    if '获取时间' in fields2line1:
        fields2line1.remove('获取时间')

    basicfield = ['获取时间']
    fields2query = basicfield + fields2line1

    sql_fields = ','.join([fieldmeaning_name[f] for f in fields2query])
    # sql = "SELECT " + sql_fields + " FROM hd_middledata_all_xfs_ffz_mean_tmp where y='2017' and m='05' and d='06' limit 2000"
    sql = "SELECT " + sql_fields + " FROM hd_premiddledata_ffz_mean_ext_orc where y='2017' and m='05' and d='06'"

    hc = HiveConn()
    hc.getConn()
    gettime = []
    datalist = []
    for i in hc.select(sql):
        # print i
        # gettime.append(time.mktime(time.strptime(i[0], '%Y-%m-%d %H:%M:%S')) * 1000 - 8 * 60 * 60 * 1000)
        gettime.append(time.mktime(time.strptime(i[0], '%Y-%m-%d %H:%M:%S.%f')) * 1000 - 8 * 60 * 60 * 1000)
        # gettime.append(i[0])
        datalist.append(i[1:])
    dataarray = np.array(datalist)

    # titletext = '-'.join([f for f in fields2line])
    titletext = '实时监控'
    legenddata = fields2line1
    xAxisdata = gettime
    seriesdata = []
    ll = len(fields2line1)
    for i in range(ll):
        seriesdata.append(dataarray[:, i].tolist())

    return render(request, 'monitor_realtime.html', {'td': dumps(treeData), 'jznames': dumps(jzData),'fields': dumps(fields2line),'titletext': dumps(titletext), 'legenddata': dumps(legenddata), 'xAxisdata': dumps(xAxisdata),
                                                     'seriesdata': dumps(seriesdata)})

#实时更新进度

def progressRealtime(request):
    return render(request, 'progressRealtime.html')

# # 倍频实时更新



def report(request):
    logger.info("request report view")
    if request.is_ajax() and request.method == 'POST':  # 是否为post请求
        # 根据选择机组，时间，条件进行数据查询，比对，显示结果
        jznames = eval(request.POST.get('jz'))
        fields = eval(request.POST.get('field'))
        params = eval(request.POST.get('param'))
        param = {}
        for x in params:
            param[x['name']] = x['value']
        # print fields


        # 连接HBase筛选
        # to do
        fuhe_start = param['fuhe_start']
        fuhe_end = param['fuhe_end']
        shuitou_start = param['shuitou_start']
        shuitou_end = param['shuitou_end']
        startTime = param['startTime']
        endTime = param['endTime']
        monitPeriod = param['monit_period']
        mainfield = param['mainfieldcontent']
        # 处理特殊情况
        if monitPeriod < 1 or monitPeriod == '':
            monitPeriod = 1
        if len(jznames) == 0:
            jznames = ["23"]
        if startTime == '':
            startTime = "2017-05-06 12:00:00"
        if endTime == '':
            endTime = "2017-05-06 13:00:00"
        monitPeriod = 1
        # if mainfield == '':
        mainField = "shangy_ffz"
        if len(fields) == 0:
            fields = ["xiax_ffz", "xiay_ffz"]
        
        data_num = 2000
        datanum = data_num
        dbDataNum = 200  # 展示数据库的数量
        userid = "007"
        activepower = 0
        rotatespeed1 = 0
        rotatespeed2 = 0
        rotatespeed3 = 0

        #衍生参数
        while '' in fields:
            fields.remove('')
        fields = case_insensitive_sort(fields)  # 先排序
        univarFields = copy.deepcopy(fields)
        bivarFields = copy.deepcopy(fields)
        bivarRawFields = rpt.getRawFields(fields)
        monitSingleFields = copy.deepcopy(fields)

        # 获取中文名fieldZname[],标准阈值thre_ground
        fieldZname, categories, thre_ground = rpt.getZname(univarFields)

        # univar个性化阈值
        jzcompare, datalist, univarExceThreholds, datalist, dataTime, datamiddle = rpt.univarModule(jznames,
                                                                                                    univarFields,
                                                                                                    startTime, endTime,
                                                                                                    data_num, userid,
                                                                                                    activepower,
                                                                                                    rotatespeed1,
                                                                                                    rotatespeed2,
                                                                                                    rotatespeed3)

        # bivar 相关性分析
        bivarFieldPairs, bivarFengFieldPairs, dbdatapair, datapair, fengdatapair, fengdbdatapair = rpt.bivarModule(
            jznames, bivarFields, bivarRawFields, startTime, endTime, data_num, userid, mainField, fieldZname)

        # isof
        isofTime, isofZ = rpt.resultIsof(startTime, endTime, data_num)
        isofZ = isofZ.tolist()
        ##趋势分析
        monitFields, monitNamepairs, monitDatas, monitSlopes, monitIntercepts, monitRSlopes, monitSegmentDatas = rpt.monitModule(
            jznames, fieldZname, monitSingleFields, datamiddle, dataTime, univarExceThreholds)

        return HttpResponse(
            dumps({"jznos": jznames, "jzcompare": jzcompare,
                   "categories": categories, "threshold_ground": thre_ground, "startTime": startTime,
                   "endTime": endTime,
                   "datalist": datalist, "exceThreholds": univarExceThreholds,
                   'allpoint': datapair, 'dballpoint':
                       dbdatapair, 'bivarFieldPair': bivarFieldPairs, 'bivarFieldPairs': bivarFieldPairs,
                   'fengallpoint': fengdatapair, 'fengdballpoint': fengdbdatapair,
                   'bivarFengFieldPairs': bivarFengFieldPairs,
                   # 'multiFieldPairs': multiFieldPairs,
                   'monitDatas': monitDatas, 'monitSlopes': monitSlopes, 'monitnamepair': monitNamepairs,
                   'monitNamepairs': monitNamepairs,
                   'monitRSlopes': monitRSlopes, 'monitfield': monitFields, 'monitFields': monitFields,
                   'monitSegmentDatas': monitSegmentDatas,
                   'isofTime': isofTime, 'isofZ': isofZ}))
    
    

    
    else:
        # 主变量下拉框渲染,treeData应该是变量树，描述不同维度，jzData是所有机组编号
        treeData, jzData = formInitNew()

        childArray = []
        childVariable = models.Middlevariable.objects.filter(parentid=0)
        for t in childVariable:
            # cNode = {'id': t.nid, 'name': t.zname, 'aliasname': t.aliasname}
            cNode = {'id': t.fieldname, 'name': t.comments}
            childArray.append(cNode)
            
        # 初始参数区
        userid = "007"
        jznames = ['23']
        fields = ["xiax_ffz", "xiay_ffz"]
        mainField = ''
        startTime = "2017-07-15 00:00:00"
        #startTime = ""
        endTime = "2017-07-15 12:00:00"
        data_num = 1000
        dbDataNum = 200  # 展示数据库的数量
        activepower = 0
        rotatespeed1 = 0
        rotatespeed2 = 0
        rotatespeed3 = 0
        
        #衍生初始参数
        while '' in fields:
            fields.remove('')
        fields = case_insensitive_sort(fields)  # 先排序
        univarFields = fields
        bivarRawFields = rpt.getRawFields(fields)
        bivarFields = fields
        monitSingleFields = fields
        #获取中文名fieldZname[],标准阈值thre_ground
        fieldZname, categories, thre_ground = rpt.getZname(univarFields)

        #univar个性化阈值
        jzcompare, datalist, univarExceThreholds, datalist, dataTime, datamiddle = rpt.univarModule(jznames,univarFields,startTime, endTime, data_num,userid,activepower,rotatespeed1,rotatespeed2,rotatespeed3)

        #bivar 相关性分析
        bivarFieldPairs, bivarFengFieldPairs, dbdatapair, datapair, fengdatapair, fengdbdatapair = rpt.bivarModule(jznames, bivarFields, bivarRawFields, startTime, endTime, data_num, userid,mainField, fieldZname)

        #isof
        isofTime, isofZ = rpt.resultIsof(startTime, endTime,data_num)
        isofZ = isofZ.tolist()
        ##趋势分析
        monitFields, monitNamepairs, monitDatas, monitSlopes, monitIntercepts, monitRSlopes,monitSegmentDatas = rpt.monitModule(jznames,fieldZname,monitSingleFields,datamiddle, dataTime,univarExceThreholds)

        # 文档保存
        # document = Document()
        # for jzname in jznames:
        #     rpt.uivarDataTable(document, jzname, categories, datalist, startTime, endTime)
        #     rpt.uivarTable(document, datalist, univarExceThreholds, categories, jzcompare,
        #                    thre_ground, jzname)
        #     rpt.uivarNearTable(document, datalist, univarExceThreholds, categories, jzcompare,
        #                        thre_ground, jzname)
        #     rpt.bivarTable(document, jzname, bivarFieldPairs)
        #     rpt.monitTable(document, jzname, monitFields, monitNamepairs, monitRSlopes, monitSlopes)
        # curTime = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        # docName = "分析报告" + curTime + ".docx"
        # rpt.saveDocument(document, "", docName)

        return render(request, "report.html",
                      {'td': dumps(treeData), 'jznames': dumps(jzData), "jznos": jznames, "jzcompare": dumps(jzcompare),
                       'childArray': dumps(childArray),
                       "categories": dumps(categories), "threshold_ground": dumps(thre_ground),
                       "startTime": dumps(startTime), "endTime": dumps(endTime),
                       "datalist": dumps(datalist), "exceThreholds": dumps(univarExceThreholds),
                       'allpoint': dumps(datapair), 'dballpoint': dumps(dbdatapair), 'bivarFieldPair': bivarFieldPairs,
                       'bivarFieldPairs': dumps(bivarFieldPairs),
                       'fengallpoint': dumps(fengdatapair), 'fengdballpoint': dumps(fengdbdatapair),
                       'bivarFengFieldPair': bivarFengFieldPairs, 'bivarFengFieldPairs': dumps(bivarFengFieldPairs),
                       # 'multiallpoint': dumps(multidatapair), 'multifieldpair': multifieldpairs,'multifieldpairs': dumps(multifieldpairs),
                       # 'multiFieldPairs': dumps(multiFieldPairs),
                       'monitDatas': dumps(monitDatas), 'monitSlopes': dumps(monitSlopes),
                       "monitIntercepts": dumps(monitIntercepts), 'monitnamepair': monitNamepairs,
                       'monitNamepairs': dumps(monitNamepairs),
                       'monitRSlopes': dumps(monitRSlopes), 'monitfield': monitFields,
                       'monitFields': dumps(monitFields), 'monitSegmentDatas': dumps(monitSegmentDatas),
                       'monitSegmentData': monitSegmentDatas,
                       'isofTime':dumps(isofTime), 'isofZ':dumps(isofZ)})


def modeldata(request):
    logger.info("request modeldata view")
    if request.is_ajax() and request.method == 'POST':  # 是否为post请求
        
        jznames = eval(request.POST.get('jz'))
        fields = eval(request.POST.get('field'))
        params = eval(request.POST.get('param'))
        param = {}
        for x in params:
            param[x['name']] = x['value']
        
        #   连接HBase筛选
        fuhe_start = param['fuhe_start']
        fuhe_end = param['fuhe_end']
        shuitou_start = param['shuitou_start']
        shuitou_end = param['shuitou_end']
        startTime = param['startTime']
        endTime = param['endTime']
        bivar_thre = param['bivar_thre']
        monit_period = param['monit_period']
        multi_num = param['multi_num']
        data_num = param['data_num']
        
        # 参数预处理
        userid = '007'
        timeIntervals = []
        if len(jznames) == 0:
            jznames = ['23']
        if len(fields) == 0:
            fields = ["shangx_ffz", "xiax_ffz","xiay_ffz"]
        if startTime == '':
            startTime = "2017-05-06 00:00:00"
            #startTime = ''
        if endTime == '':
            endTime = "2017-05-06 23:00:00"
        if bivar_thre == '':
            bivar_thre = 0.8
        if monit_period == '':
            timeIntervals = ['1']
        else:
            timeIntervals = monit_period.split(',')[:]
            while '' in timeIntervals:
                timeIntervals.remove('')
        if multi_num == '':
            multi_num = 2
        if data_num == '':
            data_num = 2000
            
        mainField = ''
        while '' in fields:
            fields.remove('')
        fields = case_insensitive_sort(fields)  # 进行排序
        # 机组,机组有功功率，转速1，转速2，转速3 影响个性化阈值的因变量
        activepower = 0
        rotatespeed1 = 0
        rotatespeed2 = 0
        rotatespeed3 = 0
        
        global logInfo
        # 记录建模模块的输出信息
        userId = "007"
        curTime = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        # 个性化阈值
        categories = []
        thre_ground = []
        fieldZname = {}  # 英文名对应中文名
        # logInfo.append("建模过程信息输出区：")
        global num_progress
        num_progress = 0
        logInfo = ''
        logInfo += "模型训练信息实时输出区：</br>"
        logInfo += "开始单维度个性化阈值分析...</br>"
        print("univar...")
        for field in fields:
            if field != '':
                categories.append(models.Middlevariable.objects.filter(fieldname=field)[0].comments)
                fieldZname[field] = models.Middlevariable.objects.filter(fieldname=field)[0].comments
                thre_ground.append(models.Middlevariable.objects.filter(fieldname=field)[0].hech)
        
        # datalist = od.hiveDataTimeNew(fields, startTime, endTime, datanum)#按照时间段读，速度比较慢
        # 中间数据读取
        datatime,dataarray = rpt.hiveDataTimeNew(fields, startTime, endTime, data_num)  # 读取前2000个，速度比较快
        datamiddle = dataarray
        # datamiddle = rpt.removeDup(datamiddle)
        
        # datamiddle = datamiddle.tolist()
        thre = rpt.allthreholdMiddle(datamiddle)  # 生成个性化阈值
        # for i in range(len(categories)):
        #     logInfo += categories[i] + "个性化阈值计算完毕</br>"
        # 机组,机组有功功率，转速1，转速2，转速3 影响个性化阈值的因变量
        jzFactor = {}
        jzCompare = {}
        for jzname in jznames:
            jzf = jzname + "-" + str(activepower) + "-" + str(rotatespeed1) + "-" + str(rotatespeed2) + "-" + str(
                rotatespeed3)
            jzCompare[jzname] = thre
            jzFactor[jzf] = thre
        # 将个性化阈值插入到models中
        # models.PersonalizedThreshold.objects.all().delete()
        for jzname in jznames:
            for i in range(len(fields)):
                aliasname = fields[i]
                zname = categories[i]
                threshold = jzCompare[jzname][i]
                logInfo += fieldZname[aliasname] + "个性化阈值:  " + str(threshold)+"<br/>"
                md = models.Personalizedthreshold.objects.filter(userid=userid, jzname=jzname, zname=zname,
                                                                 aliasname=aliasname,
                                                                 activepower=activepower,
                                                                 rotatespeed1=rotatespeed1, rotatespeed2=rotatespeed2,
                                                                 rotatespeed3=rotatespeed3, starttime=startTime,
                                                                 endtime=endTime,
                                                                 datanum=data_num)
                if md.count() != 0:
                    models.Personalizedthreshold.objects.filter(userid=userid, jzname=jzname, zname=zname,
                                                                aliasname=aliasname,
                                                                activepower=activepower,
                                                                rotatespeed1=rotatespeed1, rotatespeed2=rotatespeed2,
                                                                rotatespeed3=rotatespeed3, starttime=startTime,
                                                                endtime=endTime,
                                                                datanum=data_num).update(threshold=threshold)
                else:
                    models.Personalizedthreshold.objects.create(userid=userid, jzname=jzname, zname=zname,
                                                                aliasname=aliasname,
                                                                activepower=activepower,
                                                                rotatespeed1=rotatespeed1, rotatespeed2=rotatespeed2,
                                                                rotatespeed3=rotatespeed3, starttime=startTime,
                                                                endtime=endTime,
                                                                datanum=data_num, threshold=threshold)
        
        logInfo += "个性化阈值模型计算完毕！</br></br>"
        logInfo += "开始相关性分析...</br>"
        BivarFields = fields  # 对变量按照英文字母进行排序
        multiFieldsIdx = {}  # 变量对应在rawdata中的序号
        for i in range(len(BivarFields)):
            multiFieldsIdx[BivarFields[i]] = i
        
        mainCom = [x for x in it.combinations(BivarFields, 2)]  # 进行22组合
        lenCom = len(mainCom)
        
        # 处理峰峰值数据
        # 处理原始数据,保留原始数据中相关系数大于0.8的情况
        print("bivar...")
        bivarDataNum = data_num
        bivarRawDataNum = data_num
        bivarData = datamiddle  # 不带时间
        # bivarRawData = co.hiveRawData(var, '', '', bivarRawDataNum)  # raw表示是原始数据
        
        # 原始数据读取
        BivarRawFields = rpt.getRawFields(fields)
        bivarRawTime,bivarRawData = rpt.hiveRawDataTimeNew(BivarRawFields, startTime, endTime, bivarDataNum)  # startTime为空，取当天前datanum条数据，
        #峰峰值
        bivarFengData = datamiddle
        bivarFengTime = datatime
        # bivarRawData = rpt.removeDup(bivarRawData)
        
        # bivarRawData = bivarRawData.tolist()
        bivarDataPairs = {}
        bivarRawDataPairs = {}
        bivarFieldPairs = {}
        bivarRawFieldPairs = {}
        numNoBicorr = 0
        rotatespeed = 0
        load = 0
        activepower = 0
        for i in range(0, lenCom):
            # 原始数据相关性
            fieldpair = ''.join(mainCom[i])
            fieldpair = jzname + fieldpair
            aliasname1 = mainCom[i][0]
            aliasname2 = mainCom[i][1]
            idx1 = multiFieldsIdx[mainCom[i][0]]
            idx2 = multiFieldsIdx[mainCom[i][1]]
            if aliasname1 == 'active_power_mv' and aliasname2 == 'zs_mv':
                print aliasname1,aliasname2
            #原始值
            rawx, rawy, rawz, rawmic, rawr = co.computeCorr(bivarRawData[:, idx1], bivarRawData[:, idx2])
            if rawr > 0.8:
                print(aliasname1 + '...' + aliasname2 + '...' + str(rawr) + '\n')
            rawcoef, rawintercept, rawscore = co.linearRegression(rawx, rawy)  # 获取两列数据拟合值
            logInfo += fieldZname[mainCom[i][0]] + "和" + fieldZname[mainCom[i][1]] + "原始数据 线性相关性阈值:" + str(rawr) + ""
            logInfo += " 信息系数阈值:" + str(rawmic) + "</br>"
            #峰峰值
            fengx,fengy,fengz,fengmic,fengr = co.computeCorr(bivarFengData[:,idx1],bivarFengData[:,idx2])
            fengcoef, fengintercept, fengscore = co.linearRegression(fengx, fengy)  # 获取两列数据拟合值
            logInfo += fieldZname[mainCom[i][0]] + "和" + fieldZname[mainCom[i][1]] + "峰峰值数据 线性相关性阈值:" + str(fengr) + ""
            logInfo += " 信息系数阈值:" + str(fengmic) + "</br></br>"
            # 存表
            k = rawcoef
            b = rawintercept
            # coef1  = 0.1
            # intercept1 = -1 * rawintercept / rawcoef
            dists = []
            for j in range(len(rawx)):
                dist = abs(k * rawx[j] - rawy[j] + b) / ((k * k + 1) ** 0.5)
                dists.append(dist)
            mean = np.mean(dists)  # 均值
            std = np.std(dists, ddof=1)  # 无偏标准差
            stat = kstest(dists, 'norm')
            rawdistthre = mean + std
            # 保存相关性过程的系数，jz,rotatespeed,load,activepower,mainfield,mainCom[i-1],,mic,r
            md = models.Bivarvariable.objects.filter(userid=userid, jzname=jzname, aliasname1=mainCom[i][0],
                                                     aliasname2=mainCom[i][1])
            if md.count() != 0:
                models.Bivarvariable.objects.filter(userid=userid, jzname=jzname, aliasname1=mainCom[i][0],
                                                    aliasname2=mainCom[i][1]).update(mic=rawmic, bivarr=rawr,
                                                                                     coef=rawcoef,intercept=rawintercept,score=rawscore,
                                                                                     distthre=rawdistthre,
                                                                                     rotatespeed=rotatespeed, load=load,activepower=activepower,
                                                                                     starttime=startTime,endtime=endTime, datanum=data_num,
                                                                                     fengmic = fengmic,fengr = fengr,fengcoef = fengcoef,
                                                                                     fengintercept = fengintercept,fengscore = fengscore)
            else:
                models.Bivarvariable.objects.create(userid=userid, jzname=jzname, aliasname1=mainCom[i][0],
                                                    aliasname2=mainCom[i][1],
                                                    mic=rawmic, bivarr=rawr, coef=rawcoef, intercept=rawintercept,
                                                    score=rawscore, distthre=rawdistthre,
                                                    rotatespeed=rotatespeed, load=load, activepower=activepower,
                                                    starttime=startTime,endtime=endTime,datanum=data_num,
                                                    fengmic=fengmic, fengr=fengr, fengcoef=fengcoef,
                                                    fengintercept=fengintercept, fengscore=fengscore)
            
            if abs(rawr) < bivar_thre and numNoBicorr == 1:  # 如果没有相关性不展示
                continue;

        logInfo += "相关性阈值计算完毕！</br></br>"
        
        
        
        # print("multi....")
        # multiFields = fields
        # multiData = datamiddle  # osvm.hiveDataTime(multiFields, startTime, endTime, datanum)  # 直接获取原始表中的数据
        # multiTime = datatime
        # multiDateTime = pdt.str2Dt(multiTime)
        # # multiData = pdt.strToFloat(multiData)  # 转成数字
        # multiData = np.array(multiData)
        # multiFieldsIdx = {}  # 变量对应在rawdata中的序号
        # for i in range(len(multiFields)):
        #     multiFieldsIdx[multiFields[i]] = i
        # # 比对字段数组
        # field_data = dict(zip(fields, multiData.transpose().tolist()))
        # mainCom = [x for x in it.combinations(fields, multi_num)]
        # datapair = {}
        # fieldpairs = {}
        #
        # rotatespeed = 0
        # load = 0
        # activepower = 0
        # pathName = "data/"  # model保存路径名称
        # for jzname in jznames:
        #     for fieldCom in mainCom:
        #         fieldpair = ''.join(fieldCom)
        #         modelName = pathName + "train_model_" + jzname
        #         for fiTmp in fieldCom:
        #             modelName += "_" + fiTmp
        #         modelName += ".m"
        #         idx0 = fieldCom[0]
        #         idx1 = fieldCom[1]
        #         multistr = ""
        #         for fc in fieldCom:
        #             multistr += fieldZname[fc] + ','
        #         logInfo += multistr + "svm模型: " + modelName + "已保存</br>"
        #
        #         # 多维度
        #         multiFieldpair = '_'.join(fieldCom)  # 用空格隔开，存放在数据库中
        #         modelName = pathName + "train_model_" + jzname + "_" + multiFieldpair + ".m"
        #         trainSamples, outlierSamples = osvm.filterDataMultiVar(multiData, fieldCom,
        #                                                                multiFieldsIdx)  # 过滤mean-+std的数据
        #         smax, smin = osvm.getSvmMultiVar(trainSamples, outlierSamples, modelName)  # 多维度svm生成clf，存入modelName
        #         #multiScore = osvm.score(outlierSamples, modelName)  # z大于0时，大于50,为类中的点
        #         md = models.Multivarvariable.objects.filter(userid=userid, jzname=jzname, rotatespeed=rotatespeed,
        #                                                     load=load,activepower=activepower, fieldpair=fieldpair)
        #         if md.count() != 0:
        #             md.update(modelname=modelName)
        #         else:
        #             models.Multivarvariable.objects.create(userid=userid, jzname=jzname, rotatespeed=rotatespeed,
        #                                                    load=load,
        #                                                    activepower=activepower, fieldpair=fieldpair,
        #                                                    modelname=modelName)
        #
        # 趋势训练

        
        logInfo += "开始单维度趋势阈值分析......</br>"
        monitTime = datatime
        monitDateime = pdt.str2Dt(monitTime)
        multiData = datamiddle
        # multiData = pdt.strToFloat(multiData)  # 转成数字
        multiData = np.array(multiData)
        multiFields = fields
        
        # 在report中先要进行阈值判断
        print("moniting...")
        rotatespeed = 0  # 转速
        load = 0  # 负荷
        activepower = 0  # 有功功率
        exceThreholds = {}  # 是否超过阈值，或者劣化过快
        datajz = {}
        slopejz = {}
        #timeInterval = monit_period  # 时间间隔 1min
        namepairs = {}
        thre_slope = 0
        factor = 1000  # 斜率值太小，乘以1000,
        for jzname in jznames:
            slopedbs = []
            X_slopedbs = []
            isExce = 0
            for i in range(len(fields)):
                for timeInterval in timeIntervals:
                    datadb, X_slopedb, slopedb = pdt.timeIntervalSlope(monitDateime, multiData[:, i], timeInterval, factor)
                    # slopedb,X_slopedb,timerawdata = pdt.pdtSlope(datatimedata,rawdatas[:,i],timeInterval)
                    min_val, mid_val, max_val, alert_val, mean, std = pdt.meanstd(X_slopedb)
                    jzfield = jzname+'_'+ timeInterval +'_'+ fields[i]
                    zname = fieldZname[fields[i]]
                    logInfo += zname + "趋势模型计算完毕:</br>"
                    logInfo += "趋势阈值：" + str(mid_val) + ", 趋势最小值：" + str(min_val) + ", 最大值: " + str(max_val) + ", 均值: " + str(mean) + ", 方差:" + str(std) +", 周期：" + timeInterval+ " 分钟 <br/><br/>"
                    namepair = [jzname, fields[i], zname, min_val, mid_val, max_val, alert_val, mean, std,
                                thre_slope,timeInterval]
                    namepairs[jzfield] = namepair
                    datajz[jzfield] = datadb
                    slopejz[jzfield] = slopedb
                    md = models.Monitorvariable.objects.filter(userid=userid, jzname=jzname, rotatespeed=rotatespeed,
                                                               load=load,
                                                               activepower=activepower, aliasname=fields[i],
                                                               timeinterval=timeInterval)
                    if md.count() != 0:
                        md.update(min_val=min_val, mid_val=mid_val, max_val=max_val, alert_val=alert_val,mean = mean, std=std)
                    else:
                        models.Monitorvariable.objects.create(userid=userid, jzname=jzname, rotatespeed=rotatespeed,
                                                              load=load,
                                                              activepower=activepower, aliasname=fields[i],
                                                              timeinterval=timeInterval,
                                                              min_val=min_val, mid_val=mid_val, max_val=max_val,
                                                              alert_val=alert_val, mean = mean,std=std)
        logInfo += "趋势计算完成！</br></br>"

        # 将这次训练的结果保存起来
        
        resfields = ''
        for field in fields:
            resfields += field + '/'
        jzname = ''
        for jz in jznames:
            jzname += jz + '/'
        #for timeInterval in timeIntervals:
        md = models.Modelresult.objects.filter(userid=userid, jzname = jzname,monitperiod = monit_period,multinum = multi_num)
        if md.count() != 0:
            md.update(starttime=startTime, endtime=endTime, datanum=data_num,
                      univarfields=resfields, bivarfields=resfields, bivarmainfield=mainField,
                      multifields=resfields, monitfields=resfields,id = 0,multinum = multi_num)
        else:
            models.Modelresult.objects.create(userid=userid, jzname = jzname,starttime=startTime, endtime=endTime, datanum=data_num,
                                              univarfields=resfields, bivarfields=resfields, bivarmainfield=mainField,
                                              multifields=resfields, monitfields=resfields,monitperiod = monit_period,id = 0,multinum =multi_num)
        # svm训练模块
        logInfo += "开始独立森林多维度分析......</br>"
        startTime = "2017-05-06 00:00:00"
        allFields = isof.loopCombine()
        isofName = 'healthModelxxx'
        isof.isof(allFields, startTime, endTime, 1000,isofName)

        logInfo += "独立森林模型计算完毕！</br></br>"
        print("success...")
        num_progress = 1
        logInfo += "所有模型相关计算完成!!!</br>"

        return HttpResponse(
            dumps({}))
    
    else:
        # 获取变量树remove
        treeData, jznames = formInitNew()
        #jzData, fengData, rawData, allxfsData = formInitAllData()
        return render(request, "modeldata.html",
                      {'td': dumps(treeData), 'jznames': dumps(jznames)})

def modelresult(request):
    logger.info("request modelresult view")
    treeData, jzData = formInitNew()
    
    userid = '007'
    jzname = '23/'
    multiVarNum = 2
    activepower = 0
    rotatespeed1 = 0
    rotatespeed2 = 0
    rotatespeed3 = 0
    # 从数据读取训练结果
    md = models.Modelresult.objects.filter(userid=userid, jzname=jzname)
    if md.count() == 0:  # 数据无训练数据，一般情况下不存在
        return
    startTime = md[0].starttime
    endTime = md[0].endtime
    resfields = md[0].univarfields
    monit_period = md[0].monitperiod
    if monit_period == '':
        timeIntervals = ['1']
    else:
        timeIntervals = monit_period.split(',')[:]
        while '' in timeIntervals:
            timeIntervals.remove('')
    
    fields = resfields.split('/')[:]
    fields.pop()
    fields = case_insensitive_sort(fields)  # 先排序
    univar_fields = fields
    bivarFields = fields
    multiFields = fields
    monitFields = fields
    data_num = md[0].datanum
    resjzname = md[0].jzname
    jznames = resjzname.split('/')[:]
    jznames.pop()
    startTime = ''
    
    # modelresult个性化阈值
    bivarFields = fields
    # 获取中文名fieldZname[],标准阈值thre_ground
    univarFields = fields
    fieldZname, categories, thre_ground = rpt.getZname(univarFields)
    
    #获取个性化阈值jzcompare
    jzcompare = rpt.getJzcompare(jznames, univarFields, userid, activepower, rotatespeed1, rotatespeed2, rotatespeed3)
    
    #bivar相关性
    bivarRawDataPairs, bivarRawFieldPairs, bivarFengDataPairs, bivarFengFieldPairs,datamiddle,datatime = rpt.resultBivar(jznames, fields, startTime, endTime, data_num, userid, fieldZname)
    
    #isof独立森林
    isofTime, isofZ = rpt.resultIsof(startTime,endTime)
    
    #趋势分析
    monitNamepairs, monitFields = rpt.resultMonit(jznames, fields, datamiddle, datatime, timeIntervals, fieldZname)
    

    return render(request, "modelresult.html",
                  {'td': dumps(treeData), 'jznames': dumps(jzData),
                   "jznos": jznames, "jzcompare": dumps(jzcompare), "categories": dumps(categories),
                   "threshold_ground": dumps(thre_ground),
                   'rawallpoint': dumps(bivarRawDataPairs), 'bivarRawFieldPair': bivarRawFieldPairs,
                   'bivarRawFieldPairs': dumps(bivarRawFieldPairs),
                   'fengallpoint': dumps(bivarFengDataPairs), 'bivarFengFieldPair': bivarFengFieldPairs,
                   'bivarFengFieldPairs': dumps(bivarFengFieldPairs),
                   # 'multiallpoint': dumps(multiDataPair), 'multiFieldPair': multiFieldPairs,
                   # 'multiFieldPairs': dumps(multiFieldPairs),
                   # 'monitDatas': dumps(monitDatas), 'monitSlopes': dumps(monitSlopes),
                   # "monitIntercepts": dumps(monitIntercepts), 'monitnamepair': monitNamepairs,
                   'timeInterval': timeIntervals,
                   'monitNamepairs': dumps(monitNamepairs),'monitfield': monitFields,
                   # 'monitRSlopes': dumps(monitRSlopes),
                   # 'monitFields': dumps(monitFields), 'monitSegmentDatas': dumps(monitSegmentDatas),
                   # 'monitSegmentData': monitSegmentDatas
                   })



# 返回机组jzData,峰峰值fengData,原始数据rawData,倍频allxfsData
def formInitAllData():
    # 获取机组数据  jzData
    jzArray = []
    def getJzChildren(id=0):
        jArray = []
        for obj in jzArray:
            if obj["parentid"] == id:
                x = getJzChildren(obj["id"])
                if len(x) != 0:
                    jArray.append({"nodeid": obj["id"], "text": obj["name"], "alias": obj["aliasn"], "nodes": x})
                else:
                    jArray.append({"nodeid": obj["id"], "text": obj["name"], "alias": obj["aliasn"]})
        
        return jArray
    
    jz = models.Jzvariable.objects.all()
    for t in jz:
        jnode = {'id': t.jid, 'parentid': t.parentid, 'name': t.jzname, 'aliasn': t.aliasname}
        jzArray.append(jnode)
    jzData = getJzChildren()
    
    # 获取峰峰值表变量，fengData
    treeArray = []
    def getChildren(id=0):
        jsonArray = []
        for obj in treeArray:
            if obj["parentid"] == id:
                x = getChildren(obj["id"])
                if len(x) != 0:
                    jsonArray.append({"nodeid": obj["id"], "text": obj["name"], "alias": obj["aliasn"], "nodes": x})
                else:
                    jsonArray.append({"nodeid": obj["id"], "text": obj["name"], "alias": obj["aliasn"]})
        
        return jsonArray
    
    treeview = models.Middlevariable.objects.all()
    for t in treeview:
        comments = t.comments
        if t.fieldname == 'gettime':
            continue
        treeNode = {'id': t.id, 'parentid': t.parentid, 'name': comments, 'aliasn': t.fieldname}
        treeArray.append(treeNode)
    fengData = getChildren()

    # 获取原始值变量，rawData
    rawArray = []
    def getRawChildren(id=0):
        rawArraytmp = []
        for obj in rawArray:
            if obj["parentid"] == id:
                x = getRawChildren(obj["id"])
                if len(x) != 0:
                    rawArraytmp.append(
                        {"nodeid": obj["id"], "text": obj["name"], "alias": obj["aliasn"], "fieldtype": obj["fieldtype"], "nodes": x})
                else:
                    rawArraytmp.append({"nodeid": obj["id"], "text": obj["name"], "alias": obj["aliasn"], "fieldtype": obj["fieldtype"], })
        return rawArraytmp
    
    rawtreeview = models.Variabletype.objects.all()
    for t in rawtreeview:
        comments = t.comments
        if t.fieldname == 'gettime':
            continue
        treeNode = {'id': t.id, 'parentid': t.parentid, 'name': comments, 'aliasn': t.fieldname, 'fieldtype': t.fieldtype}
        rawArray.append(treeNode)
    rawData = getRawChildren()

    # 获取倍频变量 allxfsData
    allxfsArray = []
    def getallxfsChildren(id=0):
        jsonArray = []
        for obj in allxfsArray:
            if obj["parentid"] == id:
                x = getChildren(obj["id"])
                if len(x) != 0:
                    jsonArray.append({"nodeid": obj["id"], "text": obj["name"], "alias": obj["aliasn"], "nodes": x})
                else:
                    jsonArray.append({"nodeid": obj["id"], "text": obj["name"], "alias": obj["aliasn"]})
        
        return jsonArray
    
    allxfstreeview = models.Allxfsvariable.objects.all()
    for t in allxfstreeview:
        comments = t.comments
        if t.fieldname == 'gettime':
            continue
        # comments = comments[:-2]
        # comments = comments.replace('_','')
        treeNode = {'id': t.id, 'parentid': t.parentid, 'name': comments, 'aliasn': t.fieldname}
        allxfsArray.append(treeNode)
    allxfsData = getallxfsChildren()
    
    return jzData, fengData, rawData, allxfsData

def myindexPost(request):
    if request.is_ajax() and request.method == 'POST':  # 是否为post请求
        # 根据选择机组，时间，条件进行数据查询，比对，显示结果
        print request.POST.get("jz")

        jznames = eval(request.POST.get('jz'))
        fields = eval(request.POST.get('field'))
        param = {}
    return

#
# def myindex(request):
#     jzData,fengData,rawData,allxfsData = formInitAllData()
#     # 返回机组jzData,峰峰值fengData,原始数据rawData,倍频allxfsData
#     return render(request, "myindex.html",
#         {
#             # 'jzData': dumps(jzData),
#             # 'fengData': dumps(fengData),
#             # 'rawData': dumps(rawData),
#             # 'allxfsData': dumps(allxfsData),
#             'jzData': jzData,
#             'fengData': fengData,
#             'rawData': rawData,
#             'allxfsData': allxfsData,
#         }
#     )


def configuration(request):

    return render(request, 'configuration.html')


# def getDataJson(request):
#     # print request.method,request.GET
#     # print u'field' in request.GET
#     # print request.GET['field']
#     data = []
#     if request.method == 'GET' and 'field' in request.GET:
#         try:
#             fields2line = request.GET['field']
#             # print fields2line
#             vcs = models.Xfsvariable.objects.all()
#             # vcs = models.Middlevariable.objects.all()
#
#             fieldname_meaning = {}
#             fieldmeaning_name = {}
#
#             for vc in vcs:
#                 fieldname_meaning[vc.fieldname] = vc.comments
#                 fieldmeaning_name[vc.comments] = vc.fieldname
#
#             basicfield = ['获取时间']
#             fields2query = basicfield + [fields2line]
#
#             sql_fields = ','.join([fieldmeaning_name[f] for f in fields2query])
#             # sql = "SELECT " + sql_fields + " FROM hd_middledata_all_xfs_ffz_mean_tmp where y='2017' and m between '05' and '07'"
#             # sql = "SELECT " + sql_fields + " FROM hd_middledata_all_pafs_ffz_mean_tmp where y='2017' and m='05' and d between '06' and '31'"
#             sql = "SELECT " + sql_fields + " FROM hd_middledata_all_xfs_ffz_mean_tmp where y='2017' and m='05' and d='06'"
#             # sql = "SELECT " + sql_fields + " FROM hd_premiddledata_ffz_mean_ext_orc where y='2017' and m='05' and d='06' limit 100"
#
#             hc = PrestoConn()
#             hc.getConn()
#             for i in hc.select(sql):
#                 # gettime.append(time.mktime(time.strptime(i[0], '%Y-%m-%d %H:%M:%S')) * 1000 - 8 * 60 * 60 * 1000)
#                 data.append([time.mktime(time.strptime(i[0], '%Y-%m-%d %H:%M:%S.%f')) * 1000 - 8 * 60 * 60 * 1000, i[1]])
#         finally:
#             pass
#     return HttpResponse(dumps(data), content_type='application/json')


def realtimemonitor(request):
    vcs = models.Xfsvariable.objects.all()
    fieldname_meaning = {}
    fieldmeaning_name = {}
    for vc in vcs:
        fieldname_meaning[vc.fieldname] = vc.comments
        fieldmeaning_name[vc.comments] = vc.fieldname
    # fields2line = ['上导X摆度峰峰值均值', '上导Y摆度峰峰值最大值', '上导Y摆度峰峰值均值', '上导X摆度一倍频']
    fields2line = fieldname_meaning.values()[:4]
    # fields2line = ['上导X摆度峰峰值均值', '上导Y摆度峰峰值最大值', '上导Y摆度峰峰值均值', '上导X摆度一倍频']
    # fields2line = ['上导X摆度峰峰值均值']
    return render(request, 'scaleRealtime.html', {'fields': dumps(fields2line)})

def lines(request):
    # vcs = models.Xfsvariable.objects.all()
    vcs = models.Middlevariable.objects.all()

    fieldname_meaning = {}
    fieldmeaning_name = {}

    for vc in vcs:
        fieldname_meaning[vc.fieldname] = vc.comments
        fieldmeaning_name[vc.comments] = vc.fieldname
    # fields2line = ['上导X摆度峰峰值均值', '上导Y摆度峰峰值最大值', '上导Y摆度峰峰值均值', '上导X摆度一倍频']
    fields2line = fieldname_meaning.values()[:8]
    # print fields2line
    if '获取时间' in fields2line:
        fields2line.remove('获取时间')

    basicfield = ['获取时间']
    fields2query = basicfield + fields2line

    sql_fields = ','.join([fieldmeaning_name[f] for f in fields2query])
    # sql = "SELECT " + sql_fields + " FROM hd_middledata_all_xfs_ffz_mean_tmp where y='2017' and m='05' and d='06' limit 2000"
    sql = "SELECT " + sql_fields + " FROM hd_premiddledata_ffz_mean_ext_orc where y='2017' and m='05' and d='06'"

    hc = HiveConn()
    hc.getConn()
    gettime = []
    datalist = []
    for i in hc.select(sql):
        # print i
        # gettime.append(time.mktime(time.strptime(i[0], '%Y-%m-%d %H:%M:%S')) * 1000 - 8 * 60 * 60 * 1000)
        gettime.append(time.mktime(time.strptime(i[0], '%Y-%m-%d %H:%M:%S.%f')) * 1000 - 8 * 60 * 60 * 1000)
        # gettime.append(i[0])
        datalist.append(i[1:])
    dataarray = np.array(datalist)

    # titletext = '-'.join([f for f in fields2line])
    titletext = '实时监控'
    legenddata = fields2line
    xAxisdata = gettime
    seriesdata = []
    ll = len(fields2line)
    for i in range(ll):
        seriesdata.append(dataarray[:, i].tolist())
    # seriesdata.append({'name': fields2line[i], 'type': 'line', 'visible': 'true', 'data': dataarray[:, i].tolist()})
    # seriesdata = [{'name':'邮件营销','type':'line','stack': '总量','data': [120, 132, 101, 134, 90, 230, 210]},{'name':'联盟广告','type':'line','stack': '总量','data': [120, 132, 101, 134, 90, 230, 210]}]

    return render(request, 'realtimemonitor.html',
                  {'titletext': dumps(titletext), 'legenddata': dumps(legenddata), 'xAxisdata': dumps(xAxisdata),
                   'seriesdata': dumps(seriesdata)})

def monitor_realtime(request):
    vcs = models.Xfsvariable.objects.all()
    fieldname_meaning = {}
    fieldmeaning_name = {}
    for vc in vcs:
        fieldname_meaning[vc.fieldname] = vc.comments
        fieldmeaning_name[vc.comments] = vc.fieldname
    # fields2line = ['上导X摆度峰峰值均值', '上导Y摆度峰峰值最大值', '上导Y摆度峰峰值均值', '上导X摆度一倍频']
    fields2line = fieldname_meaning.values()[:3]
    # fields2line = ['上导X摆度峰峰值均值', '上导Y摆度峰峰值最大值', '上导Y摆度峰峰值均值', '上导X摆度一倍频']
    # fields2line = ['上导X摆度峰峰值均值']
    # return render(request, 'scaleRealtime.html', {'fields': dumps(fields2line)})

    # 获取变量树
    treeData, jzData = formInitNew()

    # vcs = models.Xfsvariable.objects.all()
    vcs = models.Middlevariable.objects.all()

    fieldname_meaning = {}
    fieldmeaning_name = {}

    for vc in vcs:
        fieldname_meaning[vc.fieldname] = vc.comments
        fieldmeaning_name[vc.comments] = vc.fieldname
    # fields2line = ['上导X摆度峰峰值均值', '上导Y摆度峰峰值最大值', '上导Y摆度峰峰值均值', '上导X摆度一倍频']
    fields2line1 = fieldname_meaning.values()[:8]
    # print fields2line
    if '获取时间' in fields2line1:
        fields2line1.remove('获取时间')

    basicfield = ['获取时间']
    fields2query = basicfield + fields2line1

    sql_fields = ','.join([fieldmeaning_name[f] for f in fields2query])
    # sql = "SELECT " + sql_fields + " FROM hd_middledata_all_xfs_ffz_mean_tmp where y='2017' and m='05' and d='06' limit 2000"
    sql = "SELECT " + sql_fields + " FROM hd_premiddledata_ffz_mean_ext_orc where y='2017' and m='05' and d='06'"

    hc = HiveConn()
    hc.getConn()
    gettime = []
    datalist = []
    for i in hc.select(sql):
        # print i
        # gettime.append(time.mktime(time.strptime(i[0], '%Y-%m-%d %H:%M:%S')) * 1000 - 8 * 60 * 60 * 1000)
        gettime.append(time.mktime(time.strptime(i[0], '%Y-%m-%d %H:%M:%S.%f')) * 1000 - 8 * 60 * 60 * 1000)
        # gettime.append(i[0])
        datalist.append(i[1:])
    dataarray = np.array(datalist)

    # titletext = '-'.join([f for f in fields2line])
    titletext = '实时监控'
    legenddata = fields2line1
    xAxisdata = gettime
    seriesdata = []
    ll = len(fields2line1)
    for i in range(ll):
        seriesdata.append(dataarray[:, i].tolist())

    return render(request, 'monitor_realtime.html', {'td': dumps(treeData), 'jznames': dumps(jzData),'fields': dumps(fields2line),'titletext': dumps(titletext), 'legenddata': dumps(legenddata), 'xAxisdata': dumps(xAxisdata),
                                                     'seriesdata': dumps(seriesdata)})

#实时更新进度

def progressRealtime(request):

    return render(request, 'progressRealtime.html')



# 倍频实时更新
xf_num = 0
df = ''
gettimes = ''
x_index = ''
fields = ''

# 频谱监控
def xf_page(request):
    global df, gettimes, x_index, fields
    df, x_index, gettimes, fields = getXFs()

    # print health_index()
    return


# def getXfsData(request):
#     global xf_num, df, gettimes, x_index, fields
#     if xf_num < df.shape[0]:
#         # print xf_num
#         xf_num += 1
#     else:
#         xf_num = 1
#     return JsonResponse(
#         {'data': dumps(df[xf_num - 1, :, :].tolist()), 'gettime': gettimes[xf_num - 1], 'x_index': x_index,
#          'fields': fields}, safe=False)
#




def myindexPost(request):
    if request.is_ajax() and request.method == 'POST':  # 是否为post请求
        # 根据选择机组，时间，条件进行数据查询，比对，显示结果
        print request.POST.get("jz")
        
        jznames = eval(request.POST.get('jz'))
        fields = eval(request.POST.get('field'))
        param = {}
        #
    return

#全局变量,post采用传进来的参数，否则采用默认的，主要list用深度拷贝
jznames = ['23']
rawFields = ["shangx","shangy"]
fengFields = ["shangx_ffz","shangy_ffz"]
xfsFields = ["shangx_xfs","shangy_xfs"]
startTime = "2017-05-06 00:00:00"
endTime = "2017-05-06 23:00:00"
dataNum = 1000
fuhe_end = 0
fuhe_start = 0
shuitou_start = 0
shuitou_end = 0
monitPeriod = 1#趋势采样周期
multiVarNum = 2#svm多维度个数
#默认全局变量,不会改变，
jznamesDef = ['23']
rawFieldsDef = ["shangx","shangy"]
fengFieldsDef = ["shangx_ffz","shangy_ffz"]
xfsFieldsDef = ["shangx_xfs","shangy_xfs"]
startTimeDef = "2017-05-06 00:00:00"
endTimeDef = "2017-05-06 23:00:00"
monitPeriodDef = 1#趋势采样周期






#原始值raw
raw_num = 512*10
raw_count = 0
raw_length = 512*3
postRawData = []
rawTime = []
def sendRawData(request):#峰峰值初始化获取
    global jznames, rawFields, startTime, endTime, dataNum
    global raw_num,raw_count,raw_length,postRawData,rawTime
    raw_count = raw_length
    if request.is_ajax() and request.method == 'POST':
        rawFields = eval(request.POST.get('rawFields'))
    else:
        rawFields = copy.deepcopy(rawFieldsDef)
    rawTime,postRawData = rpt.getRawData(jznames, rawFields, startTime, endTime, raw_num)
    postRawData = postRawData.tolist()
    postRawDataList = postRawData[0:raw_length]
    rawTimeList = rawTime[0:raw_length]
    return JsonResponse({'postRawData':postRawDataList,'rawTime':rawTimeList})#传512倍数个点

def getRawData(request):#初始化获取之后每秒发送数据
    global raw_count, raw_length,postRawData,rawTime
    if raw_count < len(rawTime)-2:
        raw_count += 1
    else:
        raw_count = 1
    return JsonResponse(
        {'raw_time': rawTime[raw_count], 'raw_data': postRawData[raw_count]}, safe=False)

#峰峰值feng
feng_num = 1000
feng_count = 0
feng_length = 100
postFengData = []
fengTime = []
def sendFengData(request):#峰峰值初始化获取
    #获取变量
    global jznames, fengFields, startTime, endTime, dataNum
    global feng_num ,feng_count,feng_length ,postFengData ,fengTime
    feng_count = feng_length
    if request.is_ajax() and request.method == 'POST':
        fengFields = eval(request.POST.get('fengFields'))
    else:
        fengFields = copy.deepcopy(fengFieldsDef)
    fengTime,postFengData = rpt.getFengData(jznames, fengFields, startTime, endTime, feng_num)
    postFengData = postFengData.tolist();
    postFengDataList = postFengData[0:feng_length]
    fengTimeList = fengTime[0:feng_length]
    return JsonResponse({'postFengData':postFengDataList,'fengTime':fengTimeList})
def getFengData(request):#初始化获取之后每秒发送数据
    global feng_num, feng_count, feng_length, postFengData, fengTime
    if feng_count <len(fengTime)-2:
        feng_count += 1
    else:
        feng_count = 1
    return JsonResponse(
        {'feng_time':fengTime[feng_count],'feng_data':postFengData[feng_count]},safe = False)

#倍频值xfs
xfs_num = 100
xfs_count = 0
xfs_length = 100
postXfsData = []
xfsTime = []
def sendXfsData(request):#频谱初始化获取
    global jznames,xfsFields,startTime,endTime,dataNum
    global xfs_num,xfs_count,xfs_length,postXfsData,xfsTime

    if request.is_ajax() and request.method == 'POST':
        xfsFields = eval(request.POST.get('xfsFields'))
    else:
        xfsFields =  copy.deepcopy(xfsFieldsDef)
    xfsTime,postXfsData = rpt.getXfsData(xfsFields, startTime, endTime, xfs_num)
    postXfsData = postXfsData.tolist()
    postXfsDataList = postXfsData[0:xfs_length]
    xfsTimeList = xfsTime[0:xfs_length]

    return JsonResponse({'postXfsData':postXfsDataList[xfs_count],"xfsTime":xfsTimeList[xfs_count]})
#
def getXfsData(request):#初始化获取之后每秒发送数据
    global xfs_num,xfs_count,xfs_length,postXfsData,xfsTime
    if len(xfsTime) == 0:
        return JsonResponse(
            {'postXfsData': postXfsData, "xfsTime": xfsTime}, safe=False)
    if xfs_count < len(xfsTime)-2:
        xfs_count += 1
    else:
        xfs_count = 1

    return JsonResponse(
        {'postXfsData':postXfsData[xfs_count],"xfsTime":xfsTime[xfs_count]}, safe=False)


#健康度isof
isof_num = 1000
isof_count = 0
isof_length = 30
isof_times = []
isof_z = []

def sendIsofData(request):#健康值初始化全部
    global startTime, endTime, dataNum
    global isof_times, isof_z, isof_num,isof_count,isof_length
    isof_length = 100
    isof_count = isof_length
    isof_times, isof_z = hi.health_index(startTime, endTime, isof_num)
    timelist = isof_times[0:isof_length]
    zlist = isof_z[0:isof_length]
    zlist = zlist.tolist()
    return JsonResponse(
        {'isof_time': timelist, 'isof_z': zlist}, safe=False)


def getIsofData(request):#初始化获取之后每秒发送数据
    global isof_times,isof_z,isof_count
    if len(isof_times)==0:
        return JsonResponse(
            {'isof_time': isof_times, 'isof_z': isof_z}, safe=False)
    if isof_count < len(isof_times):
        isof_count += 1
    else:
        isof_count = 1
    return JsonResponse(
        {'isof_time':isof_times[isof_count],'isof_z':isof_z[isof_count]},safe = False)

def setGlobalParam(fm):
    global startTime, endTime, fuhe_start, fuhe_end, shuitou_start, shuitou_end, monitPeriod, multiVarNum
    if fm[0]['value'] != '':
        fuhe_start = fm[0]['value']
    if fm[1]['value']  != '':
        fuhe_end = fm[1]['value']
    if fm[2]['value'] != '':
        shuitou_start = fm[2]['value']
    if fm[3]['value'] != '':
        shuitou_end = fm[3]['value']
    if fm[4]['value'] != '':
        startTime = fm[4]['value']
    if fm[5]['value'] != '':
        endTime = fm[5]['value']
    if fm[6]['value'] != '':
        monitPeriod = fm[6]['value']
    if fm[7]['value']  != '':
        multiVarNum = fm[7]['value']
    return

def myindex(request):
    global jznames,startTime,endTime,fuhe_start,fuhe_end,shuitou_start,shuitou_end,monitPeriod,multiVarNum
    global jznamesDef, startTimeDef, endTimeDef, monitPeriodDef
    print "myindex..."
    if request.is_ajax() and request.method == 'POST':  # 是否为post请求
        globalParam = eval(request.POST.get('golable'))
        jznames = globalParam['data']
        fm = eval(globalParam['fm'])
        setGlobalParam(fm)
        print startTime,endTime
        return JsonResponse(
            {})
    else:
        jzData, fengData, rawData, allxfsData = formInitAllData()  # 初始化数据

        startTime = startTimeDef
        endTime = endTimeDef
        monitPeriod = monitPeriodDef

        global df, gettimes, x_index, fields
        df, x_index, gettimes, fields = getXFs()
        return render(request, "myindex.html", {
            'jzData': jzData,
            'fengData': fengData,
            'rawData': rawData,
            'allxfsData': allxfsData,
        })
        # xfsTime,postXfsData = rpt.getXfsData(xfsFields, startTime, endTime, dataNum)
        #
        # rawTime,postRawData = rpt.getRawData(jznames, rawFields, startTime, endTime, dataNum)
        # fengTime,postFengData = rpt.getFengData(jznames, fengFields, startTime, endTime, dataNum)

    # 读取数据
    
    # 返回机组jzData,峰峰值fengData,原始数据rawData,倍频allxfsData
		

