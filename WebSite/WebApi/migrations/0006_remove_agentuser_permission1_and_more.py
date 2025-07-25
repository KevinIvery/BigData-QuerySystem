# Generated by Django 4.0.1 on 2025-07-10 05:51

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('WebApi', '0005_queryconfig_category'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='agentuser',
            name='permission1',
        ),
        migrations.RemoveField(
            model_name='agentuser',
            name='permission2',
        ),
        migrations.RemoveField(
            model_name='agentuser',
            name='permission3',
        ),
        migrations.AddField(
            model_name='agentuser',
            name='can_customize_settings',
            field=models.BooleanField(default=False, verbose_name='允许自定义系统设置'),
        ),
        migrations.AddField(
            model_name='agentuser',
            name='enterprise_query_customer_price',
            field=models.DecimalField(decimal_places=2, default=0.0, max_digits=10, verbose_name='企业查询客户价'),
        ),
        migrations.AddField(
            model_name='agentuser',
            name='enterprise_query_min_price',
            field=models.DecimalField(decimal_places=2, default=0.0, max_digits=10, verbose_name='企业查询最低价'),
        ),
        migrations.AddField(
            model_name='agentuser',
            name='personal_query_customer_price',
            field=models.DecimalField(decimal_places=2, default=0.0, max_digits=10, verbose_name='个人查询客户价'),
        ),
        migrations.AddField(
            model_name='agentuser',
            name='personal_query_min_price',
            field=models.DecimalField(decimal_places=2, default=0.0, max_digits=10, verbose_name='个人查询最低价'),
        ),
        migrations.AddField(
            model_name='agentuser',
            name='phone',
            field=models.CharField(blank=True, max_length=20, verbose_name='手机号'),
        ),
        migrations.AddField(
            model_name='agentuser',
            name='total_profit',
            field=models.DecimalField(decimal_places=2, default=0.0, max_digits=12, verbose_name='累计收益'),
        ),
    ]
