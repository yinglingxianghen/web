# __author__ = itsneo1990

import logging
from datetime import date

from celery import shared_task
from django.db.models import Count, QuerySet
from pymysql import MySQLError

from applications.data_manage.models import InquiriesData, OnlineClientData, OnlineProductData
from applications.production_manage.models import DataBaseInfo
from applications.workorder_manage.models import OpenStationManage, StationInfo
from ldap_server.configs import STATION_OFFICAL
from libs.datetimes import datetime_delta, dates_during, str_to_date
from libs.hash import decrypt
from libs.inquires.inquires_db import InquiresFetcher

logger = logging.getLogger(__name__)


@shared_task
def fetch_inquires():
    """celery任务：更新咨询量"""
    logger.info("start fetch inquires data")
    manager = InquiresFetcherManager()
    manager.update_inquires()
    logger.info("fetch inquires data complete")


@shared_task
def history_builder():
    """celery任务：生成历史记录"""
    logging.info("online client info build start")
    client_history_builder = OnlineClientFetcher()
    client_history_builder.update_online_client()
    logging.info("online product info build start")
    product_history_builder = OnlineProductFetcher()
    product_history_builder.update_online_product()
    logging.info("all build complete")


class InquiresFetcherManager(object):
    """该类不负责咨询量查询的过程，只负责总体的调度。执行咨询量查询的某些具体任务时，应尽量在此类中实现"""
    def __init__(self):
        db_info = DataBaseInfo.objects.filter(db_name="kf")
        self.db_list = db_info.values_list("db_address", "db_port", "db_username", "db_pwd").distinct()
        self.today = date.today()
        self.yesterday = datetime_delta(self.today, days=-1)

    def _fetch_data(self, which):
        """获取数据，传入today或者yesterday"""
        result = {}
        for host, port, user, password in self.db_list:
            try:
                fetcher = InquiresFetcher(host=host, port=int(port), user=user, password=decrypt(password))
            except MySQLError as err:
                logger.warning(err)
                continue
            data = getattr(fetcher, "fetch_" + which)()
            for site_id, channel, num in data:
                result.setdefault(site_id, {})
                result[site_id].setdefault(channel, 0)
                result[site_id][channel] += num
            del fetcher
        return result

    def fetch_history(self, from_date, to_date):
        """获取指定时间段内的咨询量
        TODO：单独封装成一个自定义命令，类似 python manage.py fetch_inquires ### ###
        """
        for host, port, user, password in self.db_list:
            try:
                fetcher = InquiresFetcher(host=host, port=int(port), user=user, password=decrypt(password))
            except MySQLError as err:
                logger.warning(err)
                continue
            dates = dates_during(from_date=from_date, to_date=to_date)
            for each in dates:
                logger.info(f"正在获取数据库：{host}， 日期：{each}")
                result = {}
                data = fetcher.fetch_date(each)
                for site_id, channel, num in data:
                    result.setdefault(site_id, {})
                    result[site_id].setdefault(channel, 0)
                    result[site_id][channel] += num
                for site_id, values in result.items():
                    try:
                        station = OpenStationManage.objects.all().get(station_info__company_id=site_id)
                    except OpenStationManage.DoesNotExist:
                        continue
                    for channel, num in values.items():
                        InquiriesData.objects.create(
                            inquires_num=num,
                            date=each,
                            channel=channel,
                            company_id=site_id,
                            industry=station.company_info.industry.industry,
                            deploy_way=station.station_info.deploy_way,
                            cli_version=station.station_info.cli_version,
                            server_grp=station.station_info.server_grp.group_name,
                        )

    def _to_local_today(self):
        # 1.新增今天的数据
        for site_id, values in self._fetch_data("today").items():
            try:
                station = OpenStationManage.objects.all().get(station_info__company_id=site_id)
            except OpenStationManage.DoesNotExist:
                continue
            for channel, num in values.items():
                InquiriesData.objects.create(
                    company_id=site_id,
                    industry=station.company_info.industry.industry,
                    server_grp=station.station_info.server_grp.group_name,
                    deploy_way=station.station_info.deploy_way,
                    cli_version=station.station_info.cli_version,
                    date=self.today,
                    channel=channel,
                    inquires_num=num,
                )
        # 2.更新昨天的数据
        for site_id, values in self._fetch_data("yesterday").items():
            try:
                station = OpenStationManage.objects.all().get(station_info__company_id=site_id)
            except OpenStationManage.DoesNotExist:
                continue
            for channel, num in values.items():
                InquiriesData.objects.update_or_create(
                    defaults={"inquires_num": num},
                    date=self.yesterday,
                    channel=channel,
                    company_id=site_id,
                    industry=station.company_info.industry.industry,
                    server_grp=station.station_info.server_grp.group_name,
                    deploy_way=station.station_info.deploy_way,
                    cli_version=station.station_info.cli_version,
                )

    def _to_local_yesterday(self):
        # 1.更新今天的数据
        for site_id, values in self._fetch_data("today").items():
            try:
                station = OpenStationManage.objects.all().get(station_info__company_id=site_id)
            except OpenStationManage.DoesNotExist:
                continue
            for channel, num in values.items():
                InquiriesData.objects.update_or_create(
                    defaults={"inquires_num": num},
                    date=self.today,
                    channel=channel,
                    company_id=site_id,
                    industry=station.company_info.industry.industry,
                    server_grp=station.station_info.server_grp.group_name,
                    deploy_way=station.station_info.deploy_way,
                    cli_version=station.station_info.cli_version,
                )

    def update_inquires(self):
        """如果当天的咨询量已存在，则只更新当天的咨询量
        如果当天的咨询量不存在，则说明是当天第一次获取咨询量，第一步更新昨天的咨询量数据，第二步获取今天的咨询量数据
        """
        today_inquires = InquiriesData.objects.all().filter(date=self.today)
        if not today_inquires.exists():
            return self._to_local_today()
        return self._to_local_yesterday()


