"""
面向最终用户的前端接口视图
"""
import json
from django.http import HttpRequest, JsonResponse, HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.conf import settings
from django.utils import timezone
from django.forms.models import model_to_dict
import requests
import os

from .response import ApiResponse, ResponseCode
from .models import SystemConfig, QueryConfig, ExternalApiConfig, AgentUser, ApiConfig, RegularUser
from .decorators import login_required
from .sms_service import SmsService


@csrf_exempt
@require_http_methods(["GET", "POST"])
def site_status_check(request: HttpRequest):
    """
    站点状态检查接口
    
    用于前端在加载时，快速检查所有关键配置是否就绪。
    """
    try:
        # 默认检查主管理员的配置 (owner_id=1, owner_type='admin')
        # 未来可以扩展，通过代理标识检查特定代理的配置状态
        owner_id = 1 
        owner_type = 'admin'

        status_report = {}

        # 1. 检查微信访问限制
        system_config = SystemConfig.objects.filter(owner_id=owner_id, owner_type=owner_type).first()
        if system_config and system_config.force_wechat_access:
            # 可以在这里通过 request.META.get('HTTP_USER_AGENT') 判断是否微信环境
            # 为简化，此处仅返回状态，由前端判断和提示
            status_report['wechat_access_required'] = True
        else:
            status_report['wechat_access_required'] = False

        # 2. 检查支付配置
        # (此处省略了对 alipay 和 wechat_payment 的检查, 因为它们不再是访问网站的硬性前置条件)

        # 3. 检查核心服务是否就绪
        core_services = {
            'query_config': QueryConfig.objects.filter(owner_id=owner_id, owner_type=owner_type).exists(),
            'tianyuan_api': ExternalApiConfig.objects.filter(owner_id=owner_id, owner_type=owner_type, config_type='tianyuan_risk_api').exists(),
            'wechat_oauth': ExternalApiConfig.objects.filter(owner_id=owner_id, owner_type=owner_type, config_type='wechat_oauth').exists(),
            'aliyun_sms': ExternalApiConfig.objects.filter(owner_id=owner_id, owner_type=owner_type, config_type='aliyun_sms').exists(),
        }
        
        missing_configs = [name for name, ready in core_services.items() if not ready]

        if missing_configs:
            status_report['ready'] = False
            status_report['reason'] = 'config_incomplete'
            status_report['missing'] = missing_configs
            status_report['message'] = f"系统配置不完整，缺少以下关键配置: {', '.join(missing_configs)}"
        else:
            status_report['ready'] = True
            status_report['reason'] = 'ok'
            status_report['message'] = "站点配置完整，可以访问"

        return ApiResponse.success(message="站点状态检查完成", data=status_report)

    except Exception as e:
        print(f"站点状态检查异常: {str(e)}")
        # 返回一个明确的错误状态
        return ApiResponse.success(message="站点状态检查时发生服务器内部错误",data={
            "ready": False, 
            "reason": "server_error",
            "message": "站点状态检查时发生服务器内部错误"
        })


@csrf_exempt
@require_http_methods(["GET", "POST"])
def get_site_data(request: HttpRequest):
    """
    根据代理标识获取站点数据 (网站配置 + 查询配置)
    
    通过Cookie中的`agent_tag`来判断是主站还是代理站。
    """
    try:
        agent_tag = request.COOKIES.get('agent_tag', None)
        agent = None
        
        # 默认加载主管理员的配置
        owner_id = 1
        owner_type = 'admin'
        
        print(f"[站点数据] 开始处理请求")
        print(f"[站点数据] 所有Cookie: {dict(request.COOKIES)}")
        print(f"[站点数据] 代理标签: {agent_tag}")
        print(f"[站点数据] 请求头: {dict(request.META)}")
        
        # 1. 如果有代理标识，则尝试查找对应的代理
        if agent_tag:
            try:
                agent = AgentUser.objects.get(domain_suffix=agent_tag)
                print(f"[站点数据] 成功找到代理: {agent.username} (ID: {agent.id})")
            except AgentUser.DoesNotExist:
                print(f"[站点数据] 代理标签 '{agent_tag}' 无效, 将加载主站配置")
                agent = None

        # 2. 获取网站配置 (SystemConfig)
        # 根据需求，代理和主站都使用管理员的系统配置
        if agent and agent.can_customize_settings:
            # 如果代理有自定义权限，优先使用代理的配置
            system_config = SystemConfig.objects.filter(owner_id=agent.id, owner_type='agent').first()
            if system_config:
                print(f"[站点数据] 使用代理 '{agent.username}' 的自定义系统配置")
            else:
                # 代理没有自定义配置，使用管理员配置
                system_config = SystemConfig.objects.filter(owner_id=1, owner_type='admin').first()
                print(f"[站点数据] 代理无自定义配置，使用管理员系统配置")
        else:
            # 主站访问或代理无自定义权限，使用管理员配置
            system_config = SystemConfig.objects.filter(owner_id=1, owner_type='admin').first()
            print(f"[站点数据] 使用管理员系统配置")

        # 新增：获取微信公众号AppID
        wechat_appid = None
        try:
            # 查找类型为'wechat_oauth'的有效配置
            wechat_oauth_config = ExternalApiConfig.objects.filter(
                owner_id=owner_id, 
                owner_type=owner_type, 
                config_type='wechat_oauth', 
                is_active=True
            ).first()
            
            if wechat_oauth_config:
                credentials = wechat_oauth_config.credentials
                # credentials字段可能是JSON字符串或已解析的字典
                if isinstance(credentials, str):
                    credentials = json.loads(credentials)
                
                if isinstance(credentials, dict):
                    wechat_appid = credentials.get('app_id')
                    print(f"[站点数据] 成功获取到微信AppID: {wechat_appid}")

        except Exception as e:
            print(f"[站点数据] 获取微信AppID时发生错误: {str(e)}")


        system_data = {
            "site_title": system_config.site_title,
            "logo": system_config.logo,
            "appid": wechat_appid,
            "keywords": system_config.keywords,
            "description": system_config.description,
            "show_query_price": system_config.show_query_price,
            "query_entrance_desc": system_config.query_entrance_desc,
            "customer_service_url": system_config.customer_service_url,
            "force_wechat_access": system_config.force_wechat_access,
            "footer_copyright": system_config.footer_copyright
        } if system_config else {}

        # 获取查询配置 (QueryConfig)
        if agent:
            # 如果是代理访问，优先使用代理的查询配置
            query_configs = QueryConfig.objects.filter(owner_id=agent.id, owner_type='agent', is_active=True).order_by('id')
            print(f"[站点数据] 代理访问，找到 {len(query_configs)} 个代理查询配置")
            
            # 如果代理没有配置，则回退到主站配置
            if not query_configs.exists():
                query_configs = QueryConfig.objects.filter(owner_id=1, owner_type='admin', is_active=True).order_by('id')
                print(f"[站点数据] 代理无配置，回退到主站，找到 {len(query_configs)} 个主站查询配置")
        else:
            # 主站访问，使用管理员配置
            query_configs = QueryConfig.objects.filter(owner_id=1, owner_type='admin', is_active=True).order_by('id')
            print(f"[站点数据] 主站访问，找到 {len(query_configs)} 个主站查询配置")

        query_data = []
        for config in query_configs:
            # 解析api_combination，获取接口名称和状态
            included_apis_data = []
            if config.api_combination:
                api_ids = config.api_combination
                # 使用字典映射来高效获取API对象，并方便地在后续循环中使用
                api_dict = {api.id: api for api in ApiConfig.objects.filter(id__in=api_ids)}
                
                # 按照api_combination中定义的顺序构建列表，确保前端显示顺序一致
                included_apis_data = [
                    {
                        "name": api_dict[api_id].api_name,
                        "api_code": api_dict[api_id].api_code,  # 新增编号
                        "is_active": api_dict[api_id].is_active
                    } 
                    for api_id in api_ids if api_id in api_dict
                ]

            # 直接使用配置中的客户价格
            customer_price = config.customer_price
            print(f"[站点数据] 配置 '{config.config_name}' 客户价格: {customer_price}")

            # 检查配置中的接口是否需要手机号
            requires_mobile = False
            requires_sms_verification = False
            
            # 判断是否需要短信验证（三要素）
            if config.category == 'three_factor':
                requires_mobile = True
                requires_sms_verification = True
            
            # 检查QueryConfig中包含的接口是否需要手机号（除了三要素验证）
            if config.api_combination and not requires_sms_verification:
                # 获取当前QueryConfig包含的接口配置
                api_ids = config.api_combination
                api_configs = ApiConfig.objects.filter(
                    id__in=api_ids, 
                    owner_id=owner_id,
                    owner_type=owner_type,
                    is_active=True
                )
                
                # 检查是否有需要手机号的接口（使用数据库字段）
                for api_config in api_configs:
                    if api_config.requires_mobile:
                        requires_mobile = True
                        break
            
            query_data.append({
                "id": config.id,
                "config_name": config.config_name,
                "category": config.category,
                "customer_price": f"{customer_price:.2f}",
                "included_apis": included_apis_data,
                "requires_mobile": requires_mobile,  # 是否需要手机号
                "requires_sms_verification": requires_sms_verification  # 是否需要短信验证
            })

        # 3. 准备代理信息
        agent_data = None
        if agent:
            agent_data = {
                "username": agent.username,
                "domain_suffix": agent.domain_suffix,
                "can_customize_settings": agent.can_customize_settings
            }

        # 最终返回的数据结构
        response_data = {
            "system_config": system_data,
            "query_configs": query_data,
            "agent_info": agent_data,
        }
        
        return ApiResponse.success(message="获取站点数据成功", data=response_data)

    except Exception as e:
        print(f"获取站点数据异常: {str(e)}")
        return ApiResponse.error(message="获取站点数据失败") 


