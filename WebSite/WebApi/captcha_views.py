"""
验证码相关的视图函数
"""

import json
import logging
from django.http import HttpRequest
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from .response import ApiResponse, ResponseCode
from .models import SliderCaptcha
from .slider import CaptchaManager

logger = logging.getLogger(__name__)


@csrf_exempt
@require_http_methods(["POST"])
def generate_captcha(request: HttpRequest):
    """
    生成文字点击验证码
    
    Args:
        request: HTTP请求，可包含fingerprint客户端指纹
        
    Returns:
        验证码图片信息，包含token和背景图片
    """
    try:
        data = json.loads(request.body)
        client_fingerprint = data.get('fingerprint', '')
        
        print(f"请求生成验证码: fingerprint={client_fingerprint}")
        
        # 获取客户端IP
        client_ip = request.META.get('REMOTE_ADDR') or request.META.get('HTTP_X_FORWARDED_FOR', '').split(',')[0].strip()
        
        # 使用验证码管理器生成验证码
        captcha_manager = CaptchaManager()
        captcha_data = captcha_manager.generate_captcha(client_fingerprint, client_ip)
        
        if captcha_data is None:
            return ApiResponse.error(message="验证码生成失败", code=ResponseCode.SERVER_ERROR)
        
        # 返回验证码数据
        print(f"生成验证码成功: token={captcha_data.get('token')}")
        response = ApiResponse.success(data=captcha_data)
        return response
        
    except Exception as e:
        logger.error(f"生成验证码异常: {str(e)}")
        print(f"生成验证码异常: {str(e)}")
        return ApiResponse.error(message="验证码生成失败", code=ResponseCode.SERVER_ERROR)

@csrf_exempt
@require_http_methods(["POST"])
def verify_captcha(request: HttpRequest):
    """
    验证文字点击验证码
    
    Args:
        request: HTTP请求，包含token和用户点击位置
        
    Returns:
        验证结果
    """
    try:
        data = json.loads(request.body)
        token = data.get('token', '')
        clicks = data.get('clicks', [])
        
        # 获取客户端IP和指纹
        client_ip = request.META.get('REMOTE_ADDR') or request.META.get('HTTP_X_FORWARDED_FOR', '').split(',')[0].strip()
        client_fingerprint = data.get('fingerprint', '')
        
        print(f"验证码请求详情: token={token}, fingerprint={client_fingerprint}")
        print(f"点击数据: {json.dumps(clicks)}")
        
        # 从数据库查询验证码记录，打印详细信息
        try:
            captcha = SliderCaptcha.objects.get(token=token)
            print(f"找到验证码记录: token={token}, fingerprint={captcha.client_fingerprint}")
            print(f"验证码状态: is_verified={captcha.is_verified}, attempts={captcha.attempts}")
            
            # 解密验证码位置进行比对
            captcha_manager = CaptchaManager()
            expected_positions = captcha_manager._decrypt_positions(captcha.correct_position)
            print(f"预期位置: {expected_positions}")
            
            # 检查验证码是否已过期
            import time
            current_time = int(time.time())
            if current_time > captcha.expire_time:
                print(f"验证码已过期: 当前时间={current_time}, 过期时间={captcha.expire_time}")
            
            # 检查指纹是否一致
            if captcha.client_fingerprint != client_fingerprint:
                print(f"指纹不匹配: 验证码指纹={captcha.client_fingerprint}, 请求指纹={client_fingerprint}")
            
        except SliderCaptcha.DoesNotExist:
            print(f"找不到验证码记录: token={token}")
        
        # 使用验证码管理器验证
        captcha_manager = CaptchaManager()
        result, message = captcha_manager.verify_captcha(
            token,
            client_ip=client_ip,
            client_fingerprint=client_fingerprint,
            clicks=clicks
        )
        
        print(f"验证结果: success={result}, message={message}")
        
        if result:
            response = ApiResponse.success(message=message)
        else:
            response = ApiResponse.error(message=message, code=ResponseCode.CAPTCHA_ERROR)
        
        return response
        
    except Exception as e:
        print(f"验证码验证异常: {str(e)}")
        return ApiResponse.error(message="验证码验证失败", code=ResponseCode.SERVER_ERROR) 