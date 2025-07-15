"""
超级管理员相关的视图函数
"""

import json
import time
import os
from django.http import HttpRequest
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.contrib.auth.hashers import check_password, make_password
from django.core.paginator import Paginator
from django.db.models import Q
from django.utils import timezone
from datetime import timedelta
from decimal import Decimal, InvalidOperation

from .response import ApiResponse, ResponseCode
from .models import (AdminUser, AgentUser, ApiConfig, QueryConfig, 
                     SliderCaptcha, SystemConfig, ExternalApiConfig)
from .slider import CaptchaManager
from .decorators import admin_required

def get_client_ip(request):
    """获取客户端IP地址"""
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0].strip()
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip

@csrf_exempt
@require_http_methods(["POST"])
def admin_login(request: HttpRequest):
    """
    超级管理员登录接口
    
    Args:
        request: 包含登录信息的HTTP请求
        {
            "username": "管理员用户名",
            "password": "管理员密码", 
            "captcha_token": "验证码token",
            "fingerprint": "客户端指纹"
        }
        
    Returns:
        登录结果: 公司名称和创建时间戳
    """
    try:
        # 解析请求数据
        data = json.loads(request.body)
        username = data.get('username', '').strip()
        password = data.get('password', '').strip()
        captcha_token = data.get('captcha_token', '').strip()
        client_fingerprint = data.get('fingerprint', '')
        
        # 获取客户端IP
        client_ip = get_client_ip(request)
        
        print(f"管理员登录请求: username={username}, ip={client_ip}, fingerprint={client_fingerprint}")
        
        # 验证必填参数
        if not username or not password:
            return ApiResponse.param_error("用户名和密码不能为空")
        
        if not captcha_token:
            return ApiResponse.captcha_error("请完成验证码验证")
        
        # 验证滑块验证码
        try:
            captcha = SliderCaptcha.objects.get(token=captcha_token)
            
            # 检查验证码是否已验证
            if not captcha.is_verified:
                return ApiResponse.captcha_error("请先完成验证码验证")
            
            # 检查验证码是否过期(验证后10分钟内有效)
            current_time = int(time.time())
            if current_time > captcha.verify_time + 600:  # 10分钟
                return ApiResponse.captcha_error("验证码已过期，请重新验证")
            
            # 检查客户端指纹是否一致
            if captcha.client_fingerprint and client_fingerprint and captcha.client_fingerprint != client_fingerprint:
                return ApiResponse.captcha_error("验证环境发生变化，请重新验证")
                
        except SliderCaptcha.DoesNotExist:
            return ApiResponse.captcha_error("验证码无效，请重新验证")
        
        # 查找管理员用户
        try:
            admin = AdminUser.objects.get(username=username)
        except AdminUser.DoesNotExist:
            print(f"管理员用户不存在: {username}")
            return ApiResponse.unauthorized("用户名或密码错误")
        
        # 检查账户是否被锁定
        if admin.is_account_locked():
            lock_time_remaining = int((admin.lock_until.timestamp() - time.time()) / 60) if admin.lock_until else 0
            return ApiResponse.forbidden(f"账户已被锁定，请{lock_time_remaining}分钟后再试")
        
        # 验证密码
        if not check_password(password, admin.password):
            # 密码错误，增加错误次数
            admin.increment_error_count()
            
            failure_reason = f"密码错误，还有{5 - admin.login_error_count}次机会"
            if admin.login_error_count >= 5:
                failure_reason = "密码错误次数过多，账户已被锁定30分钟"
            
            print(f"管理员密码错误: {username}, 错误次数: {admin.login_error_count}")
            return ApiResponse.unauthorized(failure_reason)
        
        # 登录成功，重置错误次数
        if admin.login_error_count > 0:
            admin.reset_error_count()
        
        # 设置session
        request.session['user_info'] = {
            'user_id': admin.id,
            'user_type': 'admin',
            'username': admin.username,
            'login_time': current_time
        }
        
        # 设置session过期时间为7天
        request.session.set_expiry(7 * 24 * 60 * 60)
        
        print(f"管理员登录成功: {username}, session_key: {request.session.session_key}")
        
        # 返回登录成功信息
        response_data = {
            "company_name": admin.company_name,
            "username": admin.username,
            "create_time": int(admin.created_at.timestamp())
        }
        
        return ApiResponse.success(message="登录成功", data=response_data)
        
    except json.JSONDecodeError:
        return ApiResponse.param_error("无效的JSON数据")
    except Exception as e:
        print(f"管理员登录异常: {str(e)}")
        return ApiResponse.error(message="服务器内部错误", code=ResponseCode.SERVER_ERROR)

@csrf_exempt
@require_http_methods(["POST"])
@admin_required
def admin_logout(request: HttpRequest):
    """
    超级管理员退出登录接口
    
    Args:
        request: HTTP请求
        
    Returns:
        退出结果
    """
    try:
        # 获取当前用户信息
        user_info = request.session.get('user_info')
        
        if user_info and user_info.get('user_type') == 'admin':
            username = user_info.get('username')
            print(f"管理员退出登录: {username}")
            
            # 清除session
            request.session.flush()
            
            return ApiResponse.success(message="退出成功")
        else:
            # 即使没有有效session，也清除session并返回成功
            request.session.flush()
            return ApiResponse.success(message="退出成功")
            
    except Exception as e:
        print(f"管理员退出异常: {str(e)}")
        
        # 即使出现异常，也尝试清除session
        try:
            request.session.flush()
        except:
            pass
            
        return ApiResponse.success(message="退出成功")

@csrf_exempt
@require_http_methods(["GET", "POST"])
@admin_required
def admin_auth_check(request: HttpRequest):
    """
    管理员认证状态检查接口
    
    Returns:
        认证状态信息
    """
    try:
        # 获取当前用户信息
        admin = request.user
        
   
        return ApiResponse.success(message="ok", data={})
        
    except Exception as e:
        print(f"认证检查异常: {str(e)}")
        return ApiResponse.error(message="认证检查失败", code=ResponseCode.SERVER_ERROR)

@csrf_exempt
@require_http_methods(["POST"])
@admin_required
def admin_profile_update(request: HttpRequest):
    """
    管理员个人信息更新接口
    
    Args:
        request: 包含更新信息的HTTP请求
        {
            "current_password": "当前密码",
            "username": "新用户名(可选)", 
            "new_password": "新密码(可选)"
        }
        
    Returns:
        更新结果和新的用户信息
    """
    try:
        # 解析请求数据
        data = json.loads(request.body)
        current_password = data.get('current_password', '').strip()
        new_username = data.get('username', '').strip()
        new_password = data.get('new_password', '').strip()
        
        # 获取当前管理员
        admin = request.user
        
        print(f"管理员个人信息更新请求: username={admin.username}")
        
        # 验证必填参数
        if not current_password:
            return ApiResponse.param_error("请输入当前密码")
        
        # 验证当前密码
        if not check_password(current_password, admin.password):
            return ApiResponse.unauthorized("当前密码错误")
        
        # 检查是否有要更新的内容
        if not new_username and not new_password:
            return ApiResponse.param_error("请至少修改用户名或密码其中一项")
        
        # 更新信息标记
        updated_fields = []
        
        # 更新用户名
        if new_username:
            # 检查用户名长度
            if len(new_username) < 2 or len(new_username) > 50:
                return ApiResponse.param_error("用户名长度应在2-50个字符之间")
            
            # 检查用户名是否已存在（排除自己）
            if AdminUser.objects.filter(username=new_username).exclude(id=admin.id).exists():
                return ApiResponse.param_error("用户名已存在，请选择其他用户名")
            
            admin.username = new_username
            updated_fields.append("用户名")
        
        # 更新密码
        if new_password:
            # 检查密码长度
            if len(new_password) < 6:
                return ApiResponse.param_error("新密码长度不能少于6位")
            
            # 检查新密码是否与当前密码相同
            if check_password(new_password, admin.password):
                return ApiResponse.param_error("新密码不能与当前密码相同")
            
            # 加密并设置新密码
            admin.password = make_password(new_password)
            updated_fields.append("密码")
        
        # 保存更改
        admin.save()
        
        # 如果用户名发生变化，更新session中的用户信息
        if new_username:
            user_info = request.session.get('user_info', {})
            user_info['username'] = new_username
            request.session['user_info'] = user_info
        
        print(f"管理员个人信息更新成功: {admin.username}, 更新字段: {updated_fields}")
        
        # 返回更新后的用户信息
        response_data = {
            "username": admin.username,
            "company_name": admin.company_name,
            "updated_fields": updated_fields
        }
        
        update_message = f"{'、'.join(updated_fields)}更新成功"
        return ApiResponse.success(message=update_message, data=response_data)
        
    except json.JSONDecodeError:
        return ApiResponse.param_error("无效的JSON数据")
    except Exception as e:
        print(f"管理员个人信息更新异常: {str(e)}")
        return ApiResponse.error(message="服务器内部错误", code=ResponseCode.SERVER_ERROR)

# ==================== 系统配置管理接口 ====================

@csrf_exempt
@require_http_methods(["POST"])
@admin_required
def get_system_config(request: HttpRequest):
    """
    获取系统配置接口
    
    Returns:
        系统配置信息
    """
    try:
        admin = request.user
        
        # 获取管理员的系统配置
        try:
            config = SystemConfig.objects.get(owner_id=admin.id, owner_type='admin')
            config_data = {
                "id": config.id,
                "logo": config.logo,
                "site_title": config.site_title,
                "company_name": config.company_name,
                "keywords": config.keywords,
                "description": config.description,
                "show_query_price": config.show_query_price,
                "query_entrance_desc": config.query_entrance_desc,
                "customer_service_url": config.customer_service_url,
                "force_wechat_access": config.force_wechat_access,
                "footer_copyright": config.footer_copyright,
                "created_at": config.created_at.isoformat(),
                "updated_at": config.updated_at.isoformat()
            }
        except SystemConfig.DoesNotExist:
            # 如果没有配置，返回默认值
            config_data = {
                "id": None,
                "logo": "",
                "site_title": "大数据查询平台",
                "company_name": "",
                "keywords": "大数据,查询,平台",
                "description": "专业的大数据查询服务平台",
                "show_query_price": True,
                "query_entrance_desc": "",
                "customer_service_url": "",
                "force_wechat_access": False,
                "footer_copyright": "",
                "created_at": None,
                "updated_at": None
            }
        
        return ApiResponse.success(data=config_data)
        
    except Exception as e:
        print(f"获取系统配置异常: {str(e)}")
        return ApiResponse.error(message="获取系统配置失败", code=ResponseCode.SERVER_ERROR)

