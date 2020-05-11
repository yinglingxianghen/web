# -*- coding: utf-8 -*-

from prestoConn import *

import numpy as np

from sklearn.ensemble import IsolationForest
from sklearn.externals import joblib
import report as rpt
def hiveData(sql):
	hc = PrestoConn()
	hc.getConn()
	return hc.select(sql)

def isof(fields,startTime,endTime,dataNum,isofName):
	isofField = fields
	dbName = 'hd_premiddledata_ffz_mean_ext_orc'
	sql = rpt.getSql(dbName,isofField,startTime,endTime,dataNum)
	#sql = "select " + fields + " from hd_premiddledata_ffz_mean_ext_orc where y='2017' and m='05' and d between '06' and '08'"
	print sql
	sqldata = hiveData(sql)
	
	dataResults = []
	for dataFrame in sqldata:
		dataResults.append(dataFrame[1:])

	X = np.array(dataResults)
	n_samples = dataNum
	outliers_fraction = 0.1
	clf = IsolationForest(max_samples=n_samples, contamination=outliers_fraction, random_state=None)

	clf.fit(X)
	joblib.dump(clf, isofName)
	# scores_pred = clf.decision_function(X)
	
def loopCombine():
	fl = 'shangx_ffz,shangy_ffz,xiax_ffz,xiay_ffz,shuix_ffz,shuiy_ffz,shangjjx_ffz,shangjjy_ffz,shangjjz_ffz,dingjjx_ffz,dingjjy_ffz,xiajjx_ffz,xiajjy_ffz,xiajjz_ffz,dinggx_ffz,dinggy_ffz,dinggz_ffz,dingzh1_ffz,dingzh2_ffz,dingzh3_ffz,dingzv1_ffz,dingzv2_ffz,dingzv3_ffz,ylmddg_ffz,ylmdwy_ffz,ylmdwk_ffz,ylmdshang_ffz,ylmdxia_ffz,wkyc_mv,bqfs_mv,active_power_mv,reactive_power_mv,vane_open_mv,backup_mv,waterhead_mv,exc_current_mv,exc_voltage_mv,zs_mv,flow_mv'
	# BivarFields	= fl.split(',')
	# allbf = it.combinations(BivarFields, 2)
	# for bf in allbf:
	# 	fields = ','.join(bf)
	# 	dbscan(fields)	
	return fl
if __name__ == '__main__':
	fl = 'shangx_ffz,shangy_ffz,xiax_ffz,xiay_ffz,shuix_ffz,shuiy_ffz,shangjjx_ffz,shangjjy_ffz,shangjjz_ffz,dingjjx_ffz,dingjjy_ffz,xiajjx_ffz,xiajjy_ffz,xiajjz_ffz,dinggx_ffz,dinggy_ffz,dinggz_ffz,dingzh1_ffz,dingzh2_ffz,dingzh3_ffz,dingzv1_ffz,dingzv2_ffz,dingzv3_ffz,ylmddg_ffz,ylmdwy_ffz,ylmdwk_ffz,ylmdshang_ffz,ylmdxia_ffz,wkyc_mv,bqfs_mv,active_power_mv,reactive_power_mv,vane_open_mv,backup_mv,waterhead_mv,exc_current_mv,exc_voltage_mv,zs_mv,flow_mv'
	isof(fl)

