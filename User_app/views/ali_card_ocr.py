# -*- coding: utf-8 -*- 
# @Time : 2020/5/9 14:34 
# @Author : 司云中 
# @File : ali_card_ocr.py 
# @Software: PyCharm

import base64

import json
import urllib
from e_mall.loggings import Logging

common_logger = Logging.logger('django')

consumer_logger = Logging.logger('consumer_')


class OcrIdCard:
    """阿里api身份证识别"""

    AppCode = '990dad198d304f8da8c0c599593f686c'
    url = 'https://dm-51.data.aliyun.com/rest/160601/ocr/ocr_idcard.json'

    params = {
        'image': None,
        'configure': {},
    }

    headers = {
        'Authorization': 'APPCODE 990dad198d304f8da8c0c599593f686c',  # APPCODE +你的appcod,一定要有空格!
        'Content-Type': 'application/json; charset=UTF-8'  # 根据接口的格式来
    }

    def __init__(self, image, card_type):
        image = str(base64.b64encode(image), encoding='utf-8')
        configure = {"side": card_type}
        self.params.update({'image': image, 'configure': configure})
        self.json_result = None
        self.card_type = card_type

    def get_posturl_result(self):
        """get result from aliyun api"""
        try:
            params = json.dumps(self.params).encode(encoding='utf-8')
            req = urllib.request.Request(self.url, params, self.headers)  # structure request
            r = urllib.request.urlopen(req)  # post request
            result = r.read().decode('utf-8')
            self.json_result = json.loads(result)
            common_logger.info(self.json_result)
            r.close()
        except Exception as e:
            consumer_logger.error(e)

    @property
    def address(self):
        """get detail in dict"""
        return self.json_result.get('address')

    @property
    def birth(self):
        """get birth in dict"""
        return self.json_result.get('birth')

    @property
    def actual_name(self):
        """get name in dict"""
        return self.json_result.get('name')

    @property
    def nationality(self):
        """get nationality in dict"""
        return self.json_result.get('nationality')

    @property
    def id_card(self):
        """get id card in dict"""
        return self.json_result.get('num')

    @property
    def sex(self):
        """get sex in dict"""
        return self.json_result.get('sex')

    @property
    def is_success(self):
        """get status to check whether this request is success"""
        return self.json_result.get('success')


class Interface_identify:

    def __init__(self, image, card_type):
        self.user_instance = OcrIdCard(image, card_type)
        self.user_instance.get_posturl_result()

    def get_detail(self, infor_key):
        func = getattr(self.user_instance, infor_key)
        return func

    @property
    def is_success(self):
        """get status to check whether this request is success"""
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
