# Generated by Django 4.0.1 on 2025-07-09 08:31

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('WebApi', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='SliderCaptcha',
            fields=[
                ('id', models.BigAutoField(primary_key=True, serialize=False, verbose_name='ID')),
                ('token', models.CharField(max_length=64, unique=True, verbose_name='验证令牌')),
                ('bg_image', models.TextField(verbose_name='背景图片')),
                ('slider_image', models.TextField(blank=True, verbose_name='滑块图片')),
                ('correct_position', models.CharField(max_length=255, verbose_name='正确位置')),
                ('is_verified', models.BooleanField(default=False, verbose_name='是否已验证')),
                ('attempts', models.SmallIntegerField(default=0, verbose_name='尝试次数')),
                ('last_attempt_ip', models.CharField(blank=True, max_length=50, null=True, verbose_name='最后尝试IP')),
                ('client_fingerprint', models.CharField(blank=True, max_length=128, null=True, verbose_name='客户端指纹')),
                ('create_time', models.BigIntegerField(verbose_name='创建时间(时间戳)')),
                ('verify_time', models.BigIntegerField(blank=True, null=True, verbose_name='验证时间(时间戳)')),
                ('expire_time', models.BigIntegerField(verbose_name='过期时间(时间戳)')),
            ],
            options={
                'verbose_name': '验证码',
                'verbose_name_plural': '验证码',
                'db_table': 'slider_captcha',
            },
        ),
        migrations.AddField(
            model_name='adminuser',
            name='is_locked',
            field=models.BooleanField(default=False, verbose_name='是否被锁定'),
        ),
        migrations.AddField(
            model_name='adminuser',
            name='last_login_error_time',
            field=models.DateTimeField(blank=True, null=True, verbose_name='最后错误登录时间'),
        ),
        migrations.AddField(
            model_name='adminuser',
            name='lock_until',
            field=models.DateTimeField(blank=True, null=True, verbose_name='锁定到期时间'),
        ),
        migrations.AddField(
            model_name='adminuser',
            name='login_error_count',
            field=models.SmallIntegerField(default=0, verbose_name='登录错误次数'),
        ),
        migrations.AddField(
            model_name='agentuser',
            name='is_locked',
            field=models.BooleanField(default=False, verbose_name='是否被锁定'),
        ),
        migrations.AddField(
            model_name='agentuser',
            name='last_login_error_time',
            field=models.DateTimeField(blank=True, null=True, verbose_name='最后错误登录时间'),
        ),
        migrations.AddField(
            model_name='agentuser',
            name='lock_until',
            field=models.DateTimeField(blank=True, null=True, verbose_name='锁定到期时间'),
        ),
        migrations.AddField(
            model_name='agentuser',
            name='login_error_count',
            field=models.SmallIntegerField(default=0, verbose_name='登录错误次数'),
        ),
        migrations.AddIndex(
            model_name='slidercaptcha',
            index=models.Index(fields=['token'], name='idx_slider_token'),
        ),
        migrations.AddIndex(
            model_name='slidercaptcha',
            index=models.Index(fields=['create_time'], name='idx_slider_create_time'),
        ),
    ]