# --- 新增：用户认证视图 ---

@csrf_exempt
@require_http_methods(["POST"])
def send_sms_code(request: HttpRequest):
    """发送短信验证码"""
    try:
        data = json.loads(request.body)
        phone = data.get('phone')
        if not phone or not phone.isdigit() or len(phone) != 11:
            return ApiResponse.param_error(message="无效的手机号码")

        # 获取代理标识
        agent_tag = request.COOKIES.get('agent_tag', None)
        agent = None
        
        print(f"[发送短信] 手机号: {phone}, 代理标签: {agent_tag}")
        
        # 如果有代理标识，验证代理是否存在
        if agent_tag:
            try:
                agent = AgentUser.objects.get(domain_suffix=agent_tag)
                print(f"[发送短信] 找到代理: {agent.username} (ID: {agent.id})")
            except AgentUser.DoesNotExist:
                print(f"[发送短信] 代理标签 '{agent_tag}' 无效")
                agent = None

        # 初始化短信服务 (统一使用管理员配置)
        sms_service = SmsService(owner_id=1, owner_type='admin')
        success, message = sms_service.send_verification_code(phone)
        
        if success:
            return ApiResponse.success(message=message)
        else:
            return ApiResponse.error(message=message)
            
    except ValueError as e: # Handle case where SMS config is missing
        return ApiResponse.error(message=str(e), code=ResponseCode.SERVER_ERROR)
    except Exception as e:
        print(f"发送短信验证码异常: {str(e)}")
        return ApiResponse.error(message="服务器内部错误")


@csrf_exempt
@require_http_methods(["POST"])
def login_with_sms_code(request: HttpRequest):
    """使用短信验证码登录"""
    try:
        data = json.loads(request.body)
        phone = data.get('phone')
        code = data.get('code')

        if not all([phone, code]):
            return ApiResponse.param_error(message="手机号和验证码不能为空")

        # 获取代理标识
        agent_tag = request.COOKIES.get('agent_tag', None)
        agent = None
        agent_id = None
        
        print(f"[短信登录] 手机号: {phone}, 代理标签: {agent_tag}")
        
        # 如果有代理标识，验证代理是否存在
        if agent_tag:
            try:
                agent = AgentUser.objects.get(domain_suffix=agent_tag)
                agent_id = agent.id
                print(f"[短信登录] 找到代理: {agent.username} (ID: {agent.id})")
            except AgentUser.DoesNotExist:
                print(f"[短信登录] 代理标签 '{agent_tag}' 无效")
                agent = None

        # 验证验证码 (统一使用管理员配置)
        sms_service = SmsService(owner_id=1, owner_type='admin')
        success, message = sms_service.verify_code(phone, code)

        if not success:
            return ApiResponse.error(message=message, code=ResponseCode.CAPTCHA_ERROR)

        # 验证成功，查找或创建用户
        user, created = RegularUser.objects.get_or_create(
            phone=phone,
            defaults={
                'username': RegularUser.generate_unique_username(),
                'agent_id': agent_id,  # 关联代理ID
                'openid': None  # 显式设为 None，避免唯一索引冲突
            }
        )

        # 如果用户已存在但没有关联代理，且当前有代理标识，则更新关联
        if not created and agent_id and not user.agent_id:
            user.agent_id = agent_id
            user.save()
            print(f"[短信登录] 用户 {user.username} 已关联到代理 {agent.username}")

        if user.is_deactivated:
            return ApiResponse.forbidden(message="该账户已注销")

        # 设置session
        request.session['user_info'] = {'user_id': user.id, 'user_type': 'regular'}
        
        user_data = model_to_dict(user, fields=['id', 'username', 'phone', 'agent_id'])
        
        # 添加代理信息到返回数据
        if user.agent_id:
            try:
                user_agent = AgentUser.objects.get(id=user.agent_id)
                user_data['agent_info'] = {
                    'agent_id': user_agent.id,
                    'agent_username': user_agent.username,
                    'domain_suffix': user_agent.domain_suffix
                }
            except AgentUser.DoesNotExist:
                user_data['agent_info'] = None
        else:
            user_data['agent_info'] = None
        
        login_message = "登录成功"
        if created:
            login_message = "注册并登录成功"
            if agent:
                login_message += f"，已关联到代理 {agent.username}"
        
        return ApiResponse.success(message=login_message, data=user_data)

    except ValueError as e: # Handle case where SMS config is missing
        return ApiResponse.error(message=str(e), code=ResponseCode.SERVER_ERROR)
    except Exception as e:
        print(f"短信登录异常: {str(e)}")
        return ApiResponse.error(message="服务器内部错误")


