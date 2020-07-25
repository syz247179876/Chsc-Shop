# -*- coding: utf-8 -*- 
# @Time : 2020/5/9 8:50 
# @Author : 司云中 
# @File : loggings.py 
# @Software: PyCharm
import abc
import logging


# 工厂模式
class AbstractLoggerFactory(metaclass=abc.ABCMeta):

    @abc.abstractmethod
    def common_logger(self):
        pass

    @abc.abstractmethod
    def specific_logger(self):
        pass


class ConsumerFactory(AbstractLoggerFactory):
    """the factory with consumer"""

    def common_logger(self):
        return django_logger().create_logger()

    def specific_logger(self):
        return Consumer().create_logger()


class ShopperFactory(AbstractLoggerFactory):
    """the factory with shopper"""

    def common_logger(self):
        return django_logger().create_logger()

    def specific_logger(self):
        return Shopper().create_logger()


class AppBase(metaclass=abc.ABCMeta):

    @abc.abstractmethod
    def create_logger(self):
        pass


class DjangoLogger(AppBase):

    def __init__(self, logger_name='django'):
        self.logger = logging.getLogger(logger_name)

    def create_logger(self):
        return self.logger


class Consumer(AppBase):
    def __init__(self, logger_name='consumer_'):
        self.logger = logging.getLogger(logger_name)

    def create_logger(self):
        return self.logger


class Shopper(AppBase):

    def __init__(self, logger_name='shopper_'):
        self.logger = logging.getLogger(logger_name)

    def create_logger(self):
        return self.logger


class InterfaceLogger:

    def __init__(self, factory):
        self.common_logger = factory.common_logger()
        self.specific_logger = factory.specific_logger()

    def get_common_logger(self):
        return self.common_logger

    def get_specific_logger(self):
        return self.specific_logger


# 单例模式


class Logging:
    _instance = {}

    @classmethod
    def get_logger(cls, logger_name):
        return cls._instance[logger_name]

    @classmethod
    def logger(cls, logger_name):
        if not cls._instance.setdefault(logger_name, None):
            cls._instance[logger_name] = logging.getLogger(logger_name)
        return cls._instance[logger_name]



