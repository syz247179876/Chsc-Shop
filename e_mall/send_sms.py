# -*- coding: utf-8 -*-
# @Time  : 2020/8/14 上午8:02
# @Author : 司云中
# @File : send_sms.py
# @Software: Pycharm
# import uuid
import uuid

from aliyunsdkcore import SendSmsRequest, QuerySendDetailsRequest
from aliyunsdkcore.client import AcsClient

from e_mall.settings import ACCESS_KEY_ID, ACCESS_KEY_SECRET, REGION, SIGN_NAME, TEMPLATES_CODE_REGISTER

acs_client = AcsClient(ACCESS_KEY_ID, ACCESS_KEY_SECRET, REGION)


def send_sms(business_id, phone_numbers, sign_name, template_code, template_param=None):
    smsRequest = SendSmsRequest.SendSmsRequest()
    # 申请的短信模板编码,必填
    smsRequest.set_TemplateCode(template_code)

    # 短信模板变量参数
    if template_param is not None:
        smsRequest.set_TemplateParam(template_param)

    # 设置业务请求流水号，必填。
    smsRequest.set_OutId(business_id)

    # 短信签名
    smsRequest.set_SignName(sign_name)

    # 短信发送的号码列表，必填。
    smsRequest.set_PhoneNumbers(phone_numbers)

    # 调用短信发送接口，返回json
    smsResponse = acs_client.do_action_with_exception(smsRequest)

    # 业务处理

    return smsResponse


def query_send_detail(biz_id, phone_number, page_size, current_page, send_date):
    """查询发送哦个"""
    queryRequest = QuerySendDetailsRequest.QuerySendDetailsRequest()
    # 查询的手机号码
    queryRequest.set_PhoneNumber(phone_number)
    # 可选 - 流水号
    queryRequest.set_BizId(biz_id)
    # 必填 - 发送日期 支持30天内记录查询，格式yyyyMMdd
    queryRequest.set_SendDate(send_date)
    # 必填-当前页码从1开始计数
    queryRequest.set_CurrentPage(current_page)
    # 必填-页大小
    queryRequest.set_PageSize(page_size)

    # 调用短信记录查询接口，返回json
    queryResponse = acs_client.do_action_with_exception(queryRequest)

    # 业务处理

    return queryResponse


def send_phone(phone_numbers, template_code, template_param):
    _business_id = uuid.uuid1()
    response = send_sms(_business_id, phone_numbers=phone_numbers, sign_name=SIGN_NAME, template_code=template_code,
                        template_param=template_param)
    return response


