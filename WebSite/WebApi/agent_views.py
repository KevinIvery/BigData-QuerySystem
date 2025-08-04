"""
代理管理后台相关的视图函数
"""

import json
import time
from django.http import HttpRequest
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.contrib.auth.hashers import check_password, make_password

from .response import ApiResponse, ResponseCode
from .models import AgentUser, SliderCaptcha, SystemConfig, QueryConfig, ApiConfig
from .decorators import agent_required

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
def agent_login(request: HttpRequest):
    """
    代理登录接口
    
    Args:
        request: 包含登录信息的HTTP请求
        {
            "username": "代理用户名",
            "password": "代理密码", 
            "captcha_token": "验证码token",
            "fingerprint": "客户端指纹"
        }
        
    Returns:
        登录结果: 代理信息
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
        
        print(f"代理登录请求: username={username}, ip={client_ip}, fingerprint={client_fingerprint}")
        
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
        
        # 查找代理用户
        try:
            agent = AgentUser.objects.get(username=username)
        except AgentUser.DoesNotExist:
            print(f"代理用户不存在: {username}")
            return ApiResponse.unauthorized("用户名或密码错误")
        
        # 检查账户是否被锁定
        if agent.is_locked:
            return ApiResponse.forbidden("账户已被锁定，请联系管理员")
        
        # 验证密码
        if not check_password(password, agent.password):
            print(f"代理密码错误: {username}")
            return ApiResponse.unauthorized("用户名或密码错误")
        
        # 设置session
        request.session['user_info'] = {
            'user_id': agent.id,
            'user_type': 'agent',
            'username': agent.username,
            'login_time': current_time
        }
        
        # 设置session过期时间为7天
        request.session.set_expiry(7 * 24 * 60 * 60)
        
        print(f"代理登录成功: {username}, session_key: {request.session.session_key}")
        
        # 返回登录成功信息
        response_data = {
            "username": agent.username,
            "phone": agent.phone,
            "domain_suffix": agent.domain_suffix,
            "can_customize_settings": agent.can_customize_settings,
            "created_at": int(agent.created_at.timestamp())
        }
        
        return ApiResponse.success(message="登录成功", data=response_data)
        
    except json.JSONDecodeError:
        return ApiResponse.param_error("无效的JSON数据")
    except Exception as e:
        print(f"代理登录异常: {str(e)}")
        return ApiResponse.error(message="服务器内部错误", code=ResponseCode.SERVER_ERROR)

@csrf_exempt
@require_http_methods(["POST"])
@agent_required
def agent_logout(request: HttpRequest):
    """
    代理退出登录接口
    
    Args:
        request: HTTP请求
        
    Returns:
        退出结果
    """
    try:
        # 获取当前用户信息
        user_info = request.session.get('user_info')
        
        if user_info and user_info.get('user_type') == 'agent':
            username = user_info.get('username')
            print(f"代理退出登录: {username}")
            
            # 清除session
            request.session.flush()
            
            return ApiResponse.success(message="退出成功")
        else:
            # 即使没有有效session，也清除session并返回成功
            request.session.flush()
            return ApiResponse.success(message="退出成功")
            
    except Exception as e:
        print(f"代理退出异常: {str(e)}")
        
        # 即使出现异常，也尝试清除session
        try:
            request.session.flush()
        except:
            pass
            
        return ApiResponse.success(message="退出成功")

@csrf_exempt
@require_http_methods(["GET", "POST"])
@agent_required
def agent_auth_check(request: HttpRequest):
    """
    代理认证状态检查接口
    
    Returns:
        认证状态信息
    """
    try:
        # 获取当前代理用户信息
        agent = request.user
        
        response_data = {
            "username": agent.username,
            "phone": agent.phone,
            "domain_suffix": agent.domain_suffix,
            "can_customize_settings": agent.can_customize_settings,
            "is_locked": agent.is_locked,
            "total_profit": float(agent.total_profit),
            "created_at": int(agent.created_at.timestamp())
        }
        
        return ApiResponse.success(message="ok", data=response_data)
        
    except Exception as e:
        print(f"代理认证检查异常: {str(e)}")
        return ApiResponse.error(message="no", code=ResponseCode.SERVER_ERROR)

# ==================== 代理个人信息管理接口 ====================

@csrf_exempt
@require_http_methods(["POST"])
@agent_required
def change_password(request: HttpRequest):
    """
    代理修改密码接口
    
    Args:
        request: 包含密码信息的HTTP请求
        {
            "old_password": "当前密码",
            "new_password": "新密码",
            "confirm_password": "确认新密码"
        }
        
    Returns:
        修改结果
    """
    try:
        agent = request.user
        data = json.loads(request.body)
        
        old_password = data.get('old_password', '').strip()
        new_password = data.get('new_password', '').strip()
        confirm_password = data.get('confirm_password', '').strip()
        
        # 验证必填参数
        if not old_password or not new_password or not confirm_password:
            return ApiResponse.param_error("所有密码字段都不能为空")
        
        # 验证当前密码
        if not check_password(old_password, agent.password):
            return ApiResponse.param_error("当前密码错误")
        
        # 验证新密码长度
        if len(new_password) < 6:
            return ApiResponse.param_error("新密码长度不能少于6位")
        
        # 验证新密码确认
        if new_password != confirm_password:
            return ApiResponse.param_error("两次输入的新密码不一致")
        
        # 验证新密码不能与当前密码相同
        if check_password(new_password, agent.password):
            return ApiResponse.param_error("新密码不能与当前密码相同")
        
        # 更新密码
        agent.password = make_password(new_password)
        agent.save()
        
        print(f"代理密码修改成功: {agent.username}")
        
        return ApiResponse.success(message="密码修改成功")
        
    except json.JSONDecodeError:
        return ApiResponse.param_error("无效的JSON数据")
    except Exception as e:
        print(f"代理修改密码异常: {str(e)}")
        return ApiResponse.error(message="修改密码失败", code=ResponseCode.SERVER_ERROR)

# ==================== 系统配置管理接口 ====================

@csrf_exempt
@require_http_methods(["POST"])
@agent_required
def get_system_config(request: HttpRequest):
    """
    获取代理系统配置接口
    
    Returns:
        系统配置信息和权限信息
    """
    try:
        agent = request.user
        
        # 获取代理的系统配置
        try:
            config = SystemConfig.objects.get(owner_id=agent.id, owner_type='agent')
            config_data = {
                "id": config.id,
                "logo": config.logo,
                "site_title": config.site_title,
                "keywords": config.keywords,
                "description": config.description,
                "show_query_price": config.show_query_price,
                "query_entrance_desc": config.query_entrance_desc,
                "customer_service_url": config.customer_service_url,
                "force_wechat_access": config.force_wechat_access,
                "footer_copyright": config.footer_copyright,
                "created_at": config.created_at.isoformat(),
                "updated_at": config.updated_at.isoformat(),
                # 权限控制
                "can_customize": agent.can_customize_settings,
                "readonly_message": "请联系管理员修改系统配置" if not agent.can_customize_settings else None
            }
        except SystemConfig.DoesNotExist:
            # 如果没有配置，返回默认值
            config_data = {
                "id": None,
                "logo": "",
                "site_title": "大数据查询平台",
                "keywords": "大数据,查询,平台",
                "description": "专业的大数据查询服务平台",
                "show_query_price": True,
                "query_entrance_desc": "",
                "customer_service_url": "",
                "force_wechat_access": False,
                "footer_copyright": "",
                "created_at": None,
                "updated_at": None,
                # 权限控制
                "can_customize": agent.can_customize_settings,
                "readonly_message": "请联系管理员修改系统配置" if not agent.can_customize_settings else None
            }
        
        return ApiResponse.success(data=config_data)
        
    except Exception as e:
        print(f"获取代理系统配置异常: {str(e)}")
        return ApiResponse.error(message="获取系统配置失败", code=ResponseCode.SERVER_ERROR)

@csrf_exempt
@require_http_methods(["POST"])
@agent_required
def update_system_config(request: HttpRequest):
    """
    更新代理系统配置接口
    
    Args:
        request: 包含配置信息的HTTP请求
        
    Returns:
        更新结果
    """
    try:
        agent = request.user
        
        # 检查权限
        if not agent.can_customize_settings:
            return ApiResponse.forbidden("您没有权限修改系统配置，请联系管理员")
        
        data = json.loads(request.body)
        
        # 获取或创建配置
        config, created = SystemConfig.objects.get_or_create(
            owner_id=agent.id,
            owner_type='agent',
            defaults={
                'logo': '',
                'site_title': '大数据查询平台',
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
        
        print(f"代理系统配置更新成功: {agent.username}")
        
        # 返回更新后的配置
        response_data = {
            "id": config.id,
            "logo": config.logo,
            "site_title": config.site_title,
            "keywords": config.keywords,
            "description": config.description,
            "show_query_price": config.show_query_price,
            "query_entrance_desc": config.query_entrance_desc,
            "customer_service_url": config.customer_service_url,
            "force_wechat_access": config.force_wechat_access,
            "footer_copyright": config.footer_copyright,
            "updated_at": config.updated_at.isoformat(),
            "can_customize": agent.can_customize_settings
        }
        
        return ApiResponse.success(message="系统配置更新成功", data=response_data)
        
    except json.JSONDecodeError:
        return ApiResponse.param_error("无效的JSON数据")
    except Exception as e:
        print(f"更新代理系统配置异常: {str(e)}")
        return ApiResponse.error(message="更新系统配置失败", code=ResponseCode.SERVER_ERROR)

# ==================== 查询配置管理接口 ====================

@csrf_exempt
@require_http_methods(["POST"])
@agent_required
def get_query_configs(request: HttpRequest):
    """
    获取代理查询配置及其关联的API接口信息
    
    Returns:
        返回代理的查询配置列表，包含成本价、客户价、接口状态等信息
    """
    try:
        agent = request.user
        
        # 获取该代理的所有查询配置
        query_configs = QueryConfig.objects.filter(owner_id=agent.id, owner_type='agent').order_by('id')
        
        # 获取超管的主站配置，以了解每个配置类型应该包含哪些接口
        admin_query_configs = QueryConfig.objects.filter(owner_type='admin').order_by('id')
        admin_config_map = {config.config_name: config for config in admin_query_configs}
        
        response_data = []
        for config in query_configs:
            # 获取超管对应配置的接口组合（这是该配置类型的"全集"）
            admin_config = admin_config_map.get(config.config_name)
            if admin_config and admin_config.api_combination:
                all_possible_api_ids = admin_config.api_combination
                agent_enabled_api_ids = config.api_combination or []
                
                # 获取所有可能的接口信息
                all_apis = ApiConfig.objects.filter(id__in=all_possible_api_ids).order_by('id')
                apis_data = [{
                    "id": api.id,
                    "api_name": api.api_name,
                    "is_active": api.id in agent_enabled_api_ids  # 判断是否在代理的启用列表中
                } for api in all_apis]
            else:
                apis_data = []
            
            # 获取超管设置的底价限制
            if config.config_name == '个人查询配置':
                bottom_price = agent.personal_query_price
            elif config.config_name == '企业查询配置':
                bottom_price = agent.enterprise_query_min_price
            else:
                bottom_price = 0
            
            response_data.append({
                "id": config.id,
                "config_name": config.config_name,
                "category": config.category,
                "customer_price": f"{config.customer_price:.2f}",  # 代理设置的客户价格
                "bottom_price": f"{bottom_price:.2f}",  # 超管设置的底价限制
                "is_active": config.is_active,
                "apis": apis_data,
                "readonly_message": "接口配置由管理员控制，如需修改请联系管理员"
            })
            
        return ApiResponse.success(data=response_data)
        
    except Exception as e:
        print(f"获取代理查询配置异常: {str(e)}")
        return ApiResponse.error(message="获取查询配置失败", code=ResponseCode.SERVER_ERROR)

@csrf_exempt
@require_http_methods(["POST"])
@agent_required
def update_query_config(request: HttpRequest, config_id: int):
    """
    更新代理查询配置（仅允许修改客户价格）
    
    Args:
        request: 包含更新信息的HTTP请求
        config_id: 要更新的查询配置ID
        {
            "customer_price": 19.90  // 只允许修改客户价格
        }
    """
    try:
        agent = request.user
        data = json.loads(request.body)
        
        customer_price = data.get('customer_price')
        
        if customer_price is None:
            return ApiResponse.param_error("客户价格不能为空")
        
        try:
            customer_price = float(customer_price)
        except (ValueError, TypeError):
            return ApiResponse.param_error("价格必须是有效的数字")
        
        if customer_price < 0:
            return ApiResponse.param_error("价格不能为负数")
        
        # 获取要更新的配置
        try:
            config_to_update = QueryConfig.objects.get(id=config_id, owner_id=agent.id, owner_type='agent')
        except QueryConfig.DoesNotExist:
            return ApiResponse.not_found("指定的查询配置不存在")
        
        # 检查价格是否低于底价限制
        if config_to_update.config_name == '个人查询配置':
            bottom_price = float(agent.personal_query_price)
        elif config_to_update.config_name == '企业查询配置':
            bottom_price = float(agent.enterprise_query_min_price)
        else:
            bottom_price = 0
        
        if customer_price < bottom_price:
            return ApiResponse.param_error(f"客户价格不能低于底价限制 ¥{bottom_price:.2f}")
        
        # 更新客户价格
        config_to_update.customer_price = customer_price
        config_to_update.save()
        
        print(f"代理查询配置价格更新成功: {agent.username} - {config_to_update.config_name} - ¥{customer_price}")
        
        response_data = {
            "id": config_to_update.id,
            "config_name": config_to_update.config_name,
            "customer_price": f"{config_to_update.customer_price:.2f}",
            "bottom_price": f"{bottom_price:.2f}",
            "updated_at": config_to_update.updated_at.isoformat()
        }
        
        return ApiResponse.success(message="价格更新成功", data=response_data)
        
    except json.JSONDecodeError:
        return ApiResponse.param_error("无效的JSON数据")
    except Exception as e:
        print(f"更新代理查询配置异常: {str(e)}")
        return ApiResponse.error(message="更新查询配置失败", code=ResponseCode.SERVER_ERROR) 

# ==================== 代理订单记录管理接口 ====================

@csrf_exempt
@require_http_methods(["GET"])
@agent_required
def get_agent_orders(request: HttpRequest):
    """
    获取代理订单记录列表，支持翻页、搜索和筛选
    
    Query参数:
        search: 搜索关键词（订单号）
        date_range: 日期范围 (today, 7d, 15d, 30d, all)
        status: 订单状态 (pending, paid, querying, completed, failed, cancelled, refunded)
        page: 页码
        page_size: 每页数量
    """
    try:
        agent = request.user
        search_query = request.GET.get('search', '').strip()
        date_range = request.GET.get('date_range', 'all')
        status = request.GET.get('status', '')
        page_number = int(request.GET.get('page', 1))
        page_size = int(request.GET.get('page_size', 20))

        print(f"[get_agent_orders] 代理 {agent.username} 请求订单列表: date_range={date_range}, search={search_query}, status={status}")

        from .models import Order, RegularUser
        from django.core.paginator import Paginator
        from django.db.models import Q
        from django.utils import timezone
        from datetime import timedelta
        
        # 只查询该代理的订单
        queryset = Order.objects.filter(agent_id=agent.id).order_by('-created_at')

        # 搜索过滤（订单号）
        if search_query:
            queryset = queryset.filter(order_no__icontains=search_query)

        # 日期范围过滤
        now = timezone.now()
        if date_range == 'today':
            today_start = now.replace(hour=0, minute=0, second=0, microsecond=0)
            today_end = today_start + timedelta(days=1)
            queryset = queryset.filter(created_at__gte=today_start, created_at__lt=today_end)
        elif date_range == '7d':
            queryset = queryset.filter(created_at__gte=now - timedelta(days=7))
        elif date_range == '15d':
            queryset = queryset.filter(created_at__gte=now - timedelta(days=15))
        elif date_range == '30d':
            queryset = queryset.filter(created_at__gte=now - timedelta(days=30))

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

            orders_data.append({
                'id': order.id,
                'order_no': order.order_no,
                'amount': float(order.amount),
                'username': user.username if user else '已注销用户',
                'query_type': order.query_type,
                'payment_method': order.payment_method,
                'payment_method_display': '支付宝' if order.payment_method == 'alipay' else '微信支付' if order.payment_method == 'wechat' else '待付款',
                'status': order.status,
                'status_display': order.get_status_display(),
                'agent_commission': float(order.agent_commission),  # 本次获得的佣金
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
        print(f"获取代理订单记录异常: {str(e)}")
        return ApiResponse.error(message="获取订单记录失败", code=ResponseCode.SERVER_ERROR)

# ==================== 代理仪表盘统计信息相关接口 ====================

@csrf_exempt
@require_http_methods(["GET"])
@agent_required
def get_agent_dashboard_stats(request: HttpRequest):
    """
    获取代理仪表盘统计信息
    
    Returns:
        代理的各种统计数据
    """
    try:
        agent = request.user # Changed from request.agent to request.user
        
        from .models import RegularUser, Order
        from django.db.models import Q, Count, Sum
        from django.utils import timezone
        from datetime import timedelta
        
        # 获取当前时间
        now = timezone.now()
        today_start = now.replace(hour=0, minute=0, second=0, microsecond=0)
        today_end = today_start + timedelta(days=1)
        thirty_days_ago = now - timedelta(days=30)
        
        print(f"[代理仪表盘] 代理ID: {agent.id}, 统计时间范围: 今日={today_start}~{today_end}, 30天前={thirty_days_ago}")
        
        # 1. 佣金统计信息（直接从AgentUser表获取）
        commission_stats = {
            "total_profit": float(agent.total_profit),           # 累计订单收入
            "total_commission": float(agent.total_commission),   # 累计佣金
            "unsettled_commission": float(agent.unsettled_commission),  # 未结算佣金
            "settled_commission": float(agent.settled_commission)        # 已结算佣金
        }
        
        # 2. 用户统计信息
        # 属于该代理的用户总数量
        total_users = RegularUser.objects.filter(agent_id=agent.id, is_deactivated=False).count()
        
        # 今日新增用户数量
        today_new_users = RegularUser.objects.filter(
            agent_id=agent.id,
            is_deactivated=False,
            created_at__gte=today_start,
            created_at__lt=today_end
        ).count()
        
        # 近30日每日新增用户数据（表格数据）
        daily_users_data = []
        for i in range(30):
            date = now - timedelta(days=i)
            date_start = date.replace(hour=0, minute=0, second=0, microsecond=0)
            date_end = date_start + timedelta(days=1)
            
            daily_count = RegularUser.objects.filter(
                agent_id=agent.id,
                is_deactivated=False,
                created_at__gte=date_start,
                created_at__lt=date_end
            ).count()
            
            daily_users_data.append({
                "date": date.strftime("%Y-%m-%d"),
                "new_users": daily_count
            })
        
        # 按日期倒序排列（最新的在前面）
        daily_users_data.reverse()
        
        user_stats = {
            "total_users": total_users,
            "today_new_users": today_new_users,
            "daily_users_30d": daily_users_data
        }
        
        # 3. 订单统计信息
        # 只统计已支付（paid, querying, completed）和退款（refunded）的订单
        paid_statuses = ['paid', 'querying', 'completed', 'refunded']
        
        # 累计订单数量
        total_orders = Order.objects.filter(
            agent_id=agent.id,
            status__in=paid_statuses
        ).count()
        
        # 今日订单量（已支付）
        today_orders = Order.objects.filter(
            agent_id=agent.id,
            status__in=['paid', 'querying', 'completed'],  # 今日订单不包括退款
            created_at__gte=today_start,
            created_at__lt=today_end
        ).count()
        
        # 今日退款量
        today_refunds = Order.objects.filter(
            agent_id=agent.id,
            status='refunded',
            created_at__gte=today_start,
            created_at__lt=today_end
        ).count()
        
        # 近30天每日订单和退款数据（表格数据）
        daily_orders_data = []
        for i in range(30):
            date = now - timedelta(days=i)
            date_start = date.replace(hour=0, minute=0, second=0, microsecond=0)
            date_end = date_start + timedelta(days=1)
            
            # 当日订单量
            daily_orders = Order.objects.filter(
                agent_id=agent.id,
                status__in=['paid', 'querying', 'completed'],
                created_at__gte=date_start,
                created_at__lt=date_end
            ).count()
            
            # 当日退款量
            daily_refunds = Order.objects.filter(
                agent_id=agent.id,
                status='refunded',
                created_at__gte=date_start,
                created_at__lt=date_end
            ).count()
            
            daily_orders_data.append({
                "date": date.strftime("%Y-%m-%d"),
                "orders": daily_orders,
                "refunds": daily_refunds
            })
        
        # 按日期倒序排列（最新的在前面）
        daily_orders_data.reverse()
        
        order_stats = {
            "total_orders": total_orders,
            "today_orders": today_orders,
            "today_refunds": today_refunds,
            "daily_orders_30d": daily_orders_data
        }
        
        # 4. 汇总统计数据
        dashboard_stats = {
            "commission_stats": commission_stats,
            "user_stats": user_stats,
            "order_stats": order_stats,
            "updated_at": now.isoformat()
        }
        
        print(f"[代理仪表盘] 统计完成: 用户={total_users}, 今日新增={today_new_users}, 订单={total_orders}, 今日订单={today_orders}")
        
        return ApiResponse.success(message="获取仪表盘统计成功", data=dashboard_stats)
        
    except Exception as e:
        print(f"获取代理仪表盘统计异常: {str(e)}")
        return ApiResponse.error(message="获取仪表盘统计失败", code=ResponseCode.SERVER_ERROR)

# ==================== 代理佣金提现相关接口 ====================

@csrf_exempt
@require_http_methods(["GET"])
@agent_required
def get_agent_payment_config(request: HttpRequest):
    """
    获取代理收款配置状态
    
    Returns:
        收款配置信息或未配置状态
    """
    try:
        agent = request.user # Changed from request.agent to request.user
        
        from .models import AgentPaymentConfig
        
        try:
            config = AgentPaymentConfig.objects.get(agent_id=agent.id)
            
            config_data = {
                "configured": True,
                "payment_method": config.payment_method,
                "payment_account": config.payment_account,
                "payment_name": config.payment_name,
                "payment_qr_code": config.payment_qr_code,
                "created_at": config.created_at.isoformat(),
                "updated_at": config.updated_at.isoformat()
            }
            
            return ApiResponse.success(message="获取收款配置成功", data=config_data)
            
        except AgentPaymentConfig.DoesNotExist:
            return ApiResponse.success(message="尚未配置收款信息", data={
                "configured": False,
                "payment_method": None,
                "payment_account": None,
                "payment_name": None,
                "payment_qr_code": None
            })
        
    except Exception as e:
        print(f"获取代理收款配置异常: {str(e)}")
        return ApiResponse.error(message="获取收款配置失败", code=ResponseCode.SERVER_ERROR)

@csrf_exempt
@require_http_methods(["POST"])
@agent_required
def save_agent_payment_config(request: HttpRequest):
    """
    保存代理收款配置（新增或更新）
    
    Args:
        request: 包含收款配置信息的HTTP请求
        {
            "payment_method": "alipay" | "wechat",
            "payment_account": "收款账号",
            "payment_name": "收款人姓名",
            "payment_qr_code": "收款码图片路径（可选）"
        }
        
    Returns:
        配置保存结果
    """
    try:
        agent = request.user
        
        data = json.loads(request.body)
        payment_method = data.get('payment_method', '').strip()
        payment_account = data.get('payment_account', '').strip()
        payment_name = data.get('payment_name', '').strip()
        payment_qr_code = data.get('payment_qr_code', '').strip()
        
        print(f"[收款配置] 代理ID: {agent.id}, 支付方式: {payment_method}, 账号: {payment_account}")
        
        # 参数验证
        if not payment_method or payment_method not in ['alipay', 'wechat']:
            return ApiResponse.param_error("支付方式不正确，必须是alipay或wechat")
        
        if not payment_account or len(payment_account.strip()) == 0:
            return ApiResponse.param_error("收款账号不能为空")
        
        if not payment_name or len(payment_name.strip()) == 0:
            return ApiResponse.param_error("收款人姓名不能为空")
        
        # 字符长度验证
        if len(payment_account) > 100:
            return ApiResponse.param_error("收款账号过长，最多100个字符")
        
        if len(payment_name) > 50:
            return ApiResponse.param_error("收款人姓名过长，最多50个字符")
        
        if len(payment_qr_code) > 500:
            return ApiResponse.param_error("收款码路径过长，最多500个字符")
        
        # 字符安全性验证
        import re
        
        # 姓名验证：只允许中文、英文字母和空格
        if not re.match(r'^[\u4e00-\u9fa5a-zA-Z\s]+$', payment_name):
            return ApiResponse.param_error("收款人姓名只能包含中文、英文字母和空格")
        
        # 账号验证：根据支付方式进行不同验证
        if payment_method == 'alipay':
            # 支付宝账号：手机号或邮箱
            if not (re.match(r'^1[3-9]\d{9}$', payment_account) or 
                    re.match(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$', payment_account)):
                return ApiResponse.param_error("支付宝账号格式不正确，请输入手机号或邮箱")
        elif payment_method == 'wechat':
            # 微信账号：微信号或手机号
            if not (re.match(r'^1[3-9]\d{9}$', payment_account) or 
                    re.match(r'^[a-zA-Z0-9_-]{6,20}$', payment_account)):
                return ApiResponse.param_error("微信账号格式不正确，请输入微信号或手机号")
        
        from .models import AgentPaymentConfig
        
        # 检查是否已存在配置
        try:
            config = AgentPaymentConfig.objects.get(agent_id=agent.id)
            # 更新现有配置
            config.payment_method = payment_method
            config.payment_account = payment_account
            config.payment_name = payment_name
            config.payment_qr_code = payment_qr_code
            config.save()
            
            action = "更新"
            print(f"[收款配置] 更新成功: {config.id}")
            
        except AgentPaymentConfig.DoesNotExist:
            # 创建新配置
            config = AgentPaymentConfig.objects.create(
                agent_id=agent.id,
                payment_method=payment_method,
                payment_account=payment_account,
                payment_name=payment_name,
                payment_qr_code=payment_qr_code
            )
            
            action = "配置"
            print(f"[收款配置] 创建成功: {config.id}")
        
        response_data = {
            "configured": True,
            "payment_method": config.payment_method,
            "payment_account": config.payment_account,
            "payment_name": config.payment_name,
            "payment_qr_code": config.payment_qr_code,
            "updated_at": config.updated_at.isoformat()
        }
        
        return ApiResponse.success(message=f"收款{action}成功", data=response_data)
        
    except json.JSONDecodeError:
        return ApiResponse.param_error("无效的JSON数据")
    except Exception as e:
        print(f"保存代理收款配置异常: {str(e)}")
        return ApiResponse.error(message="保存收款配置失败", code=ResponseCode.SERVER_ERROR)

@csrf_exempt
@require_http_methods(["POST"])
@agent_required
def submit_commission_withdrawal(request: HttpRequest):
    """
    提交佣金提现申请
    
    Args:
        request: 包含提现申请信息的HTTP请求
        {
            "withdrawal_amount": "提现金额"
        }
        
    Returns:
        提现申请结果
    """
    try:
        agent = request.user
        
        data = json.loads(request.body)
        withdrawal_amount = data.get('amount')
        
        print(f"[佣金提现] 代理ID: {agent.id}, 申请金额: {withdrawal_amount}")
        
        # 参数验证
        if withdrawal_amount is None:
            return ApiResponse.param_error("提现金额不能为空")
        
        try:
            withdrawal_amount = float(withdrawal_amount)
        except (ValueError, TypeError):
            return ApiResponse.param_error("提现金额必须是数字")
        
        if withdrawal_amount <= 0:
            return ApiResponse.param_error("提现金额必须大于0")
        
        if withdrawal_amount < 5:
            return ApiResponse.param_error("最低提现金额为¥5.00")
        
        if withdrawal_amount > 999999.99:
            return ApiResponse.param_error("提现金额不能超过999999.99")
        
        # 保留两位小数
        withdrawal_amount = round(withdrawal_amount, 2)
        
        from .models import AgentPaymentConfig, CommissionWithdrawal
        from decimal import Decimal
        
        # 1. 检查是否已配置收款信息
        try:
            payment_config = AgentPaymentConfig.objects.get(agent_id=agent.id)
            print(f"[佣金提现] 收款配置检查通过: {payment_config.payment_method}")
        except AgentPaymentConfig.DoesNotExist:
            return ApiResponse.error(message="请先配置收款信息后再申请提现")
        
        # 2. 检查是否有待处理的提现申请
        pending_withdrawal = CommissionWithdrawal.objects.filter(
            agent_id=agent.id,
            status='pending'
        ).first()
        
        if pending_withdrawal:
            return ApiResponse.error(message="您有待处理的提现申请，请等待处理完成后再申请", data={
                "pending_withdrawal_id": pending_withdrawal.id,
                "pending_amount": float(pending_withdrawal.withdrawal_amount),
                "created_at": pending_withdrawal.created_at.isoformat()
            })
        
        # 3. 检查提现金额是否超过未结算佣金
        current_unsettled = agent.unsettled_commission
        if Decimal(str(withdrawal_amount)) > current_unsettled:
            return ApiResponse.error(message="提现金额不能超过未结算佣金", data={
                "withdrawal_amount": withdrawal_amount,
                "unsettled_commission": float(current_unsettled),
                "max_withdrawal": float(current_unsettled)
            })
        
        # 4. 创建提现申请
        withdrawal = CommissionWithdrawal.objects.create(
            agent_id=agent.id,
            withdrawal_amount=Decimal(str(withdrawal_amount)),
            unsettled_amount_snapshot=current_unsettled,
            status='pending'
        )
        
        print(f"[佣金提现] 申请创建成功: {withdrawal.id}, 金额: {withdrawal_amount}")
        
        response_data = {
            "withdrawal_id": withdrawal.id,
            "withdrawal_amount": float(withdrawal.withdrawal_amount),
            "unsettled_amount_snapshot": float(withdrawal.unsettled_amount_snapshot),
            "status": withdrawal.status,
            "created_at": withdrawal.created_at.isoformat()
        }
        
        return ApiResponse.success(message="提现申请提交成功", data=response_data)
        
    except json.JSONDecodeError:
        return ApiResponse.param_error("无效的JSON数据")
    except Exception as e:
        print(f"提交佣金提现申请异常: {str(e)}")
        return ApiResponse.error(message="提交提现申请失败", code=ResponseCode.SERVER_ERROR)


@csrf_exempt
@require_http_methods(["GET"])
@agent_required
def get_commission_withdrawal_records(request: HttpRequest):
    """
    获取代理佣金提现记录
    
    Returns:
        提现记录列表和分页信息
    """
    try:
        agent = request.user # Changed from request.agent to request.user
        
        from .models import CommissionWithdrawal
        from django.core.paginator import Paginator
        
        # 获取分页参数
        page = int(request.GET.get('page', 1))
        per_page = int(request.GET.get('per_page', 10))
        
        # 获取该代理的所有提现记录，按创建时间倒序
        withdrawals = CommissionWithdrawal.objects.filter(
            agent_id=agent.id
        ).order_by('-created_at')
        
        # 分页处理
        paginator = Paginator(withdrawals, per_page)
        page_obj = paginator.get_page(page)
        
        # 构建记录数据
        from .models import AgentPaymentConfig
        
        records = []
        for withdrawal in page_obj:
            # 获取代理的收款配置信息
            try:
                payment_config = AgentPaymentConfig.objects.get(agent_id=withdrawal.agent_id)
                payment_method = payment_config.payment_method
                payment_account = payment_config.payment_account
                payment_name = payment_config.payment_name
            except AgentPaymentConfig.DoesNotExist:
                payment_method = None
                payment_account = "配置已删除"
                payment_name = "配置已删除"
            
            record_data = {
                "id": withdrawal.id,
                "amount": str(withdrawal.withdrawal_amount),
                "status": withdrawal.status,
                "payment_method": payment_method,
                "payment_account": payment_account,
                "payment_name": payment_name,
                "admin_remark": withdrawal.admin_note,  # 注意这里字段名是admin_note而不是admin_remark
                "created_at": withdrawal.created_at.isoformat(),
                "processed_at": withdrawal.completed_at.isoformat() if withdrawal.completed_at else None,  # 注意这里字段名是completed_at而不是processed_at
                "unsettled_commission_snapshot": str(withdrawal.unsettled_amount_snapshot),
            }
            records.append(record_data)
        
        result_data = {
            "records": records,
            "current_page": page_obj.number,
            "per_page": per_page,
            "total": paginator.count,
            "total_pages": paginator.num_pages,
            "has_next": page_obj.has_next(),
            "has_previous": page_obj.has_previous()
        }
        
        return ApiResponse.success(message="获取提现记录成功", data=result_data)
        
    except Exception as e:
        print(f"获取代理提现记录异常: {str(e)}")
        return ApiResponse.error(message="获取提现记录失败", code=ResponseCode.SERVER_ERROR) 