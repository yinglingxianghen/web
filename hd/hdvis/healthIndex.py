#coding=utf-8
"""
    26/11/2017,18:06,2017
    BY DoraZhang
"""

import sys

reload(sys)
sys.setdefaultencoding('utf-8')

from prestoConn import *
from sklearn.externals import joblib
import models
import report as rpt
import numpy as np
def health_index(startTime,endTime,dataNum,isofName='healthModelxxx'):#测试
    x = models.Healthmodel.objects.order_by('-id')
    zeroline = x[0].minvalue
    hundredline = x[0].maxvalue
    fl = 'shangx_ffz,shangy_ffz,xiax_ffz,xiay_ffz,shuix_ffz,shuiy_ffz,shangjjx_ffz,shangjjy_ffz,shangjjz_ffz,dingjjx_ffz,dingjjy_ffz,xiajjx_ffz,xiajjy_ffz,xiajjz_ffz,dinggx_ffz,dinggy_ffz,dinggz_ffz,dingzh1_ffz,dingzh2_ffz,dingzh3_ffz,dingzv1_ffz,dingzv2_ffz,dingzv3_ffz,ylmddg_ffz,ylmdwy_ffz,ylmdwk_ffz,ylmdshang_ffz,ylmdxia_ffz,wkyc_mv,bqfs_mv,active_power_mv,reactive_power_mv,vane_open_mv,backup_mv,waterhead_mv,exc_current_mv,exc_voltage_mv,zs_mv,flow_mv'
    sql = rpt.getSql('hd_premiddledata_ffz_mean_ext_orc',fl,startTime,endTime,dataNum)
    print sql
    hc = PrestoConn()
    hc.getConn()
    gettime = []
    datalist = []
    for i in hc.select(sql):
        gettime.append(i[0])
        datalist.append(i[1:])
    X = np.array(datalist)

    clf = joblib.load(isofName)
    y_pred = clf.decision_function(X)
    z = (y_pred-zeroline)/(hundredline-zeroline)
    return gettime,z#z<0.1不健康