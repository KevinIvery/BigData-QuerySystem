"""
短信服务模块：提供短信验证码发送和验证功能
"""
import json
import time
import random
from typing import Tuple

from django.utils import timezone
from aliyunsdkcore.client import AcsClient
from aliyunsdkdysmsapi.request.v20170525.SendSmsRequest import SendSmsRequest

from .models import ExternalApiConfig, SmsVerificationCode

class SmsService:
    """
    短信发送服务
    - 从数据库动态加载配置
    - 包含发送和验证逻辑
    """
    def __init__(self, owner_id=1, owner_type='admin'):
        self.client = None
        self.config = None
        self.owner_id = owner_id
        self.owner_type = owner_type
        self.code_expire_seconds = 300  # 验证码5分钟有效
        self._load_config_and_init_client()

    def _load_config_and_init_client(self):
        """从数据库加载配置并初始化阿里云客户端"""
        try:
            # 首先尝试加载指定所有者的配置
            sms_config = ExternalApiConfig.objects.filter(
                config_type='aliyun_sms',
                owner_id=self.owner_id,
                owner_type=self.owner_type,
                is_active=True
            ).first()

            # 如果代理没有配置，回退到管理员配置
            if not sms_config and self.owner_type == 'agent':
                print(f"代理(ID: {self.owner_id})没有短信配置，回退到管理员配置")
                sms_config = ExternalApiConfig.objects.filter(
                    config_type='aliyun_sms',
                    owner_id=1,
                    owner_type='admin',
                    is_active=True
                ).first()

            if not sms_config:
                raise ValueError("未找到或未启用阿里云短信配置")

            credentials = sms_config.credentials
            if isinstance(credentials, str):
                credentials = json.loads(credentials)
            
            # 检查凭证完整性
            required_keys = ['app_id', 'app_secret', 'SignName', 'TemplateCode']
            if not all(k in credentials for k in required_keys):
                 raise ValueError("短信配置凭证不完整，缺少关键字段")

            self.config = credentials
            # 注意：旧版SDK初始化方式
            self.client = AcsClient(credentials['app_id'], credentials['app_secret'], 'cn-hangzhou')
            print(f"阿里云短信客户端初始化成功 - owner_id: {sms_config.owner_id}, owner_type: {sms_config.owner_type}")
        except Exception as e:
            print(f"初始化阿里云客户端失败: {str(e)}")
            # 向上抛出异常，让调用方知道初始化失败
            raise

    def _generate_code(self) -> str:
        """生成6位随机数字验证码"""
        return ''.join(random.choices('0123456789', k=6))

    def send_verification_code(self, phone: str) -> Tuple[bool, str]:
        """
        发送验证码，包含60秒内防刷机制
        """
        if not self.client:
            return False, "短信服务不可用，请检查系统配置"

        try:
            # 1. 频率控制：检查60秒内是否已发送过
            sixty_seconds_ago = timezone.now() - timezone.timedelta(seconds=60)
            if SmsVerificationCode.objects.filter(phone=phone, created_at__gte=sixty_seconds_ago).exists():
                return False, '操作过于频繁，请稍后再试'

            # 2. 生成新验证码
            code = self._generate_code()
            expires_at = timezone.now() + timezone.timedelta(seconds=self.code_expire_seconds)
            
            # 3. 准备发送请求
            request = SendSmsRequest()
            request.set_accept_format('json')
            request.set_PhoneNumbers(phone)
            request.set_SignName(self.config['SignName'])
            request.set_TemplateCode(self.config['TemplateCode'])
            request.set_TemplateParam(json.dumps({'code': code}))

            # 4. 调用API发送
            response = self.client.do_action_with_exception(request)
            response_dict = json.loads(response)

            # 5. 处理发送结果
            if response_dict.get('Code') == 'OK':
                # 让该手机号所有未使用的旧验证码失效
                SmsVerificationCode.objects.filter(phone=phone, status='unused').update(status='expired')
                # 保存新的验证码记录
                SmsVerificationCode.objects.create(
                    phone=phone,
                    code=code,
                    expires_at=expires_at
                )
                return True, '验证码发送成功'
            else:
                error_message = response_dict.get('Message', '未知错误')
                print(f"短信发送失败: {error_message}")
                return False, f'发送失败: {error_message}'

        except Exception as e:
            print(f"短信发送过程发生异常: {str(e)}")
            return False, '短信服务异常，请稍后重试'

    def verify_code(self, phone: str, code: str) -> Tuple[bool, str]:
        """验证短信验证码"""
        try:
            # 查找未使用且有效的验证码
            verification = SmsVerificationCode.objects.filter(
                phone=phone,
                code=code,
                status='unused'
            ).first()

            if not verification:
                return False, '验证码错误'

            # 检查是否过期
            if timezone.now() > verification.expires_at:
                verification.status = 'expired'
                verification.save()
                return False, '验证码已过期'

            # 验证成功，更新状态
            verification.status = 'used'
            verification.used_at = timezone.now()
            verification.save()
            
            return True, '验证成功'

        except Exception as e:
            print(f"验证过程发生异常: {str(e)}")
            return False, '验证失败，请稍后重试' 