@csrf_exempt
@require_http_methods(["POST"])
def wechat_oauth_login(request: HttpRequest):
    """微信公众号静默授权登录"""
    try:
        data = json.loads(request.body)
        code = data.get('code')
        if not code:
            return ApiResponse.param_error(message="缺少微信授权码")

        # 获取代理标识
        agent_tag = request.COOKIES.get('agent_tag', None)
        agent = None
        agent_id = None
        
        print(f"[微信登录] 授权码: {code[:10]}..., 代理标签: {agent_tag}")
        
        # 如果有代理标识，验证代理是否存在
        if agent_tag:
            try:
                agent = AgentUser.objects.get(domain_suffix=agent_tag)
                agent_id = agent.id
                print(f"[微信登录] 找到代理: {agent.username} (ID: {agent.id})")
            except AgentUser.DoesNotExist:
                print(f"[微信登录] 代理标签 '{agent_tag}' 无效")
                agent = None

        # 1. 从数据库获取微信配置
        wechat_config_db = ExternalApiConfig.objects.filter(
            config_type='wechat_oauth', is_active=True
        ).first()
        if not wechat_config_db or not wechat_config_db.credentials:
            return ApiResponse.error(message="微信登录服务未配置", code=ResponseCode.SERVER_ERROR)
        
        credentials = wechat_config_db.credentials
        if isinstance(credentials, str):
            credentials = json.loads(credentials)
        
        app_id = credentials.get('app_id')
        app_secret = credentials.get('app_secret')

        if not all([app_id, app_secret]):
            return ApiResponse.error(message="微信登录配置不完整", code=ResponseCode.SERVER_ERROR)

        # 2. 用code换取openid
        url = f"https://api.weixin.qq.com/sns/oauth2/access_token?appid={app_id}&secret={app_secret}&code={code}&grant_type=authorization_code"
        res = requests.get(url, timeout=5)
        res_data = res.json()

        openid = res_data.get('openid')
        if not openid:
            return ApiResponse.error(message=res_data.get('errmsg', '微信授权失败'), code=ResponseCode.UNAUTHORIZED)

        print(f"[微信登录] 获取到OpenID: {openid}")

        # 3. 查找或创建用户
        user, created = RegularUser.objects.get_or_create(
            openid=openid,
            defaults={
                'username': RegularUser.generate_unique_username(),
                'agent_id': agent_id  # 关联代理ID
            }
        )
        
        # 如果用户已存在但没有关联代理，且当前有代理标识，则更新关联
        if not created and agent_id and not user.agent_id:
            user.agent_id = agent_id
            user.save()
            print(f"[微信登录] 用户 {user.username} 已关联到代理 {agent.username}")
        
        if user.is_deactivated:
            return ApiResponse.forbidden(message="该账户已注销")
            
        # 4. 设置session
        request.session['user_info'] = {'user_id': user.id, 'user_type': 'regular'}
        
        # 5. 返回前端需要的数据结构
        user_info = model_to_dict(user, fields=['id', 'username', 'phone', 'openid', 'agent_id'])
        
        # 添加代理信息到返回数据
        if user.agent_id:
            try:
                user_agent = AgentUser.objects.get(id=user.agent_id)
                user_info['agent_info'] = {
                    'agent_id': user_agent.id,
                    'agent_username': user_agent.username,
                    'domain_suffix': user_agent.domain_suffix
                }
            except AgentUser.DoesNotExist:
                user_info['agent_info'] = None
        else:
            user_info['agent_info'] = None
        
        login_message = "微信登录成功"
        if created:
            login_message = "微信注册并登录成功"
            if agent:
                login_message += f"，已关联到代理 {agent.username}"
        
        # 遵循前端期望的格式，这里我们使用自定义的JsonResponse
        return JsonResponse({
            'success': True,
            'message': login_message,
            'token': res_data.get('access_token'), # 将微信的access_token透传
            'userInfo': user_info
        })

    except requests.Timeout:
        return ApiResponse.error(message="微信服务连接超时", code=ResponseCode.SERVER_ERROR)
    except Exception as e:
        print(f"微信登录异常: {str(e)}")
        return ApiResponse.error(message="服务器内部错误")


@csrf_exempt
@require_http_methods(["POST"])
@login_required(user_types=['regular'])
def logout_view(request: HttpRequest):
    """用户退出登录"""
    try:
        request.session.flush()
        return ApiResponse.success(message="退出成功")
    except Exception as e:
        print(f"退出登录异常: {str(e)}")
        return ApiResponse.error(message="服务器内部错误")


@csrf_exempt
@require_http_methods(["GET", "POST"])
@login_required(user_types=['regular'])
def user_auth_check(request: HttpRequest):
    """
    普通用户认证状态检查接口
    
    如果用户已登录且状态正常，返回用户信息。
    如果用户已注销，则清除session并返回错误。
    """
    try:
        user = request.user
        
        # 检查账户是否已注销
        if user.is_deactivated:
            request.session.flush() # 清除会话
            return ApiResponse.forbidden(message="该账户已注销，请重新注册")
            
        user_data = model_to_dict(user, fields=['id', 'username', 'phone', 'openid'])
        
        # 添加代理信息到返回数据
        if user.agent_id:
            try:
                from .models import AgentUser
                user_agent = AgentUser.objects.get(id=user.agent_id)
                user_data['agent_info'] = {
                    'agent_id': user_agent.id,
                    'agent_username': user_agent.username,
                    'domain_suffix': user_agent.domain_suffix
                }
            except AgentUser.DoesNotExist:
                user_data['agent_info'] = None
        else:
            user_data['agent_info'] = None
        
        return ApiResponse.success(message="用户已登录", data=user_data)
        
    except Exception as e:
        print(f"用户认证检查异常: {str(e)}")
        return ApiResponse.error(message="认证检查失败", code=ResponseCode.SERVER_ERROR)

# ==================== 支付查询相关接口 ====================

