# -*- coding: utf-8 -*-
# @Time : 2020/5/1 09:42
# @Author : 司云中
# @File : tasks.py
# @Software: PyCharm

from User_app.views.ali_card_ocr import Interface_identify
from e_mall import celery_apps as app


@app.task
def ocr(image_instance, type_):
    """
    身份验证
    :param image_instance: InMemoryUploadedFile 文件对象
    :param type_: String 身份证类型 face or back
    :return:  Bool
    """
    identify_instance = Interface_identify(image_instance, type_)
    return identify_instance.is_success


# @app.task
# def add_foot(obj, user_id, validated_data):
#     """
#     添加足迹
#     :param obj: redis链接对象
#     :param user_id:用户id
#     :param validated_data: 验证后的数据
#     :return: Bool
#     """
#     try:
#         key = obj.key('foot', user_id)
#         timestamp = int(time.time())  # 毫秒级别的时间戳
#         commodity_id = validated_data['pk']
#         # pipe = self.redis.pipeline()  # 添加管道，减少客户端和服务端之间的TCP包传输次数
#         obj.redis.zadd(key, {commodity_id: timestamp})  # 分别表示用户id（加密），时间戳（分数值），商品id
#         # 每个用户最多缓存100条历史记录
#         if obj.redis.zcard(key) >= 100:  # 集合中key为键的数量
#             obj.redis.zremrangebyrank(key, 0, 0)  # 移除时间最早的那条记录
#         # pipe.execute()
#         return True
#     except Exception as e:
#         return False
#     finally:
#         obj.redis.close()



