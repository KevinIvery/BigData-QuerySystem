# Generated by Django 4.0.1 on 2025-07-09 13:25

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('WebApi', '0003_remove_apiconfig_api_type_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='queryconfig',
            name='customer_price',
            field=models.DecimalField(decimal_places=2, default=0.0, max_digits=10, verbose_name='客户查询单价'),
        ),
    ]
