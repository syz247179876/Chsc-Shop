# Generated by Django 2.2.15 on 2020-10-20 19:27

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('order_app', '0001_initial'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('user_app', '0001_initial'),
        ('shop_app', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='order_details',
            name='belong_shopper',
            field=models.ForeignKey(help_text='该商品所对应的商家', on_delete=django.db.models.deletion.CASCADE, related_name='order_details', to=settings.AUTH_USER_MODEL, verbose_name='商家'),
        ),
        migrations.AddField(
            model_name='order_details',
            name='commodity',
            field=models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='order_details', to='shop_app.Commodity', verbose_name='商品'),
        ),
        migrations.AddField(
            model_name='order_details',
            name='order_basic',
            field=models.ForeignKey(help_text='属于哪个一个订单', on_delete=django.db.models.deletion.CASCADE, related_name='order_details', to='order_app.Order_basic', verbose_name='订单号'),
        ),
        migrations.AddField(
            model_name='order_basic',
            name='consumer',
            field=models.ForeignKey(max_length=50, on_delete=django.db.models.deletion.CASCADE, related_name='order_basic', to=settings.AUTH_USER_MODEL, verbose_name='用户名'),
        ),
        migrations.AddField(
            model_name='order_basic',
            name='region',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='order_basic', to='user_app.Address', verbose_name='收货人'),
        ),
        migrations.AddField(
            model_name='logistic',
            name='order_basic',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='logistic', to='order_app.Order_basic', verbose_name='订单'),
        ),
    ]
