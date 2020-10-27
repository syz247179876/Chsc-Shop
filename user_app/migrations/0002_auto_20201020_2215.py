# Generated by Django 2.2.15 on 2020-10-20 22:15

from django.db import migrations, models
import user_app.validators


class Migration(migrations.Migration):

    dependencies = [
        ('user_app', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='user',
            name='email',
            field=models.EmailField(blank=True, error_messages={'unique': 'A user with that email already exists'}, max_length=254, null=True, unique=True, verbose_name='邮箱'),
        ),
        migrations.AlterField(
            model_name='user',
            name='full_name',
            field=models.CharField(blank=True, max_length=10, null=True, verbose_name='姓名'),
        ),
        migrations.AlterField(
            model_name='user',
            name='phone',
            field=models.CharField(blank=True, error_messages={'unique': 'A user with that email already exists'}, max_length=11, null=True, validators=[user_app.validators.PhoneValidator], verbose_name='手机号'),
        ),
    ]
