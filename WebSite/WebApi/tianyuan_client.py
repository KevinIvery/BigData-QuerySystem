"""
天远API客户端

封装天远API的调用逻辑，包括：
1. 二要素验证（姓名+身份证）
2. 三要素验证（姓名+身份证+手机号）
3. 动态查询接口（根据API编号和参数查询）
"""

import json
import time
import base64
import hashlib
import requests
from django.conf import settings
from .models import ExternalApiConfig
import logging

logger = logging.getLogger(__name__)

# 尝试多种方式导入加密模块
try:
    # 尝试从pycryptodome导入
    from Crypto.Cipher import AES
    from Crypto.Util.Padding import pad, unpad
    from Crypto.Random import get_random_bytes
except ImportError:
    try:
        # 尝试从pycryptodomex导入
        from Cryptodome.Cipher import AES
        from Cryptodome.Util.Padding import pad, unpad
        from Cryptodome.Random import get_random_bytes
    except ImportError:
        # 如果都失败，使用自定义填充函数
        from Crypto.Cipher import AES
        from Crypto.Random import get_random_bytes
        
        def pad(data_to_pad, block_size):
            """
            使用PKCS#7填充数据
            """
            padding_len = block_size - (len(data_to_pad) % block_size)
            padding = bytes([padding_len]) * padding_len
            return data_to_pad + padding
            
        def unpad(padded_data, block_size):
            """
            移除PKCS#7填充
            """
            padding_len = padded_data[-1]
            if padding_len > block_size:
                raise ValueError("填充长度无效")
            if padding_len == 0:
                raise ValueError("填充长度不能为0")
            if not all(x == padding_len for x in padded_data[-padding_len:]):
                raise ValueError("填充数据无效")
            return padded_data[:-padding_len]