@csrf_exempt
@require_http_methods(["POST"])
@admin_required
def update_system_config(request: HttpRequest):
    """
    更新系统配置接口
    
    Args:
        request: 包含配置信息的HTTP请求
        {
            "logo": "Logo URL或路径",
            "site_title": "网站标题",
            "keywords": "关键词",
            "description": "描述",
            "show_query_price": true,
            "query_entrance_desc": "查询入口描述",
            "footer_copyright": "底部版权"
        }
        
    Returns:
        更新结果
    """
    try:
        admin = request.user
        data = json.loads(request.body)
        
        # 获取或创建配置
        config, created = SystemConfig.objects.get_or_create(
            owner_id=admin.id,
            owner_type='admin',
            defaults={
                'logo': '',
                'site_title': '大数据查询平台',
                'company_name': '',
                'keywords': '',
                'description': '',
                'show_query_price': True,
                'query_entrance_desc': '',
                'customer_service_url': '',
                'force_wechat_access': False,
                'footer_copyright': ''
            }
        )
        
        # 更新配置字段
        if 'logo' in data:
            config.logo = data['logo']
        if 'site_title' in data:
            config.site_title = data['site_title']
        if 'company_name' in data:
            config.company_name = data['company_name']
        if 'keywords' in data:
            config.keywords = data['keywords']
        if 'description' in data:
            config.description = data['description']
        if 'show_query_price' in data:
            config.show_query_price = data['show_query_price']
        if 'query_entrance_desc' in data:
            config.query_entrance_desc = data['query_entrance_desc']
        if 'customer_service_url' in data:
            config.customer_service_url = data['customer_service_url']
        if 'force_wechat_access' in data:
            config.force_wechat_access = data['force_wechat_access']
        if 'footer_copyright' in data:
            config.footer_copyright = data['footer_copyright']
        
        config.save()
        
        print(f"管理员系统配置更新成功: {admin.username}")
        
        # 返回更新后的配置
        response_data = {
            "id": config.id,
            "logo": config.logo,
            "site_title": config.site_title,
            "company_name": config.company_name,
            "keywords": config.keywords,
            "description": config.description,
            "show_query_price": config.show_query_price,
            "query_entrance_desc": config.query_entrance_desc,
            "customer_service_url": config.customer_service_url,
            "force_wechat_access": config.force_wechat_access,
            "footer_copyright": config.footer_copyright,
            "updated_at": config.updated_at.isoformat()
        }
        
        return ApiResponse.success(message="系统配置更新成功", data=response_data)
        
    except json.JSONDecodeError:
        return ApiResponse.param_error("无效的JSON数据")
    except Exception as e:
        print(f"更新系统配置异常: {str(e)}")
        return ApiResponse.error(message="更新系统配置失败", code=ResponseCode.SERVER_ERROR)

# ==================== 查询配置管理接口 ====================

@csrf_exempt
@require_http_methods(["GET"])
@admin_required
def get_query_configs(request: HttpRequest):
    """
    获取所有查询配置及其关联的API接口信息
    
    Returns:
        返回一个列表，包含每个查询配置的详细信息和其子接口列表
    """
    try:
        admin = request.user
        
        # 获取该管理员的所有查询配置
        query_configs = QueryConfig.objects.filter(owner_id=admin.id, owner_type='admin').order_by('id')
        
        response_data = []
        for config in query_configs:
            api_ids = config.api_combination
            if not isinstance(api_ids, list):
                api_ids = []

            # 获取关联的API接口详细信息
            api_details = ApiConfig.objects.filter(id__in=api_ids).order_by('id')
            
            apis_data = [{
                "id": api.id,
                "api_name": api.api_name,
                "api_code": api.api_code,
                "is_active": api.is_active,
                "cost_price": f"{api.cost_price:.2f}"
            } for api in api_details]
            
            response_data.append({
                "id": config.id,
                "config_name": config.config_name,
                "category": config.category,
                "customer_price": f"{config.customer_price:.2f}",
                "is_active": config.is_active,
                "apis": apis_data
            })
            
        return ApiResponse.success(data=response_data)
        
    except Exception as e:
        print(f"获取查询配置异常: {str(e)}")
        return ApiResponse.error(message="获取查询配置失败", code=ResponseCode.SERVER_ERROR)


@csrf_exempt
@require_http_methods(["POST"])
@admin_required
def update_query_config(request: HttpRequest, config_id: int):
    """
    更新指定的查询配置
    
    Args:
        request: 包含更新信息的HTTP请求
        config_id: 要更新的查询配置ID
        {
            "is_active": true,
            "customer_price": 19.90,
            "category": "two_factor", // (可选, 仅个人查询配置有效)
            "apis": [
                {"id": 1, "is_active": true},
                {"id": 3, "is_active": false}
            ]
        }
    """
    try:
        admin = request.user
        data = json.loads(request.body)
        
        is_active_main = data.get('is_active')
        customer_price = data.get('customer_price')
        category = data.get('category')  # 获取类别字段
        apis_to_update = data.get('apis', [])

        from django.db import transaction
        with transaction.atomic():
            try:
                config_to_update = QueryConfig.objects.select_for_update().get(id=config_id, owner_id=admin.id, owner_type='admin')
            except QueryConfig.DoesNotExist:
                return ApiResponse.not_found("指定的查询配置不存在")

            # 验证1: 必须至少保留一个查询配置启用
            if is_active_main is False:
                active_configs_count = QueryConfig.objects.filter(
                    owner_id=admin.id, owner_type='admin', is_active=True
                ).exclude(id=config_id).count()
                if active_configs_count < 1:
                    return ApiResponse.param_error("必须至少保留一个查询配置处于启用状态。")

            # 验证2: 当前配置必须至少有一个启用的子接口
            if not any(api.get('is_active') for api in apis_to_update):
                return ApiResponse.param_error(f"查询配置 '{config_to_update.config_name}' 必须至少有一个启用的接口。")

            # 更新主配置
            if is_active_main is not None:
                config_to_update.is_active = is_active_main
            
            if customer_price is not None:
                try:
                    config_to_update.customer_price = float(customer_price)
                except (ValueError, TypeError):
                    return ApiResponse.param_error("价格必须是有效的数字。")
            
            # 如果是个人查询配置，则更新其类别
            if config_to_update.config_name == '个人查询配置':
                # 验证：个人查询配置的类别不能为空
                if not category:
                    return ApiResponse.param_error("个人查询配置必须选择一个查询类别。")

                valid_categories = [choice[0] for choice in QueryConfig.CATEGORY_CHOICES]
                # 允许设置为空
                if category in valid_categories:
                    config_to_update.category = category
                    
                    # 同步更新所有代理的个人查询配置类别
                    agent_personal_configs = QueryConfig.objects.filter(
                        config_name='个人查询配置',
                        owner_type='agent'
                    )
                    agent_personal_configs.update(category=category)
                    print(f"同步更新了 {agent_personal_configs.count()} 个代理的个人查询配置类别为: {category}")
            
            config_to_update.save()

            # 更新子接口状态
            for api_data in apis_to_update:
                api_id, is_active_api = api_data.get('id'), api_data.get('is_active')
                if api_id is None or is_active_api is None:
                    continue

                # 验证3: 企业查询配置的唯一接口不能被禁用
                if config_to_update.config_name == '企业查询配置' and len(config_to_update.api_combination) == 1 and not is_active_api:
                     return ApiResponse.param_error("企业查询配置的唯一接口不能被禁用。")

                ApiConfig.objects.filter(id=api_id, owner_id=admin.id, owner_type='admin').update(is_active=is_active_api)

        print(f"管理员查询配置更新成功: {config_to_update.config_name} (ID: {config_id})")
        return ApiResponse.success(message="查询配置更新成功")

    except json.JSONDecodeError:
        return ApiResponse.param_error("无效的JSON数据")
    except Exception as e:
        print(f"更新查询配置异常: {str(e)}")
        return ApiResponse.error(message="更新查询配置失败", code=ResponseCode.SERVER_ERROR)

# ==================== 代理管理接口 ====================

@csrf_exempt
@require_http_methods(["GET"])
@admin_required
def get_agents(request: HttpRequest):
    """
    获取代理列表，返回每个代理的完整配置信息（无需再请求详情接口）
    """
    try:
        search_query = request.GET.get('search', '').strip()
        date_range = request.GET.get('date_range', 'all')
        status = request.GET.get('status', 'all')
        page_number = int(request.GET.get('page', 1))
        page_size = int(request.GET.get('page_size', 10))

        queryset = AgentUser.objects.order_by('-created_at')

        if search_query:
            queryset = queryset.filter(
                Q(username__icontains=search_query) | Q(phone__icontains=search_query)
            )
        if status == 'active':
            queryset = queryset.filter(is_locked=False)
        elif status == 'locked':
            queryset = queryset.filter(is_locked=True)
        now = timezone.now()
        if date_range == '7d':
            queryset = queryset.filter(created_at__gte=now - timedelta(days=7))
        elif date_range == '30d':
            queryset = queryset.filter(created_at__gte=now - timedelta(days=30))
        elif date_range == '1y':
            queryset = queryset.filter(created_at__gte=now - timedelta(days=365))

        paginator = Paginator(queryset, page_size)
        page_obj = paginator.get_page(page_number)

        agents_data = []
        for agent in page_obj.object_list:
            # 查询个人/企业配置
            query_configs = QueryConfig.objects.filter(owner_id=agent.id, owner_type='agent')
            personal_config = query_configs.filter(config_name='个人查询配置').first()
            enterprise_config = query_configs.filter(config_name='企业查询配置').first()
            # 组装接口明细
            def build_query_block(config, bottom_price):
                if not config:
                    return {"enabled": False, "bottom_price": None, "customer_price": None, "apis": []}
                apis = []
                # 只显示代理已启用的接口
                for api_id in config.api_combination or []:
                    api = ApiConfig.objects.filter(id=api_id).first()
                    if api:
                        apis.append({
                            "id": api.id,
                            "name": api.api_name,
                            "cost_price": float(api.cost_price),
                            "enabled": True  # 既然在api_combination中，说明已启用
                        })
                return {
                    "enabled": config.is_active,  # 使用QueryConfig的is_active字段
                    "bottom_price": float(bottom_price),  # 超管设置的底价
                    "customer_price": float(config.customer_price),  # 代理设置的客户价格
                    "apis": apis
                }
            agents_data.append({
                'id': agent.id,
                'username': agent.username,
                'phone': agent.phone,
                'domain_suffix': agent.domain_suffix,
                'is_locked': agent.is_locked,
                'can_customize_settings': agent.can_customize_settings,
                'created_at': agent.created_at,
                'total_commission': float(agent.total_commission),
                'settled_commission': float(agent.settled_commission),
                'unsettled_commission': float(agent.unsettled_commission),
                'personal_query': build_query_block(personal_config, agent.personal_query_price),
                'enterprise_query': build_query_block(enterprise_config, agent.enterprise_query_min_price)
            })
        response_data = {
            'items': agents_data,
            'pagination': {
                'total_items': paginator.count,
                'total_pages': paginator.num_pages,
                'current_page': page_obj.number,
                'page_size': page_size,
                'has_next': page_obj.has_next(),
                'has_previous': page_obj.has_previous(),
            }
        } 
        return ApiResponse.success(data=response_data)
    except (ValueError, TypeError):
        return ApiResponse.param_error("分页参数必须是整数。")
    except Exception as e:
        print(f"获取代理列表异常: {str(e)}")
        return ApiResponse.error(message="获取代理列表失败", code=ResponseCode.SERVER_ERROR)