@csrf_exempt
@require_http_methods(["POST"])
@login_required(user_types=['regular'])
def send_verification_code_for_query(request: HttpRequest):
    """
    发送验证码接口（三要素验证专用）
    
    Args:
        request: 包含验证信息的HTTP请求
        {
            "query_type": "个人查询配置",
            "name": "张三",
            "id_card": "110101199001011234",
            "mobile": "13800138000"
        }
        
    Returns:
        验证结果和验证码发送状态
    """
    try:
        print(f"[frontend_views] 开始发送验证码（三要素验证）")
        
        data = json.loads(request.body)
        query_type = data.get('query_type', '').strip()
        name = data.get('name', '').strip()
        id_card = data.get('id_card', '').strip()
        mobile = data.get('mobile', '').strip()
        
        print(f"[frontend_views] 验证参数: query_type={query_type}, name={name}, id_card={id_card}, mobile={mobile}")
        
        # 验证必填参数
        if not all([query_type, name, id_card, mobile]):
            return ApiResponse.param_error("查询类型、姓名、身份证号和手机号不能为空")
        
        # 获取当前用户
        user = request.user
        
        # 根据cookie中的agent_tag获取查询配置
        agent_tag = request.COOKIES.get('agent_tag', '')
        
        if agent_tag:
            try:
                from .models import AgentUser
                agent = AgentUser.objects.get(domain_suffix=agent_tag)
                owner_id = agent.id
                owner_type = 'agent'
                print(f"[frontend_views] 使用代理查询配置: 代理ID={owner_id}")
            except AgentUser.DoesNotExist:
                print(f"[frontend_views] 代理标识无效: {agent_tag}, 使用主站配置")
                owner_id = 1
                owner_type = 'admin'
        else:
            owner_id = 1
            owner_type = 'admin'
            print(f"[frontend_views] 使用主站查询配置")
        
        # 查找查询配置
        try:
            query_config = QueryConfig.objects.get(
                config_name=query_type,
                owner_id=owner_id,
                owner_type=owner_type,
                is_active=True
            )
            print(f"[frontend_views] 查询配置: {query_config.config_name}, 类别: {query_config.category}")
        except QueryConfig.DoesNotExist:
            return ApiResponse.param_error("查询配置不存在或已停用")
        
        # 检查是否为三要素查询
        if query_config.category != 'three_factor':
            return ApiResponse.param_error("该查询配置不需要验证码")
        
        # 调用天远API进行三要素验证 (统一使用管理员配置)
        try:
            from .tianyuan_client import TianyuanApiClient
            tianyuan_client = TianyuanApiClient(owner_id=1, owner_type='admin')
            
            print(f"[frontend_views] 开始三要素验证")
            verify_result = tianyuan_client.verify_three_factor(name, id_card, mobile)
            
            if not verify_result['success']:
                print(f"[frontend_views] 三要素验证失败: {verify_result['message']}")
                return ApiResponse.error(message=f"三要素验证失败: {verify_result['message']}")
            
            if not verify_result['match']:
                print(f"[frontend_views] 三要素不匹配")
                return ApiResponse.error(message="姓名、身份证号和手机号不匹配，请检查后重试")
            
            print(f"[frontend_views] 三要素验证通过，开始发送验证码")
            
        except Exception as e:
            print(f"[frontend_views] 三要素验证异常: {str(e)}")
            return ApiResponse.error(message=f"三要素验证异常: {str(e)}")
        
        # 发送短信验证码 (统一使用管理员配置)
        try:
            from .sms_service import SmsService
            sms_service = SmsService(owner_id=1, owner_type='admin')
            sms_success, sms_message = sms_service.send_verification_code(mobile)
            
            if sms_success:
                print(f"[frontend_views] 验证码发送成功")
                return ApiResponse.success(
                    message="三要素验证通过，验证码已发送",
                    data={
                        'verified': True,
                        'code_sent': True,
                        'mobile': mobile
                    }
                )
            else:
                print(f"[frontend_views] 验证码发送失败: {sms_message}")
                return ApiResponse.error(message=f"验证码发送失败: {sms_message}")
                
        except Exception as e:
            print(f"[frontend_views] 发送验证码异常: {str(e)}")
            return ApiResponse.error(message=f"发送验证码异常: {str(e)}")
        
    except json.JSONDecodeError:
        return ApiResponse.param_error("无效的JSON数据")
    except Exception as e:
        print(f"[frontend_views] 发送验证码接口异常: {str(e)}")
        return ApiResponse.error(message="发送验证码服务异常", code=ResponseCode.SERVER_ERROR)

@csrf_exempt
@require_http_methods(["POST"])
@login_required(user_types=['regular'])
def create_query_order(request: HttpRequest):
    """
    创建查询订单接口
    
    Args:
        request: 包含查询信息的HTTP请求
        {
            "query_type": "个人查询配置",
            "query_data": {
                "name": "张三",
                "idCard": "110101199001011234",
                "phone": "13800138000",
                "code": "123456"
            }
        }
        
    Returns:
        订单信息
    """
    try:
        print(f"[frontend_views] 开始创建查询订单")
        
        data = json.loads(request.body)
        query_type = data.get('query_type', '').strip()
        query_data = data.get('query_data', {})
        
        print(f"[frontend_views] 查询类型: {query_type}")
        print(f"[frontend_views] 查询数据: {query_data}")
        
        # 验证必填参数
        if not query_type:
            print(f"[frontend_views] 参数错误: 查询类型不能为空")
            return ApiResponse.param_error("查询类型不能为空")
        
        if not query_data:
            print(f"[frontend_views] 参数错误: 查询数据不能为空")
            return ApiResponse.param_error("查询数据不能为空")
        
        # 获取当前用户
        user = request.user
        
        # 根据cookie中的agent_tag判断订单所属（订单所属和用户所属分开）
        agent_tag = request.COOKIES.get('agent_tag', '')
        
        print(f"[frontend_views] 用户ID: {user.id}, 用户代理ID: {user.agent_id}, Cookie代理标识: {agent_tag}")
        
        # 根据cookie中的agent_tag获取查询配置
        if agent_tag:
            # 有代理标识，使用代理的查询配置
            try:
                from .models import AgentUser
                agent = AgentUser.objects.get(domain_suffix=agent_tag)
                owner_id = agent.id
                owner_type = 'agent'
                print(f"[frontend_views] 使用代理查询配置: 代理ID={owner_id}, 代理标识={agent_tag}")
            except AgentUser.DoesNotExist:
                print(f"[frontend_views] 代理标识无效: {agent_tag}, 回退到主站配置")
                owner_id = 1
                owner_type = 'admin'
        else:
            # 没有代理标识，使用管理员的查询配置
            owner_id = 1
            owner_type = 'admin'
            print(f"[frontend_views] 使用主站查询配置")
        
        # 查找查询配置
        try:
            query_config = QueryConfig.objects.get(
                config_name=query_type,
                owner_id=owner_id,
                owner_type=owner_type,
                is_active=True
            )
            print(f"[frontend_views] 查询配置找到: {query_config.config_name}, 价格: {query_config.customer_price}, 类别: {query_config.category}")
        except QueryConfig.DoesNotExist:
            print(f"[frontend_views] 查询配置不存在: {query_type}")
            return ApiResponse.param_error("查询配置不存在或已停用")
        
        # 验证查询数据的完整性
        name = query_data.get('name', '').strip()
        id_card = query_data.get('idCard', '').strip()
        phone = query_data.get('phone', '').strip()
        code = query_data.get('code', '').strip()
        
        print(f"[frontend_views] 查询参数验证: name={name}, idCard={id_card}, phone={phone}, code={code}")
        
        # 基础验证
        if not name:
            print(f"[frontend_views] 参数错误: 姓名不能为空")
            return ApiResponse.param_error("姓名不能为空")
        
        if not id_card:
            print(f"[frontend_views] 参数错误: 身份证号不能为空")
            return ApiResponse.param_error("身份证号不能为空")
        
        # 根据查询配置的类别进行验证
        if query_config.category == 'three_factor':
            # 三要素查询需要手机号和验证码
            if not phone:
                print(f"[frontend_views] 参数错误: 三要素查询需要手机号")
                return ApiResponse.param_error("三要素查询需要手机号")
            
            if not code:
                print(f"[frontend_views] 参数错误: 三要素查询需要验证码")
                return ApiResponse.param_error("三要素查询需要验证码")
            
            # 验证短信验证码（三要素已在发送验证码时验证过）
            try:
                from .sms_service import SmsService
                sms_service = SmsService(owner_id=1, owner_type='admin')
                sms_success, sms_message = sms_service.verify_code(phone, code)
                
                if not sms_success:
                    print(f"[frontend_views] 验证码验证失败: {sms_message}")
                    return ApiResponse.error(message=sms_message, code=ResponseCode.CAPTCHA_ERROR)
                
                print(f"[frontend_views] 三要素查询验证码验证通过")
                
            except Exception as e:
                print(f"[frontend_views] 验证码验证异常: {str(e)}")
                return ApiResponse.error(message=f"验证码验证异常: {str(e)}")
            
        elif query_config.category == 'two_factor':
            # 二要素查询需要验证姓名和身份证
            try:
                from .tianyuan_client import TianyuanApiClient
                tianyuan_client = TianyuanApiClient(owner_id=1, owner_type='admin')
                
                print(f"[frontend_views] 开始二要素验证")
                verify_result = tianyuan_client.verify_two_factor(name, id_card)
                
                if not verify_result['success']:
                    print(f"[frontend_views] 二要素验证失败: {verify_result['message']}")
                    return ApiResponse.error(message=f"二要素验证失败: {verify_result['message']}")
                
                if not verify_result['match']:
                    print(f"[frontend_views] 二要素不匹配")
                    return ApiResponse.error(message="姓名和身份证号不匹配，请检查后重试")
                
                print(f"[frontend_views] 二要素验证通过")
                
            except Exception as e:
                print(f"[frontend_views] 二要素验证异常: {str(e)}")
                return ApiResponse.error(message=f"二要素验证异常: {str(e)}")
        elif query_config.category is None or query_config.category == '' and query_type == '企业查询配置':
            # 企业查询无需验证，立即通过（直接查询） 企业查询的 category为空 并且 query_type == '企业查询配置'
            print(f"[frontend_views] 企业查询无需验证，立即通过")    
        else:
            print(f"[frontend_views] 未知的查询类别: {query_config.category}")
            return ApiResponse.param_error("查询配置类别不正确")
        
        # 计算代理佣金（根据cookie中的agent_tag）
        agent_commission = 0.00
        order_agent_id = None  # 订单归属的代理ID
        
        if agent_tag:
            try:
                from .models import AgentUser
                agent = AgentUser.objects.get(domain_suffix=agent_tag)
                order_agent_id = agent.id
                
                # 根据查询类型计算佣金
                if query_type == '个人查询配置':
                    bottom_price = agent.personal_query_price
                elif query_type == '企业查询配置':
                    bottom_price = agent.enterprise_query_min_price
                else:
                    bottom_price = 0
                
                agent_commission = max(0, float(query_config.customer_price) - float(bottom_price))
                print(f"[frontend_views] 代理佣金计算: 代理ID={order_agent_id}, 客户价格={query_config.customer_price}, 底价={bottom_price}, 佣金={agent_commission}")
            except Exception as e:
                print(f"[frontend_views] 代理佣金计算失败: {str(e)}")
        
        # 创建订单
        from .models import Order
        order = Order.objects.create(
            user_id=user.id,
            agent_id=order_agent_id,  # 使用根据cookie确定的代理ID
            query_type=query_type,
            amount=query_config.customer_price,
            agent_commission=agent_commission,
            query_config_id=query_config.id,
            status='pending'
        )
        
        print(f"[frontend_views] 订单创建成功: {order.order_no}, 金额: {order.amount}")
        
        # 将查询参数存储到session中，供后续支付成功后使用
        session_key = f'query_params_{order.order_no}'
        query_params = {
            'name': name,
            'id_card': id_card,
            'phone': phone,
            'query_type': query_type,
            'query_category': query_config.category
        }
        
        request.session[session_key] = query_params
        print(f"[frontend_views] 查询参数已存储到session: {session_key}")
        
        # 返回订单信息
        response_data = {
            "order_id": order.id,
            "order_no": order.order_no,
            "amount": float(order.amount),
            "query_type": order.query_type,
            "status": order.status,
            "created_at": order.created_at.isoformat(),
            "agent_commission": float(order.agent_commission),
            "query_category": query_config.category  # 返回查询类别
        }
        
        print(f"[frontend_views] 返回订单数据: {response_data}")
        return ApiResponse.success(message="订单创建成功", data=response_data)
        
    except json.JSONDecodeError:
        print(f"[frontend_views] JSON解析错误")
        return ApiResponse.param_error("无效的JSON数据")
    except Exception as e:
        print(f"[frontend_views] 创建查询订单异常: {str(e)}")
        return ApiResponse.error(message="创建订单失败", code=ResponseCode.SERVER_ERROR)

