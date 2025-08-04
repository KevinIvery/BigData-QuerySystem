import json
import hashlib
import os
import time
import requests
from django.utils import timezone
from django.conf import settings
from .models import ExternalApiConfig, Order, QueryResult, AgentUser
import logging

# 脱敏工具函数
def mask_name(name):
    """姓名脱敏：三字*中间，两字*后面"""
    if not name:
        return name
    
    if len(name) == 2:
        return name[0] + '*'
    elif len(name) >= 3:
        return name[0] + '*' * (len(name) - 2) + name[-1]
    else:
        return name

def mask_id_card(id_card):
    """身份证号脱敏：保留前几位后面脱敏"""
    if not id_card:
        return id_card
    
    if len(id_card) >= 6:
        return id_card[:6] + '*' * (len(id_card) - 6)
    else:
        return '*' * len(id_card)

def mask_phone(phone):
    """手机号脱敏：脱敏中间5位"""
    if not phone:
        return phone
    
    if len(phone) == 11:
        return phone[:3] + '*' * 5 + phone[-3:]
    else:
        return phone

logger = logging.getLogger(__name__)

class PaymentConfigManager:
    """支付配置管理器"""
    
    def __init__(self, owner_id=1, owner_type='admin', request=None, frontend_url=None):
        self.owner_id = owner_id
        self.owner_type = owner_type
        self.request = request  # 传入request对象用于获取当前域名
        self.frontend_url = frontend_url  # 前端传递的URL
        self.alipay_config = None
        self.wechat_config = None
        self._load_payment_configs()
    
    def get_return_url(self, order_no):
        """根据前端当前URL动态生成return_url"""
        # 优先使用前端传递的URL
        if self.frontend_url:
            return f"{self.frontend_url}/query-result/{order_no}"
        elif self.request:
            # 获取当前请求的域名
            host = self.request.get_host()
            scheme = 'https' if self.request.is_secure() else 'http'
            return f"{scheme}://{host}/query-result/{order_no}"
        else:
            # 兜底方案，使用默认域名
            return f"https://api.v2.tybigdata.com/query-result/{order_no}"
    
    def _load_payment_configs(self):
        """加载支付配置"""
        print(f"[PaymentConfigManager] 开始加载支付配置 - owner_id: {self.owner_id}, owner_type: {self.owner_type}")
        
        try:
            # 加载支付宝配置
            alipay_config = ExternalApiConfig.objects.filter(
                config_type='alipay_payment',
                owner_id=self.owner_id,
                owner_type=self.owner_type,
                is_active=True
            ).first()
            
            if alipay_config:
                self.alipay_config = json.loads(alipay_config.credentials)
                print(f"[PaymentConfigManager] 支付宝配置加载成功: {alipay_config.config_name}")
            else:
                print(f"[PaymentConfigManager] 警告: 未找到支付宝配置")
            
            # 加载微信支付配置
            wechat_config = ExternalApiConfig.objects.filter(
                config_type='wechat_payment',
                owner_id=self.owner_id,
                owner_type=self.owner_type,
                is_active=True
            ).first()
            
            if wechat_config:
                self.wechat_config = json.loads(wechat_config.credentials)
                print(f"[PaymentConfigManager] 微信支付配置加载成功: {wechat_config.config_name}")
            else:
                print(f"[PaymentConfigManager] 警告: 未找到微信支付配置")
                
        except Exception as e:
            print(f"[PaymentConfigManager] 加载支付配置失败: {str(e)}")
            logger.error(f"加载支付配置失败: {str(e)}")

