#
# from django.contrib import admin
# from user_app.model.seller_models import Shoppers, Store
#
#
#
# # Register your models here.
#
#
# @admin.register(Store)
# class StoreAdmin(admin.ModelAdmin):
#     list_display = ('store_name', 'shopper_name', 'shop_grade', 'start_time', 'province', 'attention')
#     # readonly_fields = ('shopper','shop_grade','attention')
#     readonly_fields = ('shop_grade', 'attention', 'province', 'shopper')
#
#     def shopper_name(self, obj):
#         """商家名称"""
#         return obj.shopper.username
#
#     shopper_name.short_description = '商家名称'
#
#     def has_add_permission(self, request):
#         return False
#
#     def has_delete_permission(self, request, obj=None):
#         return False
#
#     def get_queryset(self, request):
#         result = super().get_queryset(request)
#         if not request.user.is_superuser:
#             return result.filter(shopper=request.user)
#         return result
#
#
# @admin.register(Shoppers)
# class ShoppersAdmin(admin.ModelAdmin):
#     # exclude = ('user',)
#     list_display = ('shopper_name', 'head_images', 'phone', 'credit', 'sex', 'is_vip')
#     readonly_fields = ('credit', 'is_vip', 'user')
#
#     def sex(self, obj):
#         """性别"""
#         return obj.get_sex_display()
#
#     def shopper_name(self, obj):
#         """商家名称"""
#         return obj.user.username
#
#     shopper_name.short_description = '商家名称'
#
#     def shopper_email(self, obj):
#         """商家邮箱"""
#         return obj.user.email
#
#     shopper_email.short_description = '邮箱'
#
#     def has_add_permission(self, request):
#         return False
#
#     def has_delete_permission(self, request, obj=None):
#         return False
#
#     def get_queryset(self, request):
#         result = super().get_queryset(request)
#         if not request.user.is_superuser:
#             return result.filter(user=request.user)
#         return result
#
#
