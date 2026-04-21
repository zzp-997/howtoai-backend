# 新项目接入 Docker + CI/CD 部署指南

> 适用场景：Vue/React 前端 + FastAPI/Node.js 后端 + MySQL 数据库
>
> 前置条件：已有云服务器，已安装 Docker 和 Docker Compose

---

## 快速检查清单

在开始之前，确认服务器已完成基础配置：

```bash
# SSH 连接服务器
ssh root@你的服务器IP

# 检查 Docker
docker --version          # 应显示版本号
docker compose version    # 应显示版本号

# 检查 Certbot
certbot --version         # 应显示版本号
```

如果以上命令都正常，继续下面的步骤。

---

## 第一步：准备域名

### 1.1 购买域名（如已购买可跳过）

在阿里云/腾讯云购买域名，完成实名认证。

### 1.2 配置 DNS 解析

添加两条 A 记录：

| 主机记录 | 记录类型 | 记录值 |
|---------|---------|--------|
| 前端子域名 | A | 服务器IP |
| 后端子域名 | A | 服务器IP |

**示例**：项目名为 `blog`
- `blog.coderzzp.top` → 前端
- `blogapi.coderzzp.top` → 后端

### 1.3 验证解析生效

```bash
# 在本地执行
nslookup blog.coderzzp.top
# 应返回服务器IP
```

---

## 第二步：服务器初始化

### 2.1 创建项目目录

```bash
# SSH 到服务器
ssh root@你的服务器IP

# 设置项目名
PROJECT_NAME="blog"  # 改成你的项目名
FRONTEND_DOMAIN="blog.coderzzp.top"  # 改成你的前端域名
BACKEND_DOMAIN="blogapi.coderzzp.top"  # 改成你的后端域名

# 创建目录
mkdir -p /opt/$PROJECT_NAME/{backend,frontend/dist,nginx/ssl/$FRONTEND_DOMAIN,nginx/ssl/$BACKEND_DOMAIN,sql/migrations,scripts}
```

### 2.2 申请 SSL 证书

```bash
# 申请前端域名证书
certbot certonly --standalone -d $FRONTEND_DOMAIN --register-unsafely-without-email

# 申请后端域名证书
certbot certonly --standalone -d $BACKEND_DOMAIN --register-unsafely-without-email

# 复制证书到项目目录
cp /etc/letsencrypt/live/$FRONTEND_DOMAIN/fullchain.pem /opt/$PROJECT_NAME/nginx/ssl/$FRONTEND_DOMAIN/
cp /etc/letsencrypt/live/$FRONTEND_DOMAIN/privkey.pem /opt/$PROJECT_NAME/nginx/ssl/$FRONTEND_DOMAIN/
cp /etc/letsencrypt/live/$BACKEND_DOMAIN/fullchain.pem /opt/$PROJECT_NAME/nginx/ssl/$BACKEND_DOMAIN/
cp /etc/letsencrypt/live/$BACKEND_DOMAIN/privkey.pem /opt/$PROJECT_NAME/nginx/ssl/$BACKEND_DOMAIN/
```

---

## 第三步：创建 GitHub 仓库

### 3.1 创建仓库

在 GitHub 创建两个仓库：
- `blog-backend`（后端）
- `blog`（前端）

### 3.2 配置 Secrets

进入仓库 **Settings** → **Secrets and variables** → **Actions**，添加：

| Secret 名称 | 值 |
|------------|-----|
| `SERVER_HOST` | 你的服务器IP |
| `SERVER_USER` | `root` |
| `SERVER_PASSWORD` | 你的SSH密码 |

**前后端仓库都要配置！**

---

## 第四步：本地项目配置

### 4.1 后端项目结构

```
blog-backend/
├── app/                    # 业务代码
├── Dockerfile              # Docker 构建文件
├── requirements.txt        # Python 依赖
├── run.py                  # 启动脚本
├── sql/
│   ├── init_tables.sql     # 建表脚本
│   └── migrations/         # 迁移脚本目录
└── .github/
    └── workflows/
        └── deploy.yml      # CI/CD 配置
```

### 4.2 创建后端 Dockerfile

在项目根目录创建 `Dockerfile`：

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
COPY VERSION ./VERSION

EXPOSE 8000

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

### 4.3 创建后端 CI/CD 配置

创建 `.github/workflows/deploy.yml`：