@csrf_exempt
@require_http_methods(["POST"])
@login_required(user_types=['regular'])
def create_payment(request: HttpRequest):
    """
    创建支付订单接口
    
    Args:
        request: 包含支付信息的HTTP请求
        {
            "order_no": "ORDER1234567890",
            "payment_method": "alipay" | "wechat",
            "openid": "微信openid(微信支付时需要)"
        }
        
    Returns:
        支付信息
    """
    try:
        print(f"[frontend_views] 开始创建支付订单")
        
        data = json.loads(request.body)
        order_no = data.get('order_no', '').strip()
        payment_method = data.get('payment_method', '').strip()
        openid = data.get('openid', '').strip()
        current_url = data.get('current_url', '').strip()  # 前端传递的当前URL
        is_mobile = data.get('is_mobile', False)  # 前端传递的设备类型
        
        print(f"[frontend_views] 支付参数: order_no={order_no}, payment_method={payment_method}, openid={openid}, current_url={current_url}, is_mobile={is_mobile}")
        
        # 验证必填参数
        if not order_no:
            print(f"[frontend_views] 参数错误: 订单号不能为空")
            return ApiResponse.param_error("订单号不能为空")
        
        if payment_method not in ['alipay', 'wechat']:
            print(f"[frontend_views] 参数错误: 支付方式不正确")
            return ApiResponse.param_error("支付方式不正确")
        
        if payment_method == 'wechat' and not openid:
            print(f"[frontend_views] 参数错误: 微信支付需要提供openid")
            return ApiResponse.param_error("微信支付需要提供openid")
        
        # 获取当前用户
        user = request.user
        print(f"[frontend_views] 当前用户: {user.id}")
        
        # 查找订单
        from .models import Order
        try:
            order = Order.objects.get(order_no=order_no, user_id=user.id)
            print(f"[frontend_views] 订单找到: {order.order_no}, 状态: {order.status}, 金额: {order.amount}")
        except Order.DoesNotExist:
            print(f"[frontend_views] 订单不存在: {order_no}")
            return ApiResponse.param_error("订单不存在")
        
        # 检查订单状态
        if order.status != 'pending':
            print(f"[frontend_views] 订单状态不正确: {order.status}")
            return ApiResponse.param_error("订单状态不正确，无法支付")
        
        # 初始化支付管理器 (统一使用管理员配置)
        print(f"[frontend_views] 初始化支付管理器")
        from .payment_config import PaymentManager
        payment_manager = PaymentManager(
            owner_id=1,
            owner_type='admin',
            request=request,  # 传入request对象用于获取当前域名
            frontend_url=current_url  # 传入前端URL
        )
        
        # 创建支付订单
        print(f"[frontend_views] 调用支付管理器创建支付订单")
        payment_result = payment_manager.create_payment_order(
            order_no=order.order_no,
            amount=float(order.amount),
            subject=f"查询服务-{order.query_type}",
            payment_method=payment_method,
            openid=openid if payment_method == 'wechat' else None,
            is_mobile=is_mobile if payment_method == 'alipay' else None
        )
        
        print(f"[frontend_views] 支付订单创建结果: {payment_result}")
        
        if not payment_result.get('success'):
            print(f"[frontend_views] 支付订单创建失败: {payment_result.get('error')}")
            return ApiResponse.error(message=payment_result.get('error', '支付订单创建失败'))
        
        # 更新订单的支付方式和第三方订单号
        order.payment_method = payment_method  # 设置支付方式
        
        if payment_method == 'alipay':
            order.third_party_order_id = order.order_no  # 支付宝使用我们的订单号
            print(f"[frontend_views] 支付宝订单号设置: {order.third_party_order_id}")
        elif payment_method == 'wechat':
            order.third_party_order_id = payment_result.get('prepay_id', '')
            print(f"[frontend_views] 微信预支付ID设置: {order.third_party_order_id}")
        
        print(f"[frontend_views] 订单支付方式设置: {order.payment_method}")
        order.save()
        
        # 返回支付信息
        response_data = {
            "order_no": order.order_no,
            "payment_method": payment_method,
            "amount": float(order.amount),
            "third_party_order_id": order.third_party_order_id
        }
        
        # 根据支付方式返回不同的数据
        if payment_method == 'alipay':
            response_data['pay_url'] = payment_result.get('pay_url')
            print(f"[frontend_views] 支付宝支付URL: {payment_result.get('pay_url')}")
        elif payment_method == 'wechat':
            response_data['prepay_id'] = payment_result.get('prepay_id')
            # 返回JSAPI支付参数
            jsapi_params = payment_result.get('jsapi_params', {})
            response_data.update(jsapi_params)  # 将JSAPI参数合并到响应数据中
            print(f"[frontend_views] 微信支付数据: prepay_id={payment_result.get('prepay_id')}, jsapi_params={jsapi_params}")
        
        print(f"[frontend_views] 返回支付数据: {response_data}")
        return ApiResponse.success(message="支付订单创建成功", data=response_data)
        
    except json.JSONDecodeError:
        print(f"[frontend_views] JSON解析错误")
        return ApiResponse.param_error("无效的JSON数据")
    except Exception as e:
        print(f"[frontend_views] 创建支付订单异常: {str(e)}")
        return ApiResponse.error(message="创建支付订单失败", code=ResponseCode.SERVER_ERROR)

