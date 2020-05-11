# __author__ = itsneo1990
import datetime

import pymysql

from libs.datetimes import datetime_delta, date_to_timestamp, datetime_to_timestamp

# 频道转换
CHANGE_MAP = {-1: -1, 0: 6, 1: 1, 2: 2, 3: 3, 4: 4, 5: 5, 7: 7, 8: 8}


class InquiresFetcher(object):
    """获取咨询量worker"""

    def __init__(self, host="", user="", password="", database="kf", port=3306, charset="utf8"):
        self.db = pymysql.connect(host=host, user=user, password=password, database=database, port=port,
                                  charset=charset)
        self.cursor = self.db.cursor()

    def _fetch_data(self, from_time, to_time):
        params = {
            "from_time": int(from_time),
            "to_time": int(to_time)
        }
        sql = "SELECT siteid, entrance, count(*) FROM t2d_chatscene " \
              "WHERE starttime > {from_time} AND starttime < {to_time} GROUP BY siteid, entrance".format(**params)
        self.cursor.execute(sql)
        data = self.cursor.fetchall()
        for line in data:
            line = list(line)
            if not line[1] in CHANGE_MAP.keys():
                continue
            line[1] = CHANGE_MAP[line[1]]
        return data

    def fetch_yesterday(self):
        """获取昨天的咨询量"""
        today = datetime.date.today()
        today_timestamp = date_to_timestamp(today)
        yesterday_timestamp = date_to_timestamp(datetime_delta(today, days=-1))
        return self._fetch_data(from_time=yesterday_timestamp, to_time=today_timestamp)

    def fetch_today(self):
        """获取今天的咨询量"""
        today = datetime.date.today()
        today_timestamp = date_to_timestamp(today)
        now_timestamp = datetime_to_timestamp(datetime.datetime.now())
        return self._fetch_data(from_time=today_timestamp, to_time=now_timestamp)

    def fetch_date(self, date):
        """获取指定日期的咨询量"""
        date_timestamp = date_to_timestamp(date)
        next_date_timestamp = date_to_timestamp(datetime_delta(date, days=1))
        return self._fetch_data(from_time=date_timestamp, to_time=next_date_timestamp)