@csrf_exempt
@require_http_methods(["POST"])
@admin_required
def update_agent(request: HttpRequest, agent_id: int):
    """
    更新代理信息
    """
    try:
        data = json.loads(request.body)
        agent_to_update = AgentUser.objects.get(id=agent_id)

        # 更新基础字段
        agent_to_update.phone = data.get('phone', agent_to_update.phone).strip()
        agent_to_update.can_customize_settings = bool(data.get('can_customize_settings'))
        agent_to_update.is_locked = bool(data.get('is_locked'))
        
        # 更新价格字段
        if 'personal_query_price' in data:
            agent_to_update.personal_query_price = Decimal(data['personal_query_price'])
        if 'enterprise_query_min_price' in data:
            agent_to_update.enterprise_query_min_price = Decimal(data['enterprise_query_min_price'])

        # 如果提供了密码，则更新
        password = data.get('password', '').strip()
        if password:
            if len(password) < 6:
                return ApiResponse.param_error("新密码长度不能少于6位。")
            agent_to_update.password = make_password(password)
        
        agent_to_update.save()
        
        # 同步更新代理的查询配置状态（不更新客户价格，由代理自己控制）
        agent_query_configs = QueryConfig.objects.filter(owner_id=agent_to_update.id, owner_type='agent')
        for config in agent_query_configs:
            if config.config_name == '个人查询配置':
                # 更新启用状态
                config.is_active = data.get('personal_enabled', config.is_active)
                
                # 更新个人查询的接口组合（api_combination）
                if 'personal_apis' in data:
                    config.api_combination = data['personal_apis']  # 直接设置启用的接口ID列表
                
                config.save()
                        
            elif config.config_name == '企业查询配置':
                # 更新启用状态
                config.is_active = data.get('enterprise_enabled', config.is_active)
                
                # 更新企业查询的接口组合（api_combination）
                if 'enterprise_apis' in data:
                    config.api_combination = data['enterprise_apis']  # 直接设置启用的接口ID列表
                
                config.save()
        
        response_data = {
            'id': agent_to_update.id,
            'username': agent_to_update.username,
            'phone': agent_to_update.phone,
            'domain_suffix': agent_to_update.domain_suffix,
            'can_customize_settings': agent_to_update.can_customize_settings,
            'personal_query_price': f"{agent_to_update.personal_query_price:.2f}",
            'enterprise_query_min_price': f"{agent_to_update.enterprise_query_min_price:.2f}",
            'total_commission': f"{agent_to_update.total_commission:.2f}",
            'settled_commission': f"{agent_to_update.settled_commission:.2f}",
            'unsettled_commission': f"{agent_to_update.unsettled_commission:.2f}",
            'is_locked': agent_to_update.is_locked
        }
        
        return ApiResponse.success(message="代理信息更新成功", data=response_data)

    except AgentUser.DoesNotExist:
        return ApiResponse.not_found("代理不存在")
    except (InvalidOperation, TypeError):
        return ApiResponse.param_error("价格格式无效")
    except Exception as e:
        print(f"更新代理异常: {str(e)}")
        return ApiResponse.error(message="更新代理失败")


@csrf_exempt
@require_http_methods(["POST"])
@admin_required
def delete_agent(request: HttpRequest, agent_id: int):
    """
    删除代理
    """
    try:
        agent_to_delete = AgentUser.objects.get(id=agent_id)
        agent_to_delete.delete()
        return ApiResponse.success(message="代理删除成功")
    except AgentUser.DoesNotExist:
        return ApiResponse.not_found("代理不存在")
    except Exception as e:
        print(f"删除代理异常: {str(e)}")
        return ApiResponse.error(message="删除代理失败")

@csrf_exempt
@require_http_methods(["POST"])
@admin_required
def create_agent(request: HttpRequest):
    """
    创建新代理接口
    Body:
        {
            "username": "...",
            "phone": "...",
            "password": "...",
            "domain_suffix": "...",
            "personal_query_price": 19.90,
            "enterprise_query_min_price": 29.90,
            "can_customize_settings": false
        }
    """
    try:
        data = json.loads(request.body)
        
        username = data.get('username', '').strip()
        phone = data.get('phone', '').strip()
        password = data.get('password', '').strip()
        domain_suffix = data.get('domain_suffix', '').strip()
        personal_query_price = Decimal(data.get('personal_query_price', '0.00'))
        enterprise_query_min_price = Decimal(data.get('enterprise_query_min_price', '0.00'))
        can_customize_settings = data.get('can_customize_settings', False)

        if not all([username, password, domain_suffix]):
            return ApiResponse.param_error("用户名、密码和域名后缀为必填项。")

        if len(password) < 6:
            return ApiResponse.param_error("密码长度不能少于6位。")

        if AgentUser.objects.filter(username=username).exists():
            return ApiResponse.param_error("用户名已存在。")

        if AgentUser.objects.filter(domain_suffix=domain_suffix).exists():
            return ApiResponse.param_error("域名后缀已存在。")
        
        # 验证价格
        if personal_query_price < 0 or enterprise_query_min_price < 0:
            return ApiResponse.param_error("价格不能为负数。")
        
        # 验证超管配置是否存在
        try:
            admin = request.user
            admin_query_configs = QueryConfig.objects.filter(owner_id=admin.id, owner_type='admin')
            admin_system_config = SystemConfig.objects.filter(owner_id=admin.id, owner_type='admin').first()
            
            if not admin_query_configs.exists():
                return ApiResponse.error("系统查询配置不完整，请先配置查询接口。")
                
        except Exception as e:
            return ApiResponse.error("获取系统配置失败，无法创建代理。")

        from django.db import transaction
        with transaction.atomic():
            # 创建代理用户
            new_agent = AgentUser.objects.create(
                username=username,
                phone=phone,
                password=make_password(password),
                domain_suffix=domain_suffix,
                can_customize_settings=bool(can_customize_settings),
                personal_query_price=personal_query_price,
                enterprise_query_min_price=enterprise_query_min_price
            )
            
            # 复制查询配置给代理，使用代理自定义的价格
            for admin_config in admin_query_configs:
                # 根据配置名称设置对应的价格和启用状态
                if admin_config.config_name == '个人查询配置':
                    # 初始化客户价格为底价的1.5倍
                    customer_price = personal_query_price * Decimal('1.5')
                    is_active = data.get('personal_enabled', True)
                elif admin_config.config_name == '企业查询配置':
                    # 初始化客户价格为底价的1.5倍
                    customer_price = enterprise_query_min_price * Decimal('1.5')
                    is_active = data.get('enterprise_enabled', True)
                else:
                    customer_price = admin_config.customer_price  # 其他配置使用主站价格
                    is_active = admin_config.is_active
                
                QueryConfig.objects.create(
                    config_name=admin_config.config_name,
                    category=admin_config.category,
                    customer_price=customer_price,
                    api_combination=admin_config.api_combination,
                    owner_id=new_agent.id,
                    owner_type='agent',
                    is_active=is_active
                )
            
            # 复制系统配置给代理
            if admin_system_config:
                SystemConfig.objects.create(
                    logo=admin_system_config.logo,
                    site_title=admin_system_config.site_title,
                    keywords=admin_system_config.keywords,
                    description=admin_system_config.description,
                    show_query_price=admin_system_config.show_query_price,
                    query_entrance_desc=admin_system_config.query_entrance_desc,
                    customer_service_url=admin_system_config.customer_service_url,
                    force_wechat_access=admin_system_config.force_wechat_access,
                    footer_copyright=admin_system_config.footer_copyright,
                    owner_id=new_agent.id,
                    owner_type='agent'
                )
        
        print(f"新代理创建成功: {new_agent.username}")
        
        response_data = {
            'id': new_agent.id,
            'username': new_agent.username,
            'phone': new_agent.phone,
            'domain_suffix': new_agent.domain_suffix,
            'can_customize_settings': new_agent.can_customize_settings,
            'personal_query_price': f"{new_agent.personal_query_price:.2f}",
            'enterprise_query_min_price': f"{new_agent.enterprise_query_min_price:.2f}",
            'total_commission': f"{new_agent.total_commission:.2f}",
            'settled_commission': f"{new_agent.settled_commission:.2f}",
            'unsettled_commission': f"{new_agent.unsettled_commission:.2f}",
            'is_locked': new_agent.is_locked,
            'created_at': new_agent.created_at.isoformat()
        }

        return ApiResponse.success(message="代理创建成功", data=response_data)

    except json.JSONDecodeError:
        return ApiResponse.param_error("无效的JSON数据")
    except (InvalidOperation, TypeError):
        return ApiResponse.param_error("价格格式无效")
    except Exception as e:
        print(f"创建代理异常: {str(e)}")
        return ApiResponse.error(message="创建代理失败", code=ResponseCode.SERVER_ERROR)

