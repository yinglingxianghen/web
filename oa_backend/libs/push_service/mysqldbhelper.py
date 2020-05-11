"""
function：MysqldbHelper 数据库操作类
describe：mysql数据库基本操作封装
date：20171127
author：gjf
version:1.09
"""
import pymysql
import requests
import logging
logger = logging.getLogger('django')
class MysqldbHelper:
	"""
	function:__init__
	describe:构造函数初始连接数据库
	param: string @dbhost ip或域名
	param: string @dbuser 用户名
	param: string @dbpwd 密码
	param: string @dbname 库名
	param: int @dbport 端口
	return: bool
	"""
	def __init__(self, dbhost, dbuser, dbpwd, dbname, dbport):
		try:
			# 打开数据库连接
			self.db = pymysql.connect(host=dbhost, user=dbuser, password=dbpwd, database=dbname, port=dbport,
									  charset='utf8')
			# 使用cursor()方法获取操作游标
			self.cursor = self.db.cursor()
			logger.info('连接数据库成功')
		except Exception as e:
			logger.error(e)
	"""
	function:lastrowid
	describe:获取最近执行的sql id
	return: int
	"""
	def lastrowid(self):
		return self.cursor.lastrowid

	"""
	function:select
	describe:数据查询操作
	param: string @sql sql语句
	return: bool or array
	"""
	def select(self, sql):
		logger.info(sql)
		try:
			# 执行SQL语句
			self.cursor.execute(sql)
			# 获取所有记录列表
			index = self.cursor.description
			results = self.cursor.fetchall()
			result = []
			for key in results:
				row = {}
				t = False
				for k in range(len(index)):
					row[index[k][0]] = key[k]
				for kk in row:
					if row[kk] != None:
						t = True
				if t == True:
					result.append(row)
			if result:
				return result
			else:
				return False
		except Exception as e:
			# traceback.print_exc() #排查错误
			logger.error(e)
			return False
	"""
	function:add_up_de
	describe:新增-修改-删除，sql执行不提交
	param: string @sql sql语句
	return: bool
	"""
	def add_up_de(self, sql):
		logger.info(sql)
		try:
			# 执行SQL语句
			self.cursor.execute(sql)
			return True
		except Exception as e:
			logger.error(e)
			return False
	"""
	function:rollback 回滚
	describe:回滚操作
	return: bool
	"""
	def rollback(self):
		try:
			self.db.rollback()
			return True
		except Exception as e:
			logger.error(e)
			return False

	"""
	function:commit 提交
	describe:提交操作
	return: bool
	"""
	def commit(self):
		try:
			# 提交到数据库
			self.db.commit()
			return True
		except Exception as e:
			logger.error(e)
			self.db.rollback()
			return False

	"""
	function:add_up_de_commit 
	describe:执行并提交
	return: bool
	"""
	def add_up_de_commit(self, sql):
		logger.info(sql)
		try:
			# 执行SQL语句
			self.cursor.execute(sql)
			# 提交到数据库执行
			self.db.commit()
			return True
		except Exception as e:
			# 发生错误时回滚
			self.db.rollback()
			logger.error(e)
			return False

