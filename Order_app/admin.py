from django.contrib import admin
from .models.order_models import Order_details, Order_basic, Logistic
from django.utils.translation import gettext_lazy as _
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta
from django.contrib import messages


# Register your models here.

# 自定义过滤器

class Generate_timeFilter(admin.SimpleListFilter):
    """根据订单产生时间查找"""
    # 用于查询的字段名
    parameter_name = 'generate_time'

    # 在查询选项上显示可读的文字
    title = _('搜索订单时间范围')

    def lookups(self, request, model_admin):
        """设置搜索项"""
        # 返回元祖列表，第一个元素用于搜索项，第二个元素用于将搜索项转换成可读的文字
        return [
            ('1_hour', _('一小时内')),
            ('1_day', _('一天内')),
            ('7_days', _('一周内')),
            ('1_month', _('一个月内')),
            ('3_month', _('三个月内')),
            ('6_month', _('半年内')),
            ('1_year', _('一年内'))
        ]

    def queryset(self, request, queryset):
        """针对不同搜索项，匹配不同数据"""
        # 通过self.value()取得匹配项
        if self.value() == '1_hour':
            return queryset.filter(generate_time__gte=(datetime.now() - timedelta(hours=1)),
                                   generate_time__lte=(datetime.now()))
        elif self.value() == '1_day':
            return queryset.filter(generate_time__gte=(datetime.now() - timedelta(days=1)),
                                   generate_time__lte=(datetime.now()))
        elif self.value() == '7_days':
            return queryset.filter(generate_time_gte=(datetime.now() - timedelta(days=7)),
                                   generate_time_lte=(datetime.now()))
        elif self.value() == '1_month':
            return queryset.filter(generate_time_gte=(datetime.now() - relativedelta(month=1)),
                                   generate_time_lte=(datetime.now()))
        elif self.value() == '3_month':
            return queryset.filter(generate_time_gte=(datetime.now() - relativedelta(month=3)),
                                   generate_time_lte=(datetime.now()))
        elif self.value() == '1_year':
            return queryset.filter(generate_time_gte=(datetime).now() - relativedelta(year=1),
                                   generate_time_lte=(datetime).now())
        else:
            return queryset


@admin.register(Order_basic)
class OrderAdmin(admin.ModelAdmin):
    # 显示字段
    list_display = (
        'orderId', 'consumer_name', 'region', 'payment', 'commodity_total_counts', 'total_price', 'checked')
    # 字段超链接,连接到详情页面
    list_display_links = ('orderId',)
    # 搜寻字段
    search_fields = ('colored_status',)
    # 过滤字段
    list_filter = (Generate_timeFilter,)
    # 每页显示项数
    list_per_page = 20
    # 对一对N，一对一的model进行inner join的优化，也就是一次性搜索出来，然后再搜索外键的时候，不需要在查询数据库了
    # 默认该值为False，即参照list_display中的字段进行inner join。
    # list_select_related =('commodity')
    # ordering =(,),该字段应该与model的ordering一样
    ordering = ('-generate_time',)
    # 只读字段,必须在fileds中显示指定
    # readonly_fields = ('quantity', 'commodity', 'belong_shopper', 'shopping_trolley')

    actions = ['make_Checked', 'make_Unchecked']

    # 写在admin中，模型实例用obj代替
    def consumer_name(self, obj):
        """返回商品的名称"""
        return obj.consumer.username

    consumer_name.short_description = '买家'

    '''
    def has_add_permission(self, request):
        """取消所有商家增加订单的功能"""
        return False
    '''

    def make_Checked(self, request, querysets):
        """自定义审核完成动作"""
        result = querysets.update(checked=True, status="3", remarked=True)
        if result == 1:
            message_shorthand = '一个订单已被成功审核'
        else:
            message_shorthand = '{} 个订单已被成功审核'.format(result)
        # 左侧划出的提示框,level作为消息级别，引用django.contrib.message消息后端
        self.message_user(request, message_shorthand, level=messages.SUCCESS)

    make_Checked.short_description = '审核'
    make_Checked.type = 'success'
    make_Checked.confirm = '您确定要审核选中的项嘛？'

    def make_Unchecked(self, request, querysets):
        """自定义审核取消动作"""
        result = querysets.update(checked=False, status="2", remarked=False)
        if result == 1:
            messages_shorthand = '一个订单已被取消审核'
        else:
            messages_shorthand = '{} 个订单已被取消审核'.format(result)
        self.message_user(request, messages_shorthand, level=messages.SUCCESS)

    make_Unchecked.short_description = '取消审核'
    make_Unchecked.type = 'warning'
    # 确认按钮
    make_Unchecked.confirm = '您确定要取消审核选中的项嘛？'

    def get_readonly_fields(self, request, obj=None):
        """根据是否审核，锁定审核订单"""
        try:
            if hasattr(obj, 'checked') and \
                    self.has_change_permission(request, obj) and self.has_view_permission(request, obj):
                if obj.checked:
                    self.readonly_fields = (
                        'orderId', 'consumer', 'region', 'payment', 'commodity_total_counts', 'total_price',
                        'trade_number', 'checked')
                elif not obj.checked:
                    self.readonly_fields = (
                        'orderId', 'consumer', 'region', 'payment', 'commodity_total_counts', 'trade_number',
                        'total_price',)
        except Exception as e:
            self.readonly_fields = (
                'orderId', 'consumer', 'region', 'payment', 'commodity_total_counts', 'total_price',
                'trade_number', 'checked')
        finally:
            return self.readonly_fields


@admin.register(Logistic)
class LogisticAdmin(admin.ModelAdmin):
    list_display = ('order_basic_id_', 'shipping_status_color', 'signed')

    def order_basic_id_(self, obj):
        """订单号"""
        return obj.order_basic.orderId

    order_basic_id_.short_description = '订单号'

    def has_add_permission(self, request):
        return False

    def has_delete_permission(self, request, obj=None):
        return False

    def has_change_permission(self, request, obj=None):
        return False