@csrf_exempt
@require_http_methods(["GET"])
@admin_required
def get_agent_detail(request: HttpRequest, agent_id: int):
    """
    获取代理详细信息，结构与列表一致
    """
    try:
        agent = AgentUser.objects.get(id=agent_id)
        query_configs = QueryConfig.objects.filter(owner_id=agent.id, owner_type='agent')
        personal_config = query_configs.filter(config_name='个人查询配置').first()
        enterprise_config = query_configs.filter(config_name='企业查询配置').first()
        def build_query_block(config, bottom_price):
            if not config:
                return {"enabled": False, "bottom_price": None, "customer_price": None, "apis": []}
            apis = []
            # 只显示代理已启用的接口
            for api_id in config.api_combination or []:
                api = ApiConfig.objects.filter(id=api_id).first()
                if api:
                    apis.append({
                        "id": api.id,
                        "name": api.api_name,
                        "cost_price": float(api.cost_price),
                        "enabled": True  # 既然在api_combination中，说明已启用
                    })
            return {
                "enabled": config.is_active,  # 使用QueryConfig的is_active字段
                "bottom_price": float(bottom_price),  # 超管设置的底价
                "customer_price": float(config.customer_price),  # 代理设置的客户价格
                "apis": apis
            }
        response_data = {
            'id': agent.id,
            'username': agent.username,
            'phone': agent.phone,
            'domain_suffix': agent.domain_suffix,
            'is_locked': agent.is_locked,
            'can_customize_settings': agent.can_customize_settings,
            'created_at': agent.created_at,
            'total_commission': float(agent.total_commission),
            'settled_commission': float(agent.settled_commission),
            'unsettled_commission': float(agent.unsettled_commission),
            'personal_query': build_query_block(personal_config, agent.personal_query_price),
            'enterprise_query': build_query_block(enterprise_config, agent.enterprise_query_min_price)
        }
        return ApiResponse.success(data=response_data)
    except AgentUser.DoesNotExist:
        return ApiResponse.not_found("代理不存在")
    except Exception as e:
        print(f"获取代理详情异常: {str(e)}")
        return ApiResponse.error(message="获取代理详情失败", code=ResponseCode.SERVER_ERROR)

# ==================== 外部API配置管理接口 ====================

@csrf_exempt
@require_http_methods(["GET"])
@admin_required
def get_external_api_configs(request: HttpRequest):
    """
    获取所有类型的外部API配置
    """
    try:
        admin = request.user
        configs_data = {}
        
        config_types = [choice[0] for choice in ExternalApiConfig.CONFIG_TYPE_CHOICES]
        
        for config_type in config_types:
            config = ExternalApiConfig.objects.filter(owner_id=admin.id, owner_type='admin', config_type=config_type).first()
            if config:
                configs_data[config_type] = {
                    "id": config.id,
                    "config_name": config.config_name,
                    "credentials": config.credentials,
                    "is_active": config.is_active
                }
            else:
                # 如果配置不存在，返回一个带默认值的结构
                configs_data[config_type] = None

        return ApiResponse.success(data=configs_data)

    except Exception as e:
        print(f"获取外部API配置异常: {str(e)}")
        return ApiResponse.error(message="获取外部API配置失败")

@csrf_exempt
@require_http_methods(["POST"])
@admin_required
def update_external_api_config(request: HttpRequest):
    """
    创建或更新指定的外部API配置
    Body:
        {
            "config_type": "tianyuan_risk_api",
            "config_name": "我的天远API",
            "credentials": {"app_id": "...", "app_secret": "..."},
            "is_active": true
        }
    """
    try:
        admin = request.user
        data = json.loads(request.body)
        
        config_type = data.get('config_type')
        config_name = data.get('config_name')
        credentials = data.get('credentials')
        is_active = data.get('is_active', True)

        if not config_type or not config_name or credentials is None:
            return ApiResponse.param_error("配置类型、名称和凭证为必填项。")

        # 使用 update_or_create 实现"创建或更新"
        config, created = ExternalApiConfig.objects.update_or_create(
            owner_id=admin.id,
            owner_type='admin',
            config_type=config_type,
            defaults={
                'config_name': config_name,
                'credentials': credentials,
                'is_active': is_active
            }
        )
        
        message = "API配置更新成功" if not created else "API配置创建成功"
        print(f"管理员 {message}: {config.config_name}")
        
        return ApiResponse.success(message=message)

    except json.JSONDecodeError:
        return ApiResponse.param_error("无效的JSON数据")
    except Exception as e:
        print(f"更新外部API配置异常: {str(e)}")
        return ApiResponse.error(message="更新外部API配置失败")


# ==================== 授权书管理接口 ====================

@csrf_exempt
@require_http_methods(["GET"])
@admin_required
def get_authorization_letters(request: HttpRequest):
    """
    获取授权书列表，支持翻页和搜索
    
    Query参数:
        search: 搜索关键词（姓名、身份证号）
        date_range: 日期范围 (7d, 30d, 1y, all)
        page: 页码
        page_size: 每页数量
    """
    try:
        search_query = request.GET.get('search', '').strip()
        date_range = request.GET.get('date_range', 'all')
        page_number = int(request.GET.get('page', 1))
        page_size = int(request.GET.get('page_size', 10))

        # 获取所有授权书（管理员可以查看所有）
        from .models import AuthorizationLetter
        queryset = AuthorizationLetter.objects.order_by('-created_at')

        # 搜索过滤
        if search_query:
            # 先通过用户名搜索找到用户ID
            from .models import RegularUser
            user_ids = RegularUser.objects.filter(
                username__icontains=search_query
            ).values_list('id', flat=True)
            
            queryset = queryset.filter(
                Q(masked_name__icontains=search_query) | 
                Q(masked_id_card__icontains=search_query) |
                Q(user_id__in=user_ids)
            )

        # 日期范围过滤
        now = timezone.now()
        if date_range == '7d':
            queryset = queryset.filter(created_at__gte=now - timedelta(days=7))
        elif date_range == '30d':
            queryset = queryset.filter(created_at__gte=now - timedelta(days=30))
        elif date_range == '1y':
            queryset = queryset.filter(created_at__gte=now - timedelta(days=365))

        # 分页
        paginator = Paginator(queryset, page_size)
        page_obj = paginator.get_page(page_number)

        # 构建响应数据
        letters_data = []
        for letter in page_obj.object_list:
            # 获取用户信息
            from .models import RegularUser
            user = RegularUser.objects.filter(id=letter.user_id).first()

            letters_data.append({
                'id': letter.id,
                'username': user.username if user else '用户已注销',
                'masked_name': letter.masked_name,
                'masked_id_card': letter.masked_id_card,
                'download_token': letter.download_token,
                'file_path': '',
                'file_hash': letter.file_hash,
                'is_valid': letter.is_valid,
                'created_at': letter.created_at.isoformat(),
                'updated_at': letter.updated_at.isoformat()
            })

        response_data = {
            'items': letters_data,
            'pagination': {
                'total_items': paginator.count,
                'total_pages': paginator.num_pages,
                'current_page': page_obj.number,
                'page_size': page_size,
                'has_next': page_obj.has_next(),
                'has_previous': page_obj.has_previous(),
            }
        }

        return ApiResponse.success(data=response_data)

    except (ValueError, TypeError):
        return ApiResponse.param_error("分页参数必须是整数。")
    except Exception as e:
        print(f"获取授权书列表异常: {str(e)}")
        return ApiResponse.error(message="获取授权书列表失败", code=ResponseCode.SERVER_ERROR)


@csrf_exempt
@require_http_methods(["GET"])
@admin_required
def download_authorization_letter_admin(request: HttpRequest, token: str):
    """
    管理员下载授权书接口
    
    Args:
        request: HTTP请求
        token: 下载令牌
        
    Returns:
        PDF文件下载
    """
    try:
        print(f"[admin_views] 管理员授权书下载请求: token={token}")
        
        # 查找授权书（管理员可以下载任何授权书）
        from .models import AuthorizationLetter
        try:
            authorization_letter = AuthorizationLetter.objects.get(
                download_token=token,
                is_valid=True
            )
            print(f"[admin_views] 授权书找到: ID={authorization_letter.id}")
        except AuthorizationLetter.DoesNotExist:
            print(f"[admin_views] 授权书不存在或无效: token={token}")
            return ApiResponse.param_error("授权书不存在或已失效")
        
        # 检查文件是否存在
        if not authorization_letter.file_path or not os.path.exists(authorization_letter.file_path):
            print(f"[admin_views] 授权书文件不存在: {authorization_letter.file_path}")
            return ApiResponse.error(message="授权书文件不存在")
        
        # 读取文件内容
        try:
            with open(authorization_letter.file_path, 'rb') as f:
                file_content = f.read()
        except Exception as e:
            print(f"[admin_views] 读取授权书文件失败: {str(e)}")
            return ApiResponse.error(message="读取授权书文件失败")
        
        # 验证文件哈希（可选）
        if authorization_letter.file_hash:
            import hashlib
            current_hash = hashlib.md5(file_content).hexdigest()
            if current_hash != authorization_letter.file_hash:
                print(f"[admin_views] 文件哈希验证失败")
                return ApiResponse.error(message="文件完整性验证失败")
        
        # 生成文件名（使用脱敏信息）
        filename = f"授权书_{authorization_letter.masked_name}_{authorization_letter.created_at.strftime('%Y%m%d')}.pdf"
        
        # 返回文件下载
        from django.http import HttpResponse
        response = HttpResponse(file_content, content_type='application/pdf')
        response['Content-Disposition'] = f'attachment; filename="{filename}"'
        response['Content-Length'] = len(file_content)
        
        print(f"[admin_views] 授权书下载成功: {filename}")
        return response
        
    except Exception as e:
        print(f"[admin_views] 授权书下载异常: {str(e)}")
        return ApiResponse.error(message="下载授权书失败", code=ResponseCode.SERVER_ERROR)


