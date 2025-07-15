from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.db import models
from django.utils import timezone
import uuid
import time
import random

# 普通用户表
class RegularUser(models.Model):
    """普通用户"""
    id = models.AutoField(primary_key=True)
    username = models.CharField(max_length=6, unique=True, blank=True, verbose_name='用户ID')
    openid = models.CharField(max_length=100, unique=True, blank=True, null=True, verbose_name='微信OpenID')
    phone = models.CharField(max_length=11, blank=True, verbose_name='手机号')
    agent_id = models.IntegerField(null=True, blank=True, verbose_name='所属代理ID')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    is_deactivated = models.BooleanField(default=False, verbose_name='是否已注销')
    deactivated_at = models.DateTimeField(null=True, blank=True, verbose_name='注销时间')
    
    class Meta:
        db_table = 'regular_users'
        verbose_name = '普通用户'
        verbose_name_plural = '普通用户'
    
    def __str__(self):
        return f"{self.username} - {self.openid}"

    @staticmethod
    def generate_unique_username():
        """生成一个唯一的6位随机数字用户名"""
        while True:
            new_username = str(random.randint(100000, 999999))
            if not RegularUser.objects.filter(username=new_username).exists():
                return new_username

    def save(self, *args, **kwargs):
        if not self.username:
            self.username = RegularUser.generate_unique_username()
        super().save(*args, **kwargs)
    
    @classmethod
    def get_date_filter(cls, date_range):
        """根据日期范围获取过滤条件"""
        from django.utils import timezone
        from datetime import timedelta
        
        now = timezone.now()
        
        if date_range == 'today':
            # 获取今天的开始和结束时间（UTC时间）
            today_start = now.replace(hour=0, minute=0, second=0, microsecond=0)
            today_end = today_start + timedelta(days=1)
            return {'created_at__gte': today_start, 'created_at__lt': today_end}
        elif date_range == '7d':
            return {'created_at__gte': now - timedelta(days=7)}
        elif date_range == '1m':
            return {'created_at__gte': now - timedelta(days=30)}
        elif date_range == '3m':
            return {'created_at__gte': now - timedelta(days=90)}
        elif date_range == '6m':
            return {'created_at__gte': now - timedelta(days=180)}
        else:  # all
            return {}

# 新增：短信验证码表
class SmsVerificationCode(models.Model):
    """短信验证码"""
    STATUS_CHOICES = [
        ('unused', '未使用'),
        ('used', '已使用'),
        ('expired', '已过期'),
    ]

    id = models.AutoField(primary_key=True)
    phone = models.CharField(max_length=20, db_index=True, verbose_name='手机号')
    code = models.CharField(max_length=6, verbose_name='验证码')
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='unused', verbose_name='状态')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    expires_at = models.DateTimeField(verbose_name='过期时间')
    used_at = models.DateTimeField(null=True, blank=True, verbose_name='使用时间')

    class Meta:
        db_table = 'sms_verification_codes'
        verbose_name = '短信验证码'
        verbose_name_plural = '短信验证码'

    def __str__(self):
        return f"{self.phone} - {self.code} ({self.get_status_display()})"


# 超级管理员表
class AdminUser(models.Model):
    """超级管理员"""
    id = models.AutoField(primary_key=True)
    company_name = models.CharField(max_length=200, verbose_name='公司名称')
    username = models.CharField(max_length=50, unique=True, verbose_name='用户名')
    password = models.CharField(max_length=255, verbose_name='密码')
    login_error_count = models.SmallIntegerField(default=0, verbose_name='登录错误次数')
    last_login_error_time = models.DateTimeField(null=True, blank=True, verbose_name='最后错误登录时间')
    is_locked = models.BooleanField(default=False, verbose_name='是否被锁定')
    lock_until = models.DateTimeField(null=True, blank=True, verbose_name='锁定到期时间')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    
    class Meta:
        db_table = 'admin_users'
        verbose_name = '超级管理员'
        verbose_name_plural = '超级管理员'
    
    def __str__(self):
        return f"{self.username} - {self.company_name}"
    
    def reset_error_count(self):
        """重置错误次数"""
        self.login_error_count = 0
        self.last_login_error_time = None
        self.is_locked = False
        self.lock_until = None
        self.save()
    
    def increment_error_count(self):
        """增加错误次数"""
        self.login_error_count += 1
        self.last_login_error_time = timezone.now()
        
        # 错误次数达到5次时锁定账户30分钟
        if self.login_error_count >= 5:
            self.is_locked = True
            self.lock_until = timezone.now() + timezone.timedelta(minutes=30)
        
        self.save()
    
    def is_account_locked(self):
        """检查账户是否被锁定"""
        if not self.is_locked:
            return False
        
        # 检查锁定是否已过期
        if self.lock_until and timezone.now() > self.lock_until:
            self.reset_error_count()
            return False
        
        return True

