from django.http import JsonResponse
from typing import Any

class ResponseCode:
    """响应代码"""
    SUCCESS = 0
    ERROR = -1
    PARAM_ERROR = 400
    UNAUTHORIZED = 401
    ID_VERIFY_ERROR = 402  # 身份验证错误
    FORBIDDEN = 403
    NOT_FOUND = 404
    METHOD_NOT_ALLOWED = 405
    SERVER_ERROR = 500
    CAPTCHA_ERROR = 1001  # 验证码错误
    TOO_MANY_REQUESTS = 429  # 请求过于频繁
    INSUFFICIENT_BALANCE = 1006  # 余额不足
    ENTERPRISE_NOT_VERIFIED = 1002  # 企业未认证
    NOTIFICATION_METHOD_ERROR = 4001  # 通知方式错误
    DUPLICATE_RESOURCE = 1003  # 重复资源

class ApiResponse:
    """API响应工具类"""

    @staticmethod
    def response(
            message: str = "success",
            data: Any = None,
            code: int = ResponseCode.SUCCESS
    ) -> JsonResponse:
        """
        统一响应格式

        Args:
            message: 响应消息
            data: 响应数据
            code: 响应代码
        """
        return JsonResponse({
            "message": message,
            "data": data if data is not None else {},
            "code": code
        })

    @staticmethod
    def success(
            message: str = "success",
            data: Any = None
    ) -> JsonResponse:
        """成功响应"""
        return ApiResponse.response(message=message, data=data, code=ResponseCode.SUCCESS)

    @staticmethod
    def error(
            message: str = "error",
            data: Any = None,
            code: int = ResponseCode.ERROR
    ) -> JsonResponse:
        """错误响应"""
        return ApiResponse.response(message=message, data=data, code=code)

    @staticmethod
    def unauthorized(message: str = "未授权访问") -> JsonResponse:
        """未授权响应"""
        return ApiResponse.error(message=message, code=ResponseCode.UNAUTHORIZED)

    @staticmethod
    def forbidden(message: str = "权限不足") -> JsonResponse:
        """禁止访问响应"""
        return ApiResponse.error(message=message, code=ResponseCode.FORBIDDEN)

    @staticmethod
    def not_found(message: str = "资源不存在") -> JsonResponse:
        """资源不存在响应"""
        return ApiResponse.error(message=message, code=ResponseCode.NOT_FOUND)

    @staticmethod
    def param_error(message: str = "参数错误") -> JsonResponse:
        """参数错误响应"""
        return ApiResponse.error(message=message, code=ResponseCode.PARAM_ERROR)

    @staticmethod
    def captcha_error(message: str = "验证码错误") -> JsonResponse:
        """验证码错误响应"""
        return ApiResponse.error(message=message, code=ResponseCode.CAPTCHA_ERROR)

    @staticmethod
    def insufficient_balance(message: str = "余额不足") -> JsonResponse:
        """余额不足响应"""
        return ApiResponse.error(message=message, code=ResponseCode.INSUFFICIENT_BALANCE) 