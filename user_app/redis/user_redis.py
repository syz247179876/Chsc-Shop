# -*- coding: utf-8 -*-
# @Time : 2020/5/6 15:32
# @Author : 司云中
# @File : user_redis.py
# @Software: PyCharm
from Emall.base_redis import BaseRedis, manager_redis
from Emall.loggings import Logging
from rest_framework.response import Response
from rest_framework.views import APIView
from django_redis import get_redis_connection
from rest_framework import serializers
from shop_app.models.commodity_models import Commodity
import datetime

common_logger = Logging.logger('django')

consumer_logger = Logging.logger('consumer_')


class BrowHistorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Commodity
        fields = ['']


class Add_Get_Browsing_History(APIView):
    """User's browsing history"""

    @property
    def db(self):
        return 'redis'

    @property
    def response_get(self):
        return {
            'status': 'success',
        }

    @staticmethod
    def response_set(id, history_list, counts):
        """response for history"""
        return {
            'id': id,
            'history_list': history_list,
            'counts': counts
        }

    def get_history(self, id, page):
        """Gets 10 browsing histories of the target user """
        with manager_redis(self.db) as redis:
            try:
                history_list = redis.lrange(id, page * 10, (page + 1) * 10)
                history_counts = redis.llen(id)
                return history_list, history_counts
            except Exception as e:
                consumer_logger.error(e)

    def add_history(self, id, commodity):
        """append one browsing history for target user"""
        with manager_redis(self.db) as redis:
            try:
                redis.lpush(id, commodity)
            except Exception as e:
                consumer_logger.error(e)

    def cur_page(self, page):
        """current page"""
        return page

    def previous_page(self, page):
        """previous page"""
        return page + 1

    def next_page(self, page):
        """next page"""
        return page - 1

    def get(self, request):
        """get the history of target user"""
        user_id = request.data.get('user_id')
        page = request.data.get('page')
        history_list, history_counts = self.get_history(user_id, page)
        response = self.response(user_id, history_list, history_counts)
        return Response(response)

    def post(self, request):
        """add one history for target user"""
        user_id = request.data.get('user_id')
        commodity_id = request.data.get('commodity_id')
        self.add_history(user_id, commodity_id)
        response = self.response_get
        return Response(response)


class UserStatistic(APIView):
    """count the number of login of all user used"""

    def response(self, today_visitor_counts, online_counts):
        return {
            'today_visitor_counts': today_visitor_counts,
            'online_counts': online_counts
        }

    @property
    def db(self):
        return 'redis'

    @property
    def get_key(self):
        """get the key of redis"""
        now = datetime.datetime.now()
        key = now.strftime('%Y-%m-%d')
        return key

    def add_count(self, key):
        """add one count when user login"""
        with manager_redis(self.db) as redis:
            key = self.get_key
            redis.incr(key, 1)

    def get_visit_counts(self, key):
        """statistic the number of users intraday"""
        with manager_redis(self.db) as redis:
            counts = redis.get(key)
            return counts

    def get_online_counts(self, key=None):
        """statistic the number of users who online"""
        with manager_redis(self.db) as redis:
            if not key:
                key = 'online'
            counts = redis.get(key)
            return counts

    def get(self):
        today_key = self.get_key
        self.add_count(today_key)
        today_visitor_counts = self.get_visit_counts(today_key)
        online_counts = self.get_online_counts()
        response_ = self.response(today_visitor_counts, online_counts)
        return Response(response_)


class RedisUserOperation(BaseRedis):
    """the operation of save verification code regarding to redis"""

    def __init__(self, db, redis):
        super().__init__(db, redis)

