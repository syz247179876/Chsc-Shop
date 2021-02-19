import os


from django.test import TestCase

# Create your tests here.

# if __name__ == '__main__':
#     os.environ.setdefault("DJANGO_SETTINGS_MODULE", "Emall.settings")
#     import django
#     django.setup()
#     from shop_app.models.commodity_models import CommodityCategory
#     from seller_app.serializers.commodity_serializers import CommodityCategorySerializer
#     import json
#
#     c1 = CommodityCategory.objects.create(name='潮流T血', intro="衣服种类", has_next=True)
#
#     c2 = CommodityCategory.objects.create(name='棉袄', intro="裤子种类", has_next=True)
#
#     c3 = CommodityCategory.objects.create(name="男内衣", intro="男装种类", pre=c1)
#
#     c4 = CommodityCategory.objects.create(name="男上衣", intro="男上衣种类", pre=c1)
#
#     cs = CommodityCategory.objects.all()
#
#     print(json.dumps(CommodityCategorySerializer(cs, many=True).data))

