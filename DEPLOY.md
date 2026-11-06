# 部署指南（宝塔面板 + 腾讯云/阿里云）

这份文档教你把这个资料分享站部署到国内云服务器上。
整体思路：**Nginx 接收访问 → 转给 Gunicorn 运行 Django → 数据存 MySQL → 上传文件存磁盘**。

> 说明：宝塔面板不同版本界面略有差异，以下按常见流程写，操作时以你面板实际为准。

---

## 一、前提准备

- [ ] 云服务器（建议 2核4G / 60GB 磁盘 / 8M 带宽）
- [ ] 域名已解析到服务器 IP（A 记录）
- [ ] 已完成 ICP 备案（大陆服务器必需）
- [ ] 宝塔面板已安装，能登录

## 二、宝塔软件商店安装

进入 **软件商店**，安装这三样：

1. **Nginx**（推荐最新稳定版）
2. **MySQL**（5.7 或 8.0 均可）
3. **Python**（选 3.12，与本地一致；找不到就在「Python 项目」里装）

## 三、上传代码

方式一（推荐）：在服务器上用 git 克隆你的 GitHub 仓库。

方式二：本地把项目打包成 zip，用宝塔「文件」上传到服务器解压。

**项目放在**：`/www/wwwroot/resource-share/`

## 四、建数据库

1. 宝塔 → **数据库** → 添加数据库
2. 记下四项信息（下面配置要用）：
   - 数据库名，例如 `resource_share`
   - 用户名
   - 密码
   - 访问权限选「本地服务器」

## 五、创建虚拟环境并装依赖

在项目目录 `/www/wwwroot/resource-share/` 下执行：

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

## 六、写生产环境配置

复制模板为正式配置，然后编辑：

```bash
cp .env.example .env
```

用编辑器打开 `.env`，按下面填（**这是关键一步**）：

```ini
DEBUG=False
SECRET_KEY=粘贴你生成的随机密钥
ALLOWED_HOSTS=你的域名.com,www.你的域名.com
DATABASE_URL=mysql://数据库用户:密码@127.0.0.1:3306/数据库名
```

> 生成随机密钥：在命令行运行
> `python -c "import secrets; print(secrets.token_urlsafe(50))"`
> 把输出粘贴到 `SECRET_KEY=` 后面。

## 七、初始化数据

```bash
source .venv/bin/activate
python manage.py migrate           # 建表
python manage.py collectstatic     # 收集静态文件（已自动执行过也可再跑一次）
python manage.py createsuperuser   # 建管理员账号（登录 /admin 用）
```

## 八、用 Gunicorn 启动

```bash
source .venv/bin/activate
gunicorn config.wsgi:application --bind 127.0.0.1:8000 --workers 2
```

**或者**用宝塔的「Python 项目」管理器来启动（更省心，能开机自启）：
- 项目路径选 `/www/wwwroot/resource-share`
- 启动方式选 Gunicorn
- 端口填 `8000`

## 九、配置 Nginx

在宝塔 **网站 → 添加站点**，域名填你的域名，PHP 版本选「纯静态」。
然后进入该站点的 **反向代理**，添加：

- 代理名称：`django`
- 目标 URL：`http://127.0.0.1:8000`
- 发送域名：`$host`

**再给上传的文件目录加一条映射**（这样下载更高效）：
在站点 **配置文件** 里，`server` 块内加：

```nginx
location /media/ {
    alias /www/wwwroot/resource-share/media/;
}
```

保存后重载 Nginx。

## 十、设置上传目录权限

Django 进程需要能往 media 目录写文件：

```bash
chmod -R 755 /www/wwwroot/resource-share/media
chown -R www:www /www/wwwroot/resource-share/media
```

## 十一、启用 HTTPS（强烈建议）

1. 宝塔 → 网站 → 你的站点 → **SSL** → 选择 Let's Encrypt，免费申请证书（备案完成后才能申请）
2. 申请成功后，**开启「强制 HTTPS」**
3. 编辑项目 `.env`，把 `HTTPS_ON` 改成 `True`，然后重启 Gunicorn

> 注意：反向代理要带上 `X-Forwarded-Proto` 头，Django 才能正确识别 HTTPS。
> 宝塔的反向代理一般已自动带上；若没有，在站点配置文件 `location /` 里加一行
> `proxy_set_header X-Forwarded-Proto $scheme;`。

## 十二、测试

1. 浏览器打开 `http://你的域名/` → 应该看到首页
2. 打开 `http://你的域名/admin/` → 用管理员账号登录，看后台样式是否正常
3. 注册一个普通账号，上传一个文件，再下载它 → 验证全流程

---

## 常见问题

| 现象 | 排查 |
|------|------|
| 打开显示 400 Bad Request | `ALLOWED_HOSTS` 没写对，或没加域名 |
| 上传文件报 500 | media 目录没权限（看第十步） |
| 页面能开但没样式 | `collectstatic` 没跑，或 whitenoise 没生效 |
| 打开超时 | Gunicorn 没启动，或反向代理端口不对 |
| 数据库连不上 | `DATABASE_URL` 里的账号密码/库名有误 |

## 更新代码的流程

以后你改了代码，上线更新步骤：

```bash
cd /www/wwwroot/resource-share
git pull                        # 或用宝塔文件覆盖
source .venv/bin/activate
pip install -r requirements.txt  # 如果有新依赖
python manage.py migrate         # 如果有模型改动
python manage.py collectstatic   # 如果有静态文件改动
# 重启 Gunicorn
```

---

如果卡在任何一步，把报错信息发给我，我帮你定位。