# 代理用户表
class AgentUser(models.Model):
    """代理用户"""
    id = models.AutoField(primary_key=True)
    username = models.CharField(max_length=50, unique=True, verbose_name='用户名')
    phone = models.CharField(max_length=20, blank=True, verbose_name='手机号')
    password = models.CharField(max_length=255, verbose_name='密码')
    domain_suffix = models.CharField(max_length=100, unique=True, verbose_name='域名后缀')
    
    # 权限控制
    can_customize_settings = models.BooleanField(default=False, verbose_name='允许自定义系统设置')
    
    # 定价设置
    personal_query_price = models.DecimalField(max_digits=10, decimal_places=2, default=0.00, verbose_name='个人查询最低价格')
    enterprise_query_min_price = models.DecimalField(max_digits=10, decimal_places=2, default=0.00, verbose_name='企业查询最低价格')
    
    # 收益统计
    total_profit = models.DecimalField(max_digits=12, decimal_places=2, default=0.00, verbose_name='累计收益')
    total_commission = models.DecimalField(max_digits=12, decimal_places=2, default=0.00, verbose_name='累计佣金')
    unsettled_commission = models.DecimalField(max_digits=12, decimal_places=2, default=0.00, verbose_name='未结算佣金')
    settled_commission = models.DecimalField(max_digits=12, decimal_places=2, default=0.00, verbose_name='累计结算佣金')

    # 登录与锁定
    login_error_count = models.SmallIntegerField(default=0, verbose_name='登录错误次数')
    last_login_error_time = models.DateTimeField(null=True, blank=True, verbose_name='最后错误登录时间')
    is_locked = models.BooleanField(default=False, verbose_name='是否被锁定')
    lock_until = models.DateTimeField(null=True, blank=True, verbose_name='锁定到期时间')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    
    class Meta:
        db_table = 'agent_users'
        verbose_name = '代理用户'
        verbose_name_plural = '代理用户'
    
    def __str__(self):
        return f"{self.username} - {self.domain_suffix}"
    
    def reset_error_count(self):
        """重置错误次数"""
        self.login_error_count = 0
        self.last_login_error_time = None
        self.is_locked = False
        self.lock_until = None
        self.save()
    
    def increment_error_count(self):
        """增加错误次数"""
        self.login_error_count += 1
        self.last_login_error_time = timezone.now()
        
        # 错误次数达到5次时锁定账户30分钟
        if self.login_error_count >= 5:
            self.is_locked = True
            self.lock_until = timezone.now() + timezone.timedelta(minutes=30)
        
        self.save()
    
    def is_account_locked(self):
        """检查账户是否被锁定"""
        if not self.is_locked:
            return False
        
        # 检查锁定是否已过期
        if self.lock_until and timezone.now() > self.lock_until:
            self.reset_error_count()
            return False
        
        return True

# 系统配置表
class SystemConfig(models.Model):
    """系统配置"""
    id = models.AutoField(primary_key=True)
    logo = models.CharField(max_length=500, blank=True, verbose_name='Logo(URL或路径)')
    site_title = models.CharField(max_length=200, blank=True, verbose_name='网站标题')
    company_name = models.CharField(max_length=200, blank=True, verbose_name='公司名称')  # 用于授权书等正式文件
    keywords = models.CharField(max_length=500, blank=True, verbose_name='关键词')
    description = models.TextField(blank=True, verbose_name='描述')
    show_query_price = models.BooleanField(default=True, verbose_name='是否显示查询价格')
    query_entrance_desc = models.TextField(blank=True, verbose_name='查询入口描述(支持HTML)')
    customer_service_url = models.CharField(max_length=500, blank=True, verbose_name='客服链接')
    force_wechat_access = models.BooleanField(default=False, verbose_name='仅支持微信生态打开')
    footer_copyright = models.TextField(blank=True, verbose_name='底部版权备案号(支持HTML)')
    owner_id = models.IntegerField(verbose_name='所属用户ID')  # 超级管理员或代理用户ID
    owner_type = models.CharField(max_length=10, choices=[('admin', '管理员'), ('agent', '代理')], default='admin', verbose_name='所属用户类型')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='更新时间')
    
    class Meta:
        db_table = 'system_configs'
        verbose_name = '系统配置'
        verbose_name_plural = '系统配置'
    
    def __str__(self):
        return f"{self.site_title} - {self.get_owner_type_display()}"

