# Generated by Django 4.0.1 on 2025-07-09 13:52

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('WebApi', '0004_queryconfig_customer_price'),
    ]

    operations = [
        migrations.AddField(
            model_name='queryconfig',
            name='category',
            field=models.CharField(blank=True, choices=[('two_factor', '二要素'), ('three_factor', '三要素'), ('face', '人脸')], max_length=20, null=True, verbose_name='查询配置类别'),
        ),
    ]
