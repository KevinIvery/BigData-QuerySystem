from django.utils.deprecation import MiddlewareMixin
from django.contrib.sessions.models import Session
from django.utils import timezone
from .models import RegularUser, AdminUser, AgentUser
from .response import ApiResponse, ResponseCode
import json

class AuthenticationMiddleware(MiddlewareMixin):
    """认证中间件"""
    
    def process_request(self, request):
        """处理请求，添加用户信息到request"""
        
        # 初始化用户信息
        request.user = None
        request.user_type = None
        request.user_id = None
        
        # 获取session中的用户信息
        user_info = request.session.get('user_info')
        if not user_info:
            return None
        
        user_type = user_info.get('user_type')
        user_id = user_info.get('user_id')
        
        if not user_type or not user_id:
            return None
        
        try:
            # 根据用户类型获取用户对象
            if user_type == 'regular':
                user = RegularUser.objects.get(id=user_id)
            elif user_type == 'admin':
                user = AdminUser.objects.get(id=user_id)
            elif user_type == 'agent':
                user = AgentUser.objects.get(id=user_id)
            else:
                return None
            
            # 设置request属性
            request.user = user
            request.user_type = user_type
            request.user_id = user_id
            
        except (RegularUser.DoesNotExist, AdminUser.DoesNotExist, AgentUser.DoesNotExist):
            # 用户不存在，清除session
            request.session.pop('user_info', None)
            return None
        
        return None

class DomainMiddleware(MiddlewareMixin):
    """域名中间件 - 根据域名识别代理商"""
    
    def process_request(self, request):
        """处理请求，识别域名后缀"""
        
        host = request.get_host()
        
        # 初始化域名信息
        request.domain_type = 'admin'  # 默认管理员域名
        request.agent_id = None
        request.domain_suffix = None
        
        # 检查是否为代理商域名
        if '.' in host:
            # 提取域名后缀 (如: agent001.tybigdata.com -> agent001)
            domain_parts = host.split('.')
            if len(domain_parts) >= 2:
                potential_suffix = domain_parts[0]
                
                # 查询是否存在该域名后缀的代理商
                try:
                    agent = AgentUser.objects.get(domain_suffix=potential_suffix)
                    request.domain_type = 'agent'
                    request.agent_id = agent.id
                    request.domain_suffix = potential_suffix
                except AgentUser.DoesNotExist:
                    pass
        
        return None

class CorsMiddleware(MiddlewareMixin):
    """跨域中间件"""
    
    def process_response(self, request, response):
        """处理响应，添加跨域头"""
        
        response['Access-Control-Allow-Origin'] = '*'
        response['Access-Control-Allow-Methods'] = 'GET, POST, PUT, DELETE, OPTIONS'
        response['Access-Control-Allow-Headers'] = 'Content-Type, Authorization, X-Requested-With'
        response['Access-Control-Allow-Credentials'] = 'true'
        
        return response
    
    def process_request(self, request):
        """处理预检请求"""
        if request.method == 'OPTIONS':
            from django.http import HttpResponse
            response = HttpResponse()
            response['Access-Control-Allow-Origin'] = '*'
            response['Access-Control-Allow-Methods'] = 'GET, POST, PUT, DELETE, OPTIONS'
            response['Access-Control-Allow-Headers'] = 'Content-Type, Authorization, X-Requested-With'
            response['Access-Control-Allow-Credentials'] = 'true'
            return response
        
        return None 