# API配置表
class ApiConfig(models.Model):
    """API配置表"""
    
    id = models.AutoField(primary_key=True)
    api_name = models.CharField(max_length=100, verbose_name='API名称')
    api_code = models.CharField(max_length=50, unique=True, verbose_name='API编号')
    owner_id = models.IntegerField(verbose_name='所属用户ID')
    owner_type = models.CharField(max_length=10, choices=[('admin', '管理员'), ('agent', '代理')], verbose_name='用户类型')
    cost_price = models.DecimalField(max_digits=10, decimal_places=2, default=0.00, verbose_name='成本价格')
    admin_cost_price = models.DecimalField(max_digits=10, decimal_places=2, default=0.00, verbose_name='管理员成本价格')
    is_active = models.BooleanField(default=True, verbose_name='是否启用')
    requires_mobile = models.BooleanField(default=False, verbose_name='是否需要手机号')
    
    # 新增：动态参数配置
    param_config = models.JSONField(default=dict, verbose_name='参数配置', help_text='JSON格式的参数配置')
    
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='更新时间')
    
    class Meta:
        db_table = 'api_configs'
        verbose_name = 'API配置'
        verbose_name_plural = 'API配置'
        indexes = [
            models.Index(fields=['owner_id', 'owner_type']),
            models.Index(fields=['api_code']),
            models.Index(fields=['is_active']),
        ]
    
    def __str__(self):
        return f"{self.api_name} ({self.api_code})"
    
    def get_param_config(self):
        """获取参数配置"""
        if not self.param_config:
            return {}
        return self.param_config
    
    def get_required_params(self):
        """获取必需参数列表"""
        config = self.get_param_config()
        return config.get('required_params', [])
    
    def get_optional_params(self):
        """获取可选参数列表"""
        config = self.get_param_config()
        return config.get('optional_params', [])
    
    def get_param_mapping(self):
        """获取参数映射关系"""
        config = self.get_param_config()
        return config.get('param_mapping', {})
    
    def get_default_values(self):
        """获取默认值配置"""
        config = self.get_param_config()
        return config.get('default_values', {})

# 前端查询配置表
class QueryConfig(models.Model):
    """前端查询配置"""

    CATEGORY_CHOICES = [
        ('two_factor', '二要素'),
        ('three_factor', '三要素'),
        ('face', '人脸'),
    ]

    id = models.AutoField(primary_key=True)
    config_name = models.CharField(max_length=100, verbose_name='配置名称')
    category = models.CharField(max_length=20, choices=CATEGORY_CHOICES, blank=True, null=True, verbose_name='查询配置类别')
    customer_price = models.DecimalField(max_digits=10, decimal_places=2, default=0.00, verbose_name='客户查询单价')
    api_combination = models.JSONField(verbose_name='查询搭配的接口')  # 存储接口ID列表
    owner_id = models.IntegerField(verbose_name='所属用户ID')
    owner_type = models.CharField(max_length=10, choices=[('admin', '管理员'), ('agent', '代理')], verbose_name='用户类型')
    is_active = models.BooleanField(default=True, verbose_name='是否启用')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='更新时间')
    
    class Meta:
        db_table = 'query_configs'
        verbose_name = '前端查询配置'
        verbose_name_plural = '前端查询配置'
    
    def __str__(self):
        return f"{self.config_name} - 所属: {self.get_owner_type_display()}"