```yaml
name: 后端自动部署

on:
  push:
    branches: [master]
  workflow_dispatch:

env:
  FORCE_JAVASCRIPT_ACTIONS_TO_NODE24: true

jobs:
  deploy:
    runs-on: ubuntu-latest

    steps:
      - name: 检出代码
        uses: actions/checkout@v4

      - name: 获取版本信息
        id: version
        run: |
          echo "commit_hash=$(git rev-parse --short HEAD)" >> $GITHUB_OUTPUT
          echo "commit_msg=$(git log -1 --pretty=%s)" >> $GITHUB_OUTPUT
          echo "deploy_time=$(date '+%Y-%m-%d %H:%M:%S')" >> $GITHUB_OUTPUT
          echo "deployer=$(git log -1 --pretty=%an)" >> $GITHUB_OUTPUT

      - name: 部署到服务器
        uses: appleboy/ssh-action@v1
        with:
          host: ${{ secrets.SERVER_HOST }}
          username: ${{ secrets.SERVER_USER }}
          password: ${{ secrets.SERVER_PASSWORD }}
          command_timeout: 10m
          script: |
            set -e
            PROJECT_NAME="blog"  # 改成你的项目名

            echo "🚀 开始部署..."
            cd /root/$PROJECT_NAME-backend && git pull origin master

            # 同步代码
            rsync -av --exclude='.git' --exclude='__pycache__' --exclude='.env' \
              /root/$PROJECT_NAME-backend/app/ /opt/$PROJECT_NAME/backend/app/
            cp /root/$PROJECT_NAME-backend/requirements.txt /opt/$PROJECT_NAME/backend/
            cp /root/$PROJECT_NAME-backend/Dockerfile /opt/$PROJECT_NAME/backend/

            # 写入版本信息
            echo "commit: ${{ steps.version.outputs.commit_hash }}" > /opt/$PROJECT_NAME/backend/VERSION
            echo "message: ${{ steps.version.outputs.commit_msg }}" >> /opt/$PROJECT_NAME/backend/VERSION
            echo "deploy_time: ${{ steps.version.outputs.deploy_time }}" >> /opt/$PROJECT_NAME/backend/VERSION
            echo "deployer: ${{ steps.version.outputs.deployer }}" >> /opt/$PROJECT_NAME/backend/VERSION

            # 构建并启动
            cd /opt/$PROJECT_NAME
            docker compose up -d --build backend

            sleep 15
            curl -s https://你的后端域名/health | grep -q "healthy" && echo "✅ 部署成功" || exit 1
```

### 4.4 创建 docker-compose.yml

在服务器 `/opt/项目名/` 目录创建 `docker-compose.yml`：

```yaml
services:
  mysql:
    image: mysql:8.0
    container_name: blog-mysql
    restart: always
    environment:
      MYSQL_ROOT_PASSWORD: ${MYSQL_ROOT_PASSWORD}
      MYSQL_DATABASE: blog
      MYSQL_USER: blog
      MYSQL_PASSWORD: ${MYSQL_PASSWORD}
    ports:
      - "3307:3306"  # 注意：多项目时端口不能冲突
    volumes:
      - mysql_data:/var/lib/mysql
      - ./init-sql:/docker-entrypoint-initdb.d
    command:
      --default-authentication-plugin=mysql_native_password
      --character-set-server=utf8mb4
      --collation-server=utf8mb4_unicode_ci
    networks:
      - blog-network
    healthcheck:
      test: ["CMD", "mysqladmin", "ping", "-h", "localhost"]
      interval: 10s
      timeout: 5s
      retries: 5

  backend:
    build:
      context: ./backend
      dockerfile: Dockerfile
    container_name: blog-backend
    restart: always
    depends_on:
      mysql:
        condition: service_healthy
    env_file:
      - ./backend/.env.prod
    ports:
      - "8001:8000"  # 注意：多项目时端口不能冲突
    networks:
      - blog-network

  nginx:
    image: nginx:alpine
    container_name: blog-nginx
    restart: always
    depends_on:
      - backend
    ports:
      - "8081:80"    # 注意：多项目时端口不能冲突，或共用一个 nginx
      - "8444:443"
    volumes:
      - ./nginx/nginx.conf:/etc/nginx/nginx.conf:ro
      - ./nginx/ssl:/etc/nginx/ssl:ro
      - ./frontend/dist:/usr/share/nginx/html/frontend:ro
    networks:
      - blog-network

volumes:
  mysql_data:

networks:
  blog-network:
    driver: bridge
```

### 4.5 创建 nginx.conf

创建 `/opt/项目名/nginx/nginx.conf`：

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
        server_name 你的后端域名;

        ssl_certificate /etc/nginx/ssl/你的后端域名/fullchain.pem;
        ssl_certificate_key /etc/nginx/ssl/你的后端域名/privkey.pem;
        ssl_protocols TLSv1.2 TLSv1.3;

        location / {
            proxy_pass http://backend:8000;
            proxy_set_header Host $host;
            proxy_set_header X-Real-IP $remote_addr;
            proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        }
    }

    # 前端
    server {
        listen 80;
        listen 443 ssl http2;
        server_name 你的前端域名;

        ssl_certificate /etc/nginx/ssl/你的前端域名/fullchain.pem;
        ssl_certificate_key /etc/nginx/ssl/你的前端域名/privkey.pem;
        ssl_protocols TLSv1.2 TLSv1.3;

        root /usr/share/nginx/html/frontend;
        index index.html;

        location / {
            try_files $uri $uri/ /index.html;
        }
    }
}
```

### 4.6 创建环境变量文件

创建 `/opt/项目名/.env`：

```env
MYSQL_ROOT_PASSWORD=你的root密码
MYSQL_PASSWORD=你的用户密码
```

创建 `/opt/项目名/backend/.env.prod`：

```env
DATABASE_URL=mysql+aiomysql://blog:你的密码@mysql:3306/blog
SECRET_KEY=你的JWT密钥
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=1440
APP_NAME=Blog API
APP_VERSION=1.0.0
DEBUG=false
CORS_ORIGINS=["https://你的前端域名","https://你的后端域名"]
```

---

## 第五步：前端项目配置

### 5.1 创建前端 CI/CD 配置

创建 `.github/workflows/deploy.yml`：

```yaml
name: 前端自动部署

