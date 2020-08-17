# -*- coding: utf-8 -*- 
# @Time : 2020/5/9 14:34 
# @Author : 司云中 
# @File : ali_card_ocr.py 
# @Software: PyCharm

import base64
import datetime

import json
import urllib
from e_mall.loggings import Logging
from e_mall import settings

common_logger = Logging.logger('django')

consumer_logger = Logging.logger('consumer_')


class OcrIdCard:
    """阿里api身份证识别"""

    AppCode = settings.ALI_APPCODE
    url = settings.ALI_OCR_URL

    params = {
        'image': None,
        'configure': {},
    }

    headers = {
        'Authorization': 'APPCODE {code}'.format(code=AppCode),  # APPCODE +你的appcod,一定要有空格!
        'Content-Type': 'application/json; charset=UTF-8'  # 根据接口的格式来
    }

    def __init__(self, image, card_type):
        image = str(base64.b64encode(image.read()), encoding='utf-8')  # 对二进制进行base64编码
        configure = {"side": card_type}
        self.params.update({'image': image, 'configure': configure})
        self.json_result = None   # 存储返回的结果
        self.card_type = card_type   # 在face和back中选择

    def get_posturl_result(self):
        """从接口中获取识别结果"""
        try:
            params = json.dumps(self.params).encode(encoding='utf-8')  # 原生--->JSON字符串
            req = urllib.request.Request(self.url, params, self.headers)  # 构建请求
            r = urllib.request.urlopen(req)  # 发送请求
            result = r.read().decode('utf-8')  # binary流 ---> utf-8
            self.json_result = json.loads(result)  # JSON字符串--->原生
            r.close()  # 关闭请求
        except Exception as e:
            consumer_logger.error(e)

    @property
    def address(self):
        """get detail in dict"""
        return self.json_result.get('address', None)

    @property
    def birth(self):
        """get birth in dict"""
        if self.json_result.get('birth', None):
            birthday = self.json_result.get('birth')
            year = birthday[0:4]
            month = birthday[4:6]
            day = birthday[6:8]
            birth_str = '%(year)s-%(month)s-%(day)s' % ({'year': year, 'month': month, 'day': day})
            birthday = datetime.datetime.strptime(birth_str, '%Y-%m-%d')
            return birthday
        return None

    @property
    def actual_name(self):
        """get name in dict"""
        return self.json_result.get('name', None)

    @property
    def nationality(self):
        """get nationality in dict"""
        return self.json_result.get('nationality', None)

    @property
    def id_card(self):
        """get id card in dict"""
        return self.json_result.get('num', None)

    @property
    def sex(self):
        """get sex in dict"""
        return 'm' if self.json_result.get('sex', None) == '男' else 'f'

    @property
    def is_success(self):
        """get status to check whether this request is success"""
        return self.json_result.get('success', None)


class Interface_identify:

    def __init__(self, image, card_type):
        self.user_instance = OcrIdCard(image, card_type)
        self.user_instance.get_posturl_result()

    def get_detail(self, infor_key):
        func = getattr(self.user_instance, infor_key)
        return func

    @property
    def is_success(self):
        """判断请求是否获取到正确的结果"""
        has_result = True if self.user_instance.json_result else False
        if has_result:
            is_success = self.get_detail('is_success')
            return is_success
        else:
            return False

    """def test(self, card_type):
        path = 'C:\\Users\\ASUS\\Desktop\\index.jpg'
        with open(path, 'rb') as f:
            data = f.read()
            image = str(base64.b64encode(data), encoding='utf-8')
            configure = {"side": card_type}
            self.body.update({'image': image, 'configure': configure})"""
