# 极智协同项目部署文档

> 最后更新：2026-04-21

---

## 目录

1. [项目信息](#项目信息)
2. [服务器环境](#服务器环境)
3. [已部署服务](#已部署服务)
4. [日常运维](#日常运维)
5. [新项目部署指南](#新项目部署指南)
6. [常见问题](#常见问题)

---

## 项目信息

| 项目 | 值 |
|------|-----|
| 服务器 IP | `118.25.182.15` |
| 前端域名 | `https://aixt.coderzzp.top` |
| 后端域名 | `https://admin.coderzzp.top` |
| 操作系统 | Ubuntu 22.04 LTS (腾讯云轻量服务器) |
| 部署方式 | Docker Compose 容器化 |

---

## 服务器环境

### 连接方式

```powershell
# PowerShell / Git Bash
ssh root@118.25.182.15
# 密码：19980610Zzp
```

### Docker 环境

```bash
docker --version          # Docker version 29.4.0
docker compose version    # Docker Compose version v2.x
```

### 目录结构

```
/opt/howtoai/
├── backend/                 # 后端代码
│   ├── app/                 # FastAPI 应用
│   ├── Dockerfile           # Docker 构建文件
│   ├── .env.prod            # 生产环境变量
│   ├── run.py               # 启动脚本
│   └── requirements.txt     # Python 依赖
├── frontend/
│   └── dist/                # 前端打包文件
├── nginx/
│   ├── nginx.conf           # Nginx 配置
│   └── ssl/                 # SSL 证书
│       ├── aixt.coderzzp.top/
│       └── admin.coderzzp.top/
├── init-sql/
│   └── init_tables.sql      # 数据库初始化脚本
├── docker-compose.yml        # Docker 编排文件
└── .env                      # 环境变量（密码等）
```

---

## 已部署服务

### 容器列表

| 容器名 | 镜像 | 端口 | 说明 |
|--------|------|------|------|
| howtoai-mysql | mysql:8.0 | 3306 | MySQL 数据库 |
| howtoai-backend | 自建 | 8000 | FastAPI 后端 |
| howtoai-nginx | nginx:alpine | 80, 443 | 反向代理 |
| portainer | portainer-ce | 9000, 9443 | Docker 管理面板 |

### 访问地址

| 服务 | 地址 | 说明 |
|------|------|------|
| 前端 | https://aixt.coderzzp.top | 用户访问入口 |
| 后端 API | https://admin.coderzzp.top | API 接口 |
| 健康检查 | https://admin.coderzzp.top/health | 服务状态 |
| Portainer | https://118.25.182.15:9443 | Docker 管理面板 |

### 数据库信息

| 项目 | 值 |
|------|-----|
| 数据库名 | howtoai |
| 用户名 | howtoai |
| 密码 | Howtoai2024 |
| Root 密码 | HowtoaiRoot2024Secure |

### 测试账户

| 用户名 | 密码 | 角色 |
|--------|------|------|
| admin | admin123 | 管理员 |
| zhangsan | 123456 | 普通用户 |
| lisi | 123456 | 普通用户 |

---

## 日常运维

### 项目更新部署

**方式一：使用一键脚本（推荐）**

```powershell
# 在本地项目目录执行
cd D:\coderzzp\howtoai-backend

# 更新全部（前端+后端）
.\deploy.ps1

# 仅更新后端
.\deploy.ps1 backend

# 仅更新前端
.\deploy.ps1 frontend
```

**方式二：手动操作**

```bash
# 1. 上传后端代码
scp -r app/ root@118.25.182.15:/opt/howtoai/backend/
scp run.py root@118.25.182.15:/opt/howtoai/backend/

# 2. 上传前端代码
scp -r dist/ root@118.25.182.15:/opt/howtoai/frontend/

# 3. 重启服务
ssh root@118.25.182.15
cd /opt/howtoai
docker compose up -d --build backend
docker compose restart nginx
```

### Docker 常用命令

```bash
# 查看所有容器状态
docker compose ps

# 查看容器日志
docker compose logs -f backend
docker compose logs -f nginx
docker compose logs -f mysql

# 重启服务
docker compose restart                    # 重启全部
docker compose restart backend            # 重启后端
docker compose restart nginx              # 重启nginx

# 停止服务
docker compose down

# 启动服务
docker compose up -d

# 重新构建并启动
docker compose up -d --build
```

### 数据库操作

```bash
# 进入 MySQL 容器
docker exec -it howtoai-mysql mysql -u howtoai -pHowtoai2024 howtoai

# 备份数据库
docker exec howtoai-mysql mysqldump -u root -pHowtoaiRoot2024Secure howtoai > backup_$(date +%Y%m%d).sql

# 恢复数据库
docker exec -i howtoai-mysql mysql -u root -pHowtoaiRoot2024Secure howtoai < backup_20260421.sql
```

### SSL 证书管理

```bash
# 查看证书到期时间
certbot certificates

# 手动续期
certbot renew

# 测试续期（不实际更新）
certbot renew --dry-run
```

### 日志查看

```bash
# 后端日志
docker logs -f howtoai-backend --tail 100

# Nginx 日志
docker logs -f howtoai-nginx --tail 100

# MySQL 日志
docker logs -f howtoai-mysql --tail 100
```

---

## 新项目部署指南

### 第一步：本地生成部署配置

在 `D:\coderzzp\howtoai-backend\deploy` 目录执行：

```powershell
.\new-project.ps1 -Name "项目名" -Frontend "前端域名" -Backend "后端域名" -DbPass "数据库密码"
```

**示例：**

```powershell
.\new-project.ps1 -Name "blog" -Frontend "blog.coderzzp.top" -Backend "blogapi.coderzzp.top" -DbPass "Blog2024"
```

执行后会生成：
- `D:\coderzzp\blog-deploy\` 目录
- 包含 Dockerfile、docker-compose.yml、nginx.conf、deploy.ps1 等

### 第二步：配置域名解析

在域名服务商（阿里云）添加 A 记录：

| 主机记录 | 记录类型 | 记录值 |
|---------|---------|--------|
| blog | A | 118.25.182.15 |
| blogapi | A | 118.25.182.15 |

### 第三步：服务器初始化

```bash
# 上传初始化脚本
scp deploy/init-project.sh root@118.25.182.15:/root/

# 执行初始化
ssh root@118.25.182.15
bash /root/init-project.sh blog blog.coderzzp.top blogapi.coderzzp.top Blog2024
```

### 第四步：上传代码和配置

```powershell
# 上传后端代码
scp -r D:\coderzzp\blog-backend\app root@118.25.182.15:/opt/blog/backend/
scp D:\coderzzp\blog-backend\run.py root@118.25.182.15:/opt/blog/backend/
scp D:\coderzzp\blog-backend\requirements.txt root@118.25.182.15:/opt/blog/backend/

# 上传部署配置
scp D:\coderzzp\blog-deploy\* root@118.25.182.15:/opt/blog/

# 打包并上传前端
cd D:\coderzzp\blog
npm run build
scp -r dist/ root@118.25.182.15:/opt/blog/frontend/
```

### 第五步：启动服务

```bash
ssh root@118.25.182.15
cd /opt/blog
docker compose up -d --build
```

### 第六步：初始化数据库

```bash
docker exec -it blog-backend python -m app.init_data
```

---

## 多项目端口规划

同一服务器部署多项目时，需要修改 `docker-compose.yml` 中的端口映射：

| 项目 | MySQL 端口 | 后端端口 | Nginx 端口 |
|------|-----------|---------|-----------|
| howtoai | 3306 | 8000 | 80/443 |
| blog | 3307 | 8001 | 不需要（共用nginx） |
| shop | 3308 | 8002 | 不需要（共用nginx） |

**推荐做法：** 使用单独的 Nginx 容器管理所有虚拟主机，其他项目不需要单独的 nginx。

---

## 常见问题

### Q1: SSH 连接被拒绝

```bash
# 检查密码登录是否开启
cat /etc/ssh/sshd_config | grep PasswordAuthentication

# 如需开启
sed -i 's/PasswordAuthentication no/PasswordAuthentication yes/' /etc/ssh/sshd_config
systemctl restart sshd
```

### Q2: Docker 构建很慢

确保使用了国内镜像源，Dockerfile 中应包含：

```dockerfile
RUN sed -i 's/deb.debian.org/mirrors.aliyun.com/g' /etc/apt/sources.list.d/debian.sources
RUN pip install --no-cache-dir -r requirements.txt -i https://mirrors.aliyun.com/pypi/simple/ --trusted-host mirrors.aliyun.com
```

### Q3: SSL 证书申请失败

确保：
1. 域名已正确解析到服务器 IP
2. 80 端口可访问（certbot 需要用 80 端口验证）
3. 防火墙已开放 80 端口

### Q4: 前端访问后端 API 跨域

检查后端 `.env.prod` 中的 `CORS_ORIGINS` 配置：

```env
CORS_ORIGINS=["https://你的前端域名","http://你的前端域名"]
```

### Q5: 数据库连接失败

检查：
1. MySQL 容器是否正常运行：`docker ps`
2. 数据库用户名密码是否正确
3. 容器内连接使用服务名 `mysql`，不是 `localhost`

### Q6: 容器内存占用高

```bash
# 查看资源使用
docker stats

# 限制内存（在 docker-compose.yml 中添加）
services:
  backend:
    deploy:
      resources:
        limits:
          memory: 512M
```

---

## 联系方式

如有问题，请检查以下资源：

- Docker 官方文档：https://docs.docker.com/
- Nginx 官方文档：https://nginx.org/en/docs/
- Certbot 文档：https://certbot.eff.org/

---

## 附录：一键部署脚本使用说明

### deploy.ps1 参数说明

```powershell
.\deploy.ps1          # 部署全部（前端+后端）
.\deploy.ps1 backend  # 仅部署后端
.\deploy.ps1 frontend # 仅部署前端
.\deploy.ps1 config   # 仅更新配置文件
```

### new-project.ps1 参数说明

```powershell
.\new-project.ps1 `
    -Name "项目名称" `
    -Frontend "前端域名" `
    -Backend "后端域名" `
    -DbPass "数据库密码" `
    -BackendDir "后端本地路径（可选）" `
    -FrontendDir "前端本地路径（可选）"
```

---

**文档版本：1.0**

**创建时间：2026-04-21**