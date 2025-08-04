import json
import time
import hashlib
import base64
from urllib.parse import urlencode
from Crypto.PublicKey import RSA
from Crypto.Signature import pkcs1_15
from Crypto.Hash import SHA256
import requests


class AlipayUtils:
    """支付宝工具类"""
    
    def __init__(self, app_id, app_private_key, alipay_public_key):
        self.app_id = app_id
        self.app_private_key = app_private_key
        self.alipay_public_key = alipay_public_key
        self.gateway_url = 'https://openapi.alipay.com/gateway.do'
    
    def _sign(self, params):
        """生成RSA2签名"""
        # 1. 参数排序
        sorted_params = sorted(params.items())
        
        # 2. 构建签名字符串
        sign_string = '&'.join([f"{k}={v}" for k, v in sorted_params])
        
        # 3. 使用私钥签名
        private_key = RSA.import_key(self.app_private_key)
        h = SHA256.new(sign_string.encode('utf-8'))
        signature = pkcs1_15.new(private_key).sign(h)
        
        # 4. Base64编码
        return base64.b64encode(signature).decode('utf-8')
    
    def _verify_sign(self, params, sign):
        """验证签名"""
        # 移除sign和sign_type参数
        verify_params = {k: v for k, v in params.items() if k not in ['sign', 'sign_type']}
        
        # 构建签名字符串
        sorted_params = sorted(verify_params.items())
        sign_string = '&'.join([f"{k}={v}" for k, v in sorted_params])
        
        # 验证签名
        public_key = RSA.import_key(self.alipay_public_key)
        h = SHA256.new(sign_string.encode('utf-8'))
        try:
            pkcs1_15.new(public_key).verify(h, base64.b64decode(sign))
            return True
        except:
            return False
    
    def oauth_token(self, auth_code):
        """使用auth_code换取access_token和user_id"""
        # 构建业务参数
        biz_content = {
            'grant_type': 'authorization_code',
            'code': auth_code
        }
        
        # 构建公共参数
        params = {
            'app_id': self.app_id,
            'method': 'alipay.system.oauth.token',
            'format': 'JSON',
            'charset': 'utf-8',
            'sign_type': 'RSA2',
            'timestamp': time.strftime('%Y-%m-%d %H:%M:%S'),
            'version': '1.0',
            'biz_content': json.dumps(biz_content)
        }
        
        # 生成签名
        params['sign'] = self._sign(params)
        
        # 发送请求
        response = requests.post(self.gateway_url, data=params, timeout=10)
        result = response.json()
        
        # 验证响应签名
        oauth_response = result.get('alipay_system_oauth_token_response', {})
        sign = result.get('sign')
        
        if sign and not self._verify_sign(oauth_response, sign):
            raise Exception("支付宝响应签名验证失败")
        
        return oauth_response
    
    def user_info_share(self, access_token):
        """获取用户信息"""
        # 构建业务参数
        biz_content = {
            'auth_token': access_token
        }
        
        # 构建公共参数
        params = {
            'app_id': self.app_id,
            'method': 'alipay.user.info.share',
            'format': 'JSON',
            'charset': 'utf-8',
            'sign_type': 'RSA2',
            'timestamp': time.strftime('%Y-%m-%d %H:%M:%S'),
            'version': '1.0',
            'biz_content': json.dumps(biz_content)
        }
        
        # 生成签名
        params['sign'] = self._sign(params)
        
        # 发送请求
        response = requests.post(self.gateway_url, data=params, timeout=10)
        result = response.json()
        
        # 验证响应签名
        user_info_response = result.get('alipay_user_info_share_response', {})
        sign = result.get('sign')
        
        if sign and not self._verify_sign(user_info_response, sign):
            raise Exception("支付宝响应签名验证失败")
        
        return user_info_response 