@csrf_exempt
@require_http_methods(["GET"])
@login_required(user_types=['regular'])
def get_query_result(request: HttpRequest, order_no: str):
    """
    查询结果统一接口（用于查询结果页面）
    
    Args:
        request: HTTP请求
        order_no: 订单号
        
    Returns:
        订单状态 + 查询结果（如果有）
    """
    try:
        print(f"[frontend_views] 查询结果统一接口: {order_no}")
        
        # 获取当前用户
        user = request.user
        print(f"[frontend_views] 当前用户: {user.id}")
        
        # 查找订单并验证归属
        from .models import Order, QueryResult
        try:
            order = Order.objects.get(order_no=order_no, user_id=user.id)
            print(f"[frontend_views] 订单验证成功: {order.order_no}, 状态: {order.status}, 支付方式: {order.payment_method}")
        except Order.DoesNotExist:
            print(f"[frontend_views] 订单不存在或不属于当前用户: {order_no}")
            return ApiResponse.param_error("订单不存在或无权访问")
        
        # 如果订单状态是pending且有支付方式，自动查询支付状态
        print(f"[frontend_views] 检查支付状态条件: status={order.status}, payment_method={order.payment_method}")
        if order.status == 'pending' and order.payment_method:
            print(f"[frontend_views] 自动查询支付状态: {order.order_no}")
            
            # 初始化支付管理器并查询支付状态 (统一使用管理员配置)
            try:
                from .payment_config import PaymentManager
                payment_manager = PaymentManager(
                    owner_id=1,
                    owner_type='admin',
                    request=request
                )
                
                query_result = payment_manager.query_payment_status(order.order_no, order.payment_method)
                print(f"[frontend_views] 支付状态查询结果: {query_result}")
                
                # 检查支付是否成功（支付宝：TRADE_SUCCESS，微信：SUCCESS）
                trade_status = query_result.get('trade_status')
                is_payment_success = (
                    query_result.get('success') and 
                    (trade_status == 'TRADE_SUCCESS' or trade_status == 'SUCCESS')
                )
                
                if is_payment_success:
                    print(f"[frontend_views] 支付成功，更新订单状态 - 状态: {trade_status}")
                    
                    success_result = payment_manager.process_payment_success(
                        order_no=order.order_no,
                        payment_method=order.payment_method,
                        trade_no=query_result.get('trade_no'),
                        amount=query_result.get('total_amount')
                    )
                    
                    if success_result.get('success'):
                        print(f"[frontend_views] 支付成功处理完成，重新获取订单")
                        order.refresh_from_db()
                    else:
                        print(f"[frontend_views] 支付成功处理失败: {success_result.get('error')}")
                else:
                    print(f"[frontend_views] 支付尚未成功或查询失败")
                    
            except Exception as e:
                print(f"[frontend_views] 自动查询支付状态失败: {str(e)}")
                # 继续执行，不影响正常的订单状态返回
        
        # 构建订单信息
        response_data = {
            "order_no": order.order_no,
            "query_type": order.query_type,
            "amount": float(order.amount),
            "status": order.status,
            "payment_method": order.payment_method,
            "payment_time": order.payment_time.isoformat() if order.payment_time else None,
            "query_start_time": order.query_start_time.isoformat() if order.query_start_time else None,
            "query_complete_time": order.query_complete_time.isoformat() if order.query_complete_time else None,
            "created_at": order.created_at.isoformat(),
            "query_result": None  # 默认为空
        }
        
        # 如果订单已支付，尝试获取查询结果
        if order.status in ['querying', 'completed', 'failed']:
            try:
                query_result = QueryResult.objects.get(order_id=order.id)
                print(f"[frontend_views] 查询结果状态: {query_result.status}")
                result_data = {
                    "status": query_result.status,
                    "error_message": query_result.error_message,
                    "created_at": query_result.created_at.isoformat(),
                    "expires_at": query_result.expires_at.isoformat()
                }
                # 如果查询成功，返回解密后的结果
                if query_result.status == 'success' and query_result.encrypted_result_data:
                    print(f"[frontend_views] 查询成功，准备解密结果")
                    # 这里应该解密查询结果
                    raw = json.loads(query_result.encrypted_result_data)
                    # 补充每个api_result都带api_code
                    api_results = raw.get('api_results', [])
                    for api in api_results:
                        if 'api_code' not in api:
                            # 尝试从api_name查找code
                            from .models import ApiConfig
                            code = None
                            try:
                                code = ApiConfig.objects.filter(api_name=api.get('api_name')).values_list('api_code', flat=True).first()
                            except:
                                pass
                            if code:
                                api['api_code'] = code
                    raw['api_results'] = api_results
                    result_data['result_data'] = {
                        "message": "查询成功",
                        "data": raw
                    }
                response_data['query_result'] = result_data
            except QueryResult.DoesNotExist:
                print(f"[frontend_views] 查询结果不存在")
                # query_result保持为None
        
        print(f"[frontend_views] 返回统一查询结果数据")
        return ApiResponse.success(data=response_data)
        
    except Exception as e:
        print(f"[frontend_views] 查询结果统一接口异常: {str(e)}")
        return ApiResponse.error(message="获取查询结果失败", code=ResponseCode.SERVER_ERROR)