# API接口配置表
class ExternalApiConfig(models.Model):
    """
    外部API接口配置（通用版）
    
    采用通用字段设计，通过JSON字段存储不同API的特定凭证，
    实现了高度的可扩展性，未来新增API无需修改数据库。
    """
    
    CONFIG_TYPE_CHOICES = [
        ('tianyuan_risk_api', '天远风险查询'),
        ('aliyun_sms', '阿里云短信'),
        ('wechat_oauth', '微信公众号登录'),
        ('alipay_payment', '支付宝支付'),
        ('wechat_payment', '微信支付'),
    ]
    
    id = models.AutoField(primary_key=True)
    config_type = models.CharField(max_length=50, choices=CONFIG_TYPE_CHOICES, verbose_name='配置类型')
    config_name = models.CharField(max_length=100, verbose_name='配置名称 (方便后台识别)')
    
    # 将所有敏感密钥加密后存入此JSON字段
    credentials = models.JSONField(verbose_name='加密凭证 (JSON格式)',default=None)
    
    # 关联到管理员或代理
    owner_id = models.IntegerField(verbose_name='所属用户ID', default=1)
    owner_type = models.CharField(max_length=10, choices=[('admin', '管理员'), ('agent', '代理')], default='admin', verbose_name='用户类型')
    
    is_active = models.BooleanField(default=True, verbose_name='是否启用')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='更新时间')
    
    class Meta:
        db_table = 'external_api_configs'
        verbose_name = '外部API接口配置'
        verbose_name_plural = '外部API接口配置'
        unique_together = ('config_type', 'owner_id', 'owner_type') # 每个所有者每种类型只能有一个配置
    
    def __str__(self):
        return f"{self.get_config_type_display()} - {self.config_name}"

# 订单表 (扩展版)
class Order(models.Model):
    """订单表"""
    
    STATUS_CHOICES = [
        ('pending', '待支付'),
        ('paid', '已支付'),
        ('querying', '查询中'),
        ('completed', '查询完成'),
        ('failed', '查询失败'),
        ('cancelled', '已取消'),
        ('refunded', '已退款'),
    ]
    
    id = models.AutoField(primary_key=True)
    order_no = models.CharField(max_length=50, unique=True, verbose_name='订单号')
    user_id = models.IntegerField(verbose_name='用户ID')
    agent_id = models.IntegerField(null=True, blank=True, verbose_name='代理ID')
    query_type = models.CharField(max_length=50, verbose_name='查询类型')
    amount = models.DecimalField(max_digits=10, decimal_places=2, verbose_name='订单金额')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending', verbose_name='订单状态')
    
    # 支付相关字段
    payment_method = models.CharField(max_length=20, null=True, blank=True, verbose_name='支付方式: alipay/wechat')
    payment_time = models.DateTimeField(null=True, blank=True, verbose_name='支付完成时间')
    third_party_order_id = models.CharField(max_length=100, null=True, blank=True, verbose_name='第三方订单号')
    third_party_trade_no = models.CharField(max_length=100, null=True, blank=True, verbose_name='第三方交易号')
    refund_time = models.DateTimeField(null=True, blank=True, verbose_name='退款时间')
    
    # 查询相关字段
    query_start_time = models.DateTimeField(null=True, blank=True, verbose_name='查询开始时间')
    query_complete_time = models.DateTimeField(null=True, blank=True, verbose_name='查询完成时间')
    query_config_id = models.IntegerField(null=True, blank=True, verbose_name='查询配置ID')
    
    # 代理佣金
    agent_commission = models.DecimalField(max_digits=10, decimal_places=2, default=0.00, verbose_name='代理佣金')
    
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='更新时间')
    
    class Meta:
        db_table = 'orders'
        verbose_name = '订单'
        verbose_name_plural = '订单'
        indexes = [
            models.Index(fields=['order_no']),
            models.Index(fields=['user_id', 'created_at']),
            models.Index(fields=['agent_id', 'created_at']),
            models.Index(fields=['status', 'created_at']),
        ]
    
    def __str__(self):
        return f"{self.order_no} - {self.amount}"
    
    def generate_order_no(self):
        """生成订单号"""
        import time
        import random
        timestamp = int(time.time() * 1000)
        random_num = random.randint(1000, 9999)
        return f"ORDER{timestamp}{random_num}"
    
    def save(self, *args, **kwargs):
        if not self.order_no:
            self.order_no = self.generate_order_no()
        super().save(*args, **kwargs)
    
    @classmethod
    def get_date_filter(cls, date_range):
        """根据日期范围获取过滤条件"""
        from django.utils import timezone
        from datetime import timedelta
        
        now = timezone.now()
        
        if date_range == 'today':
            # 获取今天的开始和结束时间（UTC时间）
            today_start = now.replace(hour=0, minute=0, second=0, microsecond=0)
            today_end = today_start + timedelta(days=1)
            return {'created_at__gte': today_start, 'created_at__lt': today_end}
        elif date_range == '7d':
            return {'created_at__gte': now - timedelta(days=7)}
        elif date_range == '6m':
            return {'created_at__gte': now - timedelta(days=180)}
        else:  # all
            return {}

