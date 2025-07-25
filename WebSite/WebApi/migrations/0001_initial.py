# Generated by Django 4.0.1 on 2025-07-09 06:44

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='AdminUser',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('company_name', models.CharField(max_length=200, verbose_name='公司名称')),
                ('username', models.CharField(max_length=50, unique=True, verbose_name='用户名')),
                ('password', models.CharField(max_length=255, verbose_name='密码')),
                ('created_at', models.DateTimeField(auto_now_add=True, verbose_name='创建时间')),
            ],
            options={
                'verbose_name': '超级管理员',
                'verbose_name_plural': '超级管理员',
                'db_table': 'admin_users',
            },
        ),
        migrations.CreateModel(
            name='AgentUser',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('username', models.CharField(max_length=50, unique=True, verbose_name='用户名')),
                ('password', models.CharField(max_length=255, verbose_name='密码')),
                ('domain_suffix', models.CharField(max_length=100, unique=True, verbose_name='域名后缀')),
                ('permission1', models.BooleanField(default=True, verbose_name='权限1')),
                ('permission2', models.BooleanField(default=True, verbose_name='权限2')),
                ('permission3', models.BooleanField(default=True, verbose_name='权限3')),
                ('created_at', models.DateTimeField(auto_now_add=True, verbose_name='创建时间')),
            ],
            options={
                'verbose_name': '代理用户',
                'verbose_name_plural': '代理用户',
                'db_table': 'agent_users',
            },
        ),
        migrations.CreateModel(
            name='ApiConfig',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('api_type', models.CharField(choices=[('judicial', '司法接口'), ('marriage', '婚姻接口'), ('multi_loan', '多头借贷接口'), ('sms', '短信验证码接口'), ('face_recognition', '人脸识别接口')], max_length=20, verbose_name='接口类型')),
                ('api_name', models.CharField(max_length=100, verbose_name='接口名称')),
                ('owner_id', models.IntegerField(verbose_name='关联用户ID')),
                ('owner_type', models.CharField(choices=[('admin', '管理员'), ('agent', '代理')], max_length=10, verbose_name='用户类型')),
                ('cost_price', models.DecimalField(decimal_places=2, max_digits=10, verbose_name='成本价')),
                ('admin_cost_price', models.DecimalField(decimal_places=2, max_digits=10, verbose_name='管理员成本价')),
                ('is_active', models.BooleanField(default=True, verbose_name='是否启用')),
                ('created_at', models.DateTimeField(auto_now_add=True, verbose_name='创建时间')),
                ('updated_at', models.DateTimeField(auto_now=True, verbose_name='更新时间')),
            ],
            options={
                'verbose_name': '接口配置',
                'verbose_name_plural': '接口配置',
                'db_table': 'api_configs',
            },
        ),
        migrations.CreateModel(
            name='AuthorizationLetter',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('user_id', models.IntegerField(verbose_name='关联用户ID')),
                ('agent_id', models.IntegerField(blank=True, null=True, verbose_name='代理ID')),
                ('authorization_content', models.TextField(verbose_name='授权书内容')),
                ('authorization_file_url', models.CharField(blank=True, max_length=500, verbose_name='授权书文件URL')),
                ('file_hash', models.CharField(blank=True, max_length=64, verbose_name='文件哈希值')),
                ('is_valid', models.BooleanField(default=True, verbose_name='是否有效')),
                ('created_at', models.DateTimeField(auto_now_add=True, verbose_name='创建时间')),
                ('updated_at', models.DateTimeField(auto_now=True, verbose_name='更新时间')),
            ],
            options={
                'verbose_name': '授权书',
                'verbose_name_plural': '授权书',
                'db_table': 'authorization_letters',
            },
        ),
        migrations.CreateModel(
            name='ExternalApiConfig',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('config_type', models.CharField(choices=[('aliyun_sms', '阿里云短信配置'), ('tianyuan_api', '天远API接口配置'), ('wechat_login', '公众号登录配置')], max_length=20, verbose_name='配置类型')),
                ('config_name', models.CharField(max_length=100, verbose_name='配置名称')),
                ('access_key_id', models.CharField(blank=True, max_length=200, verbose_name='AccessKeyId')),
                ('access_key_secret', models.CharField(blank=True, max_length=200, verbose_name='AccessKeySecret')),
                ('api_key', models.CharField(blank=True, max_length=200, verbose_name='API Key')),
                ('api_secret', models.CharField(blank=True, max_length=200, verbose_name='API Secret')),
                ('app_id', models.CharField(blank=True, max_length=100, verbose_name='AppID')),
                ('app_secret', models.CharField(blank=True, max_length=200, verbose_name='AppSecret')),
                ('redirect_domain', models.CharField(blank=True, max_length=200, verbose_name='重定向域名')),
                ('owner_id', models.IntegerField(verbose_name='所属用户ID')),
                ('owner_type', models.CharField(choices=[('admin', '管理员'), ('agent', '代理')], max_length=10, verbose_name='用户类型')),
                ('is_active', models.BooleanField(default=True, verbose_name='是否启用')),
                ('created_at', models.DateTimeField(auto_now_add=True, verbose_name='创建时间')),
                ('updated_at', models.DateTimeField(auto_now=True, verbose_name='更新时间')),
            ],
            options={
                'verbose_name': 'API接口配置',
                'verbose_name_plural': 'API接口配置',
                'db_table': 'external_api_configs',
            },
        ),
        migrations.CreateModel(
            name='Order',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('order_no', models.CharField(max_length=50, unique=True, verbose_name='订单号')),
                ('user_id', models.IntegerField(verbose_name='用户ID')),
                ('agent_id', models.IntegerField(blank=True, null=True, verbose_name='代理ID')),
                ('query_type', models.CharField(max_length=50, verbose_name='查询类型')),
                ('amount', models.DecimalField(decimal_places=2, max_digits=10, verbose_name='订单金额')),
                ('status', models.CharField(choices=[('pending', '待支付'), ('paid', '已支付'), ('completed', '已完成'), ('cancelled', '已取消')], default='pending', max_length=20, verbose_name='订单状态')),
                ('created_at', models.DateTimeField(auto_now_add=True, verbose_name='创建时间')),
                ('updated_at', models.DateTimeField(auto_now=True, verbose_name='更新时间')),
            ],
            options={
                'verbose_name': '订单',
                'verbose_name_plural': '订单',
                'db_table': 'orders',
            },
        ),
        migrations.CreateModel(
            name='PaymentConfig',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('payment_type', models.CharField(choices=[('wechat', '微信支付'), ('alipay', '支付宝支付')], max_length=20, verbose_name='支付类型')),
                ('config_name', models.CharField(max_length=100, verbose_name='配置名称')),
                ('config_data', models.JSONField(verbose_name='配置数据')),
                ('owner_id', models.IntegerField(verbose_name='所属用户ID')),
                ('owner_type', models.CharField(choices=[('admin', '管理员'), ('agent', '代理')], max_length=10, verbose_name='用户类型')),
                ('is_active', models.BooleanField(default=True, verbose_name='是否启用')),
                ('created_at', models.DateTimeField(auto_now_add=True, verbose_name='创建时间')),
                ('updated_at', models.DateTimeField(auto_now=True, verbose_name='更新时间')),
            ],
            options={
                'verbose_name': '支付系统配置',
                'verbose_name_plural': '支付系统配置',
                'db_table': 'payment_configs',
            },
        ),
        migrations.CreateModel(
            name='QueryConfig',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('config_name', models.CharField(max_length=100, verbose_name='配置名称')),
                ('api_combination', models.JSONField(verbose_name='查询搭配的接口')),
                ('input_type', models.CharField(choices=[('two_factor', '二要素'), ('three_factor', '三要素'), ('face_recognition', '人脸识别')], max_length=20, verbose_name='查询入参类型')),
                ('result_types', models.JSONField(verbose_name='查询结果类型')),
                ('owner_id', models.IntegerField(verbose_name='所属用户ID')),
                ('owner_type', models.CharField(choices=[('admin', '管理员'), ('agent', '代理')], max_length=10, verbose_name='用户类型')),
                ('is_active', models.BooleanField(default=True, verbose_name='是否启用')),
                ('created_at', models.DateTimeField(auto_now_add=True, verbose_name='创建时间')),
                ('updated_at', models.DateTimeField(auto_now=True, verbose_name='更新时间')),
            ],
            options={
                'verbose_name': '前端查询配置',
                'verbose_name_plural': '前端查询配置',
                'db_table': 'query_configs',
            },
        ),
        migrations.CreateModel(
            name='QueryHistory',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('user_id', models.IntegerField(verbose_name='用户ID')),
                ('agent_id', models.IntegerField(blank=True, null=True, verbose_name='代理ID')),
                ('order_id', models.IntegerField(blank=True, null=True, verbose_name='关联订单ID')),
                ('authorization_letter_id', models.IntegerField(verbose_name='授权书ID')),
                ('encrypted_result', models.TextField(blank=True, verbose_name='加密查询结果')),
                ('result_hash', models.CharField(blank=True, max_length=64, verbose_name='结果哈希值')),
                ('query_status', models.CharField(choices=[('pending', '查询中'), ('success', '查询成功'), ('failed', '查询失败'), ('timeout', '查询超时')], default='pending', max_length=20, verbose_name='查询状态')),
                ('error_message', models.TextField(blank=True, verbose_name='错误信息')),
                ('cost_amount', models.DecimalField(decimal_places=2, default=0.0, max_digits=10, verbose_name='查询费用')),
                ('query_time', models.DateTimeField(auto_now_add=True, verbose_name='查询时间')),
                ('completed_time', models.DateTimeField(blank=True, null=True, verbose_name='完成时间')),
            ],
            options={
                'verbose_name': '查询历史记录',
                'verbose_name_plural': '查询历史记录',
                'db_table': 'query_histories',
            },
        ),
        migrations.CreateModel(
            name='RegularUser',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('openid', models.CharField(max_length=100, unique=True, verbose_name='微信OpenID')),
                ('phone', models.CharField(blank=True, max_length=11, verbose_name='手机号')),
                ('agent_id', models.IntegerField(blank=True, null=True, verbose_name='所属代理ID')),
                ('created_at', models.DateTimeField(auto_now_add=True, verbose_name='创建时间')),
            ],
            options={
                'verbose_name': '普通用户',
                'verbose_name_plural': '普通用户',
                'db_table': 'regular_users',
            },
        ),
        migrations.CreateModel(
            name='SystemConfig',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('logo', models.CharField(blank=True, max_length=500, verbose_name='Logo(URL或路径)')),
                ('site_title', models.CharField(blank=True, max_length=200, verbose_name='网站标题')),
                ('keywords', models.CharField(blank=True, max_length=500, verbose_name='关键词')),
                ('description', models.TextField(blank=True, verbose_name='描述')),
                ('show_query_price', models.BooleanField(default=True, verbose_name='是否显示查询价格')),
                ('query_entrance_desc', models.TextField(blank=True, verbose_name='查询入口描述(支持HTML)')),
                ('footer_copyright', models.TextField(blank=True, verbose_name='底部版权备案号(支持HTML)')),
                ('owner_id', models.IntegerField(verbose_name='所属用户ID')),
                ('owner_type', models.CharField(choices=[('admin', '管理员'), ('agent', '代理')], default='admin', max_length=10, verbose_name='所属用户类型')),
                ('created_at', models.DateTimeField(auto_now_add=True, verbose_name='创建时间')),
                ('updated_at', models.DateTimeField(auto_now=True, verbose_name='更新时间')),
            ],
            options={
                'verbose_name': '系统配置',
                'verbose_name_plural': '系统配置',
                'db_table': 'system_configs',
            },
        ),
        migrations.AddIndex(
            model_name='queryhistory',
            index=models.Index(fields=['user_id', 'query_time'], name='query_histo_user_id_d9955f_idx'),
        ),
        migrations.AddIndex(
            model_name='queryhistory',
            index=models.Index(fields=['agent_id', 'query_time'], name='query_histo_agent_i_a38368_idx'),
        ),
    ]
