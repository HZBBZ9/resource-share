# 资料分享站

一个开源的资料分享网站，用户可以注册、登录、上传文件，其他用户浏览和下载。

## 功能

- 用户注册 / 登录 / 登出
- 上传资料（标题、描述、分类、文件）
- 浏览资料列表，支持关键词搜索和分类筛选
- 下载资料（自动计数）
- 删除自己上传的资料
- Django Admin 后台管理

## 技术栈

- Python 3.12
- Django 6
- SQLite（默认，可换成 PostgreSQL）

## 本地运行

```bash
# 1. 创建并激活虚拟环境
python3 -m venv .venv
source .venv/bin/activate

# 2. 安装依赖
pip install -r requirements.txt

# 3. 初始化数据库
python manage.py migrate

# 4. 创建管理员账号（用于 /admin 后台）
python manage.py createsuperuser

# 5. 启动开发服务器
python manage.py runserver
```

访问 http://127.0.0.1:8000/ 即可。

## 项目结构

```
config/        # 项目配置
resources/     # 核心应用（模型、视图、模板）
media/         # 上传的文件（运行时生成，不入库）
```

## 部署

上线时可部署到 Railway / Render / Fly.io 等平台，把 `DEBUG` 改为 `False`、
设置 `ALLOWED_HOSTS` 和 `SECRET_KEY`，数据库换成 PostgreSQL，上传文件改用云存储。

## 开源协议

[MIT](LICENSE)