# 查询结果表（用于历史记录和结果存储）
class QueryResult(models.Model):
    """查询结果表(用于历史记录和结果存储)"""
    
    STATUS_CHOICES = [
        ('processing', '处理中'),
        ('success', '成功'),
        ('failed', '失败'),
        ('timeout', '超时'),
    ]
    
    id = models.BigAutoField(primary_key=True)
    order_id = models.BigIntegerField(verbose_name='关联订单ID', null=True, blank=True)
    user_id = models.IntegerField(verbose_name='用户ID', null=True, blank=True)  # 普通用户ID
    agent_id = models.IntegerField(null=True, blank=True, verbose_name='代理ID')  # 代理商ID
    
    # 查询结果 (加密存储，定期删除)
    encrypted_result_data = models.TextField(null=True, blank=True, verbose_name='加密的查询结果')
    result_hash = models.CharField(max_length=64, null=True, blank=True, verbose_name='结果完整性校验')
    
    # 状态管理
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='processing', verbose_name='查询状态')
    error_message = models.TextField(null=True, blank=True, verbose_name='错误信息')
    
    # 费用信息
    cost_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0.00, verbose_name='查询费用')
    
    # 时间记录
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    completed_time = models.DateTimeField(null=True, blank=True, verbose_name='完成时间')
    expires_at = models.DateTimeField(verbose_name='过期时间(30天后自动过期)')
    is_expired = models.BooleanField(default=False, verbose_name='是否已过期')
    
    class Meta:
        db_table = 'query_results'
        verbose_name = '查询结果'
        verbose_name_plural = '查询结果'
        indexes = [
            models.Index(fields=['order_id']),
            models.Index(fields=['user_id', 'created_at']),  # 按用户和时间查询的索引
            models.Index(fields=['agent_id', 'created_at']),  # 按代理和时间查询的索引
            models.Index(fields=['expires_at']),
            models.Index(fields=['is_expired']),  # 过期状态索引
            models.Index(fields=['status', 'created_at']),
            models.Index(fields=['is_expired', 'expires_at']),  # 过期查询复合索引
        ]
    
    def __str__(self):
        return f"订单{self.order_id}的查询结果 - {self.get_status_display()}"
    
    def save(self, *args, **kwargs):
        if not self.expires_at:
            from django.utils import timezone
            from datetime import timedelta
            # 设置30天后过期
            self.expires_at = timezone.now() + timedelta(days=30)
        super().save(*args, **kwargs)
    
    @classmethod
    def cleanup_expired(cls):
        """清理过期的查询结果"""
        from django.utils import timezone
        # 标记已过期的记录
        expired_count = cls.objects.filter(
            expires_at__lt=timezone.now(),
            is_expired=False
        ).update(is_expired=True)
        return expired_count
    
    @classmethod
    def delete_expired(cls):
        """删除已过期的查询结果"""
        from django.utils import timezone
        # 删除已过期的记录
        deleted_count = cls.objects.filter(
            is_expired=True
        ).delete()
        return deleted_count[0] if deleted_count else 0
    
    @classmethod
    def get_date_filter(cls, date_range):
        """根据日期范围获取过滤条件"""
        from django.utils import timezone
        from datetime import timedelta
        
        now = timezone.now()
        
        if date_range == 'today':
            # 获取今天的开始和结束时间（UTC时间）
            today_start = now.replace(hour=0, minute=0, second=0, microsecond=0)
            today_end = today_start + timedelta(days=1)
            return {'created_at__gte': today_start, 'created_at__lt': today_end}
        elif date_range == '7d':
            return {'created_at__gte': now - timedelta(days=7)}
        elif date_range == '1m':
            return {'created_at__gte': now - timedelta(days=30)}
        elif date_range == '3m':
            return {'created_at__gte': now - timedelta(days=90)}
        elif date_range == '6m':
            return {'created_at__gte': now - timedelta(days=180)}
        else:  # all
            return {}
    
    @classmethod
    def mark_expired(cls):
        """标记过期的查询结果并清空结果数据"""
        from django.utils import timezone
        # 标记已过期的记录并清空结果数据
        expired_records = cls.objects.filter(
            expires_at__lt=timezone.now(),
            is_expired=False
        )
        
        expired_count = 0
        for record in expired_records:
            record.is_expired = True
            record.encrypted_result_data = '{}'  # 清空结果数据
            record.save()
            expired_count += 1
            
        return expired_count
    
    def is_result_expired(self):
        """检查当前结果是否已过期"""
        from django.utils import timezone
        return self.is_expired or (self.expires_at and timezone.now() > self.expires_at)
    
    def get_decrypted_result(self, encryption_key):
        """
        解密查询结果
        
        Args:
            encryption_key: AES解密密钥
            
        Returns:
            解密后的查询结果
        """
        # 检查是否已过期，过期记录返回空结果
        if self.is_expired or self.is_result_expired():
            return {}
        
        if not self.encrypted_result_data:
            return None
        
        try:
            # TODO: 数据解密位置 - 在这里实现AES解密逻辑
            # 解密方法：
            # 1. Base64解码加密数据
            # 2. 使用AES-CBC模式解密
            # 3. 去除PKCS#7填充
            # 4. 解析JSON数据
            
            from Crypto.Cipher import AES
            from Crypto.Util.Padding import unpad
            import base64
            import json
            
            encrypted_data = base64.b64decode(self.encrypted_result_data)
            cipher = AES.new(encryption_key.encode('utf-8'), AES.MODE_CBC)
            decrypted_data = unpad(cipher.decrypt(encrypted_data), AES.block_size)
            return json.loads(decrypted_data.decode('utf-8'))
        except Exception as e:
            return None
    
    def get_formatted_result(self, encryption_key=None):
        """
        获取格式化后的查询结果
        
        Args:
            encryption_key: AES解密密钥（如果数据是加密的）
            
        Returns:
            格式化后的查询结果
        """
        # 检查是否已过期，过期记录返回空结果
        if self.is_expired or self.is_result_expired():
            return {}
        
        # TODO: 数据格式化位置 - 在这里实现数据格式化逻辑
        # 格式化方法：
        # 1. 获取原始数据（解密或直接读取）
        # 2. 根据api_results中的api_code判断数据类型
        # 3. 对不同类型的API结果进行格式化：
        #    - 司法涉诉数据：提取案件信息、统计信息等
        #    - 借贷行为数据：提取借贷指标、风险等级等
        #    - 婚姻状况数据：提取婚姻状态、匹配结果等
        # 4. 返回结构化的格式化数据
        
        raw_data = self.get_decrypted_result(encryption_key) if encryption_key else self.encrypted_result_data
        
        if not raw_data:
            return None
        
        # 如果是字符串，尝试解析JSON
        if isinstance(raw_data, str):
            try:
                import json
                raw_data = json.loads(raw_data)
            except:
                return None
        
        # 这里可以添加具体的格式化逻辑
        return raw_data
    
    @staticmethod
    def encrypt_result(result_data, encryption_key):
        """
        加密查询结果
        
        Args:
            result_data: 要加密的结果数据
            encryption_key: AES加密密钥
            
        Returns:
            加密后的字符串
        """
        try:
            # TODO: 数据加密位置 - 在这里实现AES加密逻辑
            # 加密方法：
            # 1. 将数据转换为JSON字符串
            # 2. 使用AES-CBC模式加密
            # 3. 添加PKCS#7填充
            # 4. Base64编码
            
            from Crypto.Cipher import AES
            from Crypto.Util.Padding import pad
            from Crypto.Random import get_random_bytes
            import base64
            import json
            
            data_str = json.dumps(result_data, ensure_ascii=False)
            data_bytes = data_str.encode('utf-8')
            
            key = encryption_key.encode('utf-8')
            cipher = AES.new(key, AES.MODE_CBC)
            encrypted_data = cipher.encrypt(pad(data_bytes, AES.block_size))
            
            return base64.b64encode(encrypted_data).decode('utf-8')
        except Exception as e:
            return None

