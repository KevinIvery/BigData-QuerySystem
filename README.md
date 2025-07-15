# 大数据查询平台

一个基于 Django + Nuxt.js 的大数据查询系统源码，前后端分离。支持司法，婚姻。多头借贷等多种接口配置。支持支付宝微信支付，支持短信验证码和微信自动登录。带有代理系统。后台管理系统。客户端。API配置

## 📑 目录

- [🚀 项目特性](#-项目特性)
- [🛠 技术栈](#-技术栈)
- [📸 系统界面预览](#-系统界面预览)
- [📁 项目结构](#-项目结构)
- [🚀 快速部署](#-快速部署)
  - [环境要求](#环境要求)
  - [后端部署 (Django)](#2-后端部署-django)
  - [前端部署 (Nuxt.js)](#3-前端部署-nuxtjs)
- [📋 系统说明](#-系统说明)
- [🔗 商业合作](#-商业合作)
- [🤝 贡献指南](#-贡献指南)
- [📝 许可证](#-许可证)
- [📞 技术支持](#-技术支持)
- [🙏 致谢](#-致谢)
- [📸 系统界面预览](#-系统界面预览)


## 🚀 项目特性

- **多角色支持**: 普通用户、代理商、管理员三种角色
- **多种查询类型**: 个人风险、企业信息、司法信息、婚姻信息等支持扩展API
- **支付系统**: 支持微信支付、支付宝等多种支付方式
- **代理商系统**: 完整的代理商申请、审核、佣金管理流程
- **响应式设计**: 支持PC端和移动端访问
- **实时数据**: 基于天远大数据API的实时数据查询
- **用户管理**: 支持微信自动登录和短信验证码登录方式
## 🛠 技术栈

### 后端 (Django)
- **框架**: Django 5.2.4
- **数据库**: MySQL 8.0+
- **认证**: session 认证
- **支付**: 微信支付、支付宝集成

### 前端 (Nuxt.js)
- **框架**: Nuxt.js 3.17.6
- **UI框架**: Tailwind CSS
- **图表**: Chart.js



## 📁 项目结构

```
django_web/
├── big-data-platform-frontend/     # Nuxt.js 前端项目
│   ├── components/                 # Vue组件
│   │   ├── admin/                 # 管理员组件
│   │   ├── agent/                 # 代理商组件
│   │   ├── frontend/              # 前台用户组件
│   │   ├── agreements/            # 协议页面组件
│   │   └── query-results/         # 查询结果组件
│   ├── pages/                     # 页面路由
│   │   ├── admin/                 # 管理员页面
│   │   ├── agent/                 # 代理商页面
│   │   └── query-result/          # 查询结果页面
│   ├── composables/               # 组合式函数
│   ├── middleware/                # 中间件
│   ├── plugins/                   # 插件
│   ├── public/                    # 静态资源
│   ├── nuxt.config.ts            # Nuxt配置
│   └── package.json              # 依赖配置
├── WebSite/                       # Django 后端项目
│   ├── WebApi/                   # 主应用
│   │   ├── models.py            # 数据模型
│   │   ├── views.py             # 视图函数
│   │   ├── admin_views.py       # 管理员视图
│   │   ├── agent_views.py       # 代理商视图
│   │   ├── frontend_views.py    # 前台视图
│   │   ├── urls.py              # URL路由
│   │   ├── middleware.py        # 中间件
│   │   └── migrations/          # 数据库迁移
│   ├── WebSite/                 # 项目配置
│   │   ├── settings.py         # Django设置
│   │   └── urls.py             # 主URL配置
│   ├── media/                   # 媒体文件
│   └── manage.py               # Django管理脚本
├── 系统使用手册.md              # 系统使用说明
└── README.md                    # 项目说明文档
```

## 🚀 快速部署

### 环境要求

- **Python**: 3.10+
- **Node.js**: 20+
- **MySQL**: 8.0+

### 1. 克隆项目

```bash
git clone https://github.com/KevinIvery/BigData-QuerySystem.git
cd BigData-QuerySystem
```

### 2. 后端部署 (Django)

#### 2.1 修改数据库配置

编辑 `WebSite/WebSite/settings.py`：

```python
DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.mysql",
        "NAME": "your-database-name",
        "USER": "your-database-user",
        "PASSWORD": "your-database-password",
        "HOST": "your-database-host",
        "PORT": "3306",
        "OPTIONS": {
            "charset": "utf8mb4",
            "init_command": "SET sql_mode='STRICT_TRANS_TABLES'",
        },
    }
}
```

#### 2.2 导入数据库（必须导入数据库文件）

```bash
# 导入提供的MySQL数据库文件
mysql -u your-user -p your-database < database_backup.sql
```

#### 2.3 安装依赖

```bash
cd WebSite
pip install -r requirements.txt
```

#### 2.4 启动后端服务

```bash
python manage.py runserver 0.0.0.0:8000
```

#### 2.5 配置外网访问

设置服务器防火墙和端口转发，确保8000端口可以外网访问。

### 3. 前端部署 (Nuxt.js)

#### 3.1 配置环境变量

编辑 `big-data-platform-frontend/.env`：

```bash
NUXT_PUBLIC_API_BASE_URL=http://api.v2.tybigdata.com/api
NUXT_FILE_URL=http://api.v2.tybigdata.com
NUXT_Agents_USL=https://web.tybigdata.com/
NUXT_Company_Name=海南天远大数据科技有限公司
```

**配置说明：**
- `NUXT_PUBLIC_API_BASE_URL`: 后端域名地址/api
- `NUXT_FILE_URL`: 后端域名地址
- `NUXT_Agents_USL`: 前端域名地址
- `NUXT_Company_Name`: 公司名称

#### 3.2 构建项目

```bash
cd big-data-platform-frontend
npm install
npm run build
```

#### 3.3 上传到服务器

将生成的 `.output` 文件夹上传到服务器。

#### 3.4 服务器部署

```bash
# 在服务器上安装依赖
npm install

# 启动服务
node .output/server/index.mjs
```

#### 3.5 配置外网访问

- 开启服务器3000端口的外网映射
- 绑定域名到3000端口
- 配置SSL证书（可选）

## 📋 系统说明

本系统提供完整的数据库文件，可直接导入使用。系统包含：

- **用户系统**: 支持微信登录、手机验证
- **代理商系统**: 代理商申请、审核、佣金管理
- **管理后台**: 用户管理、订单管理、系统配置
- **支付系统**: 微信支付、支付宝支付
- **查询服务**: 对接天远大数据API接口

## 🔗 商业合作

### API接口服务
本系统对接海南天远大数据科技有限公司的数据查询API，如需使用完整功能，请联系获取API接口权限。

### 技术支持
- 系统定制开发
- 部署技术支持  
- API接口对接
- 二次开发服务

联系方式: 微信：post0025

## 🤝 贡献指南

1. Fork 项目
2. 创建特性分支 (`git checkout -b feature/AmazingFeature`)
3. 提交更改 (`git commit -m 'Add some AmazingFeature'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 打开 Pull Request

## 📝 许可证

本项目采用 GPL-3.0 许可证 - 查看 [LICENSE](LICENSE) 文件了解详情。

### 许可说明

- **开源使用**: 遵循GPL-3.0协议，可自由使用、修改和分发
- **商业使用**: 如需商业使用或不开源的定制版本，请联系获取商业授权
- **API服务**: 数据查询功能需要单独的API接口授权

## 📞 技术支持

- 技术文档: [系统使用手册.md](系统使用手册.md)
- 问题反馈: [GitHub Issues](https://github.com/KevinIvery/BigData-QuerySystem/issues)
- 商业合作: 微信：post0025

## 🙏 致谢

感谢所有为这个项目做出贡献的开发者和用户。

---

**注意**: 部署前请确保：
1. 修改所有默认密码和密钥
2. 配置正确的域名和SSL证书
3. 设置适当的防火墙规则
4. 定期更新依赖包
5. 监控系统性能和日志 

## 📸 系统界面预览

### 管理后台
![管理员后台](系统图片/管理员后台.png)

### 代理商系统
![代理系统后台](系统图片/代理系统后台.png)

### 用户端界面
![首页](系统图片/首页.jpg)
![用户中心](系统图片/用户中心.jpg)

### 查询报告示例
![个人报告示例](系统图片/个人报告示例.jpg)
![企业报告示例](系统图片/企业报告示例.jpg)