@csrf_exempt
@require_http_methods(["GET"])
def example_report(request):
    """
    示例报告接口，根据查询类型返回不同的示例数据。
    
    URL参数:
        type: 查询类型 (personal=个人查询, enterprise=企业查询)
    """
    try:
        # 获取查询类型参数
        query_type = request.GET.get('type', 'personal')
        
        print(f"[frontend_views] 示例报告请求: type={query_type}")
        
        # 根据查询类型选择不同的示例文件
        if query_type == 'enterprise':
            demo_file_name = '企业查询示例.json'
        else:
            demo_file_name = '个人查询示例.json'
        
        # 构建文件路径
        demo_file_path = os.path.join(os.path.dirname(__file__), demo_file_name)
        
        # 读取示例数据
        with open(demo_file_path, 'r', encoding='utf-8') as f:
            example_report_json = json.load(f)
        
        print(f"[frontend_views] 成功读取示例数据: {demo_file_name}")
        return ApiResponse.success(data=example_report_json)
        
    except json.JSONDecodeError as e:
        print(f"[frontend_views] 示例数据文件格式错误: {str(e)}")
        return ApiResponse.error(message="示例数据文件格式错误")
    except Exception as e:
        print(f"[frontend_views] 读取示例数据异常: {str(e)}")
        return ApiResponse.error(message="读取示例数据失败")


# ==================== 用户个人中心接口 ====================

@csrf_exempt
@require_http_methods(["POST"])
@login_required(user_types=['regular'])
def deactivate_account(request: HttpRequest):
    """
    注销用户账户接口
    
    将用户账户标记为已注销状态（软删除）
    """
    try:
        print(f"[frontend_views] 开始注销用户账户")
        
        # 获取当前用户
        user = request.user
        print(f"[frontend_views] 当前用户: {user.id}, {user.username}")
        
        # 检查用户是否已经注销
        if user.is_deactivated:
            return ApiResponse.error(message="该账户已处于注销状态")
        
        # 设置注销状态
        user.is_deactivated = True
        user.deactivated_at = timezone.now()
        user.save()
        
        print(f"[frontend_views] 用户账户注销成功: {user.username}")
        
        # 清除用户session
        request.session.flush()
        
        return ApiResponse.success(message="账户注销成功，您将被退出登录")
        
    except Exception as e:
        print(f"[frontend_views] 注销账户异常: {str(e)}")
        return ApiResponse.error(message="注销账户失败", code=ResponseCode.SERVER_ERROR)


@csrf_exempt
@require_http_methods(["GET"])
@login_required(user_types=['regular'])
def get_user_query_history(request: HttpRequest):
    """
    获取当前用户查询历史记录接口
    
    返回用户的查询历史，包括查询项目、时间、状态、关联订单号
    """
    try:
        print(f"[frontend_views] 获取用户查询历史记录")
        
        # 获取当前用户
        user = request.user
        print(f"[frontend_views] 当前用户: {user.id}, {user.username}")
        
        # 获取分页参数
        page = int(request.GET.get('page', 1))
        page_size = int(request.GET.get('page_size', 10))
        
        print(f"[frontend_views] 分页参数: page={page}, page_size={page_size}")
        
        # 查询用户的查询结果记录
        from .models import QueryResult, Order
        from django.core.paginator import Paginator
        
        # 通过订单关联查询结果，只查询该用户的记录
        # 首先获取用户的所有订单ID
        user_order_ids = Order.objects.filter(user_id=user.id).values_list('id', flat=True)
        
        # 然后查询这些订单的查询结果
        query_results = QueryResult.objects.filter(
            order_id__in=user_order_ids
        ).order_by('-created_at')
        
        # 分页处理
        paginator = Paginator(query_results, page_size)
        page_obj = paginator.get_page(page)
        
        # 构建查询历史数据
        history_data = []
        # 获取所有相关订单信息，优化查询
        order_ids = [qr.order_id for qr in page_obj]
        orders_dict = {order.id: order for order in Order.objects.filter(id__in=order_ids)}
        
        for query_result in page_obj:
            order = orders_dict.get(query_result.order_id)
            
            # 如果订单不存在，跳过这条记录
            if not order:
                continue
            
            # 判断查询状态
            if query_result.status == 'success':
                # 检查是否过期
                if query_result.expires_at and timezone.now() > query_result.expires_at:
                    status = 'expired'
                    status_text = '已过期'
                else:
                    status = 'completed'
                    status_text = '已完成'
            elif query_result.status == 'failed':
                status = 'failed'
                status_text = '失败'
            elif query_result.status == 'pending':
                status = 'pending'
                status_text = '查询中'
            else:
                status = query_result.status
                status_text = query_result.status
            
            history_item = {
                "id": query_result.id,
                "query_type": order.query_type,
                "order_no": order.order_no,
                "status": status,
                "status_text": status_text,
                "created_at": query_result.created_at.isoformat(),
                "expires_at": query_result.expires_at.isoformat() if query_result.expires_at else None,
                "error_message": query_result.error_message if query_result.status == 'failed' else None
            }
            
            history_data.append(history_item)
        
        # 构建分页信息
        pagination_info = {
            "total_items": paginator.count,
            "total_pages": paginator.num_pages,
            "current_page": page,
            "page_size": page_size,
            "has_next": page_obj.has_next(),
            "has_previous": page_obj.has_previous()
        }
        
        response_data = {
            "query_history": history_data,
            "pagination": pagination_info
        }
        
        print(f"[frontend_views] 返回查询历史: 总数={paginator.count}, 当前页={page}")
        return ApiResponse.success(message="获取查询历史成功", data=response_data)
        
    except Exception as e:
        print(f"[frontend_views] 获取查询历史异常: {str(e)}")
        return ApiResponse.error(message="获取查询历史失败", code=ResponseCode.SERVER_ERROR)


@csrf_exempt
@require_http_methods(["GET"])
@login_required(user_types=['regular'])
def get_user_order_history(request: HttpRequest):
    """
    获取当前用户历史订单列表接口
    
    返回用户的订单历史，包括金额、订单号、时间、状态
    """
    try:
        print(f"[frontend_views] 获取用户历史订单")
        
        # 获取当前用户
        user = request.user
        print(f"[frontend_views] 当前用户: {user.id}, {user.username}")
        
        # 获取分页参数
        page = int(request.GET.get('page', 1))
        page_size = int(request.GET.get('page_size', 10))
        
        print(f"[frontend_views] 分页参数: page={page}, page_size={page_size}")
        
        # 查询用户的订单记录
        from .models import Order
        from django.core.paginator import Paginator
        
        orders = Order.objects.filter(user_id=user.id).order_by('-created_at')
        
        # 分页处理
        paginator = Paginator(orders, page_size)
        page_obj = paginator.get_page(page)
        
        # 构建订单历史数据
        order_data = []
        for order in page_obj:
            # 状态文本映射
            status_mapping = {
                'pending': '待支付',
                'paid': '已支付',
                'querying': '查询中',
                'completed': '已完成',
                'failed': '查询失败',
                'cancelled': '已取消',
                'refunded': '已退款'
            }
            
            order_item = {
                "id": order.id,
                "order_no": order.order_no,
                "query_type": order.query_type,
                "amount": float(order.amount),
                "status": order.status,
                "status_text": status_mapping.get(order.status, order.status),
                "payment_method": order.payment_method,
                "created_at": order.created_at.isoformat(),
                "payment_time": order.payment_time.isoformat() if order.payment_time else None,
                "query_start_time": order.query_start_time.isoformat() if order.query_start_time else None,
                "query_complete_time": order.query_complete_time.isoformat() if order.query_complete_time else None
            }
            
            order_data.append(order_item)
        
        # 构建分页信息
        pagination_info = {
            "total_items": paginator.count,
            "total_pages": paginator.num_pages,
            "current_page": page,
            "page_size": page_size,
            "has_next": page_obj.has_next(),
            "has_previous": page_obj.has_previous()
        }
        
        response_data = {
            "order_history": order_data,
            "pagination": pagination_info
        }
        
        print(f"[frontend_views] 返回订单历史: 总数={paginator.count}, 当前页={page}")
        return ApiResponse.success(message="获取订单历史成功", data=response_data)
        
    except Exception as e:
        print(f"[frontend_views] 获取订单历史异常: {str(e)}")
        return ApiResponse.error(message="获取订单历史失败", code=ResponseCode.SERVER_ERROR)


