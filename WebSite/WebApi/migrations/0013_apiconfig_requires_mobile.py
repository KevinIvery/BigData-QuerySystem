# Generated by Django 4.0.1 on 2025-07-13 13:30

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('WebApi', '0012_queryresult_agentuser_settled_commission_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='apiconfig',
            name='requires_mobile',
            field=models.BooleanField(default=False, verbose_name='是否需要手机号'),
        ),
    ]