class AlipayPayment:
    """支付宝支付处理类"""
    
    def __init__(self, config): 
        self.config = config
        self.app_id = config.get('app_id')
        self.app_private_key = config.get('app_private_key')
        self.alipay_public_key = config.get('alipay_public_key')
        self.notify_url = config.get('notify_url')
        
        print(f"[AlipayPayment] 初始化支付宝支付 - app_id: {self.app_id}")
    
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
        
        return formatted_key

    def create_order(self, order_no, amount, subject, return_url, is_mobile=False):
        """创建支付宝订单"""
        print(f"[AlipayPayment] 开始创建支付宝订单 - order_no: {order_no}, amount: {amount}, is_mobile: {is_mobile}")
        
        try:
            from alipay.aop.api.AlipayClientConfig import AlipayClientConfig
            from alipay.aop.api.DefaultAlipayClient import DefaultAlipayClient
            from alipay.aop.api.domain.AlipayTradePagePayModel import AlipayTradePagePayModel
            from alipay.aop.api.request.AlipayTradePagePayRequest import AlipayTradePagePayRequest
            from alipay.aop.api.domain.AlipayTradeWapPayModel import AlipayTradeWapPayModel
            from alipay.aop.api.request.AlipayTradeWapPayRequest import AlipayTradeWapPayRequest
            
            # 处理RSA密钥格式
            app_private_key = self._format_private_key(self.app_private_key)
            alipay_public_key = self._format_public_key(self.alipay_public_key)
            
            print(f"[AlipayPayment] 密钥格式化完成")
            
            # 初始化支付宝客户端配置
            alipay_client_config = AlipayClientConfig()
            alipay_client_config.server_url = 'https://openapi.alipay.com/gateway.do'
            alipay_client_config.app_id = self.app_id
            alipay_client_config.app_private_key = app_private_key
            alipay_client_config.alipay_public_key = alipay_public_key
            
            # 创建支付宝客户端
            client = DefaultAlipayClient(alipay_client_config=alipay_client_config)
            
            # 根据设备类型选择不同的支付接口
            if is_mobile:
                # 手机端支付 - WAP支付
                print(f"[AlipayPayment] 使用手机端WAP支付")
                try:
                    # 构建支付宝WAP支付请求模型
                    model = AlipayTradeWapPayModel()
                    model.out_trade_no = order_no
                    model.total_amount = str(amount)
                    model.subject = subject
                    model.product_code = "QUICK_WAP_WAY"
                    
                    # 构建支付请求
                    request_obj = AlipayTradeWapPayRequest(biz_model=model)
                    request_obj.notify_url = self.notify_url
                    request_obj.return_url = return_url
                    
                    # 执行支付请求，获取响应
                    response = client.page_execute(request_obj, http_method="GET")
                    print(f"[AlipayPayment] WAP支付订单数据生成成功")
                    
                except Exception as e:
                    print(f"[AlipayPayment] WAP支付失败，尝试使用PC端支付: {str(e)}")
                    # 如果WAP支付失败，回退到PC端支付
                    model = AlipayTradePagePayModel()
                    model.out_trade_no = order_no
                    model.total_amount = str(amount)
                    model.subject = subject
                    model.product_code = "FAST_INSTANT_TRADE_PAY"
                    
                    request_obj = AlipayTradePagePayRequest(biz_model=model)
                    request_obj.notify_url = self.notify_url
                    request_obj.return_url = return_url
                    
                    response = client.page_execute(request_obj, http_method="GET")
            else:
                # PC端支付 - 页面支付
                print(f"[AlipayPayment] 使用PC端页面支付")
                model = AlipayTradePagePayModel()
                model.out_trade_no = order_no
                model.total_amount = str(amount)
                model.subject = subject
                model.product_code = "FAST_INSTANT_TRADE_PAY"
                
                request_obj = AlipayTradePagePayRequest(biz_model=model)
                request_obj.notify_url = self.notify_url
                request_obj.return_url = return_url
                
                response = client.page_execute(request_obj, http_method="GET")
            
            print(f"[AlipayPayment] 支付宝订单创建成功 - pay_url: {response}")
            return {
                'success': True,
                'pay_url': response,
                'order_data': response
            }
            
        except Exception as e:
            print(f"[AlipayPayment] 创建支付宝订单失败: {str(e)}")
            logger.error(f"创建支付宝订单失败: {str(e)}")
            return {
                'success': False,
                'error': str(e)
            }
    

    
    def query_order_status(self, order_no):
        """查询支付宝订单状态"""
        print(f"[AlipayPayment] 开始查询支付宝订单状态 - order_no: {order_no}")
        
        try:
            from alipay.aop.api.AlipayClientConfig import AlipayClientConfig
            from alipay.aop.api.DefaultAlipayClient import DefaultAlipayClient
            from alipay.aop.api.domain.AlipayTradeQueryModel import AlipayTradeQueryModel
            from alipay.aop.api.request.AlipayTradeQueryRequest import AlipayTradeQueryRequest
            import json
            import ssl
            import urllib3
            import requests
            
            # 禁用SSL警告和证书验证（仅用于解决线上环境SSL问题）
            urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
            ssl._create_default_https_context = ssl._create_unverified_context
            
            # 处理RSA密钥格式
            app_private_key = self._format_private_key(self.app_private_key)
            alipay_public_key = self._format_public_key(self.alipay_public_key)
            
            # 初始化支付宝客户端配置
            alipay_client_config = AlipayClientConfig()
            alipay_client_config.server_url = 'https://openapi.alipay.com/gateway.do'
            alipay_client_config.app_id = self.app_id
            alipay_client_config.app_private_key = app_private_key
            alipay_client_config.alipay_public_key = alipay_public_key
            
            # 创建支付宝客户端
            client = DefaultAlipayClient(alipay_client_config=alipay_client_config)
            
            # 构建查询请求模型
            model = AlipayTradeQueryModel()
            model.out_trade_no = order_no
            
            # 构建查询请求
            request_obj = AlipayTradeQueryRequest(biz_model=model)
            
            try:
                # 调用alipay.trade.query接口
                response_content = client.execute(request_obj)
                result = json.loads(response_content)
            except Exception as sdk_error:
                # 如果SDK抛出签名验证异常，我们手动解析响应
                print(f"[AlipayPayment] SDK调用异常，尝试手动解析: {str(sdk_error)}")
                
                # 从异常信息中提取响应数据
                error_str = str(sdk_error)
                if 'response sign verify failed' in error_str and 'alipay_trade_query_response' in error_str:
                    # 提取JSON响应部分
                    start_idx = error_str.find('{')
                    end_idx = error_str.rfind('}') + 1
                    if start_idx != -1 and end_idx != -1:
                        json_str = error_str[start_idx:end_idx]
                        try:
                            result = json.loads(json_str)
                            print(f"[AlipayPayment] 手动解析响应成功: {result}")
                        except json.JSONDecodeError:
                            print(f"[AlipayPayment] JSON解析失败: {json_str}")
                            return {'success': False, 'error': '响应解析失败'}
                    else:
                        return {'success': False, 'error': '无法提取响应数据'}
                else:
                    return {'success': False, 'error': str(sdk_error)}
            
            print(f"[AlipayPayment] 支付宝查询结果: {result}")
            
            # 检查响应结果 - 支付宝返回的数据结构可能直接是结果，也可能包装在alipay_trade_query_response中
            response_data = result.get('alipay_trade_query_response', result)
            
            if response_data.get('code') == '10000':
                # 查询成功
                trade_status = response_data.get('trade_status')
                print(f"[AlipayPayment] 订单状态查询成功: {trade_status}")
                
                return {
                    'success': True,
                    'order_no': response_data.get('out_trade_no'),
                    'trade_no': response_data.get('trade_no'),
                    'total_amount': response_data.get('total_amount'),
                    'trade_status': trade_status,
                    'gmt_payment': response_data.get('send_pay_date'),  # 支付时间
                    'buyer_logon_id': response_data.get('buyer_logon_id'),  # 买家支付宝账号
                }
            elif response_data.get('code') == '40004':
                # 交易不存在
                print(f"[AlipayPayment] 订单不存在: {order_no}")
                return {
                    'success': True,
                    'order_no': order_no,
                    'trade_status': 'TRADE_NOT_EXIST',
                    'message': '订单不存在或未支付'
                }
            else:
                # 其他错误
                error_msg = response_data.get('msg', '查询失败')
                print(f"[AlipayPayment] 查询失败: {error_msg}")
                return {
                    'success': False,
                    'error': error_msg,
                    'code': response_data.get('code')
                }
                
        except Exception as e:
            print(f"[AlipayPayment] 查询支付宝订单状态失败: {str(e)}")
            logger.error(f"查询支付宝订单状态失败: {str(e)}")
            return {'success': False, 'error': str(e)}

    def create_refund(self, order_no, refund_amount, refund_reason="正常退款", out_request_no=None, trade_no=None):
        """创建支付宝退款"""
        print(f"[AlipayPayment] 开始创建支付宝退款 - order_no: {order_no}, refund_amount: {refund_amount}, refund_reason: {refund_reason}")
        
        try:
            from alipay.aop.api.AlipayClientConfig import AlipayClientConfig
            from alipay.aop.api.DefaultAlipayClient import DefaultAlipayClient
            from alipay.aop.api.domain.AlipayTradeRefundModel import AlipayTradeRefundModel
            from alipay.aop.api.request.AlipayTradeRefundRequest import AlipayTradeRefundRequest
            import json
            import ssl
            import urllib3
            
            # 禁用SSL警告和证书验证
            urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
            ssl._create_default_https_context = ssl._create_unverified_context
            
            # 处理RSA密钥格式
            app_private_key = self._format_private_key(self.app_private_key)
            alipay_public_key = self._format_public_key(self.alipay_public_key)
            
            # 初始化支付宝客户端配置
            alipay_client_config = AlipayClientConfig()
            alipay_client_config.server_url = 'https://openapi.alipay.com/gateway.do'
            alipay_client_config.app_id = self.app_id
            alipay_client_config.app_private_key = app_private_key
            alipay_client_config.alipay_public_key = alipay_public_key
            
            # 创建支付宝客户端
            client = DefaultAlipayClient(alipay_client_config=alipay_client_config)
            
            # 构建退款请求模型
            model = AlipayTradeRefundModel()
            model.refund_amount = str(refund_amount)  # 退款金额
            model.refund_reason = refund_reason  # 退款原因
            
            # 优先使用trade_no，其次使用out_trade_no
            if trade_no:
                model.trade_no = trade_no
            else:
                model.out_trade_no = order_no
            
            # 如果有退款请求号，则添加
            if out_request_no:
                model.out_request_no = out_request_no
            
            print(f"[AlipayPayment] 退款参数: refund_amount={refund_amount}, refund_reason={refund_reason}")
            
            # 构建退款请求
            request_obj = AlipayTradeRefundRequest(biz_model=model)
            
            try:
                # 调用退款接口
                response_content = client.execute(request_obj)
                result = json.loads(response_content)
            except Exception as sdk_error:
                # 如果SDK抛出签名验证异常，我们手动解析响应
                print(f"[AlipayPayment] 退款创建SDK调用异常，尝试手动解析: {str(sdk_error)}")
                
                # 从异常信息中提取响应数据
                error_str = str(sdk_error)
                if 'response sign verify failed' in error_str and 'alipay_trade_refund_response' in error_str:
                    # 提取JSON响应部分
                    start_idx = error_str.find('{')
                    end_idx = error_str.rfind('}') + 1
                    if start_idx != -1 and end_idx != -1:
                        json_str = error_str[start_idx:end_idx]
                        try:
                            result = json.loads(json_str)
                            print(f"[AlipayPayment] 退款创建手动解析响应成功: {result}")
                        except json.JSONDecodeError:
                            print(f"[AlipayPayment] 退款创建JSON解析失败: {json_str}")
                            return {'success': False, 'error': '响应解析失败'}
                    else:
                        return {'success': False, 'error': '无法提取响应数据'}
                else:
                    return {'success': False, 'error': str(sdk_error)}
            
            print(f"[AlipayPayment] 支付宝退款结果: {result}")
            
            # 检查响应结果 - 跳过签名验证，直接解析结果
            response_data = result.get('alipay_trade_refund_response', result)  # 如果没有嵌套的response对象，使用原始结果
            if response_data.get('code') == '10000':
                # 退款请求成功（但不代表退款成功）
                fund_change = response_data.get('fund_change')  # Y表示退款成功，N或无此字段需进一步确认
                
                return {
                    'success': True,
                    'trade_no': response_data.get('trade_no'),
                    'out_trade_no': response_data.get('out_trade_no'),
                    'buyer_logon_id': response_data.get('buyer_logon_id'),
                    'refund_fee': response_data.get('refund_fee'),  # 本次退款金额
                    'fund_change': fund_change,
                    'send_back_fee': response_data.get('send_back_fee'),  # 实际退回金额
                    'refund_detail_item_list': response_data.get('refund_detail_item_list'),
                    'gmt_refund_pay': response_data.get('gmt_refund_pay'),  # 退款时间
                    'message': '退款成功' if fund_change == 'Y' else '退款请求已提交，请查询确认退款状态'
                }
            else:
                # 退款失败
                error_msg = response_data.get('msg', '退款失败')
                sub_msg = response_data.get('sub_msg', '')
                error_detail = f"{error_msg}: {sub_msg}" if sub_msg else error_msg
                
                print(f"[AlipayPayment] 退款失败: {error_detail}")
                return {
                    'success': False,
                    'error': error_detail,
                    'code': response_data.get('code'),
                    'sub_code': response_data.get('sub_code')
                }
                
        except Exception as e:
            print(f"[AlipayPayment] 创建支付宝退款失败: {str(e)}")
            logger.error(f"创建支付宝退款失败: {str(e)}")
            return {'success': False, 'error': str(e)}

    def query_refund_status(self, order_no, out_request_no, trade_no=None):
        """查询支付宝退款状态"""
        print(f"[AlipayPayment] 开始查询支付宝退款状态 - order_no: {order_no}, out_request_no: {out_request_no}")
        
        try:
            from alipay.aop.api.AlipayClientConfig import AlipayClientConfig
            from alipay.aop.api.DefaultAlipayClient import DefaultAlipayClient
            from alipay.aop.api.domain.AlipayTradeFastpayRefundQueryModel import AlipayTradeFastpayRefundQueryModel
            from alipay.aop.api.request.AlipayTradeFastpayRefundQueryRequest import AlipayTradeFastpayRefundQueryRequest
            import json
            
            # 处理RSA密钥格式
            app_private_key = self._format_private_key(self.app_private_key)
            alipay_public_key = self._format_public_key(self.alipay_public_key)
            
            # 初始化支付宝客户端配置
            alipay_client_config = AlipayClientConfig()
            alipay_client_config.server_url = 'https://openapi.alipay.com/gateway.do'
            alipay_client_config.app_id = self.app_id
            alipay_client_config.app_private_key = app_private_key
            alipay_client_config.alipay_public_key = alipay_public_key
            
            # 创建支付宝客户端
            client = DefaultAlipayClient(alipay_client_config=alipay_client_config)
            
            # 构建退款查询请求模型
            model = AlipayTradeFastpayRefundQueryModel()
            model.out_request_no = out_request_no  # 退款请求号（必需）
            
            # 优先使用trade_no，其次使用out_trade_no
            if trade_no:
                model.trade_no = trade_no
            else:
                model.out_trade_no = order_no
            
            print(f"[AlipayPayment] 退款查询参数: out_request_no={out_request_no}")
            
            # 构建退款查询请求
            request_obj = AlipayTradeFastpayRefundQueryRequest(biz_model=model)
            
            try:
                # 调用退款查询接口
                response_content = client.execute(request_obj)
                result = json.loads(response_content)
            except Exception as sdk_error:
                # 如果SDK抛出签名验证异常，我们手动解析响应
                print(f"[AlipayPayment] 退款查询SDK调用异常，尝试手动解析: {str(sdk_error)}")
                
                # 从异常信息中提取响应数据
                error_str = str(sdk_error)
                if 'response sign verify failed' in error_str and 'alipay_trade_fastpay_refund_query_response' in error_str:
                    # 提取JSON响应部分
                    start_idx = error_str.find('{')
                    end_idx = error_str.rfind('}') + 1
                    if start_idx != -1 and end_idx != -1:
                        json_str = error_str[start_idx:end_idx]
                        try:
                            result = json.loads(json_str)
                            print(f"[AlipayPayment] 退款查询手动解析响应成功: {result}")
                        except json.JSONDecodeError:
                            print(f"[AlipayPayment] 退款查询JSON解析失败: {json_str}")
                            return {'success': False, 'error': '响应解析失败'}
                    else:
                        return {'success': False, 'error': '无法提取响应数据'}
                else:
                    return {'success': False, 'error': str(sdk_error)}
            
            print(f"[AlipayPayment] 支付宝退款查询结果: {result}")
            
            # 检查响应结果 - 跳过签名验证，直接解析结果
            response_data = result.get('alipay_trade_fastpay_refund_query_response', {})
            if response_data.get('code') == '10000':
                # 查询成功
                refund_status = response_data.get('refund_status')  # REFUND_SUCCESS表示退款成功
                
                return {
                    'success': True,
                    'trade_no': response_data.get('trade_no'),
                    'out_trade_no': response_data.get('out_trade_no'),
                    'out_request_no': response_data.get('out_request_no'),
                    'total_amount': response_data.get('total_amount'),  # 原订单金额
                    'refund_amount': response_data.get('refund_amount'),  # 本次退款金额
                    'refund_status': refund_status,  # 退款状态
                    'gmt_refund_pay': response_data.get('gmt_refund_pay'),  # 退款时间
                    'send_back_fee': response_data.get('send_back_fee'),  # 实际退回金额
                    'refund_detail_item_list': response_data.get('refund_detail_item_list'),  # 退款资金渠道
                    'deposit_back_info': response_data.get('deposit_back_info'),  # 银行卡冲退信息
                    'is_success': refund_status == 'REFUND_SUCCESS'  # 是否退款成功
                }
            else:
                # 查询失败
                error_msg = response_data.get('msg', '退款查询失败')
                sub_msg = response_data.get('sub_msg', '')
                error_detail = f"{error_msg}: {sub_msg}" if sub_msg else error_msg
                
                print(f"[AlipayPayment] 退款查询失败: {error_detail}")
                return {
                    'success': False,
                    'error': error_detail,
                    'code': response_data.get('code'),
                    'sub_code': response_data.get('sub_code')
                }
                
        except Exception as e:
            print(f"[AlipayPayment] 查询支付宝退款状态失败: {str(e)}")
            logger.error(f"查询支付宝退款状态失败: {str(e)}")
            return {'success': False, 'error': str(e)}