# ==================== 查询记录管理接口 ====================

@csrf_exempt
@require_http_methods(["GET"])
@admin_required
def get_query_records(request: HttpRequest):
    """
    获取查询记录列表，支持翻页、搜索和筛选
    
    Query参数:
        search: 搜索关键词（用户名）
        date_range: 日期范围 (today, 7d, 1m, 3m, 6m, all)
        query_type: 查询类型 (个人查询配置, 企业查询配置)
        status: 查询状态 (success, failed, processing, timeout)
        is_agent: 是否代理查询 (true, false)
        page: 页码
        page_size: 每页数量
    """
    try:
        search_query = request.GET.get('search', '').strip()
        date_range = request.GET.get('date_range', 'all')
        query_type = request.GET.get('query_type', '')
        status = request.GET.get('status', '')
        is_agent = request.GET.get('is_agent', '')
        page_number = int(request.GET.get('page', 1))
        page_size = int(request.GET.get('page_size', 20))

        print(f"[get_query_records] 请求参数: date_range={date_range}, search={search_query}, query_type={query_type}, status={status}")

        from .models import QueryResult, RegularUser, AgentUser
        queryset = QueryResult.objects.order_by('-created_at')

        # 搜索过滤
        if search_query:
            # 通过用户名搜索找到用户ID
            user_ids = RegularUser.objects.filter(
                username__icontains=search_query
            ).values_list('id', flat=True)
            queryset = queryset.filter(user_id__in=user_ids)

        # 日期范围过滤
        date_filter = QueryResult.get_date_filter(date_range)
        print(f"[get_query_records] 日期过滤条件: {date_filter}")
        if date_filter:
            queryset = queryset.filter(**date_filter)

        # 记录过滤后的数量
        filtered_count = queryset.count()
        print(f"[get_query_records] 过滤后记录数量: {filtered_count}")

        # 查询类型过滤（通过关联的订单查询）
        if query_type:
            from .models import Order
            order_ids = Order.objects.filter(query_type=query_type).values_list('id', flat=True)
            queryset = queryset.filter(order_id__in=order_ids)

        # 状态过滤
        if status:
            queryset = queryset.filter(status=status)

        # 代理过滤
        if is_agent == 'true':
            queryset = queryset.filter(agent_id__isnull=False)
        elif is_agent == 'false':
            queryset = queryset.filter(agent_id__isnull=True)

        # 分页
        paginator = Paginator(queryset, page_size)
        page_obj = paginator.get_page(page_number)

        # 构建响应数据
        records_data = []
        for record in page_obj.object_list:
            # 获取用户信息
            user = None
            if record.user_id:
                user = RegularUser.objects.filter(id=record.user_id).first()
            
            # 获取代理信息
            agent_info = None
            if record.agent_id:
                agent = AgentUser.objects.filter(id=record.agent_id).first()
                if agent:
                    agent_info = {
                        "username": agent.username,
                        "phone": agent.phone
                    }

            # 获取订单信息
            order_info = None
            if record.order_id:
                from .models import Order
                order = Order.objects.filter(id=record.order_id).first()
                if order:
                    order_info = {
                        "order_no": order.order_no,
                        "query_type": order.query_type,
                        "amount": float(order.amount)
                    }

            records_data.append({
                'id': record.id,
                'order_id': record.order_id,
                'order_info': order_info,
                'username': user.username if user else '用户已注销',
                'agent_info': agent_info,
                'status': record.status,
                'status_display': record.get_status_display(),
                'error_message': record.error_message,
                'cost_amount': float(record.cost_amount),
                'created_at': record.created_at.isoformat(),
                'completed_time': record.completed_time.isoformat() if record.completed_time else None,
                'is_expired': record.is_expired
            })

        response_data = {
            'items': records_data,
            'pagination': {
                'total_items': paginator.count,
                'total_pages': paginator.num_pages,
                'current_page': page_obj.number,
                'page_size': page_size,
                'has_next': page_obj.has_next(),
                'has_previous': page_obj.has_previous(),
            }
        }

        return ApiResponse.success(data=response_data)

    except (ValueError, TypeError):
        return ApiResponse.param_error("分页参数必须是整数。")
    except Exception as e:
        print(f"获取查询记录异常: {str(e)}")
        return ApiResponse.error(message="获取查询记录失败", code=ResponseCode.SERVER_ERROR)


@csrf_exempt
@require_http_methods(["POST"])
@admin_required
def delete_query_record(request: HttpRequest, record_id: int):
    """
    删除查询记录
    
    Args:
        request: HTTP请求
        record_id: 查询记录ID
        
    Returns:
        删除结果
    """
    try:
        from .models import QueryResult
        
        try:
            record = QueryResult.objects.get(id=record_id)
            record.delete()
            return ApiResponse.success(message="查询记录删除成功")
        except QueryResult.DoesNotExist:
            return ApiResponse.not_found("查询记录不存在")
            
    except Exception as e:
        print(f"删除查询记录异常: {str(e)}")
        return ApiResponse.error(message="删除查询记录失败", code=ResponseCode.SERVER_ERROR)


# ==================== 订单记录管理接口 ====================

@csrf_exempt
@require_http_methods(["GET"])
@admin_required
def get_orders(request: HttpRequest):
    """
    获取订单记录列表，支持翻页、搜索和筛选
    
    Query参数:
        search: 搜索关键词（订单号、用户名）
        agent_search: 代理搜索关键词（代理用户名、手机号）
        date_range: 日期范围 (today, 7d, 6m, all)
        payment_method: 支付方式 (alipay, wechat)
        status: 订单状态 (pending, paid, querying, completed, failed, cancelled)
        page: 页码
        page_size: 每页数量
    """
    try:
        search_query = request.GET.get('search', '').strip()
        agent_search = request.GET.get('agent_search', '').strip()
        date_range = request.GET.get('date_range', 'all')
        payment_method = request.GET.get('payment_method', '')
        status = request.GET.get('status', '')
        page_number = int(request.GET.get('page', 1))
        page_size = int(request.GET.get('page_size', 20))

        from .models import Order, RegularUser, AgentUser
        queryset = Order.objects.order_by('-created_at')

        # 搜索过滤
        if search_query:
            # 通过订单号或用户名搜索
            user_ids = RegularUser.objects.filter(
                username__icontains=search_query
            ).values_list('id', flat=True)
            queryset = queryset.filter(
                Q(order_no__icontains=search_query) |
                Q(user_id__in=user_ids)
            )

        # 代理搜索过滤
        if agent_search:
            # 通过代理用户名或手机号搜索
            agent_ids = AgentUser.objects.filter(
                Q(username__icontains=agent_search) |
                Q(phone__icontains=agent_search)
            ).values_list('id', flat=True)
            queryset = queryset.filter(agent_id__in=agent_ids)

        # 日期范围过滤
        date_filter = Order.get_date_filter(date_range)
        if date_filter:
            queryset = queryset.filter(**date_filter)

        # 支付方式过滤
        if payment_method:
            queryset = queryset.filter(payment_method=payment_method)

        # 状态过滤
        if status:
            queryset = queryset.filter(status=status)

        # 分页
        paginator = Paginator(queryset, page_size)
        page_obj = paginator.get_page(page_number)

        # 构建响应数据
        orders_data = []
        for order in page_obj.object_list:
            # 获取用户信息
            user = RegularUser.objects.filter(id=order.user_id).first()
            
            # 获取代理信息
            agent_info = None
            if order.agent_id:
                agent = AgentUser.objects.filter(id=order.agent_id).first()
                if agent:
                    agent_info = {
                        "username": agent.username,
                        "phone": agent.phone
                    }

            orders_data.append({
                'id': order.id,
                'order_no': order.order_no,
                'third_party_order_id': order.third_party_order_id,
                'third_party_trade_no': order.third_party_trade_no,
                'amount': float(order.amount),
                'username': user.username if user else '未知用户',
                'agent_info': agent_info,
                'query_type': order.query_type,
                'payment_method': order.payment_method,
                'payment_method_display': '支付宝' if order.payment_method == 'alipay' else '微信支付' if order.payment_method == 'wechat' else '未知',
                'status': order.status,
                'status_display': order.get_status_display(),
                'agent_commission': float(order.agent_commission),
                'payment_time': order.payment_time.isoformat() if order.payment_time else None,
                'query_start_time': order.query_start_time.isoformat() if order.query_start_time else None,
                'query_complete_time': order.query_complete_time.isoformat() if order.query_complete_time else None,
                'created_at': order.created_at.isoformat(),
                'updated_at': order.updated_at.isoformat()
            })

        response_data = {
            'items': orders_data,
            'pagination': {
                'total_items': paginator.count,
                'total_pages': paginator.num_pages,
                'current_page': page_obj.number,
                'page_size': page_size,
                'has_next': page_obj.has_next(),
                'has_previous': page_obj.has_previous(),
            }
        }

        return ApiResponse.success(data=response_data)

    except (ValueError, TypeError):
        return ApiResponse.param_error("分页参数必须是整数。")
    except Exception as e:
        print(f"获取订单记录异常: {str(e)}")
        return ApiResponse.error(message="获取订单记录失败", code=ResponseCode.SERVER_ERROR)


