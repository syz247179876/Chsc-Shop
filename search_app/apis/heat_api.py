# -*- coding: utf-8 -*-
# @Time  : 2021/1/11 下午7:21
# @Author : 司云中
# @File : heat_api.py
# @Software: Pycharm
from rest_framework.generics import GenericAPIView
from rest_framework.response import Response

from collections import OrderedDict
from search_app import signals


class HeatSearchOperation(GenericAPIView):
    """热度搜索操作"""

    def get(self, request):
        """
        获取当天搜索热度关键字

        获取前一天热搜关键字,与今天进行比较,生成上涨还是下降

        """
        result = signals.retrieve_heat_keyword.send(sender=None)
        cur_heat = result[0][1]  # 当天热搜词
        prev_heat = result[1][1]  # 前天热搜词

        cur_rank = {cur_heat[i]: i for i in range(len(cur_heat))}
        prev_rank = {prev_heat[i]: i for i in range(len(prev_heat))}

        fluctuate = [0 for _ in cur_rank]

        # 如果是第一天显示热搜榜, 2显示最新
        if not prev_rank:
            return Response({
                'fluctuate': [2 for _ in cur_rank],
                'cur_heat': cur_heat
            })

        for keyword, rank in cur_rank.items():
            # 如果今天的关键词在前一天中不存在的话, 则显示"新"
            if prev_rank.get(keyword, None) is None :
                fluctuate[rank] = 2
            # 如果当天排名相较于昨天排名上升, 则为上涨
            elif rank < prev_rank.get(keyword):
                fluctuate[rank] = 1
            # 如果排名不变,则不变
            elif rank == prev_rank.get(keyword):
                fluctuate[rank] = 0
            # 如果排名下降,则下降
            else:
                fluctuate[rank] = -1

        data = {
            'fluctuate': fluctuate,
            'cur_heat': cur_heat
        }

        return Response(data)