class OnlineClientFetcher(object):
    def __init__(self):
        self.today = date.today()
        self.values = self._fetch()

    def _fetch(self) -> QuerySet:
        """
        统计条件：
        1. 状态为开
        2. 正式站点
        3. 在有效期内
        """
        return OpenStationManage.objects.all() \
            .filter(online_status=OpenStationManage.STATUS_ONLINE,
                    company_info__station_type=STATION_OFFICAL,
                    station_info__open_station_time__lte=self.today,
                    station_info__close_station_time__gte=self.today) \
            .values_list("company_info__industry__industry",
                         "station_info__deploy_way",
                         "station_info__cli_version") \
            .annotate(count=Count("*"))

    def update_online_client(self) -> None:
        if OnlineClientData.objects.filter(date=self.today).exists():  # 保证每天只会运行一次
            return
        for industry, deploy_way, cli_version, count in self.values:
            OnlineClientData.objects.create(
                date=self.today,
                industry=industry,
                deploy_way=deploy_way,
                cli_version=cli_version,
                online_num=count
            )


class OnlineProductFetcher(object):
    def __init__(self):
        self.today = date.today()
        self.values = self._fetch()

    def _fetch(self) -> QuerySet:
        model = StationInfo.pact_products.through
        return model.objects.all() \
            .filter(stationinfo__open_station__company_info__station_type=STATION_OFFICAL,
                    stationinfo__open_station__online_status=OpenStationManage.STATUS_ONLINE,
                    stationinfo__open_station_time__lte=self.today,
                    stationinfo__close_station_time__gte=self.today) \
            .values_list("product_id",
                         "stationinfo__open_station__company_info__industry__industry",
                         "stationinfo__deploy_way",
                         "stationinfo__cli_version") \
            .annotate(count=Count("*"))

    def update_online_product(self) -> None:
        if OnlineProductData.objects.filter(date=self.today).exists():  # 保证每天只会运行一次
            return
        for product_id, industry, deploy_way, cli_version, count in self.values:
            OnlineProductData.objects.create(
                date=self.today,
                industry=industry,
                deploy_way=deploy_way,
                cli_version=cli_version,
                product_id=product_id,
                online_num=count
            )
