from functools import wraps
from .response import ApiResponse, ResponseCode

def login_required(user_types=None):
    """
    登录认证装饰器
    
    Args:
        user_types: 允许的用户类型列表，如 ['admin', 'agent'] 或 ['regular']
                   如果为None，则允许所有已登录用户
    """
    def decorator(view_func):
        @wraps(view_func)
        def wrapper(request, *args, **kwargs):
            # 检查用户是否登录
            if not hasattr(request, 'user') or request.user is None:
                return ApiResponse.unauthorized("请先登录")
            
            # 检查用户类型
            if user_types is not None:
                if not hasattr(request, 'user_type') or request.user_type not in user_types:
                    return ApiResponse.forbidden("权限不足")
            
            return view_func(request, *args, **kwargs)
        return wrapper
    return decorator

def admin_required(view_func):
    """超级管理员权限装饰器"""
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        if not hasattr(request, 'user') or request.user is None:
            return ApiResponse.unauthorized("请先登录")
        
        if not hasattr(request, 'user_type') or request.user_type != 'admin':
            return ApiResponse.forbidden("需要超级管理员权限")
        
        return view_func(request, *args, **kwargs)
    return wrapper

def agent_required(view_func):
    """代理用户权限装饰器"""
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        if not hasattr(request, 'user') or request.user is None:
            return ApiResponse.unauthorized("请先登录")
        
        if not hasattr(request, 'user_type') or request.user_type != 'agent':
            return ApiResponse.forbidden("需要代理用户权限")
        
        return view_func(request, *args, **kwargs)
    return wrapper

def regular_user_required(view_func):
    """普通用户权限装饰器"""
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        if not hasattr(request, 'user') or request.user is None:
            return ApiResponse.unauthorized("请先登录")
        
        if not hasattr(request, 'user_type') or request.user_type != 'regular':
            return ApiResponse.forbidden("需要普通用户权限")
        
        return view_func(request, *args, **kwargs)
    return wrapper

def admin_or_agent_required(view_func):
    """管理员或代理用户权限装饰器"""
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        if not hasattr(request, 'user') or request.user is None:
            return ApiResponse.unauthorized("请先登录")
        
        if not hasattr(request, 'user_type') or request.user_type not in ['admin', 'agent']:
            return ApiResponse.forbidden("需要管理员或代理用户权限")
        
        return view_func(request, *args, **kwargs)
    return wrapper

 