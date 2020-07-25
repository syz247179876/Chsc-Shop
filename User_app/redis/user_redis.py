# -*- coding: utf-8 -*-
# @Time : 2020/5/6 15:32
# @Author : 司云中
# @File : user_redis.py
# @Software: PyCharm
from User_app.redis.base_redis import BaseRedis
from e_mall.loggings import Logging
from rest_framework.response import Response
from rest_framework.views import APIView
from django_redis import get_redis_connection
from rest_framework import serializers
from Shop_app.models.commodity_models import Commodity
import datetime

common_logger = Logging.logger('django')

consumer_logger = Logging.logger('consumer_')


class BrowHistorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Commodity
        fields = ['']


class Add_Get_Browsing_History(APIView):
    """User's browsing history"""

    _redis = get_redis_connection('redis')

    @property
    def redis(self):
        return self._redis

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
        try:
            history_list = self.redis.lrange(id, page * 10, (page + 1) * 10)
            history_counts = self.redis.llen(id)
            return history_list, history_counts
        except Exception as e:
            consumer_logger.error(e)
        finally:
            self.redis.close()

    def add_history(self, id, commodity):
        """append one browsing history for target user"""
        try:
            self.redis.lpush(id, commodity)
        except Exception as e:
            consumer_logger.error(e)
        finally:
            self.redis.close()

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
    _redis = get_redis_connection('redis')

    def response(self, today_visitor_counts, online_counts):
        return {
            'today_visitor_counts': today_visitor_counts,
            'online_counts': online_counts
        }

    @property
    def redis(self):
        return self._redis

    @property
    def get_key(self):
        """get the key of redis"""
        now = datetime.datetime.now()
        key = now.strftime('%Y-%m-%d')
        return key

    def add_count(self, key):
        """add one count when user login"""
        key = self.get_key
        self.redis.incr(key, 1)

    def get_visit_counts(self, key):
        """statistic the number of users intraday"""
        counts = self.redis.get(key)
        return counts

    def get_online_counts(self, key=None):
        """statistic the number of users who online"""
        if not key:
            key = 'online'
        counts = self.redis.get(key)
        return counts

    def get(self):
        today_key = self.get_key
        self.add_count(today_key)
        today_visitor_counts = self.get_visit_counts(today_key)
        online_counts = self.get_online_counts()
        response_ = self.response(today_visitor_counts, online_counts)
        return Response(response_)


class RedisVerificationOperation(BaseRedis):
    """the operation of save verification code about redis"""

    def __init__(self, redis_instance):
        super().__init__(redis_instance)

    def check_code(self, key, value):
        """compare key-value code and code in redis for equality """
        try:
            if self.redis.exists(key):
                _value = self.redis.get(key).decode()
                return True if _value == value else False
            else:
                return False
        except Exception as e:
            consumer_logger.error(e)
        finally:
            self.redis.close()

    def save_code(self, key, code, time):
        """cache verification code for ten minutes"""
        try:
            self.redis.set(key, code)
            self.redis.expire(key, time)
        except Exception as e:
            consumer_logger.error(e)
        finally:
            self.redis.close()
