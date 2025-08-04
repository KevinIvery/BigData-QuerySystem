import json
import time
import hashlib
import base64
from urllib.parse import urlencode
import requests
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import rsa, padding


class AlipayUtils:
    """支付宝工具类 - 使用open_id，跳过签名验证"""
    
    def __init__(self, app_id, app_private_key, alipay_public_key):
        self.app_id = app_id
        self.app_private_key = self._format_private_key(app_private_key)
        self.alipay_public_key = self._format_public_key(alipay_public_key)
        self.gateway_url = 'https://openapi.alipay.com/gateway.do'
        print(f"[AlipayUtils] 初始化完成，AppID: {app_id}")
    
    def _format_private_key(self, private_key):
        """格式化应用私钥"""
        if not private_key:
            return private_key
        
        # 移除可能的前后缀和换行符
        private_key = private_key.strip()
        private_key = private_key.replace('-----BEGIN PRIVATE KEY-----', '')
        private_key = private_key.replace('-----END PRIVATE KEY-----', '')
        private_key = private_key.replace('-----BEGIN RSA PRIVATE KEY-----', '')
        private_key = private_key.replace('-----END RSA PRIVATE KEY-----', '')
        private_key = private_key.replace('\n', '').replace('\r', '').replace(' ', '')
        
        # 添加标准格式
        formatted_key = f"-----BEGIN RSA PRIVATE KEY-----\n"
        # 每64个字符换行
        for i in range(0, len(private_key), 64):
            formatted_key += private_key[i:i+64] + "\n"
        formatted_key += "-----END RSA PRIVATE KEY-----"
        
        print(f"[AlipayUtils] 私钥格式化完成")
        return formatted_key
    
    def _format_public_key(self, public_key):
        """格式化支付宝公钥"""
        if not public_key:
            return public_key
        
        # 移除可能的前后缀和换行符
        public_key = public_key.strip()
        public_key = public_key.replace('-----BEGIN PUBLIC KEY-----', '')
        public_key = public_key.replace('-----END PUBLIC KEY-----', '')
        public_key = public_key.replace('\n', '').replace('\r', '').replace(' ', '')
        
        # 添加标准格式
        formatted_key = f"-----BEGIN PUBLIC KEY-----\n"
        # 每64个字符换行
        for i in range(0, len(public_key), 64):
            formatted_key += public_key[i:i+64] + "\n"
        formatted_key += "-----END PUBLIC KEY-----"
        
        print(f"[AlipayUtils] 公钥格式化完成")
        return formatted_key
    
    def _sign(self, params):
        """生成RSA2签名 - 使用cryptography库"""
        print(f"[AlipayUtils] 开始生成签名...")
        
        # 1. 参数排序
        sorted_params = sorted(params.items())
        print(f"[AlipayUtils] 排序后参数: {sorted_params}")
        
        # 2. 构建签名字符串
        sign_string = '&'.join([f"{k}={v}" for k, v in sorted_params])
        print(f"[AlipayUtils] 签名字符串: {sign_string}")
        
        # 3. 使用私钥签名
        try:
            # 使用cryptography库加载私钥
            private_key = serialization.load_pem_private_key(
                self.app_private_key.encode('utf-8'),
                password=None
            )
            
            # 使用RSA-SHA256签名
            signature = private_key.sign(
                sign_string.encode('utf-8'),
                padding.PKCS1v15(),
                hashes.SHA256()
            )
            
            # 4. Base64编码
            sign_result = base64.b64encode(signature).decode('utf-8')
            print(f"[AlipayUtils] 签名结果: {sign_result[:20]}...")
            
            return sign_result
        except Exception as e:
            print(f"[AlipayUtils] 签名生成失败: {str(e)}")
            print(f"[AlipayUtils] 私钥长度: {len(self.app_private_key)}")
            print(f"[AlipayUtils] 私钥前100字符: {self.app_private_key[:100]}")
            raise e
    
    def oauth_token(self, auth_code):
        """使用auth_code换取access_token和open_id"""
        print(f"[AlipayUtils] 开始调用alipay.system.oauth.token接口")
        print(f"[AlipayUtils] auth_code: {auth_code[:10]}...")
        
        # 构建公共参数 - 严格按照官方文档
        params = {
            'app_id': self.app_id,
            'method': 'alipay.system.oauth.token',
            'charset': 'utf-8',
            'sign_type': 'RSA2',
            'timestamp': time.strftime('%Y-%m-%d %H:%M:%S'),
            'version': '1.0',
            'grant_type': 'authorization_code',
            'code': auth_code
        }
        print(f"[AlipayUtils] 请求参数: {params}")
        
        # 生成签名
        params['sign'] = self._sign(params)
        print(f"[AlipayUtils] 完整请求参数: {params}")
        
        # 发送请求
        print(f"[AlipayUtils] 发送请求到: {self.gateway_url}")
        response = requests.post(self.gateway_url, data=params, timeout=10)
        print(f"[AlipayUtils] 响应状态码: {response.status_code}")
        print(f"[AlipayUtils] 响应内容: {response.text}")
        
        result = response.json()
        print(f"[AlipayUtils] 解析后响应: {result}")
        
        # 跳过签名验证，直接返回响应
        oauth_response = result.get('alipay_system_oauth_token_response', {})
        print(f"[AlipayUtils] oauth_token调用完成: {oauth_response}")
        return oauth_response
    
    def user_info_share(self, access_token):
        """获取用户信息"""
        print(f"[AlipayUtils] 开始调用alipay.user.info.share接口")
        print(f"[AlipayUtils] access_token: {access_token[:20]}...")
        
        # 构建公共参数 - 严格按照官方文档
        params = {
            'app_id': self.app_id,
            'method': 'alipay.user.info.share',
            'charset': 'utf-8',
            'sign_type': 'RSA2',
            'timestamp': time.strftime('%Y-%m-%d %H:%M:%S'),
            'version': '1.0',
            'auth_token': access_token
        }
        print(f"[AlipayUtils] 请求参数: {params}")
        
        # 生成签名
        params['sign'] = self._sign(params)
        print(f"[AlipayUtils] 完整请求参数: {params}")
        
        # 发送请求
        print(f"[AlipayUtils] 发送请求到: {self.gateway_url}")
        response = requests.post(self.gateway_url, data=params, timeout=10)
        print(f"[AlipayUtils] 响应状态码: {response.status_code}")
        print(f"[AlipayUtils] 响应内容: {response.text}")
        
        result = response.json()
        print(f"[AlipayUtils] 解析后响应: {result}")
        
        # 跳过签名验证，直接返回响应
        user_info_response = result.get('alipay_user_info_share_response', {})
        print(f"[AlipayUtils] user_info_share调用完成: {user_info_response}")
        return user_info_response