@csrf_exempt
@require_http_methods(["POST"])
@admin_required
def refund_order(request: HttpRequest):
    """
    订单退款接口
    
    Args:
        request: HTTP请求，包含退款信息
        {
            "order_id": "订单ID",
            "reason": "退款原因(可选)"
        }
        
    Returns:
        退款结果
    """
    try:
        data = json.loads(request.body)
        order_id = data.get('order_id')
        reason = data.get('reason', '管理员操作退款')
        
        if not order_id:
            return ApiResponse.param_error("缺少订单ID参数")
        
        from .models import Order, AgentUser
        
        # 获取订单
        try:
            order = Order.objects.get(id=order_id)
        except Order.DoesNotExist:
            return ApiResponse.not_found("订单不存在")
        
        # 检查订单状态
        if order.status not in ['paid', 'completed']:
            return ApiResponse.forbidden(f"订单状态不允许退款，当前状态: {order.get_status_display()}")
        
        # 检查是否已经退款
        if order.status == 'refunded':
            return ApiResponse.forbidden("订单已经退款，不能重复退款")
        
        # 获取管理员信息用于配置
        admin = request.user
        
        from .payment_config import PaymentManager
        
        # 初始化支付管理器
        payment_manager = PaymentManager(
            owner_id=admin.id,
            owner_type='admin',
            request=request
        )
        
        # 调用退款接口
        refund_result = payment_manager.create_refund(
            order_no=order.order_no,
            transaction_id=order.third_party_trade_no,
            payment_method=order.payment_method,
            refund_amount=float(order.amount),
            total_amount=float(order.amount),
            reason=reason
        )
        
        print(f"退款接口调用结果: {refund_result}")
        
        if refund_result.get('success'):
            # 处理不同支付方式的退款状态
            refund_no = refund_result.get('out_refund_no', '') or refund_result.get('out_request_no', '')
            final_status = 'PROCESSING'
            status_message = '退款申请已提交'
            
            if order.payment_method == 'alipay':
                # 支付宝退款处理
                fund_change = refund_result.get('fund_change')
                if fund_change == 'Y':
                    # 支付宝退款立即成功
                    final_status = 'SUCCESS'
                    status_message = '退款成功'
                else:
                    # 需要查询确认退款状态
                    try:
                        import time
                        time.sleep(2)  # 等待2秒
                        
                        status_result = payment_manager.query_refund_status(refund_no, order.payment_method)
                        print(f"支付宝退款状态查询结果: {status_result}")
                        
                        if status_result.get('success') and status_result.get('is_success'):
                            final_status = 'SUCCESS'
                            status_message = '退款成功'
                        else:
                            # 继续使用处理中状态
                            status_message = '退款申请已提交，请稍后查询状态'
                            
                    except Exception as e:
                        print(f"查询支付宝退款状态异常: {str(e)}")
                        
            else:
                # 微信退款处理
                try:
                    # 等待2秒后查询状态（给微信一点处理时间）
                    import time
                    time.sleep(2)
                    
                    status_result = payment_manager.query_refund_status(refund_no, order.payment_method)
                    print(f"微信退款状态查询结果: {status_result}")
                    
                    if status_result.get('success'):
                        final_status = status_result.get('status', 'PROCESSING')
                        if final_status == 'SUCCESS':
                            status_message = '退款成功'
                        elif final_status == 'PROCESSING':
                            status_message = '退款处理中'
                        elif final_status in ['CLOSED', 'ABNORMAL']:
                            status_message = f'退款失败: {final_status}'
                        else:
                            status_message = f'退款状态: {final_status}'
                    else:
                        print(f"查询微信退款状态失败: {status_result.get('message')}")
                        
                except Exception as e:
                    print(f"查询微信退款状态异常: {str(e)}")
            
            # 使用数据库事务确保数据一致性
            from django.db import transaction
            
            with transaction.atomic():
                # 如果是代理订单，需要扣减代理的未结算佣金
                if order.agent_id and order.agent_commission > 0:
                    try:
                        agent = AgentUser.objects.select_for_update().get(id=order.agent_id)
                        
                        # 检查未结算佣金是否足够扣减
                        if agent.unsettled_commission >= order.agent_commission:
                            # 扣减未结算佣金
                            agent.unsettled_commission -= order.agent_commission
                            # 扣减总佣金
                            agent.total_commission -= order.agent_commission
                            agent.save()
                            
                            print(f"代理佣金扣减成功: agent_id={order.agent_id}, commission={order.agent_commission}")
                        else:
                            print(f"代理未结算佣金不足，无法扣减: 需要扣减={order.agent_commission}, 当前未结算={agent.unsettled_commission}")
                            # 可以根据业务需求决定是否继续退款或者报错
                            # 这里选择继续退款，但记录日志
                    except AgentUser.DoesNotExist:
                        print(f"代理用户不存在: agent_id={order.agent_id}")
                    except Exception as agent_e:
                        print(f"处理代理佣金扣减异常: {str(agent_e)}")
                        # 佣金扣减失败，但可以继续退款流程
                
            # 更新订单状态
            order.status = 'refunded'
            order.refund_time = timezone.now()
            order.save()
            
            print(f"订单 {order.order_no} 退款成功，金额: {order.amount}")
            
            return ApiResponse.success(
                message=status_message,
                data={
                    'refund_id': refund_result.get('refund_id'),
                    'refund_no': refund_no,
                    'refund_amount': float(order.amount),
                    'order_no': order.order_no,
                    'refund_status': final_status,
                    'refund_success': final_status == 'SUCCESS',
                    'refund_processing': final_status == 'PROCESSING'
                }
            )
        else:
            return ApiResponse.error(
                message=refund_result.get('message', '退款申请失败'),
                code=ResponseCode.ERROR
            )
            
    except json.JSONDecodeError:
        return ApiResponse.param_error("无效的JSON数据")
    except Exception as e:
        print(f"订单退款异常: {str(e)}")
        return ApiResponse.error(message="退款失败，请稍后重试", code=ResponseCode.SERVER_ERROR)


# 旧的退款方法已移除，现在使用PaymentManager统一处理
 
# ==================== 普通用户管理接口 ====================

@csrf_exempt
@require_http_methods(["GET"])
@admin_required
def get_regular_users(request: HttpRequest):
    """
    获取普通用户列表，支持翻页、搜索和筛选
    
    Query参数:
        search: 搜索关键词（用户名、手机号）
        date_range: 日期范围 (today, 7d, 1m, 3m, 6m, all)
        login_type: 登录类型筛选 (wechat, mobile, all)
        agent_id: 代理筛选 (数字ID或'main'表示主站)
        status: 用户状态 (active, deactivated)
        page: 页码
        page_size: 每页数量
    """
    try:
        search_query = request.GET.get('search', '').strip()
        date_range = request.GET.get('date_range', 'all')
        login_type = request.GET.get('login_type', 'all')
        agent_id = request.GET.get('agent_id', '')
        status = request.GET.get('status', 'all')
        page_number = int(request.GET.get('page', 1))
        page_size = int(request.GET.get('page_size', 20))

        from .models import RegularUser, AgentUser
        # 注销用户优先排序，然后按创建时间倒序
        queryset = RegularUser.objects.order_by('-is_deactivated', '-created_at')

        # 搜索过滤
        if search_query:
            queryset = queryset.filter(
                Q(username__icontains=search_query) |
                Q(phone__icontains=search_query)
            )

        # 日期范围过滤
        now = timezone.now()
        if date_range == 'today':
            today_start = now.replace(hour=0, minute=0, second=0, microsecond=0)
            today_end = today_start + timedelta(days=1)
            queryset = queryset.filter(created_at__gte=today_start, created_at__lt=today_end)
        elif date_range == '7d':
            queryset = queryset.filter(created_at__gte=now - timedelta(days=7))
        elif date_range == '1m':
            queryset = queryset.filter(created_at__gte=now - timedelta(days=30))
        elif date_range == '3m':
            queryset = queryset.filter(created_at__gte=now - timedelta(days=90))
        elif date_range == '6m':
            queryset = queryset.filter(created_at__gte=now - timedelta(days=180))

        # 登录类型过滤
        if login_type == 'wechat':
            # 有openid的用户（微信登录）
            queryset = queryset.filter(openid__isnull=False).exclude(openid='')
        elif login_type == 'mobile':
            # 有手机号的用户（手机号登录）
            queryset = queryset.filter(phone__isnull=False).exclude(phone='')

        # 代理筛选
        if agent_id == 'main':
            # 主站用户（无代理）
            queryset = queryset.filter(agent_id__isnull=True)
        elif agent_id and agent_id.isdigit():
            # 特定代理的用户
            queryset = queryset.filter(agent_id=int(agent_id))

        # 状态过滤
        if status == 'active':
            queryset = queryset.filter(is_deactivated=False)
        elif status == 'deactivated':
            queryset = queryset.filter(is_deactivated=True)

        # 分页
        paginator = Paginator(queryset, page_size)
        page_obj = paginator.get_page(page_number)

        # 构建响应数据
        users_data = []
        for user in page_obj.object_list:
            # 获取代理信息
            agent_info = None
            if user.agent_id:
                agent = AgentUser.objects.filter(id=user.agent_id).first()
                if agent:
                    agent_info = {
                        "id": agent.id,
                        "username": agent.username,
                        "domain_suffix": agent.domain_suffix
                    }

            # 判断登录类型
            login_type_display = []
            if user.openid:
                login_type_display.append("微信")
            if user.phone:
                login_type_display.append("手机号")
            if not login_type_display:
                login_type_display.append("未知")

            users_data.append({
                'id': user.id,
                'username': user.username,
                'openid': user.openid,
                'phone': user.phone,
                'agent_info': agent_info,
                'login_type_display': "、".join(login_type_display),
                'is_deactivated': user.is_deactivated,
                'deactivated_at': user.deactivated_at.isoformat() if user.deactivated_at else None,
                'created_at': user.created_at.isoformat()
            })

        # 统计申请注销的用户数量（总数，不受当前筛选条件影响）
        deactivated_count = RegularUser.objects.filter(is_deactivated=True).count()

        response_data = {
            'items': users_data,
            'deactivated_count': deactivated_count,
            'pagination': {
                'total_items': paginator.count,
                'total_pages': paginator.num_pages,
                'current_page': page_obj.number,
                'page_size': page_size,
                'has_next': page_obj.has_next(),
                'has_previous': page_obj.has_previous(),
            }
        }

        return ApiResponse.success(data=response_data)

    except (ValueError, TypeError):
        return ApiResponse.param_error("分页参数必须是整数。")
    except Exception as e:
        print(f"获取普通用户列表异常: {str(e)}")
        return ApiResponse.error(message="获取普通用户列表失败", code=ResponseCode.SERVER_ERROR)


@csrf_exempt
@require_http_methods(["POST"])
@admin_required
def delete_regular_user(request: HttpRequest, user_id: int):
    """
    删除普通用户（软删除，标记为注销）
    
    Args:
        request: HTTP请求
        user_id: 用户ID
        
    Returns:
        删除结果
    """
    try:
        from .models import RegularUser
        
        try:
            user = RegularUser.objects.get(id=user_id)
            
            # 直接删除
            user.delete()
            
            print(f"用户注销成功: {user.username} (ID: {user_id})")
            return ApiResponse.success(message="用户注销成功")
            
        except RegularUser.DoesNotExist:
            return ApiResponse.not_found("用户不存在")
            
    except Exception as e:
        print(f"删除普通用户异常: {str(e)}")
        return ApiResponse.error(message="删除用户失败", code=ResponseCode.SERVER_ERROR)


