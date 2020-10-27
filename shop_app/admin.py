from datetime import datetime

from django.contrib import admin, messages
# Register your models here.
from django.utils.translation import gettext_lazy as _

from shop_app.models.commodity_models import Commodity


class Putaway_status(admin.SimpleListFilter):
    """上架状态过滤器"""
    title = _('查询商品状态')
    parameter_name = 'status'

    def lookups(self, request, model_admin):
        return [
            ('0', _('下架状态')),
            ('1', _('上架状态')),
        ]

    def queryset(self, request, queryset):
        if self.value() == '0':
            return queryset.filter(status='0')
        elif self.value() == '1':
            return queryset.filter(status='1')
        else:
            return queryset


@admin.register(Commodity)
class CommodityAdmin(admin.ModelAdmin):
    exclude = ('store', 'shopper')  # 不在form中显示
    list_display = (
        'commodity_name', 'images', 'category', 'price', 'colored_status', 'discounts', 'stock', 'status')
    list_filter = (Putaway_status,)
    list_per_page = 20
    # model中自定义的colored_status无法用于排序和修改
    # list_editable = ('colored_status',)
    # ordering = ('colored_status',)
    actions_on_top = True
    actions = ['make_shelve', 'make_unshelve', 'sell_counts']
    search_fields = ['category', ]

    '''
    def formfield_for_dbfield(self, db_field, request, **kwargs):
        """根据不同用户筛选其对应的数据，重新生成modelform"""
        # db_field.name 获取model的字段
        # 查找出店家的所有信息
        if db_field.name == 'store':
            # 店家
            user = User.objects.get(username=request.user.username)
            shopper = Shoppers.shoppers_.get(user=user)
            kwargs['queryset'] = Commodity.commodity_.filter(shopper=shopper)
        return super().formfield_for_dbfield(db_field,request,**kwargs)
    '''

    def save_model(self, request, obj, form, change):
        """保存对象后的自动添加商铺和用户"""
        # 使用多对一，1对1的select_related优化查询
        # Commodity.commodity_.select_related('shopper__user')
        # 使用多对多，1对多的prefetch_related优化查询
        # Shoppers.shoppers_.prefetch_related('commodity__store')
        # result = self.get_queryset(request).select_related('shopper__user').first()
        obj.store = request.user.store
        obj.shopper = request.user
        super().save_model(request, obj, form, change)

    def get_queryset(self, request):
        """每个商家只允许查看自己的上架的商品信息"""
        result = super().get_queryset(request).filter(shopper=request.user)
        return result

    # def search_stock_null(self, request, queryset):
    #     """搜索库存为0的商品"""
    #     pass

    def make_shelve(self, request, queryset):
        """更新上架动作"""
        try:
            result = queryset.update(status='1')
            queryset.update(onshelve_time=datetime.now())
            if result == 1:
                message_shorthand = _('一个商品已经上架')
            else:
                message_shorthand = _('{} 个商品已经上架'.format(result))
                # 左侧划出的提示框,level作为消息级别，引用django.contrib.message消息后端
            self.message_user(request, message_shorthand, level=messages.SUCCESS)
        except:
            self.message_user(request, '上架商品操作失败，请联系管理员解决', level=messages.ERROR)

    make_shelve.short_description = '上架'
    # 自定义按钮图标
    make_shelve.icon = 'fas fa-audio-description'
    # 自定义按钮格式
    make_shelve.type = 'success'

    def make_unshelve(self, request, queryset):
        """更新上架动作"""
        try:
            result = queryset.update(status='0')
            queryset.update(unshelve_time=datetime.now())
            if result == 1:
                message_shorthand = _('一个商品已经下架')
            else:
                message_shorthand = _('{} 个商品已经下架'.format(result))
                # 左侧划出的提示框,level作为消息级别，引用django.contrib.message消息后端
            self.message_user(request, message_shorthand, level=messages.SUCCESS)
        except:
            self.message_user(request, '下架商品操作失败，请联系管理员解决', level=messages.ERROR)

    make_unshelve.short_description = '下架'
    # 自定义按钮图标
    make_unshelve.icon = 'fas fa-audio-description'
    # 自定义按钮格式
    make_unshelve.type = 'warning'

    def get_readonly_fields(self, request, obj=None):
        """根据商品的上架状态设定其是否可以修改"""
        # obj为注册的model
        try:
            if hasattr(obj, 'status') and self.has_view_or_change_permission(request, obj):
                if obj.status == 'Unshelve':
                    self.readonly_fields = ('store', 'shopper', 'sell_counts')
                elif obj.status == 'Onshelve':
                    self.readonly_fields = (
                        'store', 'shopper', 'commodity_name', 'price', 'details', 'intro', 'category', 'discounts',
                        'sell_counts')
        except:
            self.readonly_fields = ()
        finally:
            return self.readonly_fields
