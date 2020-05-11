# coding=utf-8

import happybase
import time
from datetime import datetime
from django.conf import settings

def string2timestamp(strValue):  
    try:
    	if(len(strValue)==19):
    		d = datetime.strptime(strValue, "%Y-%m-%d %H:%M:%S")
    	else:
    		d = datetime.strptime(strValue, "%Y-%m-%d %H:%M:%S.%f")       
        t = d.timetuple()  
        timeStamp = int(time.mktime(t))  
        timeStamp = int(str(timeStamp) + str("%06d" % d.microsecond))/1000 
        return timeStamp  
    except ValueError as e:  
        print e  

def timestamp2string(timeStamp):  
    try:  
        d = datetime.fromtimestamp(timeStamp)  
        strtime = d.strftime("%Y-%m-%d %H:%M:%S.%f")  
        # 2015-08-28 16:43:37.283000'  
        return strtime  
    except Exception as e:  
        print e  
        return ''


class HbaseConnection():
	def __init__(self,host=settings.HBASE_CONF['HOST']):
		self.connection = happybase.Connection(host)
		
	def get_tables(self):
		self.connection.open()
		tables = self.connection.tables()
		self.connection.close()
		return tables

	# 返回距离timeStamp最近的后一条记录
	def get_next_data(self,tablename,columns,timeStamp):
		self.connection.open()
		table = self.connection.table(tablename)

		timeStamp = timeStamp / 1000.0
		strtime = timestamp2string(timeStamp)
		scan = table.scan(row_start=strtime,columns=[columns],limit=1)
		for key,data in scan:
			x = string2timestamp(key)
			y = int(data[columns])
		self.connection.close()	
		return x,y


	def get_init_data(self,tablename,columns,limit):
		self.connection.open()
		table = self.connection.table(tablename)

		scan = table.scan(columns=[columns],limit=limit)
		data = []
		for key,value in scan:
			x = string2timestamp(key)
			y = int(value[columns])
			data.append([x,y])
		self.connection.close()
		return data
 
# 根据row_key读取一行
# row = table.row(b'2017-07-16 07:18:34')
# print row[b'bd:shangx']

	