on:
  push:
    branches: [master]
  workflow_dispatch:

env:
  FORCE_JAVASCRIPT_ACTIONS_TO_NODE24: true

jobs:
  deploy:
    runs-on: ubuntu-latest

    steps:
      - name: 检出代码
        uses: actions/checkout@v4

      - name: 获取版本信息
        id: version
        run: |
          echo "commit_hash=$(git rev-parse --short HEAD)" >> $GITHUB_OUTPUT
          echo "deploy_time=$(date '+%Y-%m-%d %H:%M:%S')" >> $GITHUB_OUTPUT

      - name: 安装 Node.js
        uses: actions/setup-node@v4
        with:
          node-version: 20

      - name: 安装依赖
        run: npm ci

      - name: 生成版本文件
        run: |
          mkdir -p public
          echo '{"commit":"${{ steps.version.outputs.commit_hash }}","deploy_time":"${{ steps.version.outputs.deploy_time }}"}' > public/version.json

      - name: 打包
        run: npm run build

      - name: 部署到服务器
        uses: appleboy/scp-action@v0.1.7
        with:
          host: ${{ secrets.SERVER_HOST }}
          username: ${{ secrets.SERVER_USER }}
          password: ${{ secrets.SERVER_PASSWORD }}
          source: "dist/*"
          target: "/opt/blog/frontend/dist"  # 改成你的项目路径
          strip_components: 1

      - name: 重启 Nginx
        uses: appleboy/ssh-action@v1
        with:
          host: ${{ secrets.SERVER_HOST }}
          username: ${{ secrets.SERVER_USER }}
          password: ${{ secrets.SERVER_PASSWORD }}
          script: |
            cd /opt/blog  # 改成你的项目路径
            docker compose restart nginx
            echo "✅ 前端部署完成"
```

### 5.2 修改前端 API 地址

修改 `.env.prod`：

```env
VITE_API_URL=https://你的后端域名
VITE_USE_MOCK=false
```

---

## 第六步：服务器克隆仓库

```bash
# SSH 到服务器
ssh root@你的服务器IP

# 克隆后端仓库
cd /root
git clone https://github.com/你的用户名/blog-backend.git

# 克隆前端仓库
git clone https://github.com/你的用户名/blog.git
```

---

## 第七步：首次部署

```bash
# 同步后端代码
rsync -av --exclude='.git' --exclude='__pycache__' /root/blog-backend/app/ /opt/blog/backend/app/
cp /root/blog-backend/requirements.txt /opt/blog/backend/
cp /root/blog-backend/Dockerfile /opt/blog/backend/
cp /root/blog-backend/sql/init_tables.sql /opt/blog/init-sql/ 2>/dev/null || true

# 启动服务
cd /opt/blog
docker compose up -d --build

# 初始化数据库
docker exec -it blog-backend python -m app.init_data
```

---

## 第八步：验证部署

| 检查项 | 地址 |
|-------|------|
| 前端 | https://你的前端域名 |
| 后端 API | https://你的后端域名 |
| 健康检查 | https://你的后端域名/health |
| 版本信息 | https://你的后端域名/version |

---

## 多项目端口规划

同一服务器部署多个项目时，注意端口冲突：

| 项目 | MySQL | 后端 | Nginx HTTP | Nginx HTTPS |
|------|-------|------|------------|-------------|
| howtoai | 3306 | 8000 | 80 | 443 |
| blog | 3307 | 8001 | 不需要 | 不需要 |
| shop | 3308 | 8002 | 不需要 | 不需要 |

**推荐方案**：所有项目共用一个 Nginx 容器（端口 80/443），通过域名区分不同项目。

---

## 常见问题

### Q: GitHub Actions SSH 连接失败
检查 Secrets 配置，确保没有多余空格。

### Q: Docker 构建很慢
确认 Dockerfile 使用了国内镜像源。

### Q: 数据库连接失败
检查 `.env.prod` 中的数据库连接字符串，容器内使用服务名 `mysql` 而不是 `localhost`。

### Q: 前端访问后端跨域
检查后端 `CORS_ORIGINS` 配置是否包含前端域名。

---

## 快速命令参考

```bash
# 查看容器状态
docker compose ps

# 查看日志
docker compose logs -f backend

# 重启服务
docker compose restart

# 更新部署
docker compose up -d --build

# 备份数据库
docker exec blog-mysql mysqldump -u root -p密码 blog > backup.sql
```

---

**文档版本：1.0**

**创建时间：2026-04-21**