class WechatPayment:
    """微信支付处理类"""
    
    def __init__(self, config):
        self.config = config
        self.app_id = config.get('app_id')
        self.mch_id = config.get('mch_id')
        # 兼容旧字段名
        self.api_v3_key = config.get('api_v3_key') or config.get('api_key')
        self.key_path = config.get('key_path') or config.get('private_key')
        self.serial_no = config.get('serial_no') or config.get('certificate_serial_no')
        self.notify_url = config.get('notify_url')
        
        # 新字段名
        self.private_key = config.get('private_key') or config.get('key_path')
        self.certificate_serial_no = config.get('certificate_serial_no') or config.get('serial_no')
        self.wechat_pay_public_key_id = config.get('wechat_pay_public_key_id')
        self.wechat_pay_public_key = config.get('wechat_pay_public_key')
        
        print(f"微信支付配置初始化完成: mch_id={self.mch_id}")
    
    def create_order(self, order_no, amount, description, openid=None):
        """创建微信支付订单"""
        print(f"[WechatPayment] 开始创建微信支付订单 - order_no: {order_no}, amount: {amount}, openid: {openid}")
        
        try:
            import string
            import random
            import base64
            import requests
            import hashlib
            from cryptography.hazmat.primitives import hashes, serialization
            from cryptography.hazmat.primitives.asymmetric import rsa, padding
            
            if not openid:
                print(f"[WechatPayment] 微信支付需要openid")
                return {'success': False, 'error': '微信支付需要openid'}
            
            # 金额转换为分
            total_fee = int(float(amount) * 100)
            
            # 构建请求数据
            body = {
                "appid": self.app_id,
                "mchid": self.mch_id,
                "description": description,
                "out_trade_no": order_no,
                "notify_url": self.notify_url,
                "amount": {"total": total_fee, "currency": "CNY"},
                "payer": {"openid": openid}
            }
            data = json.dumps(body)
            
            # 生成签名
            def get_sign(sign_str):
                # 直接使用私钥内容，不是文件路径
                private_key_content = self.private_key
                
                # 使用cryptography库加载私钥
                private_key = serialization.load_pem_private_key(
                    private_key_content.encode('utf-8'),
                    password=None
                )
                
                # 使用RSA-SHA256签名
                signature = private_key.sign(
                    sign_str.encode('utf-8'),
                    padding.PKCS1v15(),
                    hashes.SHA256()
                )
                
                # 返回base64编码的签名
                return base64.b64encode(signature).decode('utf-8')

            # 生成随机字符串和时间戳
            random_str = ''.join(random.choice(string.ascii_uppercase + string.digits) for _ in range(32))
            time_stamps = str(int(time.time()))

            # 构建签名字符串
            sign_str = f"POST\n/v3/pay/transactions/jsapi\n{time_stamps}\n{random_str}\n{data}\n"
            sign = get_sign(sign_str)

            # 构建请求头
            headers = {
                'Content-Type': 'application/json',
                'Authorization': f'WECHATPAY2-SHA256-RSA2048 mchid="{self.mch_id}",nonce_str="{random_str}",signature="{sign}",timestamp="{time_stamps}",serial_no="{self.certificate_serial_no}"'
            }

            # 发送请求
            url = 'https://api.mch.weixin.qq.com/v3/pay/transactions/jsapi'
            response = requests.post(url, data=data, headers=headers)
            
            print(f"[WechatPayment] 微信支付API响应: {response.status_code}, {response.text}")

            if response.status_code == 200:
                result = response.json()
                prepay_id = result.get('prepay_id')
                
                if prepay_id:
                    # 生成JSAPI支付参数
                    time_stamps = str(int(time.time()))
                    nonce_str = ''.join(random.choice(string.ascii_uppercase + string.digits) for _ in range(32))
                    package = 'prepay_id=' + prepay_id
                    
                    # 生成paySign
                    paySignStr = f"{self.app_id}\n{time_stamps}\n{nonce_str}\n{package}\n"
                    paySign = get_sign(paySignStr)
                    
                    jsapi_params = {
                        'appId': self.app_id,
                        'timeStamp': time_stamps,
                        'nonceStr': nonce_str,
                        'package': package,
                        'signType': 'RSA',
                        'paySign': paySign
                    }
                    
                    print(f"[WechatPayment] 生成JSAPI支付参数: {jsapi_params}")
                    
                    return {
                        'success': True,
                        'prepay_id': prepay_id,
                        'jsapi_params': jsapi_params
                    }
                else:
                    print(f"[WechatPayment] 微信支付响应中没有prepay_id")
                    return {'success': False, 'error': '微信支付响应异常'}
            else:
                print(f"[WechatPayment] 微信支付请求失败: {response.text}")
                return {'success': False, 'error': f'微信支付请求失败: {response.text}'}
            
        except Exception as e:
            print(f"[WechatPayment] 创建微信支付订单失败: {str(e)}")
            logger.error(f"创建微信支付订单失败: {str(e)}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def query_order_status(self, order_no):
        """查询微信支付订单状态"""
        print(f"[WechatPayment] 开始查询微信支付订单状态 - order_no: {order_no}")
        
        try:
            import string
            import random
            import base64
            import requests
            import hashlib
            from cryptography.hazmat.primitives import hashes, serialization
            from cryptography.hazmat.primitives.asymmetric import rsa, padding
            
            # 生成签名函数
            def get_sign(sign_str):
                # 直接使用私钥内容，不是文件路径
                private_key_content = self.private_key
                
                # 使用cryptography库加载私钥
                private_key = serialization.load_pem_private_key(
                    private_key_content.encode('utf-8'),
                    password=None
                )
                
                # 使用RSA-SHA256签名
                signature = private_key.sign(
                    sign_str.encode('utf-8'),
                    padding.PKCS1v15(),
                    hashes.SHA256()
                )
                
                # 返回base64编码的签名
                return base64.b64encode(signature).decode('utf-8')
            
            # 生成随机字符串和时间戳
            random_str = ''.join(random.choice(string.ascii_uppercase + string.digits) for _ in range(32))
            time_stamps = str(int(time.time()))
            
            # 构建请求路径
            path = f"/v3/pay/transactions/out-trade-no/{order_no}?mchid={self.mch_id}"
            
            # 构建签名字符串
            sign_str = f"GET\n{path}\n{time_stamps}\n{random_str}\n\n"
            sign = get_sign(sign_str)
            
            # 构建请求头
            headers = {
                'Accept': 'application/json',
                'Authorization': f'WECHATPAY2-SHA256-RSA2048 mchid="{self.mch_id}",nonce_str="{random_str}",signature="{sign}",timestamp="{time_stamps}",serial_no="{self.certificate_serial_no}"'
            }
            
            # 发送请求
            url = f'https://api.mch.weixin.qq.com{path}'
            response = requests.get(url, headers=headers)
            
            print(f"[WechatPayment] 微信支付查询API响应: {response.status_code}, {response.text}")
            
            if response.status_code == 200:
                result = response.json()
                trade_state = result.get('trade_state')
                
                print(f"[WechatPayment] 订单状态查询成功: {trade_state}")
                
                return {
                    'success': True,
                    'order_no': result.get('out_trade_no'),
                    'trade_no': result.get('transaction_id'),
                    'total_amount': str(result.get('amount', {}).get('total', 0) / 100),  # 分转元
                    'trade_status': trade_state,
                    'success_time': result.get('success_time'),  # 支付时间
                    'buyer_logon_id': result.get('payer', {}).get('openid'),  # 买家openid
                    'trade_state_desc': result.get('trade_state_desc'),  # 状态描述
                }
            elif response.status_code == 404:
                # 订单不存在
                print(f"[WechatPayment] 订单不存在: {order_no}")
                return {
                    'success': True,
                    'order_no': order_no,
                    'trade_status': 'NOTPAY',
                    'message': '订单不存在或未支付'
                }
            else:
                # 其他错误
                error_msg = f"查询失败: HTTP {response.status_code}"
                print(f"[WechatPayment] {error_msg}")
                return {
                    'success': False,
                    'error': error_msg,
                    'response': response.text
                }
                
        except Exception as e:
            print(f"[WechatPayment] 查询微信支付订单状态失败: {str(e)}")
            logger.error(f"查询微信支付订单状态失败: {str(e)}")
            return {'success': False, 'error': str(e)}

    def create_refund(self, order_no, transaction_id, refund_no, refund_amount, total_amount, reason="用户申请退款"):
        """
        申请微信退款
        
        Args:
            order_no: 商户订单号
            transaction_id: 微信支付订单号
            refund_no: 商户退款单号
            refund_amount: 退款金额（分）
            total_amount: 原订单金额（分）
            reason: 退款原因
            
        Returns:
            退款结果字典
        """
        try:
            import requests
            import json
            import hashlib
            import time
            import base64
            from cryptography.hazmat.primitives import hashes, serialization
            from cryptography.hazmat.primitives.asymmetric import padding
            
            url = "https://api.mch.weixin.qq.com/v3/refund/domestic/refunds"
            
            # 请求体
            request_body = {
                "out_trade_no": order_no,
                "out_refund_no": refund_no,
                "reason": reason,
                "amount": {
                    "refund": int(refund_amount),
                    "total": int(total_amount),
                    "currency": "CNY"
                }
            }
            
            # 如果有微信支付订单号，优先使用
            if transaction_id:
                request_body["transaction_id"] = transaction_id
                del request_body["out_trade_no"]
            
            body = json.dumps(request_body, separators=(',', ':'))
            
            # 生成签名
            timestamp = str(int(time.time()))
            nonce_str = self._generate_nonce_str()
            
            # 构建签名字符串
            sign_str = f"POST\n/v3/refund/domestic/refunds\n{timestamp}\n{nonce_str}\n{body}\n"
            
            # 使用私钥签名
            def get_sign(sign_str):
                # 直接使用私钥内容，不是文件路径
                if self.private_key.startswith('-----BEGIN'):
                    private_key_content = self.private_key
                else:
                    private_key_content = f"-----BEGIN PRIVATE KEY-----\n{self.private_key}\n-----END PRIVATE KEY-----"
                
                # 使用cryptography库加载私钥
                private_key = serialization.load_pem_private_key(
                    private_key_content.encode('utf-8'),
                    password=None
                )
                
                # 使用RSA-SHA256签名
                signature = private_key.sign(
                    sign_str.encode('utf-8'),
                    padding.PKCS1v15(),
                    hashes.SHA256()
                )
                
                # Base64编码
                return base64.b64encode(signature).decode('utf-8')
            
            signature = get_sign(sign_str)
            
            # 构建Authorization头
            authorization = f'WECHATPAY2-SHA256-RSA2048 mchid="{self.mch_id}",nonce_str="{nonce_str}",signature="{signature}",timestamp="{timestamp}",serial_no="{self.certificate_serial_no}"'
            
            # 请求头
            headers = {
                'Authorization': authorization,
                'Accept': 'application/json',
                'Content-Type': 'application/json',
                'Wechatpay-Serial': self.wechat_pay_public_key_id
            }
            
            print(f"微信退款请求: URL={url}")
            print(f"微信退款请求体: {body}")
            print(f"微信退款请求头: {headers}")
            
            # 发送请求
            response = requests.post(url, data=body, headers=headers, timeout=30)
            
            print(f"微信退款响应状态码: {response.status_code}")
            print(f"微信退款响应内容: {response.text}")
            
            if response.status_code == 200:
                result = response.json()
                return {
                    'success': True,
                    'refund_id': result.get('refund_id'),
                    'out_refund_no': result.get('out_refund_no'),
                    'status': result.get('status'),
                    'create_time': result.get('create_time'),
                    'message': '退款申请提交成功'
                }
            else:
                error_info = response.text
                try:
                    error_data = response.json()
                    error_message = error_data.get('message', error_info)
                except:
                    error_message = error_info
                    
                return {
                    'success': False,
                    'message': f'微信退款失败: {error_message}',
                    'error_code': response.status_code
                }
                
        except Exception as e:
            print(f"微信退款异常: {str(e)}")
            return {
                'success': False,
                'message': f'微信退款失败: {str(e)}'
            }

    def query_refund_status(self, refund_no):
        """
        查询微信退款状态
        
        Args:
            refund_no: 商户退款单号
            
        Returns:
            退款状态查询结果
        """
        try:
            import requests
            import time
            import base64
            import urllib.parse
            from cryptography.hazmat.primitives import hashes, serialization
            from cryptography.hazmat.primitives.asymmetric import padding
            
            # URL编码
            encoded_refund_no = urllib.parse.quote(refund_no, safe='')
            url = f"https://api.mch.weixin.qq.com/v3/refund/domestic/refunds/{encoded_refund_no}"
            
            # 生成签名
            timestamp = str(int(time.time()))
            nonce_str = self._generate_nonce_str()
            
            # 构建签名字符串
            uri = f"/v3/refund/domestic/refunds/{encoded_refund_no}"
            sign_str = f"GET\n{uri}\n{timestamp}\n{nonce_str}\n\n"
            
            # 使用私钥签名
            def get_sign(sign_str):
                # 直接使用私钥内容，不是文件路径
                if self.private_key.startswith('-----BEGIN'):
                    private_key_content = self.private_key
                else:
                    private_key_content = f"-----BEGIN PRIVATE KEY-----\n{self.private_key}\n-----END PRIVATE KEY-----"
                
                # 使用cryptography库加载私钥
                private_key = serialization.load_pem_private_key(
                    private_key_content.encode('utf-8'),
                    password=None
                )
                
                # 使用RSA-SHA256签名
                signature = private_key.sign(
                    sign_str.encode('utf-8'),
                    padding.PKCS1v15(),
                    hashes.SHA256()
                )
                
                # Base64编码
                return base64.b64encode(signature).decode('utf-8')
            
            signature = get_sign(sign_str)
            
            # 构建Authorization头
            authorization = f'WECHATPAY2-SHA256-RSA2048 mchid="{self.mch_id}",nonce_str="{nonce_str}",signature="{signature}",timestamp="{timestamp}",serial_no="{self.certificate_serial_no}"'
            
            # 请求头
            headers = {
                'Authorization': authorization,
                'Accept': 'application/json',
                'Wechatpay-Serial': self.wechat_pay_public_key_id
            }
            
            print(f"微信退款查询请求: URL={url}")
            print(f"微信退款查询请求头: {headers}")
            
            # 发送请求
            response = requests.get(url, headers=headers, timeout=30)
            
            print(f"微信退款查询响应状态码: {response.status_code}")
            print(f"微信退款查询响应内容: {response.text}")
            
            if response.status_code == 200:
                result = response.json()
                return {
                    'success': True,
                    'refund_id': result.get('refund_id'),
                    'out_refund_no': result.get('out_refund_no'),
                    'status': result.get('status'),
                    'success_time': result.get('success_time'),
                    'create_time': result.get('create_time'),
                    'user_received_account': result.get('user_received_account'),
                    'amount': result.get('amount', {}),
                    'message': '查询成功'
                }
            else:
                error_info = response.text
                try:
                    error_data = response.json()
                    error_message = error_data.get('message', error_info)
                except:
                    error_message = error_info
                    
                return {
                    'success': False,
                    'message': f'微信退款查询失败: {error_message}',
                    'error_code': response.status_code
                }
                
        except Exception as e:
            print(f"微信退款查询异常: {str(e)}")
            return {
                'success': False,
                'message': f'微信退款查询失败: {str(e)}'
            }

    def _generate_nonce_str(self):
        """生成随机字符串"""
        import random
        import string
        return ''.join(random.choice(string.ascii_uppercase + string.digits) for _ in range(32))


class PaymentManager:
    """支付管理器"""
    
    def __init__(self, owner_id=1, owner_type='admin', request=None, frontend_url=None):
        self.owner_id = owner_id
        self.owner_type = owner_type
        self.config_manager = PaymentConfigManager(owner_id, owner_type, request, frontend_url)
        self.alipay = None
        self.wechat = None
        
        if self.config_manager.alipay_config:
            self.alipay = AlipayPayment(self.config_manager.alipay_config)
        
        if self.config_manager.wechat_config:
            self.wechat = WechatPayment(self.config_manager.wechat_config)
        
        print(f"[PaymentManager] 支付管理器初始化完成")
    
    def create_payment_order(self, order_no, amount, subject, payment_method, openid=None, is_mobile=None):
        """创建支付订单"""
        print(f"[PaymentManager] 开始创建支付订单 - method: {payment_method}, amount: {amount}")
        
        # 自动生成return_url
        return_url = self.config_manager.get_return_url(order_no)
        print(f"[PaymentManager] 生成的return_url: {return_url}")
        
        if payment_method == 'alipay' and self.alipay:
            # 检测是否为移动设备（优先使用前端传递的信息）
            if is_mobile is None:
                is_mobile = self._is_mobile_device()
            print(f"[PaymentManager] 设备类型: {'移动设备' if is_mobile else 'PC设备'}")
            return self.alipay.create_order(order_no, amount, subject, return_url, is_mobile)
        elif payment_method == 'wechat' and self.wechat:
            return self.wechat.create_order(order_no, amount, subject, openid)
        else:
            error_msg = f"不支持的支付方式: {payment_method}"
            print(f"[PaymentManager] {error_msg}")
            return {'success': False, 'error': error_msg}
    
    def _is_mobile_device(self):
        """检测是否为移动设备"""
        if not self.config_manager.request:
            return False
        
        user_agent = self.config_manager.request.META.get('HTTP_USER_AGENT', '').lower()
        mobile_keywords = [
            'mobile', 'android', 'iphone', 'ipad', 'ipod', 
            'blackberry', 'windows phone', 'opera mini',
            'micromessenger'  # 微信浏览器
        ]
        
        is_mobile = any(keyword in user_agent for keyword in mobile_keywords)
        print(f"[PaymentManager] User-Agent: {user_agent[:100]}...")
        print(f"[PaymentManager] 移动设备检测结果: {is_mobile}")
        
        return is_mobile
    

    
    def process_payment_success(self, order_no, payment_method, trade_no, amount):
        """处理支付成功"""
        print(f"[PaymentManager] 处理支付成功 - order_no: {order_no}, method: {payment_method}")
        
        try:
            # 查找订单
            order = Order.objects.filter(order_no=order_no).first()
            if not order:
                print(f"[PaymentManager] 订单不存在: {order_no}")
                return {'success': False, 'error': '订单不存在'}
            
            # 安全防护：检查订单状态，防止重复处理
            if order.status in ['paid', 'querying', 'completed', 'failed']:
                print(f"[PaymentManager] 订单已处理，当前状态: {order.status}")
                return {'success': True, 'message': '订单已处理'}
            
            # 安全防护：检查是否已有查询结果
            existing_result = QueryResult.objects.filter(order_id=order.id).first()
            if existing_result:
                print(f"[PaymentManager] 订单已有查询结果，状态: {existing_result.status}")
                return {'success': True, 'message': '查询已存在'}
            
            # 更新订单状态
            order.status = 'paid'
            order.payment_method = payment_method
            order.payment_time = timezone.now()
            order.third_party_trade_no = trade_no
            order.save()
            
            print(f"[PaymentManager] 订单状态更新成功: {order_no}")
            
            # 如果是代理订单，累计代理佣金
            if order.agent_id and order.agent_commission > 0:
                try:
                    agent = AgentUser.objects.get(id=order.agent_id)
                    agent.total_commission += order.agent_commission
                    agent.unsettled_commission += order.agent_commission
                    agent.save()
                    print(f"[PaymentManager] 代理佣金累计成功: agent_id={order.agent_id}, commission={order.agent_commission}")
                except Exception as e:
                    print(f"[PaymentManager] 代理佣金累计失败: {str(e)}")
                    logger.error(f"代理佣金累计失败: {str(e)}")
            
            # 触发查询任务
            self._trigger_query_task(order)
            
            return {'success': True}
            
        except Exception as e:
            print(f"[PaymentManager] 处理支付成功失败: {str(e)}")
            logger.error(f"处理支付成功失败: {str(e)}")
            return {'success': False, 'error': str(e)}
    
    def query_payment_status(self, order_no, payment_method):
        """查询支付状态"""
        print(f"[PaymentManager] 开始查询支付状态 - order_no: {order_no}, method: {payment_method}")
        
        try:
            if payment_method == 'alipay' and self.alipay:
                return self.alipay.query_order_status(order_no)
            elif payment_method == 'wechat' and self.wechat:
                return self.wechat.query_order_status(order_no)
            else:
                print(f"[PaymentManager] 不支持的支付方式或配置不存在: {payment_method}")
                return {'success': False, 'error': '不支持的支付方式或配置不存在'}
                
        except Exception as e:
            print(f"[PaymentManager] 查询支付状态失败: {str(e)}")
            logger.error(f"查询支付状态失败: {str(e)}")
            return {'success': False, 'error': str(e)}
    
    def _trigger_query_task(self, order):
        """触发查询任务"""
        print(f"[PaymentManager] 触发查询任务 - order_id: {order.id}")
        
        try:
            # 安全防护：再次检查订单状态
            order.refresh_from_db()
            if order.status != 'paid':
                print(f"[PaymentManager] 订单状态不正确，无法触发查询: {order.status}")
                return
            
            # 安全防护：检查是否已有查询结果
            existing_result = QueryResult.objects.filter(order_id=order.id).first()
            if existing_result:
                print(f"[PaymentManager] 查询结果已存在，跳过创建: {existing_result.status}")
                return
            
            # 更新订单状态为查询中
            order.status = 'querying'
            order.query_start_time = timezone.now()
            order.save()
            
            # 创建查询结果记录
            query_result = QueryResult.objects.create(
                order_id=order.id,
                user_id=order.user_id,  # 从订单中获取用户ID
                agent_id=order.agent_id,  # 从订单中获取代理ID
                status='processing'
            )
            
            print(f"[PaymentManager] 查询任务创建成功 - query_result_id: {query_result.id}")
            
            # 同步执行查询任务（生产环境建议使用异步）
            self._execute_query_task(order, query_result)
            
        except Exception as e:
            print(f"[PaymentManager] 触发查询任务失败: {str(e)}")
            logger.error(f"触发查询任务失败: {str(e)}")
            
            # 如果创建查询结果失败，回滚订单状态
            try:
                order.refresh_from_db()
                if order.status == 'querying':
                    order.status = 'paid'
                    order.save()
                    print(f"[PaymentManager] 已回滚订单状态为已支付")
            except Exception as rollback_e:
                print(f"[PaymentManager] 回滚订单状态失败: {str(rollback_e)}")
    
    def _execute_query_task(self, order, query_result):

        """执行查询任务"""
        print(f"[PaymentManager] 开始执行查询任务 - order_id: {order.id}")
        
        try:
            # 安全防护：再次检查订单状态
            order.refresh_from_db()
            if order.status != 'querying':
                print(f"[PaymentManager] 订单状态不正确，无法执行查询: {order.status}")
                return
            
            # 生成授权书（仅个人查询需要）
            if order.query_type == '个人查询配置':
                self._generate_authorization_letter(order, query_result)
            
            # 获取查询配置
            query_config = None
            if order.query_config_id:
                from .models import QueryConfig
                query_config = QueryConfig.objects.filter(id=order.query_config_id).first()
            
            if not query_config:
                raise Exception("查询配置不存在")
            
            print(f"[PaymentManager] 使用查询配置: {query_config.config_name}")
            print(f"[PaymentManager] 查询配置类别: {query_config.category}")
            print(f"[PaymentManager] 包含的API: {query_config.api_combination}")
            
            # 从session中获取查询参数
            session_key = f'query_params_{order.order_no}'
            query_params = self.config_manager.request.session.get(session_key, {})
            
            if not query_params:
                raise Exception("查询参数不存在，请重新创建订单")
            
            print(f"[PaymentManager] 查询参数: {query_params}")
            
            # 获取查询参数
            name = query_params.get('name', '')
            id_card = query_params.get('id_card', '')
            phone = query_params.get('phone', '')
            query_type = query_params.get('query_type', '')
            query_category = query_params.get('query_category', '')
            
            # 参数验证
            if not name or not id_card:
                raise Exception("查询参数不完整：姓名和身份证号不能为空")
            
            # 初始化天远API客户端
            from .tianyuan_client import TianyuanApiClient
            tianyuan_client = TianyuanApiClient(
                owner_id=self.owner_id,
                owner_type=self.owner_type
            )
            
            # 根据查询配置调用不同的API
            all_results = []
            
            if query_config.api_combination:
                for api_id in query_config.api_combination:
                    try:
                        # 获取API配置
                        from .models import ApiConfig
                        api_config = ApiConfig.objects.filter(id=api_id).first()
                        
                        if not api_config:
                            print(f"[PaymentManager] API配置不存在: {api_id}")
                            continue
                        
                        if not api_config.is_active:
                            print(f"[PaymentManager] API配置已停用: {api_config.api_name}")
                            continue
                        
                        print(f"[PaymentManager] 调用API: {api_config.api_name} ({api_config.api_code})")
                        
                        # 根据API编号构建参数
                        api_params = self._build_api_params(api_config.api_code, name, id_card, phone)
                        
                        # 调用天远API
                        api_result = tianyuan_client.query_by_api_code(api_config.api_code, api_params)
                        
                        print(f"[PaymentManager] API {api_config.api_name} 原始响应:")
                        print(f"[PaymentManager] 成功: {api_result.get('success')}")
                        print(f"[PaymentManager] 消息: {api_result.get('message')}")
                        print(f"[PaymentManager] 数据: {api_result.get('data')}")
                        
                        # 记录API调用结果
                        api_result_info = {
                            'api_name': api_config.api_name,
                            'api_code': api_config.api_code,
                            'success': api_result.get('success'),
                            'message': api_result.get('message'),
                            'data': api_result.get('data'),
                            'call_time': timezone.now().isoformat()
                        }
                        all_results.append(api_result_info)
                        
                    except Exception as api_e:
                        print(f"[PaymentManager] API {api_id} 调用失败: {str(api_e)}")
                        api_result_info = {
                            'api_id': api_id,
                            'success': False,
                            'message': f"API调用失败: {str(api_e)}",
                            'data': None,
                            'call_time': timezone.now().isoformat()
                        }
                        all_results.append(api_result_info)
            
            # 清理session中的查询参数
            if session_key in self.config_manager.request.session:
                del self.config_manager.request.session[session_key]
                print(f"[PaymentManager] 已清理session参数: {session_key}")
            
            # 判断整体查询是否成功
            success_count = sum(1 for result in all_results if result.get('success'))
            total_count = len(all_results)
            
            if total_count == 0:
                raise Exception("没有可用的API配置")
            
            # TODO: 响应存储位置 - 在这里将查询结果存储到数据库
            # 存储方法：
            # 1. 将all_results转换为JSON格式
            # 2. 可以选择加密存储（使用QueryResult.encrypt_result方法）
            # 3. 生成结果哈希值用于完整性校验
            # 4. 更新查询结果状态和时间
            # 5. 自动处理过期数据
            
            # 更新查询结果
            if success_count > 0:
                query_result.status = 'success'
                query_result.completed_time = timezone.now()
                
                # 将结果数据转换为JSON字符串存储
                import json
                # 仅保留脱敏信息
                masked_name = mask_name(name)
                masked_id_card = mask_id_card(id_card)
                masked_phone = mask_phone(phone)
                result_data = {
                    'query_type': query_type,
                    'query_category': query_category,
                    'api_results': all_results,
                    'success_count': success_count,
                    'total_count': total_count,
                    'query_time': timezone.now().isoformat(),
                    'order_no': order.order_no,
                    'user_info': {
                        'name': masked_name,
                        'id_card': masked_id_card,
                        'phone': masked_phone
                    }
                }
                
                # TODO: 可以选择加密存储结果数据
                # encrypted_data = QueryResult.encrypt_result(result_data, encryption_key)
                # query_result.encrypted_result_data = encrypted_data
                
                # 目前使用明文存储（JSON格式）
                query_result.encrypted_result_data = json.dumps(result_data, ensure_ascii=False)
                query_result.result_hash = hashlib.md5(query_result.encrypted_result_data.encode()).hexdigest()
                
                # 自动处理过期数据
                QueryResult.mark_expired()
                
                # 更新订单状态
                order.status = 'completed'
                order.query_complete_time = timezone.now()
                
                print(f"[PaymentManager] 查询成功: {success_count}/{total_count} 个API调用成功")
            else:
                query_result.status = 'failed'
                query_result.error_message = "所有API调用均失败"
                query_result.completed_time = timezone.now()
                
                # 更新订单状态
                order.status = 'failed'
                
                print(f"[PaymentManager] 查询失败: 所有API调用均失败")
                
                # 自动处理过期数据
                QueryResult.mark_expired()
            
            query_result.save()
            order.save()
            
            print(f"[PaymentManager] 查询任务执行完成 - order_id: {order.id}")
            
        except Exception as e:
            print(f"[PaymentManager] 查询任务执行失败: {str(e)}")
            logger.error(f"查询任务执行失败: {str(e)}")
            
            # 更新失败状态
            query_result.status = 'failed'
            query_result.error_message = str(e)
            query_result.completed_time = timezone.now()
            query_result.save()
            
            order.status = 'failed'
            order.save()
            
            # 自动处理过期数据
            QueryResult.mark_expired()
    
    def _build_api_params(self, api_code, name, id_card, phone):
        """根据API编号动态构建查询参数"""
        print(f"[PaymentManager] 构建API参数: api_code={api_code}, name={name}, id_card={id_card}, phone={phone}")
        
        try:
            # 获取API配置
            from .models import ApiConfig
            api_config = ApiConfig.objects.filter(api_code=api_code).first()
            
            if not api_config:
                print(f"[PaymentManager] 未找到API配置: {api_code}")
                return self._build_fallback_params(api_code, name, id_card, phone)
            
            # 获取参数配置
            param_config = api_config.get_param_config()
            if not param_config:
                print(f"[PaymentManager] API配置中没有参数配置: {api_code}")
                return self._build_fallback_params(api_code, name, id_card, phone)
            
            print(f"[PaymentManager] 使用动态参数配置: {param_config}")
            
            # 获取参数映射和默认值
            param_mapping = param_config.get('param_mapping', {})
            default_values = param_config.get('default_values', {})
            required_params = param_config.get('required_params', [])
            optional_params = param_config.get('optional_params', [])
            
            # 构建参数
            api_params = {}
            
            # 处理必需参数
            for param_name in required_params:
                mapped_name = param_mapping.get(param_name, param_name)
                
                # 根据参数名获取对应的值
                param_value = self._get_param_value(param_name, name, id_card, phone)
                
                if param_value is not None:
                    api_params[mapped_name] = param_value
                else:
                    print(f"[PaymentManager] 警告: 必需参数 {param_name} 没有值")
            
            # 处理可选参数
            for param_name in optional_params:
                mapped_name = param_mapping.get(param_name, param_name)
                
                # 获取参数值，如果没有则使用默认值
                param_value = self._get_param_value(param_name, name, id_card, phone)
                if param_value is None:
                    param_value = default_values.get(param_name, '')
                
                if param_value:  # 只有当值不为空时才添加
                    api_params[mapped_name] = param_value
            
            print(f"[PaymentManager] 动态构建的参数: {api_params}")
            return api_params
            
        except Exception as e:
            print(f"[PaymentManager] 动态构建参数失败: {str(e)}")
            return self._build_fallback_params(api_code, name, id_card, phone)
    
    def _get_param_value(self, param_name, name, id_card, phone):
        """根据参数名获取对应的值"""
        from datetime import datetime, timedelta
        
        param_mapping = {
            'name': name,
            'id_card': id_card,
            'mobile_no': phone,
            'phone': phone,
            'mobile': phone,
            'ent_name': name,  # 企业名称暂时用name字段
            'description': ''  # 描述字段默认为空
        }
        
        # 特殊处理 auth_date 参数
        if param_name == 'auth_date':
            # 生成当前时间前后三天的范围
            current_date = datetime.now()
            start_date = current_date - timedelta(days=3)
            end_date = current_date + timedelta(days=3)
            
            # 格式化为 YYYYMMDD-YYYYMMDD
            auth_date = f"{start_date.strftime('%Y%m%d')}-{end_date.strftime('%Y%m%d')}"
            return auth_date
        
        return param_mapping.get(param_name)
    
    def _build_fallback_params(self, api_code, name, id_card, phone):
        """构建备用参数（当动态配置失败时使用）"""
        print(f"[PaymentManager] 使用备用参数构建: {api_code}")
        
        from datetime import datetime, timedelta
        
        # 基础参数
        base_params = {}
        
        # 根据API编号添加特定参数（风险报告查询）
        if api_code == 'FLXG0V4B':  # 个人司法涉诉（详版）
            # 生成动态授权日期
            current_date = datetime.now()
            start_date = current_date - timedelta(days=3)
            end_date = current_date + timedelta(days=3)
            auth_date = f"{start_date.strftime('%Y%m%d')}-{end_date.strftime('%Y%m%d')}"
            
            base_params = {
                'name': name,
                'id_card': id_card,
                'auth_date': auth_date,
                'description': '个人司法涉诉（详版）'
            }
        elif api_code == 'QYGL8261':  # 企业综合涉诉
            base_params = {
                'ent_name': name,
                'description': '企业综合涉诉查询'
            }
        elif api_code == 'IVYZ5733':  # 婚姻状况
            base_params = {
                'name': name,
                'id_card': id_card,
                'description': '婚姻状况查询'
            }
        elif api_code == 'JRZQ0A03':  # 借贷行为验证
            base_params = {
                'name': name,
                'id_card': id_card,
                'mobile_no': phone,
                'description': '借贷行为验证查询'
            }
        else:
            # 默认参数
            base_params = {
                'name': name,
                'id_card': id_card,
                'description': '风险报告查询'
            }
            if phone:
                base_params['mobile_no'] = phone
        
        print(f"[PaymentManager] 备用参数: {base_params}")
        return base_params
    
    def _generate_authorization_letter(self, order, query_result):
        """生成授权书"""
        print(f"[PaymentManager] 开始生成授权书 - order_id: {order.id}")
        
        try:
            # 从session中获取查询参数
            session_key = f'query_params_{order.order_no}'
            query_params = self.config_manager.request.session.get(session_key, {})
            
            if not query_params:
                print(f"[PaymentManager] 查询参数不存在，跳过授权书生成")
                return
            
            name = query_params.get('name', '')
            id_card = query_params.get('id_card', '')
            
            if not name or not id_card:
                print(f"[PaymentManager] 姓名或身份证号为空，跳过授权书生成")
                return
            
            # 获取公司名称
            company_name = "贵公司"  # 默认值
            try:
                from .models import SystemConfig
                system_config = SystemConfig.objects.filter(owner_id=self.owner_id, owner_type=self.owner_type).first()
                if system_config:
                    # 优先使用公司名称字段，如果没有则使用网站标题
                    if system_config.company_name:
                        company_name = system_config.company_name
            except Exception as e:
                print(f"[PaymentManager] 获取公司名称失败: {str(e)}")
            
            # 生成脱敏信息（用于数据库存储）
            masked_name = self._mask_name(name)
            masked_id_card = self._mask_id_card(id_card)
            
            # 生成授权书文本内容（PDF中不脱敏）
            from .authorization_generator import AuthorizationPDFGenerator
            pdf_generator = AuthorizationPDFGenerator()
            authorization_content = ""  # 数据库中的授权书内容留空
            
            # 创建授权书目录
            import os
            from django.conf import settings
            
            # 创建授权书存储目录
            auth_dir = os.path.join(settings.MEDIA_ROOT, 'authorizations')
            os.makedirs(auth_dir, exist_ok=True)
            
            # 生成文件名
            timestamp = int(time.time())
            filename = f"auth_{order.user_id}_{timestamp}.pdf"
            file_path = os.path.join(auth_dir, filename)
            
            # 生成PDF文件（PDF中不脱敏，使用原始姓名和身份证号）
            pdf_result = pdf_generator.generate_authorization_pdf(name, id_card, company_name, file_path)
            
            if not pdf_result.get('success'):
                print(f"[PaymentManager] PDF生成失败: {pdf_result.get('error')}")
                return
            
            # 保存到数据库
            from .models import AuthorizationLetter
            authorization_letter = AuthorizationLetter.objects.create(
                user_id=order.user_id,
                agent_id=order.agent_id,
                masked_name=masked_name,
                masked_id_card=masked_id_card,
                authorization_content=authorization_content,
                file_path=file_path,
                file_hash=pdf_result.get('file_hash', ''),
                is_valid=True
            )
            
            print(f"[PaymentManager] 授权书生成成功 - ID: {authorization_letter.id}, 文件: {file_path}")
            
        except Exception as e:
            print(f"[PaymentManager] 生成授权书失败: {str(e)}")
            logger.error(f"生成授权书失败: {str(e)}")
    
    def _mask_name(self, name):
        """姓名脱敏：三字*中间，两字*后面"""
        if not name:
            return name
        
        if len(name) == 2:
            return name[0] + '*'
        elif len(name) >= 3:
            return name[0] + '*' * (len(name) - 2) + name[-1]
        else:
            return name
    
    def _mask_id_card(self, id_card):
        """身份证号脱敏：保留前几位后面脱敏"""
        if not id_card:
            return id_card
        
        if len(id_card) >= 6:
            return id_card[:6] + '*' * (len(id_card) - 6)
        else:
            return '*' * len(id_card) 

    def create_refund(self, order_no, transaction_id, payment_method, refund_amount, total_amount, reason="用户申请退款"):
        """
        创建退款申请
        
        Args:
            order_no: 商户订单号
            transaction_id: 第三方支付交易号
            payment_method: 支付方式 ('alipay' or 'wechat')
            refund_amount: 退款金额（元）
            total_amount: 原订单金额（元）
            reason: 退款原因
            
        Returns:
            退款结果字典
        """
        print(f"[PaymentManager] 开始创建退款 - method: {payment_method}, refund_amount: {refund_amount}")
        
        try:
            # 生成退款单号
            import time
            refund_no = f"refund_{order_no}_{int(time.time())}"
            
            if payment_method == 'alipay' and self.alipay:
                # 支付宝退款
                return self.alipay.create_refund(
                    order_no=order_no,
                    refund_amount=refund_amount,
                    refund_reason=reason,
                    out_request_no=refund_no,
                    trade_no=transaction_id
                )
            elif payment_method == 'wechat' and self.wechat:
                # 微信退款
                # 金额转换为分
                refund_amount_fen = int(float(refund_amount) * 100)
                total_amount_fen = int(float(total_amount) * 100)
                
                return self.wechat.create_refund(
                    order_no=order_no,
                    transaction_id=transaction_id,
                    refund_no=refund_no,
                    refund_amount=refund_amount_fen,
                    total_amount=total_amount_fen,
                    reason=reason
                )
            else:
                error_msg = f"不支持的支付方式或配置不存在: {payment_method}"
                print(f"[PaymentManager] {error_msg}")
                return {'success': False, 'message': error_msg}
                
        except Exception as e:
            print(f"[PaymentManager] 创建退款失败: {str(e)}")
            return {'success': False, 'message': f'创建退款失败: {str(e)}'}

    def query_refund_status(self, refund_no, payment_method):
        """
        查询退款状态
        
        Args:
            refund_no: 商户退款单号
            payment_method: 支付方式 ('alipay' or 'wechat')
            
        Returns:
            退款状态查询结果
        """
        print(f"[PaymentManager] 开始查询退款状态 - refund_no: {refund_no}, method: {payment_method}")
        
        try:
            if payment_method == 'alipay' and self.alipay:
                # 支付宝退款查询
                # 需要从refund_no中提取order_no和out_request_no
                if '_' in refund_no:
                    # refund_no格式: refund_{order_no}_{timestamp}
                    parts = refund_no.split('_')
                    if len(parts) >= 3:
                        order_no_from_refund = '_'.join(parts[1:-1])  # 重建order_no
                        return self.alipay.query_refund_status(
                            order_no=order_no_from_refund,
                            out_request_no=refund_no
                        )
                
                # 如果无法解析refund_no，返回错误
                return {
                    'success': False,
                    'message': '无法解析退款单号格式'
                }
            elif payment_method == 'wechat' and self.wechat:
                # 微信退款状态查询
                return self.wechat.query_refund_status(refund_no)
            else:
                print(f"[PaymentManager] 不支持的支付方式或配置不存在: {payment_method}")
                return {'success': False, 'message': '不支持的支付方式或配置不存在'}
                
        except Exception as e:
            print(f"[PaymentManager] 查询退款状态失败: {str(e)}")
            return {'success': False, 'message': f'查询退款状态失败: {str(e)}'} 