# ==================== 代理申请相关接口 ====================

@csrf_exempt
@require_http_methods(["POST"])
@login_required(user_types=['regular'])
def submit_agency_application(request: HttpRequest):
    """提交代理申请"""
    try:
        print(f"[代理申请] 开始处理申请请求")
        print(f"[代理申请] Session数据: {request.session.items()}")
        
        data = json.loads(request.body)
        applicant_name = data.get('applicant_name', '').strip()
        contact_type = data.get('contact_type', '').strip()
        contact_info = data.get('contact_info', '').strip()
        
        print(f"[代理申请] 申请数据: name={applicant_name}, type={contact_type}, info={contact_info}")
        
        # 基础参数验证
        if not all([applicant_name, contact_type, contact_info]):
            return ApiResponse.param_error("姓名、联系方式类别和联系方式不能为空")
        
        if contact_type not in ['phone', 'wechat']:
            return ApiResponse.param_error("联系方式类别不正确")
        
        # 字符安全性验证
        import re
        
        # 姓名验证：长度2-20字符，只允许中文、英文字母和空格
        if len(applicant_name) < 2 or len(applicant_name) > 20:
            return ApiResponse.param_error("姓名长度应为2-20个字符")
        
        if not re.match(r'^[\u4e00-\u9fa5a-zA-Z\s]+$', applicant_name):
            return ApiResponse.param_error("姓名只能包含中文、英文字母和空格")
        
        # 联系方式验证
        if len(contact_info) > 100:
            return ApiResponse.param_error("联系方式过长，最多100个字符")
        
        if contact_type == 'phone':
            # 手机号验证：必须是11位数字，1开头
            if not re.match(r'^1[3-9]\d{9}$', contact_info):
                return ApiResponse.param_error("请输入正确的手机号码")
        elif contact_type == 'wechat':
            # 微信号验证：6-20字符，字母、数字、下划线、减号
            if len(contact_info) < 6 or len(contact_info) > 20:
                return ApiResponse.param_error("微信号长度应为6-20个字符")
            if not re.match(r'^[a-zA-Z0-9_-]+$', contact_info):
                return ApiResponse.param_error("微信号只能包含字母、数字、下划线和减号")
        
        # 防止危险字符
        dangerous_patterns = [
            r'<script', r'</script>', r'javascript:', r'vbscript:',
            r'onload=', r'onerror=', r'onclick=', r'onmouseover=',
            r'<iframe', r'</iframe>', r'<object', r'</object>',
            r'<embed', r'</embed>', r'<link', r'<meta',
            r'drop\s+table', r'delete\s+from', r'insert\s+into',
            r'update\s+set', r'select\s+.*\s+from'
        ]
        
        combined_text = f"{applicant_name} {contact_info}".lower()
        for pattern in dangerous_patterns:
            if re.search(pattern, combined_text, re.IGNORECASE):
                return ApiResponse.param_error("输入内容包含不允许的字符")
        
        # 获取当前用户
        user = request.user
        print(f"[代理申请] 当前用户: {user.id}, {user.username}")
        
        # 严格检查用户是否已经申请过（多重验证）
        from .models import AgentApplication
        
        # 1. 按用户ID查询
        existing_by_user = AgentApplication.objects.filter(user_id=user.id).first()
        if existing_by_user:
            print(f"[代理申请] 用户已申请过（按用户ID）: {existing_by_user.id}")
            return ApiResponse.error(message="您已提交过代理申请，请勿重复申请", data={
                "application_time": existing_by_user.application_time.isoformat(),
                "applicant_name": existing_by_user.applicant_name
            })
        
        # 2. 按联系方式查询（防止同一人用不同账号申请）
        existing_by_contact = AgentApplication.objects.filter(
            contact_type=contact_type,
            contact_info=contact_info
        ).first()
        if existing_by_contact:
            print(f"[代理申请] 该联系方式已申请过: {existing_by_contact.id}")
            return ApiResponse.error(message="该联系方式已申请过代理，请勿重复申请")
        
        # 3. 按姓名+联系方式组合查询
        existing_by_name_contact = AgentApplication.objects.filter(
            applicant_name=applicant_name,
            contact_info=contact_info
        ).first()
        if existing_by_name_contact:
            print(f"[代理申请] 该姓名+联系方式组合已申请过: {existing_by_name_contact.id}")
            return ApiResponse.error(message="该申请信息已存在，请勿重复申请")
        
        # 创建申请记录
        application = AgentApplication.objects.create(
            user_id=user.id,
            applicant_name=applicant_name,
            contact_type=contact_type,
            contact_info=contact_info
        )
        
        print(f"[代理申请] 申请创建成功: {application.id}")
        
        return ApiResponse.success(message="代理申请提交成功", data={
            "application_id": application.id,
            "application_time": application.application_time.isoformat()
        })
        
    except json.JSONDecodeError:
        return ApiResponse.param_error("无效的JSON数据")
    except Exception as e:
        print(f"[代理申请] 提交代理申请异常: {str(e)}")
        return ApiResponse.error(message="提交申请失败")


@csrf_exempt
@require_http_methods(["GET"])
@login_required(user_types=['regular'])
def check_agency_application_status(request: HttpRequest):
    """检查代理申请状态"""
    try:
        print(f"[代理申请状态] 开始检查申请状态")
        print(f"[代理申请状态] Session数据: {request.session.items()}")
        
        # 获取当前用户
        user = request.user
        print(f"[代理申请状态] 当前用户: {user.id}, {user.username}")
        
        # 查询用户是否已申请
        from .models import AgentApplication
        application = AgentApplication.objects.filter(user_id=user.id).first()
        
        if application:
            print(f"[代理申请状态] 找到申请记录: {application.id}")
            return ApiResponse.success(data={
                "has_applied": True,
                "application_time": application.application_time.isoformat(),
                "applicant_name": application.applicant_name,
                "contact_type": application.contact_type,
                "contact_info": application.contact_info
            })
        else:
            print(f"[代理申请状态] 未找到申请记录")
            return ApiResponse.success(data={
                "has_applied": False,
                "application_time": None
            })
        
    except Exception as e:
        print(f"[代理申请状态] 检查代理申请状态异常: {str(e)}")
        return ApiResponse.error(message="检查申请状态失败")