# 授权书表
class AuthorizationLetter(models.Model):
    """授权书表"""
    
    id = models.AutoField(primary_key=True)
    user_id = models.IntegerField(verbose_name='关联用户ID')  # 普通用户ID
    agent_id = models.IntegerField(null=True, blank=True, verbose_name='代理ID')  # 代理商ID
    
    # 脱敏信息
    masked_name = models.CharField(max_length=50,default='', verbose_name='脱敏姓名')  # 如：张*明
    masked_id_card = models.CharField(max_length=20,default='', verbose_name='脱敏身份证号')  # 如：110101****1234
    
    # 授权书内容
    authorization_content = models.TextField(verbose_name='授权书内容')  # 存储授权书的文本内容
    
    # 文件相关
    file_path = models.CharField(max_length=500, blank=True, verbose_name='授权书文件路径')  # 文件在服务器上的路径
    download_token = models.CharField(max_length=64, unique=True,default=None, verbose_name='下载令牌')  # 用于下载验证的token
    file_hash = models.CharField(max_length=64, blank=True, verbose_name='文件哈希值')  # 用于验证文件完整性
    
    # 状态
    is_valid = models.BooleanField(default=True, verbose_name='是否有效')
    
    # 时间
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='更新时间')
    
    class Meta:
        db_table = 'authorization_letters'
        verbose_name = '授权书'
        verbose_name_plural = '授权书'
        indexes = [
            models.Index(fields=['download_token']),
            models.Index(fields=['user_id', 'created_at']),
            models.Index(fields=['agent_id', 'created_at']),
        ]
    
    def __str__(self):
        return f"用户{self.user_id}的授权书 - {self.created_at.strftime('%Y-%m-%d %H:%M')}"
    
    def generate_download_token(self):
        """生成下载令牌"""
        import uuid
        import hashlib
        import time
        
        # 生成基于时间戳和随机数的token
        timestamp = str(int(time.time()))
        random_uuid = str(uuid.uuid4())
        token_base = f"{self.user_id}_{timestamp}_{random_uuid}"
        
        # 使用SHA256生成token
        token = hashlib.sha256(token_base.encode()).hexdigest()
        return token
    
    def save(self, *args, **kwargs):
        if not self.download_token:
            self.download_token = self.generate_download_token()
        super().save(*args, **kwargs)

