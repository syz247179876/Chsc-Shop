from django.contrib import admin
from .models.remark_models import Remark, RemarkReply
from django.utils.translation import gettext_lazy as _
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta


class remark_time_filter(admin.SimpleListFilter):
    # 思路：获取前端传来的查询字符串，自定义parameter_name，将查询字符串以键值赋给parameter_name，存储到字典中
    # 然后自定义搜索项，针对搜索项，也就是所有的查询字符串，
    # 匹配parameter_name的值，即查询字符串，根据其查询相应的查询集
    title = '根据时间段搜索用户评论'
    parameter_name = 'reward_time'

    def lookups(self, request, model_admin):
        """制定搜索项"""
        return [
            ('30_minutes', _('三十分钟内')),
            ('half_day', _('半天内')),
            ('1_hour', _('一小时内')),
            ('1_day', _('一天内')),
            ('7_day', _('一周内')),
            ('30_day', _('一个月内')),
        ]

    def queryset(self, request, queryset):
        if self.value() == '30_minutes':
            return queryset.filter(reward_time__gte=datetime.now() - timedelta(minutes=30),
                                   reward_time__lte=datetime.now())
        elif self.value() == '1_hour':
            return queryset.filter(reward_time__gte=datetime.now() - timedelta(hours=1),
                                   reward_time__lte=datetime.now())
        elif self.value() == 'half_day':
            return queryset.filter(reward_time__gte=datetime.now() - timedelta(hours=12),
                                   reward_time__lte=datetime.now())
        elif self.value() == '1_day':
            return queryset.filter(reward_time__gte=datetime.now() - timedelta(days=1),
                                   reward_time__lte=datetime.now())
        elif self.value() == '7_day':
            return queryset.filter(reward_time__gte=datetime.now() - timedelta(days=7),
                                   reward_time__lte=datetime.now())
        elif self.value() == '30_day':
            return queryset.filter(reward_time__gte=datetime.now() - timedelta(days=30),
                                   reward_time__lte=datetime.now())
        else:
            return queryset


@admin.register(Remark)
class RemarkAdmin(admin.ModelAdmin):
    list_display = ('consumer_name', 'commodity', 'grade', 'reward_time')
    ordering = ('-reward_time',)
    list_per_page = 20
    search_fields = ('grade',)
    list_filter = (remark_time_filter,)


    def consumer_name(self, obj):
        """返回消费者名字"""
        return obj.consumer.username
    consumer_name.short_description = '消费者昵称'

    def commodity_category(self, obj):
        """返回商品所属的种类"""
        return obj.commodity.category
    consumer_name.short_description = '商品种类'

    def has_add_permission(self, request):
        """回去backend查找对应用户的对应model的权限是否存在"""
        """禁止商家删除权限"""
        return False

    def has_delete_permission(self, request, obj=None):
        """禁止商家删除评论"""
        return False

    def has_change_permission(self, request, obj=None):
        """禁止商家改变评论"""
        return False


    def get_queryset(self, request):
        """只显示当前用户名下的评论"""
        # 如果指定了ordering，get_queryset中也需要重写
        result = super().get_queryset(request).filter(shopper=request.user)
        # ordering = self.get_ordering(request)  # 获取self.ordering
        if self.ordering:
            result = result.order_by(*self.ordering)
        return result


@admin.register(RemarkReply)
class Remark_replyAdmin(admin.ModelAdmin):
    list_display = ('reply_commodity_name','part_reward_content','reward_time','reply_time')
    ordering = ('reply_time',)
    list_per_page = 20

    def reply_commodity_name(self,obj):
        """返回评论商品"""
        return obj.remark.commodity.commodity_name
    reply_commodity_name.short_description = '商品名称'

    def reward_time(self,obj):
        """返回用户评论时间"""
        return obj.remark.reward_time
    reward_time.short_description = '用户评论时间'

    def part_reward_content(self,obj):
        return obj.reply_content
    part_reward_content.short_description = '回复内容'