# ==================== 仪表盘统计接口 ====================

@csrf_exempt
@require_http_methods(["GET"])
@admin_required
def get_dashboard_stats(request: HttpRequest):
    """
    获取仪表盘统计数据
    
    Returns:
        仪表盘统计信息，包括用户统计、查询统计、订单统计等
    """
    try:
        from .models import RegularUser, QueryResult, Order, QueryConfig
        from django.db.models import Count, Sum, Q
        
        # 获取当前时间和今天的时间范围
        now = timezone.now()
        today_start = now.replace(hour=0, minute=0, second=0, microsecond=0)
        today_end = today_start + timedelta(days=1)
        
        print(f"[get_dashboard_stats] 今日时间范围: {today_start} - {today_end}")
        
        # ==================== 用户统计 ====================
        
        # 用户总数
        total_users = RegularUser.objects.filter(is_deactivated=False).count()
        
        # 今日新增用户
        today_new_users = RegularUser.objects.filter(
            created_at__gte=today_start,
            created_at__lt=today_end,
            is_deactivated=False
        ).count()
        
        # 外部来源用户（有手机号的）
        external_users = RegularUser.objects.filter(
            phone__isnull=False,
            is_deactivated=False
        ).exclude(phone='').count()
        
        # 微信来源用户（有openid的）
        wechat_users = RegularUser.objects.filter(
            openid__isnull=False,
            is_deactivated=False
        ).exclude(openid='').count()
        
        user_stats = {
            "total_users": total_users,
            "today_new_users": today_new_users,
            "external_users": external_users,
            "wechat_users": wechat_users
        }
        
        # ==================== 查询统计 ====================
        
        # 查询总数（累计）
        total_queries = QueryResult.objects.count()
        
        # 今日查询总数
        today_queries = QueryResult.objects.filter(
            created_at__gte=today_start,
            created_at__lt=today_end
        ).count()
        
        # 获取个人查询配置ID列表
        personal_config_ids = QueryConfig.objects.filter(
            config_name='个人查询配置'
        ).values_list('id', flat=True)
        
        # 获取企业查询配置ID列表  
        enterprise_config_ids = QueryConfig.objects.filter(
            config_name='企业查询配置'
        ).values_list('id', flat=True)
        
        # 个人查询统计（通过关联的订单查询配置）
        personal_query_orders = Order.objects.filter(
            query_config_id__in=personal_config_ids
        ).values_list('id', flat=True)
        
        total_personal_queries = QueryResult.objects.filter(
            order_id__in=personal_query_orders
        ).count()
        
        today_personal_queries = QueryResult.objects.filter(
            order_id__in=personal_query_orders,
            created_at__gte=today_start,
            created_at__lt=today_end
        ).count()
        
        # 企业查询统计
        enterprise_query_orders = Order.objects.filter(
            query_config_id__in=enterprise_config_ids
        ).values_list('id', flat=True)
        
        total_enterprise_queries = QueryResult.objects.filter(
            order_id__in=enterprise_query_orders
        ).count()
        
        today_enterprise_queries = QueryResult.objects.filter(
            order_id__in=enterprise_query_orders,
            created_at__gte=today_start,
            created_at__lt=today_end
        ).count()
        
        query_stats = {
            "total_queries": total_queries,
            "today_queries": today_queries,
            "personal_queries": {
                "total": total_personal_queries,
                "today": today_personal_queries
            },
            "enterprise_queries": {
                "total": total_enterprise_queries,
                "today": today_enterprise_queries
            }
        }
        
        # ==================== 订单统计 ====================
        
        # 订单总数（累计）
        total_orders = Order.objects.count()
        
        # 今日新增订单
        today_orders = Order.objects.filter(
            created_at__gte=today_start,
            created_at__lt=today_end
        ).count()
        
        # 代理订单（累计和今日）
        total_agent_orders = Order.objects.filter(agent_id__isnull=False).count()
        today_agent_orders = Order.objects.filter(
            agent_id__isnull=False,
            created_at__gte=today_start,
            created_at__lt=today_end
        ).count()
        
        # 主站订单（累计和今日）
        total_main_orders = Order.objects.filter(agent_id__isnull=True).count()
        today_main_orders = Order.objects.filter(
            agent_id__isnull=True,
            created_at__gte=today_start,
            created_at__lt=today_end
        ).count()
        
        # 支付方式统计
        alipay_orders = Order.objects.filter(payment_method='alipay').count()
        wechat_orders = Order.objects.filter(payment_method='wechat').count()
        
        # 订单状态分析
        order_status_stats = Order.objects.values('status').annotate(count=Count('id'))
        status_counts = {item['status']: item['count'] for item in order_status_stats}
        
        # 确保所有状态都有值
        all_statuses = ['pending', 'paid', 'querying', 'completed', 'failed', 'cancelled', 'refunded']
        for status in all_statuses:
            if status not in status_counts:
                status_counts[status] = 0
        
        order_stats = {
            "total_orders": total_orders,
            "today_orders": today_orders,
            "agent_orders": {
                "total": total_agent_orders,
                "today": today_agent_orders
            },
            "main_orders": {
                "total": total_main_orders,
                "today": today_main_orders
            },
            "payment_method": {
                "alipay": alipay_orders,
                "wechat": wechat_orders
            },
            "status_analysis": {
                "completed": status_counts.get('completed', 0),
                "refunded": status_counts.get('refunded', 0),
                "pending": status_counts.get('pending', 0),
                "failed": status_counts.get('failed', 0),
                "paid": status_counts.get('paid', 0),
                "querying": status_counts.get('querying', 0),
                "cancelled": status_counts.get('cancelled', 0)
            }
        }
        
        # ==================== 收入统计 ====================
        
        # 计算总收入（已完成订单）
        total_revenue_result = Order.objects.filter(
            status__in=['completed', 'paid']
        ).aggregate(total=Sum('amount'))
        total_revenue = float(total_revenue_result.get('total') or 0)
        
        # 今日收入
        today_revenue_result = Order.objects.filter(
            status__in=['completed', 'paid'],
            created_at__gte=today_start,
            created_at__lt=today_end
        ).aggregate(total=Sum('amount'))
        today_revenue = float(today_revenue_result.get('total') or 0)
        
        revenue_stats = {
            "total_revenue": total_revenue,
            "today_revenue": today_revenue
        }
        
        # ==================== 汇总响应数据 ====================
        
        response_data = {
            "users": user_stats,
            "queries": query_stats,
            "orders": order_stats,
            "revenue": revenue_stats,
            "generated_at": now.isoformat()
        }
        
        print(f"[get_dashboard_stats] 统计数据生成成功")
        return ApiResponse.success(data=response_data)
        
    except Exception as e:
        print(f"获取仪表盘统计异常: {str(e)}")
        return ApiResponse.error(message="获取统计数据失败", code=ResponseCode.SERVER_ERROR)

# ==================== 代理申请管理接口 ====================

@csrf_exempt
@require_http_methods(["GET"])
@admin_required
def get_agent_applications(request: HttpRequest):
    """
    获取代理申请列表，支持翻页
    
    Query参数:
        page: 页码
        page_size: 每页数量
    """
    try:
        page_number = int(request.GET.get('page', 1))
        page_size = int(request.GET.get('page_size', 20))

        from .models import AgentApplication, RegularUser
        # 按申请时间倒序排列
        queryset = AgentApplication.objects.order_by('-application_time')

        # 分页
        paginator = Paginator(queryset, page_size)
        page_obj = paginator.get_page(page_number)

        # 构建响应数据
        applications_data = []
        for application in page_obj.object_list:
            # 获取关联的用户信息
            user = None
            if application.user_id:
                user = RegularUser.objects.filter(id=application.user_id).first()

            applications_data.append({
                'id': application.id,
                'user_id': application.user_id,
                'username': user.username if user else '未关联',
                'applicant_name': application.applicant_name,
                'contact_type': application.contact_type,
                'contact_type_display': application.get_contact_type_display(),
                'contact_info': application.contact_info,
                'application_time': application.application_time.isoformat()
            })

        response_data = {
            'items': applications_data,
            'pagination': {
                'total_items': paginator.count,
                'total_pages': paginator.num_pages,
                'current_page': page_obj.number,
                'page_size': page_size,
                'has_next': page_obj.has_next(),
                'has_previous': page_obj.has_previous(),
            }
        }

        return ApiResponse.success(data=response_data)

    except (ValueError, TypeError):
        return ApiResponse.param_error("分页参数必须是整数。")
    except Exception as e:
        print(f"获取代理申请列表异常: {str(e)}")
        return ApiResponse.error(message="获取代理申请列表失败", code=ResponseCode.SERVER_ERROR)


@csrf_exempt
@require_http_methods(["POST"])
@admin_required
def delete_agent_application(request: HttpRequest, application_id: int):
    """
    删除代理申请
    
    Args:
        request: HTTP请求
        application_id: 代理申请ID
        
    Returns:
        删除结果
    """
    try:
        from .models import AgentApplication
        
        try:
            application = AgentApplication.objects.get(id=application_id)
            applicant_name = application.applicant_name  # 保存用于日志
            application.delete()
            
            print(f"代理申请删除成功: {applicant_name} (ID: {application_id})")
            return ApiResponse.success(message="代理申请删除成功")
            
        except AgentApplication.DoesNotExist:
            return ApiResponse.not_found("代理申请不存在")
            
    except Exception as e:
        print(f"删除代理申请异常: {str(e)}")
        return ApiResponse.error(message="删除代理申请失败", code=ResponseCode.SERVER_ERROR)

# ==================== 佣金申请管理接口 ====================

