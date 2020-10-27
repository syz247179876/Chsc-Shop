# Generated by Django 2.2.15 on 2020-10-20 19:27

from django.conf import settings
import django.contrib.auth.validators
from django.db import migrations, models
import django.utils.timezone
import user_app.models
import user_app.utils.validators


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('auth', '0011_update_proxy_permissions'),
        ('shop_app', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='User',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('password', models.CharField(max_length=128, verbose_name='password')),
                ('last_login', models.DateTimeField(blank=True, null=True, verbose_name='last login')),
                ('is_superuser', models.BooleanField(default=False, help_text='Designates that this user has all permissions without explicitly assigning them.', verbose_name='superuser status')),
                ('username', models.CharField(error_messages={'unique': 'A user with that username already exists.'}, help_text='Required. 30 characters or fewer. Letters, digits and @/./+/-/_ only.', max_length=30, unique=True, validators=[django.contrib.auth.validators.UnicodeUsernameValidator()], verbose_name='昵称')),
                ('full_name', models.CharField(blank=True, max_length=10, verbose_name='姓名')),
                ('email', models.EmailField(blank=True, error_messages={'unique': 'A user with that email already exists'}, max_length=254, unique=True, verbose_name='邮箱')),
                ('phone', models.CharField(blank=True, error_messages={'unique': 'A user with that email already exists'}, max_length=11, validators=[
                    user_app.utils.validators.PhoneValidator], verbose_name='手机号')),
                ('is_seller', models.BooleanField(default=False, help_text='Consumer upgrade to sellers by registering to open storewho have access to the background', verbose_name='卖家身份')),
                ('is_staff', models.BooleanField(default=False, help_text='Consumer upgrade to sellers by registering to open storewho have access to the background', verbose_name='销售员工')),
                ('is_active', models.BooleanField(default=True, help_text='Stranger who has registered to become usersDesignates whether this user should be treated as active. Unselect this instead of deleting accounts.', verbose_name='激活状态')),
                ('birthday', models.DateField(blank=True, null=True, verbose_name='出生日期')),
                ('sex', models.CharField(choices=[('m', '男'), ('f', '女'), ('s', '保密')], default='s', max_length=1, verbose_name='性别')),
                ('head_image', models.ImageField(blank=True, null=True, upload_to='', verbose_name='头像')),
                ('date_joined', models.DateTimeField(default=django.utils.timezone.now, verbose_name='date joined')),
                ('groups', models.ManyToManyField(blank=True, help_text='The groups this user belongs to. A user will get all permissions granted to each of their groups.', related_name='user_set', related_query_name='user', to='auth.Group', verbose_name='groups')),
                ('user_permissions', models.ManyToManyField(blank=True, help_text='Specific permissions for this user.', related_name='user_set', related_query_name='user', to='auth.Permission', verbose_name='user permissions')),
            ],
            options={
                'verbose_name': 'user',
                'verbose_name_plural': 'users',
                'db_table': 'User',
                'abstract': False,
                'swappable': 'AUTH_USER_MODEL',
            },
            managers=[
                ('objects', user_app.models.UserManager()),
            ],
        ),
        migrations.CreateModel(
            name='Store',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('store_name', models.CharField(help_text='请定义您的商铺名，默认为您的有户名+"的商铺"', max_length=30, verbose_name='店铺')),
                ('register_time', models.DateTimeField(auto_now_add=True, verbose_name='注册时间')),
                ('province', models.CharField(blank=True, help_text='请填写您的省份', max_length=10, verbose_name='省份')),
                ('city', models.CharField(blank=True, help_text='请填写您的城市', max_length=10, verbose_name='城市')),
                ('attention', models.PositiveIntegerField(default=0, verbose_name='关注量')),
                ('shop_grade', models.DecimalField(decimal_places=1, default=0.0, max_digits=2, verbose_name='店铺评分')),
                ('shopper', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='store', to=settings.AUTH_USER_MODEL, verbose_name='商家')),
            ],
            options={
                'verbose_name': '店铺',
                'verbose_name_plural': '店铺',
                'db_table': 'Store',
            },
            managers=[
                ('store_', django.db.models.manager.Manager()),
            ],
        ),
        migrations.CreateModel(
            name='Trolley',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('time', models.DateTimeField(auto_now_add=True)),
                ('count', models.PositiveIntegerField(default=1, verbose_name='商品数量')),
                ('price', models.DecimalField(decimal_places=2, max_digits=11, verbose_name='商品价格')),
                ('label', models.TextField(verbose_name='标签')),
                ('commodity', models.ForeignKey(on_delete=True, related_name='trolley', to='shop_app.Commodity', verbose_name='商品')),
                ('store', models.ForeignKey(on_delete=True, related_name='trolley', to='user_app.Store', verbose_name='店铺')),
                ('user', models.ForeignKey(on_delete=True, related_name='trolley', to=settings.AUTH_USER_MODEL, verbose_name='用户')),
            ],
            options={
                'verbose_name': '购物车',
                'verbose_name_plural': '购物车',
                'db_table': 'Trolley',
                'ordering': ('-time',),
            },
            managers=[
                ('trolley_', django.db.models.manager.Manager()),
            ],
        ),
        migrations.CreateModel(
            name='Shoppers',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('phone', models.CharField(max_length=11, unique=True, validators=[
                    user_app.utils.validators.PhoneValidator()], verbose_name='手机号')),
                ('credit', models.CharField(choices=[('1', '1星'), ('2', '2星'), ('3', '3星'), ('4', '4星'), ('5', '5星'), ('6', '1钻'), ('7', '2钻'), ('8', '3钻'), ('9', '4钻'), ('10', '5钻')], default=1, help_text='您的信誉等级', max_length=1, verbose_name='信誉')),
                ('sex', models.CharField(blank=True, choices=[('m', '男'), ('f', '女')], help_text='性别', max_length=1, verbose_name='性别')),
                ('sell_category', models.CharField(choices=[('衣服', '衣服'), ('裤子', '裤子'), ('生活用品', '生活用品'), ('家具', '家具'), ('鞋子', '鞋子'), ('化妆品', '化妆品'), ('零食', '零食')], default='衣服', max_length=10)),
                ('nationality', models.CharField(default='', max_length=50)),
                ('is_vip', models.BooleanField(default=True, verbose_name='是否是vip')),
                ('user', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='shoppers', to=settings.AUTH_USER_MODEL, verbose_name='商家id')),
            ],
            options={
                'verbose_name': '商家',
                'verbose_name_plural': '商家',
                'db_table': 'Seller',
            },
            managers=[
                ('shopper_', django.db.models.manager.Manager()),
            ],
        ),
        migrations.CreateModel(
            name='Foot',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('time', models.DateField(auto_now_add=True, verbose_name='浏览时间')),
                ('commodity', models.ManyToManyField(related_name='foots', to='shop_app.Commodity', verbose_name='商品')),
                ('user', models.ForeignKey(on_delete=True, related_name='foots', to=settings.AUTH_USER_MODEL, verbose_name='用户')),
            ],
            options={
                'verbose_name': '足迹',
                'verbose_name_plural': '足迹',
                'db_table': 'Foot',
                'ordering': ('time',),
            },
        ),
        migrations.CreateModel(
            name='Consumer',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('rank', models.CharField(choices=[('1', '先锋会员'), ('2', '卫士会员'), ('3', '中军会员'), ('4', '统帅会员'), ('5', '传奇会员'), ('6', '万古流芳会员'), ('7', '超凡入圣会员'), ('8', '冠绝一世会员')], default=1, help_text='您的会员等级', max_length=1, verbose_name='会员等级')),
                ('safety', models.DecimalField(decimal_places=0, default=60, help_text='您的信息安全分数', max_digits=3, verbose_name='安全分数')),
                ('nationality', models.CharField(blank=True, help_text='详细地址信息', max_length=30, null=True, verbose_name='详细地址')),
                ('integral', models.PositiveIntegerField(default=0, verbose_name='积分值')),
                ('user', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='consumer', to=settings.AUTH_USER_MODEL, verbose_name='消费者')),
            ],
            options={
                'verbose_name': '消费者',
                'verbose_name_plural': '消费者',
                'db_table': 'Consumer',
            },
            managers=[
                ('consumer_', django.db.models.manager.Manager()),
            ],
        ),
        migrations.CreateModel(
            name='Collection',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('datetime', models.DateTimeField(auto_now_add=True, verbose_name='收藏时间')),
                ('commodity', models.ForeignKey(null=True, on_delete=True, related_name='collections', to='shop_app.Commodity', verbose_name='商品')),
                ('store', models.ForeignKey(null=True, on_delete=True, related_name='store', to='user_app.Store', verbose_name='店铺')),
                ('user', models.ForeignKey(on_delete=True, related_name='collections', to=settings.AUTH_USER_MODEL, verbose_name='用户')),
            ],
            options={
                'verbose_name': '收藏夹',
                'verbose_name_plural': '收藏夹',
                'db_table': 'Collection',
                'ordering': ('datetime',),
            },
            managers=[
                ('collection_', django.db.models.manager.Manager()),
            ],
        ),
        migrations.CreateModel(
            name='Address',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('recipients', models.CharField(max_length=20, validators=[
                    user_app.utils.validators.RecipientsValidator()], verbose_name='收件人')),
                ('region', models.CharField(max_length=50, validators=[user_app.utils.validators.RegionValidator()], verbose_name='所在地区')),
                ('address_tags', models.CharField(choices=[('1', '家'), ('2', '公司'), ('3', '学校')], max_length=1, validators=[
                    user_app.utils.validators.AddressTagValidator()], verbose_name='地址标签')),
                ('default_address', models.BooleanField(default=False, verbose_name='默认地址')),
                ('phone', models.CharField(error_messages={'unique': 'A telephone number with this already exists.'}, help_text='Please write your cell-phone number', max_length=11, validators=[
                    user_app.utils.validators.PhoneValidator()], verbose_name='手机号')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='address', to=settings.AUTH_USER_MODEL, verbose_name='消费者')),
            ],
            options={
                'verbose_name': '收获地址',
                'verbose_name_plural': '收获地址',
                'db_table': 'Address',
                'ordering': ('-default_address',),
            },
            managers=[
                ('address_', django.db.models.manager.Manager()),
            ],
        ),
    ]