class TianyuanApiClient:
    """天远API客户端"""
    
    def __init__(self, owner_id=1, owner_type='admin'):
        """
        初始化天远API客户端
        
        Args:
            owner_id: 所有者ID
            owner_type: 所有者类型 ('admin' 或 'agent')
        """
        self.owner_id = owner_id
        self.owner_type = owner_type
        self.base_url = 'https://api.tianyuanapi.com'
        self.timeout = 30
        
        # 加载API配置
        self._load_config()
    
    def _load_config(self):
        """加载天远API配置"""
        try:
            config = ExternalApiConfig.objects.filter(
                config_type='tianyuan_risk_api',
                owner_id=self.owner_id,
                owner_type=self.owner_type,
                is_active=True
            ).first()
            
            if not config:
                raise Exception(f"未找到天远API配置 - owner_id: {self.owner_id}, owner_type: {self.owner_type}")
            
            credentials = config.credentials
            if isinstance(credentials, str):
                credentials = json.loads(credentials)
            
            self.app_id = credentials.get('app_id')
            self.app_secret = credentials.get('app_secret')
            
            # 检查是否有access_id和encryption_key（兼容你的另一个项目格式）
            self.access_id = credentials.get('access_id') or self.app_id
            self.encryption_key = credentials.get('encryption_key') or self.app_secret
            
            if not self.app_id or not self.app_secret:
                raise Exception("天远API配置不完整，缺少app_id或app_secret")
            
        except Exception as e:
            logger.error(f"天远API配置加载失败: {str(e)}")
            raise
    
    def verify_two_factor(self, name, id_card):
        """
        二要素验证（姓名+身份证）
        
        Args:
            name: 姓名
            id_card: 身份证号
            
        Returns:
            dict: 验证结果
            {
                'success': bool,
                'message': str,
                'data': dict,
                'match': bool  # 是否匹配
            }
        """
        try:
            # 二要素验证API编号
            api_code = 'YYSYBE08'
            
            # 二要素验证参数格式
            params = {
                'name': name,
                'id_card': id_card
            }
            
            result = self._call_api(api_code, params)
            
            if result['success']:
                # 根据天远API的返回格式判断是否匹配
                data = result.get('data', {})
                
                # 判断二要素是否匹配的逻辑
                match = False
                
                # 检查不同API的返回格式
                if api_code == 'YYSYBE08':
                    # 身份证二要素验证API的格式
                    ctid_request = data.get('ctidRequest', {})
                    ctid_auth = ctid_request.get('ctidAuth', {})
                    result_code = ctid_auth.get('resultCode', '')
                    
                    # 0XXX表示匹配成功
                    if result_code.startswith('0'):
                        match = True
                    
                elif api_code == 'YYSY09CD':
                    # 运营商三要素API的格式
                    if data.get('code') == '1000' or data.get('code') == 1000:
                        inner_data = data.get('data', {})
                        if inner_data.get('msg') == '一致' or inner_data.get('code') == 1000:
                            match = True
                
                return {
                    'success': True,
                    'message': '二要素验证完成',
                    'data': data,
                    'match': match
                }
            else:
                return {
                    'success': False,
                    'message': result.get('message', '二要素验证失败'),
                    'data': None,
                    'match': False
                }
                
        except Exception as e:
            logger.error(f"二要素验证异常: {str(e)}")
            return {
                'success': False,
                'message': f'二要素验证异常: {str(e)}',
                'data': None,
                'match': False
            }
    
    def verify_three_factor(self, name, id_card, mobile):
        """
        三要素验证（姓名+身份证+手机号）
        
        Args:
            name: 姓名
            id_card: 身份证号
            mobile: 手机号
            
        Returns:
            dict: 验证结果
            {
                'success': bool,
                'message': str,
                'data': dict,
                'match': bool  # 是否匹配
            }
        """
        try:
            # 三要素验证API编号
            api_code = 'YYSY09CD'
            
            # 三要素验证参数格式
            params = {
                'name': name,
                'id_card': id_card,
                'mobile_type': '',
                'mobile_no': mobile
            }
            
            result = self._call_api(api_code, params)
            
            if result['success']:
                # 根据天远API的返回格式判断是否匹配
                data = result.get('data', {})
                
                # 判断三要素是否匹配的逻辑
                match = False
                
                # 运营商三要素API的格式
                if data.get('code') == '1000' or data.get('code') == 1000:
                    # 检查内层数据
                    inner_data = data.get('data', {})
                    if inner_data.get('msg') == '一致' or inner_data.get('code') == 1000:
                        match = True
                
                return {
                    'success': True,
                    'message': '三要素验证完成',
                    'data': data,
                    'match': match
                }
            else:
                return {
                    'success': False,
                    'message': result.get('message', '三要素验证失败'),
                    'data': None,
                    'match': False
                }
                
        except Exception as e:
            logger.error(f"三要素验证异常: {str(e)}")
            return {
                'success': False,
                'message': f'三要素验证异常: {str(e)}',
                'data': None,
                'match': False
            }
    
    def query_by_api_code(self, api_code, params):
        """
        根据API编号动态查询
        
        Args:
            api_code: API编号（如：FLXGCA3D, QYGL8261等）
            params: 查询参数（根据不同API有不同的参数要求）
            
        Returns:
            dict: 查询结果
            {
                'success': bool,
                'message': str,
                'data': dict,
                'api_code': str,
                'api_name': str
            }
        """
        try:
            # 获取API名称（从数据库配置中获取）
            api_name = self._get_api_name_by_code(api_code)
            
            result = self._call_api(api_code, params)
            
            if result['success']:
                return {
                    'success': True,
                    'message': f'{api_name}查询完成',
                    'data': result.get('data', {}),
                    'api_code': api_code,
                    'api_name': api_name
                }
            else:
                return {
                    'success': False,
                    'message': result.get('message', f'{api_name}查询失败'),
                    'data': None,
                    'api_code': api_code,
                    'api_name': api_name
                }
                
        except Exception as e:
            logger.error(f"动态查询异常: {str(e)}")
            return {
                'success': False,
                'message': f'查询异常: {str(e)}',
                'data': None,
                'api_code': api_code,
                'api_name': self._get_api_name_by_code(api_code)
            }
    
    def _get_api_name_by_code(self, api_code):
        """根据API编号获取API名称"""
        try:
            from .models import ApiConfig
            api_config = ApiConfig.objects.filter(
                api_code=api_code,
                owner_id=self.owner_id,
                owner_type=self.owner_type,
                is_active=True
            ).first()
            
            if api_config:
                return api_config.api_name
            else:
                return f'未知接口({api_code})'
                
        except Exception as e:
            return f'未知接口({api_code})'
    
    def _call_api(self, api_code, params):
        """
        调用天远API
        
        Args:
            api_code: API编号
            params: 请求参数
            
        Returns:
            dict: API响应结果
        """
        try:
            start_time = time.time()
            
            # 将参数转换为JSON字符串
            params_json = json.dumps(params, ensure_ascii=False)
            
            # 对请求参数进行加密
            encrypted_data = self._encrypt_data(params_json)
            
            # 构建请求头
            headers = {
                'Content-Type': 'application/json',
                'Access-Id': self.app_id
            }
            
            # API请求地址
            url = f"{self.base_url}/api/v1/{api_code}"
            
            # 发送请求
            response = requests.post(
                url,
                json={'data': encrypted_data,'options':{'json': True}},
                headers=headers,
                timeout=self.timeout
            )
            
            # 计算请求耗时
            elapsed_time = (time.time() - start_time) * 1000
            
            # 检查响应状态码
            if response.status_code != 200:
                error_msg = f"API请求失败，状态码: {response.status_code}"
                return {
                    'success': False,
                    'code': response.status_code,
                    'message': error_msg,
                    'data': None
                }
            
            # 解析响应数据
            try:
                response_json = response.json()
            except json.JSONDecodeError:
                error_msg = "API响应不是有效的JSON格式"
                return {
                    'success': False,
                    'code': -3,
                    'message': error_msg,
                    'data': None
                }
            
            # 检查响应是否符合标准格式
            if 'code' not in response_json:
                # 可能是直接返回业务数据的API
                return {
                    'success': True,
                    'code': 0,
                    'message': '成功',
                    'data': response_json
                }
            
            # 标准API响应处理
            api_response_code = response_json.get('code')
            api_message = response_json.get('message', '')
            encrypted_response = response_json.get('data', '')
            
            # 判断API响应码
            if api_response_code != 0:
                error_msg = f"API响应错误: {api_message}"
                return {
                    'success': False,
                    'code': api_response_code,
                    'message': api_message,
                    'data': None
                }
            
            # 如果没有返回加密数据
            if not encrypted_response:
                return {
                    'success': True,
                    'code': 0,
                    'message': api_message,
                    'data': {}
                }
            
            # 解密响应数据
            try:
                decrypted_data = self._decrypt_data(encrypted_response)
                
                # 解析JSON
                result = json.loads(decrypted_data)
                
                # TODO: 在这里可以添加响应数据格式化逻辑
                # 格式化数据判断方法：
                # 1. 根据api_code判断数据类型（司法、借贷、婚姻等）
                # 2. 根据返回的data结构进行格式化
                # 3. 可以在这里添加数据清洗、字段映射等逻辑
                
                return {
                    'success': True,
                    'code': 0,
                    'message': api_message,
                    'data': result
                }
                
            except Exception as e:
                error_msg = f"响应数据解密或解析失败: {str(e)}"
                return {
                    'success': False,
                    'code': -2,
                    'message': error_msg,
                    'data': None
                }
            
        except Exception as e:
            error_msg = f"调用API异常: {str(e)}"
            logger.error(f"调用天远API异常: {str(e)}")
            return {
                'success': False,
                'code': -1,
                'message': error_msg,
                'data': None
            }
    
    def _encrypt_data(self, data):
        """
        AES-128-CBC加密数据
        
        Args:
            data: 要加密的字符串
            
        Returns:
            加密后的Base64字符串
        """
        try:
            # 将16进制密钥转换为字节
            key = bytes.fromhex(self.app_secret)
            
            # 生成随机IV（初始化向量）
            iv = get_random_bytes(16)
            
            # 创建AES-CBC加密器
            cipher = AES.new(key, AES.MODE_CBC, iv)
            
            # 对数据进行填充并加密
            padded_data = pad(data.encode('utf-8'), AES.block_size)
            encrypted_data = cipher.encrypt(padded_data)
            
            # 将IV和加密后的数据拼接，并进行Base64编码
            result = base64.b64encode(iv + encrypted_data).decode('utf-8')
            
            return result
        except Exception as e:
            raise
    
    def _decrypt_data(self, encrypted_data):
        """
        AES-128-CBC解密数据
        
        Args:
            encrypted_data: Base64编码的加密数据
            
        Returns:
            解密后的字符串
        """
        try:
            # 将16进制密钥转换为字节
            key = bytes.fromhex(self.app_secret)
            
            # Base64解码
            encrypted_bytes = base64.b64decode(encrypted_data)
            
            # 提取IV和加密数据
            iv = encrypted_bytes[:16]
            ciphertext = encrypted_bytes[16:]
            
            # 创建AES-CBC解密器
            cipher = AES.new(key, AES.MODE_CBC, iv)
            
            # 解密并去除填充
            padded_data = cipher.decrypt(ciphertext)
            decrypted_data = unpad(padded_data, AES.block_size).decode('utf-8')
            
            return decrypted_data
        except Exception as e:
            raise 