@csrf_exempt
@require_http_methods(["GET"])
@admin_required
def get_commission_withdrawals(request: HttpRequest):
    """
    获取佣金提现申请列表，支持翻页、搜索和筛选
    
    Query参数:
        search: 搜索关键词（代理用户名、手机号）
        date_range: 日期范围 (today, 7d, 1m, 3m, all)
        status: 申请状态 (pending, completed, rejected)
        page: 页码
        page_size: 每页数量
    """
    try:
        search_query = request.GET.get('search', '').strip()
        date_range = request.GET.get('date_range', 'all')
        status = request.GET.get('status', '')
        page_number = int(request.GET.get('page', 1))
        page_size = int(request.GET.get('page_size', 20))

        from .models import CommissionWithdrawal, AgentUser, AgentPaymentConfig
        queryset = CommissionWithdrawal.objects.order_by('-created_at')

        # 搜索过滤
        if search_query:
            # 通过代理用户名或手机号搜索
            agent_ids = AgentUser.objects.filter(
                Q(username__icontains=search_query) |
                Q(phone__icontains=search_query)
            ).values_list('id', flat=True)
            queryset = queryset.filter(agent_id__in=agent_ids)

        # 日期范围过滤
        now = timezone.now()
        if date_range == 'today':
            today_start = now.replace(hour=0, minute=0, second=0, microsecond=0)
            today_end = today_start + timedelta(days=1)
            queryset = queryset.filter(created_at__gte=today_start, created_at__lt=today_end)
        elif date_range == '7d':
            queryset = queryset.filter(created_at__gte=now - timedelta(days=7))
        elif date_range == '1m':
            queryset = queryset.filter(created_at__gte=now - timedelta(days=30))
        elif date_range == '3m':
            queryset = queryset.filter(created_at__gte=now - timedelta(days=90))

        # 状态过滤
        if status:
            queryset = queryset.filter(status=status)

        # 分页
        paginator = Paginator(queryset, page_size)
        page_obj = paginator.get_page(page_number)

        # 构建响应数据
        withdrawals_data = []
        for withdrawal in page_obj.object_list:
            # 获取代理信息
            agent = AgentUser.objects.filter(id=withdrawal.agent_id).first()
            
            # 获取收款配置
            payment_config = AgentPaymentConfig.objects.filter(agent_id=withdrawal.agent_id).first()
            payment_info = None
            if payment_config:
                payment_info = {
                    "payment_method": payment_config.payment_method,
                    "payment_method_display": payment_config.get_payment_method_display(),
                    "payment_account": payment_config.payment_account,
                    "payment_name": payment_config.payment_name,
                    "payment_qr_code": payment_config.payment_qr_code
                }

            withdrawals_data.append({
                'id': withdrawal.id,
                'agent_id': withdrawal.agent_id,
                'agent_info': {
                    "username": agent.username if agent else '未知代理',
                    "phone": agent.phone if agent else '',
                    "domain_suffix": agent.domain_suffix if agent else '',
                    "total_commission": float(agent.total_commission) if agent else 0,
                    "settled_commission": float(agent.settled_commission) if agent else 0,
                    "unsettled_commission": float(agent.unsettled_commission) if agent else 0
                } if agent else None,
                'withdrawal_amount': float(withdrawal.withdrawal_amount),
                'unsettled_amount_snapshot': float(withdrawal.unsettled_amount_snapshot),
                'status': withdrawal.status,
                'status_display': withdrawal.get_status_display(),
                'admin_note': withdrawal.admin_note,
                'payment_info': payment_info,
                'created_at': withdrawal.created_at.isoformat(),
                'completed_at': withdrawal.completed_at.isoformat() if withdrawal.completed_at else None
            })

        response_data = {
            'items': withdrawals_data,
            'pagination': {
                'total_items': paginator.count,
                'total_pages': paginator.num_pages,
                'current_page': page_obj.number,
                'page_size': page_size,
                'has_next': page_obj.has_next(),
                'has_previous': page_obj.has_previous(),
            }
        }

        return ApiResponse.success(data=response_data)

    except (ValueError, TypeError):
        return ApiResponse.param_error("分页参数必须是整数。")
    except Exception as e:
        print(f"获取佣金提现申请列表异常: {str(e)}")
        return ApiResponse.error(message="获取佣金提现申请列表失败", code=ResponseCode.SERVER_ERROR)


@csrf_exempt
@require_http_methods(["POST"])
@admin_required
def process_commission_withdrawal(request: HttpRequest):
    """
    处理佣金提现申请
    
    Args:
        request: HTTP请求，包含处理信息
        {
            "withdrawal_id": "提现申请ID",
            "action": "approve|reject",
            "admin_note": "管理员备注"
        }
        
    Returns:
        处理结果
    """
    try:
        data = json.loads(request.body)
        withdrawal_id = data.get('withdrawal_id')
        action = data.get('action')  # approve 或 reject
        admin_note = data.get('admin_note', '').strip()
        
        if not withdrawal_id or not action:
            return ApiResponse.param_error("缺少必要参数")
        
        if action not in ['approve', 'reject']:
            return ApiResponse.param_error("无效的操作类型")
        
        from .models import CommissionWithdrawal, AgentUser
        
        # 获取提现申请
        try:
            withdrawal = CommissionWithdrawal.objects.get(id=withdrawal_id)
        except CommissionWithdrawal.DoesNotExist:
            return ApiResponse.not_found("提现申请不存在")
        
        # 检查申请状态
        if withdrawal.status != 'pending':
            return ApiResponse.forbidden("该申请已被处理")
        
        # 获取代理信息
        try:
            agent = AgentUser.objects.get(id=withdrawal.agent_id)
        except AgentUser.DoesNotExist:
            return ApiResponse.not_found("代理用户不存在")
        
        from django.db import transaction
        with transaction.atomic():
            if action == 'approve':
                # 批准提现申请
                
                # 验证代理当前未结算佣金是否足够
                if agent.unsettled_commission < withdrawal.withdrawal_amount:
                    return ApiResponse.param_error("代理当前未结算佣金不足")
                
                # 更新代理佣金字段
                agent.unsettled_commission -= withdrawal.withdrawal_amount
                agent.settled_commission += withdrawal.withdrawal_amount
                agent.save()
                
                # 更新提现申请状态
                withdrawal.status = 'completed'
                withdrawal.completed_at = timezone.now()
                withdrawal.admin_note = admin_note or '管理员已批准提现申请'
                withdrawal.save()
                
                print(f"佣金提现申请已批准: 代理{agent.username}, 金额{withdrawal.withdrawal_amount}元")
                
                return ApiResponse.success(
                    message="提现申请已批准",
                    data={
                        'withdrawal_id': withdrawal.id,
                        'agent_id': agent.id,
                        'withdrawal_amount': float(withdrawal.withdrawal_amount),
                        'agent_current_status': {
                            'total_commission': float(agent.total_commission),
                            'settled_commission': float(agent.settled_commission),
                            'unsettled_commission': float(agent.unsettled_commission)
                        }
                    }
                )
                
            elif action == 'reject':
                # 拒绝提现申请
                withdrawal.status = 'rejected'
                withdrawal.completed_at = timezone.now()
                withdrawal.admin_note = admin_note or '管理员已拒绝提现申请'
                withdrawal.save()
                
                print(f"佣金提现申请已拒绝: 代理{agent.username}, 金额{withdrawal.withdrawal_amount}元")
                
                return ApiResponse.success(
                    message="提现申请已拒绝",
                    data={
                        'withdrawal_id': withdrawal.id,
                        'agent_id': agent.id,
                        'withdrawal_amount': float(withdrawal.withdrawal_amount)
                    }
                )
            
    except json.JSONDecodeError:
        return ApiResponse.param_error("无效的JSON数据")
    except Exception as e:
        print(f"处理佣金提现申请异常: {str(e)}")
        return ApiResponse.error(message="处理提现申请失败，请稍后重试", code=ResponseCode.SERVER_ERROR)


@csrf_exempt
@require_http_methods(["GET"])
@admin_required
def get_commission_withdrawal_detail(request: HttpRequest, withdrawal_id: int):
    """
    获取佣金提现申请详情，包括代理信息和收款配置
    
    Args:
        request: HTTP请求
        withdrawal_id: 提现申请ID
        
    Returns:
        提现申请详情
    """
    try:
        from .models import CommissionWithdrawal, AgentUser, AgentPaymentConfig
        
        # 获取提现申请
        try:
            withdrawal = CommissionWithdrawal.objects.get(id=withdrawal_id)
        except CommissionWithdrawal.DoesNotExist:
            return ApiResponse.not_found("提现申请不存在")
        
        # 获取代理信息
        agent = AgentUser.objects.filter(id=withdrawal.agent_id).first()
        if not agent:
            return ApiResponse.not_found("代理用户不存在")
        
        # 获取收款配置
        payment_config = AgentPaymentConfig.objects.filter(agent_id=withdrawal.agent_id).first()
        
        response_data = {
            'withdrawal': {
                'id': withdrawal.id,
                'withdrawal_amount': float(withdrawal.withdrawal_amount),
                'unsettled_amount_snapshot': float(withdrawal.unsettled_amount_snapshot),
                'status': withdrawal.status,
                'status_display': withdrawal.get_status_display(),
                'admin_note': withdrawal.admin_note,
                'created_at': withdrawal.created_at.isoformat(),
                'completed_at': withdrawal.completed_at.isoformat() if withdrawal.completed_at else None
            },
            'agent': {
                'id': agent.id,
                'username': agent.username,
                'phone': agent.phone,
                'domain_suffix': agent.domain_suffix,
                'total_commission': float(agent.total_commission),
                'settled_commission': float(agent.settled_commission),
                'unsettled_commission': float(agent.unsettled_commission),
                'created_at': agent.created_at.isoformat()
            },
            'payment_config': {
                'payment_method': payment_config.payment_method if payment_config else '',
                'payment_method_display': payment_config.get_payment_method_display() if payment_config else '',
                'payment_account': payment_config.payment_account if payment_config else '',
                'payment_name': payment_config.payment_name if payment_config else '',
                'payment_qr_code': payment_config.payment_qr_code if payment_config else '',
                'created_at': payment_config.created_at.isoformat() if payment_config else None
            } if payment_config else None
        }
        
        return ApiResponse.success(data=response_data)
        
    except Exception as e:
        print(f"获取佣金提现申请详情异常: {str(e)}")
        return ApiResponse.error(message="获取提现申请详情失败", code=ResponseCode.SERVER_ERROR)
 