# 滑块验证码记录
class SliderCaptcha(models.Model):
    """
    验证码模型（支持文字点击验证和滑块验证）
    
    主要用于记录验证码的生成和验证信息。目前系统主要使用文字点击验证码，
    即用户需要依次点击"天远数据"四个字来完成验证。
    
    验证码验证成功后的令牌可用于登录等需要验证的操作，有效期为10分钟。
    """
    
    id = models.BigAutoField(primary_key=True, verbose_name='ID')
    # 验证码唯一标识
    token = models.CharField(max_length=64, unique=True, verbose_name='验证令牌')
    # 背景图存储为Base64编码的图片数据
    bg_image = models.TextField(verbose_name='背景图片')
    # 滑块图片 (文字点击验证码不使用此字段)
    slider_image = models.TextField(blank=True, verbose_name='滑块图片')
    # 正确的位置信息(加密存储)
    # 对于文字点击验证码，存储的是四个字的坐标位置
    correct_position = models.CharField(max_length=255, verbose_name='正确位置')
    # 验证状态(是否已通过验证)
    is_verified = models.BooleanField(default=False, verbose_name='是否已验证')
    # 验证尝试次数(防止暴力破解)
    attempts = models.SmallIntegerField(default=0, verbose_name='尝试次数')
    # 最后一次尝试的IP地址
    last_attempt_ip = models.CharField(max_length=50, null=True, blank=True, verbose_name='最后尝试IP')
    # 客户端指纹，用于防止多设备共享验证码
    client_fingerprint = models.CharField(max_length=128, null=True, blank=True, verbose_name='客户端指纹')
    # 时间字段，使用时间戳便于比较
    create_time = models.BigIntegerField(verbose_name='创建时间(时间戳)')
    verify_time = models.BigIntegerField(null=True, blank=True, verbose_name='验证时间(时间戳)')
    expire_time = models.BigIntegerField(verbose_name='过期时间(时间戳)')
    
    class Meta:
        db_table = 'slider_captcha'
        verbose_name = '验证码'
        verbose_name_plural = '验证码'
        indexes = [
            models.Index(fields=['token'], name='idx_slider_token'),
            models.Index(fields=['create_time'], name='idx_slider_create_time'),
        ]
        
    def __str__(self):
        return f"验证码:{self.token[:8]}... ({'已验证' if self.is_verified else '未验证'})"
        
    def is_expired(self) -> bool:
        """检查验证码是否已过期"""
        return time.time() > self.expire_time
        
    @property
    def remaining_attempts(self) -> int:
        """获取剩余尝试次数，默认最多5次"""
        return max(0, 5 - self.attempts)
    
    def increment_attempts(self):
        """增加尝试次数"""
        self.attempts += 1
        self.save()
    
    def mark_verified(self):
        """标记为已验证"""
        self.is_verified = True
        self.verify_time = int(time.time())
        self.save()
    
    @classmethod
    def cleanup_expired(cls):
        """清理过期的验证码记录"""
        current_time = int(time.time())
        expired_count = cls.objects.filter(expire_time__lt=current_time).delete()
        return expired_count[0] if expired_count else 0

