"""
文件上传相关的视图函数
"""

import os
import uuid
import time
from PIL import Image
from django.http import HttpRequest
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.conf import settings
from django.core.files.storage import default_storage
from django.core.files.base import ContentFile

from .response import ApiResponse, ResponseCode
from .decorators import admin_required, agent_required, admin_or_agent_required

# 允许的图片格式
ALLOWED_IMAGE_FORMATS = {
    'jpg', 'jpeg', 'png', 'gif', 'bmp', 'webp'
}

# 最大文件大小 (5MB)
MAX_FILE_SIZE = 5 * 1024 * 1024

def get_upload_path(file_type='images'):
    """
    生成上传路径
    
    Args:
        file_type: 文件类型目录
        
    Returns:
        上传路径
    """
    # 按日期分目录存储
    date_path = time.strftime('%Y/%m/%d')
    return f'uploads/{file_type}/{date_path}'

def validate_image_file(file):
    """
    验证图片文件
    
    Args:
        file: 上传的文件对象
        
    Returns:
        (is_valid, error_message)
    """
    # 检查文件大小
    if file.size > MAX_FILE_SIZE:
        return False, f"文件大小不能超过{MAX_FILE_SIZE // (1024*1024)}MB"
    
    # 检查文件扩展名
    file_ext = file.name.lower().split('.')[-1] if '.' in file.name else ''
    if file_ext not in ALLOWED_IMAGE_FORMATS:
        return False, f"不支持的文件格式，只允许: {', '.join(ALLOWED_IMAGE_FORMATS)}"
    
    # 验证是否为真实的图片文件
    try:
        # 尝试用PIL打开图片
        file.seek(0)  # 重置文件指针
        with Image.open(file) as img:
            # 验证图片格式
            if img.format.lower() not in ['jpeg', 'png', 'gif', 'bmp', 'webp']:
                return False, "文件内容不是有效的图片格式"
            
            # 检查图片尺寸限制 (可选)
            max_width, max_height = 4096, 4096  # 最大尺寸
            if img.width > max_width or img.height > max_height:
                return False, f"图片尺寸不能超过{max_width}x{max_height}像素"
        
        file.seek(0)  # 重置文件指针
        return True, None
        
    except Exception as e:
        return False, "文件不是有效的图片格式"

def generate_filename(original_name):
    """
    生成唯一的文件名
    
    Args:
        original_name: 原始文件名
        
    Returns:
        新的文件名
    """
    # 获取文件扩展名
    file_ext = original_name.lower().split('.')[-1] if '.' in original_name else 'jpg'
    
    # 生成UUID作为文件名
    unique_id = str(uuid.uuid4()).replace('-', '')
    timestamp = str(int(time.time()))
    
    return f"{timestamp}_{unique_id}.{file_ext}"

@csrf_exempt
@require_http_methods(["POST"])
@admin_or_agent_required
def upload_image(request: HttpRequest):
    """
    通用图片上传接口
    
    Args:
        request: 包含图片文件的HTTP请求
        支持的文件字段名: file, image, logo, avatar
        
    Returns:
        上传结果和文件URL
    """
    try:
        # 简化权限检查：支持管理员和代理用户上传
        if not hasattr(request, 'user_type') or request.user_type not in ['admin', 'agent']:
            return ApiResponse.forbidden("您没有权限上传文件")
        
        # 检查是否有文件上传，支持多种字段名
        uploaded_file = None
        file_field_name = None
        
        # 支持的文件字段名
        supported_fields = ['file', 'image', 'logo', 'avatar']
        
        for field_name in supported_fields:
            if field_name in request.FILES:
                uploaded_file = request.FILES[field_name]
                file_field_name = field_name
                break
        
        if not uploaded_file:
            return ApiResponse.param_error("请选择要上传的文件")
        
        # 检查文件名
        if not uploaded_file.name:
            return ApiResponse.param_error("文件名不能为空")
        
        # 获取用户信息用于日志
        user_info = "超管" if request.user_type == 'admin' else f"代理({request.user.username})"
        print(f"收到图片上传请求: {uploaded_file.name}, 字段: {file_field_name}, 大小: {uploaded_file.size} bytes, 用户: {user_info}")
        
        # 验证图片文件
        is_valid, error_msg = validate_image_file(uploaded_file)
        if not is_valid:
            return ApiResponse.param_error(error_msg)
        
        # 根据文件类型和用户类型确定存储目录
        if file_field_name == 'logo':
            upload_dir = get_upload_path('logos')
            # 为代理用户的logo添加用户标识
            if request.user_type == 'agent':
                filename = f"agent_{request.user.id}_logo_{generate_filename(uploaded_file.name)}"
            else:
                filename = f"admin_logo_{generate_filename(uploaded_file.name)}"
        elif file_field_name == 'avatar':
            upload_dir = get_upload_path('avatars')
            # 为代理用户的头像添加用户标识
            if request.user_type == 'agent':
                filename = f"agent_{request.user.id}_avatar_{generate_filename(uploaded_file.name)}"
            else:
                filename = f"admin_avatar_{generate_filename(uploaded_file.name)}"
        else:
            upload_dir = get_upload_path('images')
            # 为代理用户的普通图片添加用户标识
            if request.user_type == 'agent':
                filename = f"agent_{request.user.id}_{generate_filename(uploaded_file.name)}"
            else:
                filename = f"admin_{generate_filename(uploaded_file.name)}"
        
        file_path = f"{upload_dir}/{filename}"
        
        # 确保上传目录存在
        full_upload_dir = os.path.join(settings.MEDIA_ROOT, upload_dir)
        os.makedirs(full_upload_dir, exist_ok=True)
        
        # 保存文件
        try:
            # 使用Django的文件存储系统
            saved_path = default_storage.save(file_path, ContentFile(uploaded_file.read()))
            
            # 生成访问URL
            file_url = f"{settings.MEDIA_URL}{saved_path}"
            
            # 如果部署时使用CDN或其他域名，可以在这里处理
            if hasattr(settings, 'MEDIA_DOMAIN') and settings.MEDIA_DOMAIN:
                file_url = f"{settings.MEDIA_DOMAIN}{file_url}"
            
            print(f"图片上传成功: {saved_path}, 用户: {user_info}")
            
            # 返回文件信息
            file_info = {
                "filename": filename,
                "original_name": uploaded_file.name,
                "file_path": saved_path,
                "file_url": file_url,
                "file_size": uploaded_file.size,
                "file_type": file_field_name,
                "upload_time": int(time.time()),
                "uploaded_by": request.user_type,
                "user_id": request.user.id
            }
            
            return ApiResponse.success(message="图片上传成功", data=file_info)
            
        except Exception as e:
            print(f"文件保存失败: {str(e)}")
            return ApiResponse.error(message="文件保存失败", code=ResponseCode.SERVER_ERROR)
        
    except Exception as e:
        print(f"图片上传异常: {str(e)}")
        return ApiResponse.error(message="图片上传失败", code=ResponseCode.SERVER_ERROR)



 