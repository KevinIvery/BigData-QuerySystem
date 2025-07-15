"""
WebApi应用的URL配置
"""
from django.urls import path
from . import captcha_views, admin_views, upload_views, frontend_views, agent_views

urlpatterns = [
    # 验证码相关接口
    path('captcha/generate/', captcha_views.generate_captcha, name='generate_captcha'),
    path('captcha/verify/', captcha_views.verify_captcha, name='verify_captcha'),
    # 超级管理员相关接口
    path('admin/login/', admin_views.admin_login, name='admin_login'),
    path('admin/logout/', admin_views.admin_logout, name='admin_logout'),
    path('admin/auth-check/', admin_views.admin_auth_check, name='admin_auth_check'),
    path('admin/profile/update/', admin_views.admin_profile_update, name='admin_profile_update'),
    
    # 系统配置接口
    path('admin/system-config/', admin_views.get_system_config, name='get_system_config'),
    path('admin/system-config/update/', admin_views.update_system_config, name='update_system_config'),
    
    # 查询配置接口
    path('admin/query-configs/', admin_views.get_query_configs, name='get_query_configs'),
    path('admin/query-configs/update/<int:config_id>/', admin_views.update_query_config, name='update_query_config'),

    # 代理管理接口
    path('admin/agents/', admin_views.get_agents, name='get_agents'),
    path('admin/agents/create/', admin_views.create_agent, name='create_agent'),
    path('admin/agents/update/<int:agent_id>/', admin_views.update_agent, name='update_agent'),
    path('admin/agents/delete/<int:agent_id>/', admin_views.delete_agent, name='delete_agent'),
    path('admin/agents/detail/<int:agent_id>/', admin_views.get_agent_detail, name='get_agent_detail'),
    # 外部API配置接口
    path('admin/external-api-configs/', admin_views.get_external_api_configs, name='get_external_api_configs'),
    path('admin/external-api-configs/update/', admin_views.update_external_api_config, name='update_external_api_config'),
    
    # 授权书管理接口
    path('admin/authorization-letters/', admin_views.get_authorization_letters, name='get_authorization_letters'),
    path('admin/authorization-letters/download/<str:token>/', admin_views.download_authorization_letter_admin, name='download_authorization_letter_admin'),
    
    # 查询记录管理接口
    path('admin/query-records/', admin_views.get_query_records, name='get_query_records'),
    path('admin/query-records/delete/<int:record_id>/', admin_views.delete_query_record, name='delete_query_record'),
    
    # 订单记录管理接口
    path('admin/orders/', admin_views.get_orders, name='get_orders'),
    path('admin/orders/refund/', admin_views.refund_order, name='refund_order'),
    
    # 普通用户管理接口
    path('admin/regular-users/', admin_views.get_regular_users, name='get_regular_users'),
    path('admin/regular-users/delete/<int:user_id>/', admin_views.delete_regular_user, name='delete_regular_user'),
    
    # 仪表盘统计接口
    path('admin/dashboard/stats/', admin_views.get_dashboard_stats, name='get_dashboard_stats'),
    
    # 代理申请管理接口
    path('admin/agent-applications/', admin_views.get_agent_applications, name='get_agent_applications'),
    path('admin/agent-applications/delete/<int:application_id>/', admin_views.delete_agent_application, name='delete_agent_application'),

    # 佣金申请管理接口
    path('admin/commission-withdrawals/', admin_views.get_commission_withdrawals, name='get_commission_withdrawals'),
    path('admin/commission-withdrawals/process/', admin_views.process_commission_withdrawal, name='process_commission_withdrawal'),
    path('admin/commission-withdrawals/detail/<int:withdrawal_id>/', admin_views.get_commission_withdrawal_detail, name='get_commission_withdrawal_detail'),

    # ==================== 代理管理后台接口 ====================
    path('agent/login/', agent_views.agent_login, name='agent_login'),
    path('agent/logout/', agent_views.agent_logout, name='agent_logout'),
    path('agent/auth-check/', agent_views.agent_auth_check, name='agent_auth_check'),
    
    # 代理个人信息管理接口
    path('agent/change-password/', agent_views.change_password, name='agent_change_password'),
    
    # 代理系统配置接口
    path('agent/system-config/', agent_views.get_system_config, name='agent_get_system_config'),
    path('agent/system-config/update/', agent_views.update_system_config, name='agent_update_system_config'),
    
    # 代理查询配置接口
    path('agent/query-configs/', agent_views.get_query_configs, name='agent_get_query_configs'),
    path('agent/query-configs/update/<int:config_id>/', agent_views.update_query_config, name='agent_update_query_config'),
    
    # 代理订单记录接口
    path('agent/orders/', agent_views.get_agent_orders, name='agent_get_orders'),

    # 代理仪表盘统计接口
    path('agent/dashboard/stats/', agent_views.get_agent_dashboard_stats, name='agent_dashboard_stats'),
    
    # 代理佣金提现相关接口
    path('agent/payment-config/', agent_views.get_agent_payment_config, name='agent_get_payment_config'),
    path('agent/payment-config/save/', agent_views.save_agent_payment_config, name='agent_save_payment_config'),
    path('agent/withdrawal/submit/', agent_views.submit_commission_withdrawal, name='agent_submit_withdrawal'),
    path('agent/withdrawal/records/', agent_views.get_commission_withdrawal_records, name='agent_withdrawal_records'),

    # 文件上传接口
    path('upload/', upload_views.upload_image, name='upload_image'),

    # ==================== 前端站点接口 ====================
    path('frontend/status/', frontend_views.site_status_check, name='site_status_check'),
    path('frontend/data/', frontend_views.get_site_data, name='get_site_data'),

    # --- 新增：前端用户认证接口 ---
    path('frontend/send-sms-code/', frontend_views.send_sms_code, name='send_sms_code'),
    path('frontend/login/sms/', frontend_views.login_with_sms_code, name='login_with_sms_code'),
    path('frontend/login/wechat/', frontend_views.wechat_oauth_login, name='wechat_oauth_login'),
    path('frontend/logout/', frontend_views.logout_view, name='logout_view'),
    path('frontend/auth-check/', frontend_views.user_auth_check, name='user_auth_check'),
    
    # --- 新增：前端支付查询接口 ---
    path('frontend/send-verification-code-for-query/', frontend_views.send_verification_code_for_query, name='send_verification_code_for_query'),
    path('frontend/create-order/', frontend_views.create_query_order, name='create_query_order'),
    path('frontend/create-payment/', frontend_views.create_payment, name='create_payment'),
    path('frontend/query-result/<str:order_no>/', frontend_views.get_query_result, name='get_query_result'),
    path('frontend/example-report/', frontend_views.example_report, name='example_report'),
    
    # --- 新增：用户个人中心接口 ---
    path('frontend/deactivate-account/', frontend_views.deactivate_account, name='deactivate_account'),
    path('frontend/query-history/', frontend_views.get_user_query_history, name='get_user_query_history'),
    path('frontend/order-history/', frontend_views.get_user_order_history, name='get_user_order_history'),
    
    # 代理申请相关接口
    path('frontend/submit-agency-application/', frontend_views.submit_agency_application, name='submit_agency_application'),
    path('frontend/check-agency-application-status/', frontend_views.check_agency_application_status, name='check_agency_application_status'),
]