# 代理申请表
class AgentApplication(models.Model):
    """代理申请表"""
    
    CONTACT_TYPE_CHOICES = [
        ('wechat', '微信'),
        ('phone', '手机号'),
    ]
    
    id = models.AutoField(primary_key=True)
    user_id = models.IntegerField(verbose_name='关联用户ID',null=True, blank=True)  # 普通用户ID
    applicant_name = models.CharField(max_length=100, verbose_name='申请用户姓名')
    contact_type = models.CharField(max_length=10, choices=CONTACT_TYPE_CHOICES, verbose_name='联系方式类别')
    contact_info = models.CharField(max_length=100, verbose_name='联系方式')
    application_time = models.DateTimeField(auto_now_add=True, verbose_name='申请时间')
    
    class Meta:
        db_table = 'agent_applications'
        verbose_name = '代理申请'
        verbose_name_plural = '代理申请'
        indexes = [
            models.Index(fields=['user_id']),
            models.Index(fields=['application_time']),
            models.Index(fields=['contact_type']),
        ]
    
    def __str__(self):
        return f"用户{self.user_id}-{self.applicant_name} - {self.get_contact_type_display()}: {self.contact_info}"

# 代理收款配置表
class AgentPaymentConfig(models.Model):
    """代理收款方式配置"""
    PAYMENT_METHOD_CHOICES = [
        ('alipay', '支付宝'),
        ('wechat', '微信支付'),
    ]
    
    id = models.AutoField(primary_key=True)
    agent_id = models.IntegerField(unique=True, verbose_name='代理ID')  # 一个代理只能有一个收款配置
    payment_method = models.CharField(max_length=10, choices=PAYMENT_METHOD_CHOICES, verbose_name='收款方式')
    payment_account = models.CharField(max_length=100, verbose_name='收款账号')
    payment_name = models.CharField(max_length=50, verbose_name='收款人姓名')
    payment_qr_code = models.CharField(max_length=500, blank=True, verbose_name='收款码图片路径')
    
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='更新时间')
    
    class Meta:
        db_table = 'agent_payment_configs'
        verbose_name = '代理收款配置'
        verbose_name_plural = '代理收款配置'
        indexes = [
            models.Index(fields=['agent_id']),
        ]
    
    def __str__(self):
        return f"代理{self.agent_id}的{self.get_payment_method_display()}收款配置"

# 佣金提现申请表
class CommissionWithdrawal(models.Model):
    """佣金提现申请"""
    STATUS_CHOICES = [
        ('pending', '待处理'),
        ('completed', '已完成'),
        ('rejected', '已拒绝'),
    ]
    
    id = models.AutoField(primary_key=True)
    agent_id = models.IntegerField(verbose_name='代理ID')
    withdrawal_amount = models.DecimalField(max_digits=12, decimal_places=2, verbose_name='提现金额')
    
    # 申请时的快照数据
    unsettled_amount_snapshot = models.DecimalField(max_digits=12, decimal_places=2, verbose_name='申请时未结算金额')
    
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending', verbose_name='状态')
    admin_note = models.TextField(blank=True, verbose_name='管理员备注')
    
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='申请时间')
    completed_at = models.DateTimeField(null=True, blank=True, verbose_name='完成时间')
    
    class Meta:
        db_table = 'commission_withdrawals'
        verbose_name = '佣金提现申请'
        verbose_name_plural = '佣金提现申请'
        indexes = [
            models.Index(fields=['agent_id', 'created_at']),
            models.Index(fields=['status', 'created_at']),
        ]
    
    def __str__(self):
        return f"代理{self.agent_id}提现申请 - {self.withdrawal_amount}元 ({self.get_status_display()})"
