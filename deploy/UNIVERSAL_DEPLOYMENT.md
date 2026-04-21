# 通用项目部署指南

> 适用于：Vue/React 前端 + FastAPI/Node.js 后端 + MySQL 数据库
>
> 最后更新：2026-04-21

---

## 目录

1. [准备工作](#准备工作)
2. [服务器初始化](#服务器初始化)
3. [项目部署](#项目部署)
4. [日常运维](#日常运维)
5. [模板文件](#模板文件)

---

## 准备工作

### 1.1 购买服务器

**推荐配置：**

| 配置项 | 推荐值 | 说明 |
|--------|--------|------|
| CPU | 2核 | 基础项目够用 |
| 内存 | 4GB | Docker + MySQL 最低要求 |
| 硬盘 | 50GB SSD | 代码 + 数据库 + 日志 |
| 带宽 | 3-5Mbps | 国内用户访问 |
| 系统 | Ubuntu 22.04 LTS | 稳定、社区支持好 |

**推荐服务商：**
- 腾讯云轻量服务器（国内访问快）
- 阿里云 ECS
- 华为云

### 1.2 准备域名

1. 购买域名（阿里云、腾讯云、GoDaddy 等）
2. 完成实名认证（国内需要）
3. 配置 DNS 解析（部署时操作）

### 1.3 本地环境

确保本地已安装：
- Git
- Node.js 18+（前端打包）
- Python 3.11+（后端开发）
- SSH 客户端

---

## 服务器初始化

### 2.1 连接服务器

```bash
ssh root@你的服务器IP
```

### 2.2 执行初始化脚本

一键完成 Docker、Docker Compose、Certbot 安装：

```bash
# 下载并执行初始化脚本
curl -fsSL https://raw.githubusercontent.com/你的仓库/init-server.sh | bash
```

或手动执行：

```bash
# 更新系统
apt update && apt upgrade -y

# 安装基础工具
apt install -y curl wget git vim htop

# 设置时区
timedatectl set-timezone Asia/Shanghai

# 安装 Docker
curl -fsSL https://get.docker.com | bash -s docker --mirror Aliyun

# 安装 Docker Compose
apt install -y docker-compose-plugin

# 启动 Docker
systemctl start docker
systemctl enable docker

# 安装 Certbot（SSL 证书）
apt install -y certbot

# 配置 Docker 镜像加速
mkdir -p /etc/docker
cat > /etc/docker/daemon.json <<EOF
{
    "registry-mirrors": [
        "https://docker.1ms.run",
        "https://docker.xuanyuan.me"
    ]
}
EOF
systemctl daemon-reload
systemctl restart docker
```

### 2.3 配置防火墙

```bash
# 开放必要端口
ufw allow 22/tcp     # SSH
ufw allow 80/tcp     # HTTP
ufw allow 443/tcp    # HTTPS
ufw --force enable
```

**腾讯云轻量服务器：** 需在控制台「防火墙」标签页添加规则

**阿里云：** 需在控制台「安全组」添加规则

---

## 项目部署

### 3.1 目录结构

```
/opt/项目名/
├── backend/              # 后端代码
│   ├── app/              # 应用代码
│   ├── Dockerfile        # Docker 构建文件
│   ├── .env.prod         # 生产环境变量
│   ├── run.py            # 启动脚本
│   └── requirements.txt  # Python 依赖
├── frontend/
│   └── dist/             # 前端打包文件
├── nginx/
│   ├── nginx.conf        # Nginx 配置
│   └── ssl/              # SSL 证书目录
├── init-sql/
│   └── init.sql          # 数据库初始化脚本
├── docker-compose.yml    # Docker 编排文件
└── .env                  # 敏感变量（密码等）
```

### 3.2 配置域名解析

在域名服务商添加 A 记录：

| 主机记录 | 记录类型 | 记录值 |
|---------|---------|--------|
| 前端子域名 | A | 服务器IP |
| 后端子域名 | A | 服务器IP |

**示例：**
- `app.example.com` → 前端
- `api.example.com` → 后端

### 3.3 申请 SSL 证书

```bash
# 申请前端域名证书
certbot certonly --standalone -d app.example.com

# 申请后端域名证书
certbot certonly --standalone -d api.example.com

# 证书位置
/etc/letsencrypt/live/app.example.com/
/etc/letsencrypt/live/api.example.com/
```

### 3.4 创建项目目录

```bash
PROJECT_NAME="myproject"
mkdir -p /opt/$PROJECT_NAME/{backend,frontend/dist,nginx/ssl,init-sql}
```

### 3.5 复制证书

```bash
# 复制前端证书
cp /etc/letsencrypt/live/app.example.com/fullchain.pem /opt/$PROJECT_NAME/nginx/ssl/app.example.com/
cp /etc/letsencrypt/live/app.example.com/privkey.pem /opt/$PROJECT_NAME/nginx/ssl/app.example.com/

# 复制后端证书
cp /etc/letsencrypt/live/api.example.com/fullchain.pem /opt/$PROJECT_NAME/nginx/ssl/api.example.com/
cp /etc/letsencrypt/live/api.example.com/privkey.pem /opt/$PROJECT_NAME/nginx/ssl/api.example.com/
```

### 3.6 上传代码

```bash
# 本地执行
# 上传后端
scp -r backend/app root@服务器IP:/opt/项目名/backend/
scp backend/run.py root@服务器IP:/opt/项目名/backend/
scp backend/requirements.txt root@服务器IP:/opt/项目名/backend/
scp backend/Dockerfile root@服务器IP:/opt/项目名/backend/
scp backend/.env.prod root@服务器IP:/opt/项目名/backend/

# 上传前端
scp -r frontend/dist root@服务器IP:/opt/项目名/frontend/

# 上传配置文件
scp docker-compose.yml root@服务器IP:/opt/项目名/
scp .env root@服务器IP:/opt/项目名/
scp nginx/nginx.conf root@服务器IP:/opt/项目名/nginx/
scp -r init-sql root@服务器IP:/opt/项目名/
```

### 3.7 启动服务

```bash
# SSH 到服务器
cd /opt/项目名

# 构建并启动
docker compose up -d --build

# 查看状态
docker compose ps

# 查看日志
docker compose logs -f
```

### 3.8 初始化数据库

```bash
# 如果有初始化脚本
docker exec -it 项目名-backend python -m app.init_data
```

### 3.9 验证部署

访问以下地址验证：
- 前端：`https://app.example.com`
- 后端：`https://api.example.com`
- 健康检查：`https://api.example.com/health`

---

## 日常运维

### 4.1 更新部署

```bash
# 上传新代码后重启
cd /opt/项目名
docker compose up -d --build backend
docker compose restart nginx
```

### 4.2 查看日志

```bash
# 实时日志
docker compose logs -f backend

# 最近 100 行
docker logs 项目名-backend --tail 100
```

### 4.3 数据库备份

```bash
# 备份
docker exec 项目名-mysql mysqldump -u root -p密码 数据库名 > backup_$(date +%Y%m%d).sql

# 恢复
docker exec -i 项目名-mysql mysql -u root -p密码 数据库名 < backup_20260421.sql
```

### 4.4 SSL 证书续期

```bash
# 查看到期时间
certbot certificates

# 手动续期
certbot renew

# 自动续期已配置（certbot timer）
```

### 4.5 清理 Docker 资源

```bash
# 清理未使用的镜像
docker image prune -a

# 清理未使用的容器
docker container prune

# 清理未使用的数据卷
docker volume prune
```

---

## 模板文件

以下模板文件可直接复制使用，只需修改标记为 `{{变量}}` 的部分。

### 5.1 Dockerfile（Python 后端）

```dockerfile
FROM python:3.11-slim

WORKDIR /app

# 国内镜像加速
RUN sed -i 's/deb.debian.org/mirrors.aliyun.com/g' /etc/apt/sources.list.d/debian.sources && \
    apt-get update && \
    apt-get install -y --no-install-recommends gcc && \
    rm -rf /var/lib/apt/lists/*

# 安装依赖
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt -i https://mirrors.aliyun.com/pypi/simple/ --trusted-host mirrors.aliyun.com

# 复制代码
COPY app/ ./app/
COPY run.py .

EXPOSE 8000

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

### 5.2 docker-compose.yml

```yaml
services:
  mysql:
    image: mysql:8.0
    container_name: {{项目名}}-mysql
    restart: always
    environment:
      MYSQL_ROOT_PASSWORD: ${MYSQL_ROOT_PASSWORD}
      MYSQL_DATABASE: {{数据库名}}
      MYSQL_USER: {{数据库用户}}
      MYSQL_PASSWORD: ${MYSQL_PASSWORD}
    ports:
      - "3306:3306"
    volumes:
      - mysql_data:/var/lib/mysql
      - ./init-sql:/docker-entrypoint-initdb.d
    command:
      --default-authentication-plugin=mysql_native_password
      --character-set-server=utf8mb4
      --collation-server=utf8mb4_unicode_ci
    networks:
      - app-network
    healthcheck:
      test: ["CMD", "mysqladmin", "ping", "-h", "localhost"]
      interval: 10s
      timeout: 5s
      retries: 5

  backend:
    build:
      context: ./backend
      dockerfile: Dockerfile
    container_name: {{项目名}}-backend
    restart: always
    depends_on:
      mysql:
        condition: service_healthy
    env_file:
      - ./backend/.env.prod
    ports:
      - "8000:8000"
    networks:
      - app-network

  nginx:
    image: nginx:alpine
    container_name: {{项目名}}-nginx
    restart: always
    depends_on:
      - backend
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./nginx/nginx.conf:/etc/nginx/nginx.conf:ro
      - ./nginx/ssl:/etc/nginx/ssl:ro
      - ./frontend/dist:/usr/share/nginx/html/frontend:ro
    networks:
      - app-network

volumes:
  mysql_data:

networks:
  app-network:
    driver: bridge
```

### 5.3 nginx.conf

```nginx
user nginx;
worker_processes auto;

events {
    worker_connections 1024;
}

http {
    include       mime.types;
    default_type  application/octet-stream;
    sendfile        on;
    keepalive_timeout 65;

    gzip on;
    gzip_types text/plain text/css application/json application/javascript;

    # 后端 API
    server {
        listen 80;
        listen 443 ssl http2;
        server_name {{后端域名}};

        ssl_certificate /etc/nginx/ssl/{{后端域名}}/fullchain.pem;
        ssl_certificate_key /etc/nginx/ssl/{{后端域名}}/privkey.pem;
        ssl_protocols TLSv1.2 TLSv1.3;

        location / {
            proxy_pass http://backend:8000;
            proxy_set_header Host $host;
            proxy_set_header X-Real-IP $remote_addr;
            proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
            proxy_set_header X-Forwarded-Proto $scheme;
        }
    }

    # 前端
    server {
        listen 80;
        listen 443 ssl http2;
        server_name {{前端域名}};

        ssl_certificate /etc/nginx/ssl/{{前端域名}}/fullchain.pem;
        ssl_certificate_key /etc/nginx/ssl/{{前端域名}}/privkey.pem;
        ssl_protocols TLSv1.2 TLSv1.3;

        root /usr/share/nginx/html/frontend;
        index index.html;

        location / {
            try_files $uri $uri/ /index.html;
        }

        location ~* \.(js|css|png|jpg|jpeg|gif|ico|svg)$ {
            expires 30d;
        }
    }
}
```

### 5.4 .env（Docker Compose 变量）

```env
MYSQL_ROOT_PASSWORD={{Root密码}}
MYSQL_PASSWORD={{用户密码}}
SECRET_KEY={{JWT密钥}}
```

### 5.5 backend/.env.prod（后端环境变量）

```env
DATABASE_URL=mysql+aiomysql://{{用户名}}:{{密码}}@mysql:3306/{{数据库名}}
SECRET_KEY={{JWT密钥}}
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=1440
APP_NAME={{应用名称}}
APP_VERSION=1.0.0
DEBUG=false
CORS_ORIGINS=["https://{{前端域名}}","https://{{后端域名}}"]
```

### 5.6 一键部署脚本（PowerShell）

```powershell
# deploy.ps1
param([string]$Target = "all")

$SERVER = "服务器IP"
$USER = "root"
$REMOTE_DIR = "/opt/项目名"

function Deploy-Backend {
    scp -r app/ ${USER}@${SERVER}:${REMOTE_DIR}/backend/
    scp run.py requirements.txt ${USER}@${SERVER}:${REMOTE_DIR}/backend/
    ssh ${USER}@${SERVER} "cd ${REMOTE_DIR} && docker compose up -d --build backend"
}

function Deploy-Frontend {
    npm run build
    scp -r dist/ ${USER}@${SERVER}:${REMOTE_DIR}/frontend/
    ssh ${USER}@${SERVER} "cd ${REMOTE_DIR} && docker compose restart nginx"
}

switch ($Target) {
    "backend"  { Deploy-Backend }
    "frontend" { Deploy-Frontend }
    "all"      { Deploy-Backend; Deploy-Frontend }
}
```

---

## 快速检查清单

部署前检查：

- [ ] 服务器已购买，SSH 可连接
- [ ] 域名已购买，实名认证完成
- [ ] DNS 解析已配置（A 记录指向服务器 IP）
- [ ] Docker 已安装
- [ ] Docker Compose 已安装
- [ ] Certbot 已安装
- [ ] SSL 证书已申请
- [ ] 防火墙已开放 80、443 端口

部署后验证：

- [ ] 前端可访问
- [ ] 后端 API 可访问
- [ ] 健康检查返回正常
- [ ] 数据库连接正常
- [ ] HTTPS 证书有效

---

**文档版本：1.0**

**适用场景：** 小型团队/个人项目的快速部署