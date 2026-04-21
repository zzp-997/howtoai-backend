# ============================================
# 新项目部署脚本生成器
# 用法: .\new-project.ps1 -Name "项目名" -Frontend "前端域名" -Backend "后端域名" -DbPass "数据库密码"
# ============================================

param(
    [Parameter(Mandatory=$true)]
    [string]$Name,              # 项目名称

    [Parameter(Mandatory=$true)]
    [string]$Frontend,          # 前端域名，如 app.example.com

    [Parameter(Mandatory=$true)]
    [string]$Backend,           # 后端域名，如 api.example.com

    [string]$DbPass = "ChangeMe123",  # 数据库密码

    [string]$BackendDir = "",   # 后端本地路径（可选）
    [string]$FrontendDir = ""   # 前端本地路径（可选）
)

$SERVER_IP = "118.25.182.15"
$SCRIPT_DIR = Split-Path -Parent $MyInvocation.MyCommand.Definition

# 如果没有指定本地路径，假设在同级目录
if ([string]::IsNullOrEmpty($BackendDir)) {
    $BackendDir = "D:\coderzzp\$Name-backend"
}
if ([string]::IsNullOrEmpty($FrontendDir)) {
    $FrontendDir = "D:\coderzzp\Name"
}

# 生成强密钥
$SECRET_KEY = -join ((48..57) + (65..90) + (97..122) | Get-Random -Count 32 | ForEach-Object {[char]$_})

Write-Host "============================================" -ForegroundColor Green
Write-Host "创建新项目部署配置" -ForegroundColor Green
Write-Host "============================================" -ForegroundColor Green
Write-Host "项目名称: $Name"
Write-Host "前端域名: $Frontend"
Write-Host "后端域名: $Backend"
Write-Host "服务器: $SERVER_IP"
Write-Host ""

# 创建项目部署目录
$PROJECT_DEPLOY_DIR = Join-Path $SCRIPT_DIR "..\$Name-deploy"
if (-not (Test-Path $PROJECT_DEPLOY_DIR)) {
    New-Item -ItemType Directory -Path $PROJECT_DEPLOY_DIR -Force | Out-Null
    New-Item -ItemType Directory -Path "$PROJECT_DEPLOY_DIR\backend" -Force | Out-Null
    New-Item -ItemType Directory -Path "$PROJECT_DEPLOY_DIR\nginx" -Force | Out-Null
    New-Item -ItemType Directory -Path "$PROJECT_DEPLOY_DIR\init-sql" -Force | Out-Null
}

# 生成 Dockerfile
$DOCKERFILE = @"
FROM python:3.11-slim

WORKDIR /app

RUN sed -i 's/deb.debian.org/mirrors.aliyun.com/g' /etc/apt/sources.list.d/debian.sources && \
    apt-get update && \
    apt-get install -y --no-install-recommends gcc && \
    rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt -i https://mirrors.aliyun.com/pypi/simple/ --trusted-host mirrors.aliyun.com

COPY app/ ./app/
COPY run.py .

EXPOSE 8000

CMD [`"uvicorn`", `"app.main:app`", `"--host`", `"0.0.0.0`", `"--port`", `"8000`"]
"@

$DOCKERFILE | Out-File -FilePath "$PROJECT_DEPLOY_DIR\backend\Dockerfile" -Encoding UTF8

# 生成 .env.prod
$ENV_PROD = @"
DATABASE_URL=mysql+aiomysql://${Name}:${DbPass}@mysql:3306/${Name}
SECRET_KEY=${SECRET_KEY}
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=1440
APP_NAME=${Name} API
APP_VERSION=1.0.0
DEBUG=false
CORS_ORIGINS=["https://${Frontend}","https://${Backend}","http://${Frontend}","http://${Backend}"]
"@

$ENV_PROD | Out-File -FilePath "$PROJECT_DEPLOY_DIR\backend\.env.prod" -Encoding UTF8

# 生成 .env
$DOTENV = @"
MYSQL_ROOT_PASSWORD=${DbPass}Root
MYSQL_PASSWORD=${DbPass}
SECRET_KEY=${SECRET_KEY}
CORS_ORIGINS=["https://${Frontend}","https://${Backend}"]
"@

$DOTENV | Out-File -FilePath "$PROJECT_DEPLOY_DIR\.env" -Encoding UTF8

# 生成 docker-compose.yml
$DOCKER_COMPOSE = @"
version: '3.8'

services:
  mysql:
    image: mysql:8.0
    container_name: ${Name}-mysql
    restart: always
    environment:
      MYSQL_ROOT_PASSWORD: `${MYSQL_ROOT_PASSWORD}
      MYSQL_DATABASE: ${Name}
      MYSQL_USER: ${Name}
      MYSQL_PASSWORD: `${MYSQL_PASSWORD}
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
      - ${Name}-network
    healthcheck:
      test: ["CMD", "mysqladmin", "ping", "-h", "localhost"]
      interval: 10s
      timeout: 5s
      retries: 5

  backend:
    build:
      context: ./backend
      dockerfile: Dockerfile
    container_name: ${Name}-backend
    restart: always
    depends_on:
      mysql:
        condition: service_healthy
    env_file:
      - ./backend/.env.prod
    environment:
      - DATABASE_URL=mysql+aiomysql://${Name}:`${MYSQL_PASSWORD}@mysql:3306/${Name}
    ports:
      - "8000:8000"
    networks:
      - ${Name}-network

  nginx:
    image: nginx:alpine
    container_name: ${Name}-nginx
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
      - ${Name}-network

volumes:
  mysql_data:

networks:
  ${Name}-network:
    driver: bridge
"@

$DOCKER_COMPOSE | Out-File -FilePath "$PROJECT_DEPLOY_DIR\docker-compose.yml" -Encoding UTF8

# 生成 nginx.conf
$NGINX_CONF = @"
user nginx;
worker_processes auto;

events {
    worker_connections 1024;
}

http {
    include       mime.types;
    default_type  application/octet-stream;

    log_format main '`$remote_addr - `$remote_user [`$time_local] "`$request" '
                     '`$status `$body_bytes_sent "`$http_referer" '
                     '"`$http_user_agent"';

    sendfile        on;
    keepalive_timeout 65;

    gzip on;
    gzip_types text/plain text/css application/json application/javascript;

    server {
        listen 80;
        listen 443 ssl http2;
        server_name ${Backend};

        ssl_certificate /etc/nginx/ssl/${Backend}/fullchain.pem;
        ssl_certificate_key /etc/nginx/ssl/${Backend}/privkey.pem;
        ssl_protocols TLSv1.2 TLSv1.3;

        location / {
            proxy_pass http://backend:8000;
            proxy_set_header Host `$host;
            proxy_set_header X-Real-IP `$remote_addr;
            proxy_set_header X-Forwarded-For `$proxy_add_x_forwarded_for;
        }
    }

    server {
        listen 80;
        listen 443 ssl http2;
        server_name ${Frontend};

        ssl_certificate /etc/nginx/ssl/${Frontend}/fullchain.pem;
        ssl_certificate_key /etc/nginx/ssl/${Frontend}/privkey.pem;
        ssl_protocols TLSv1.2 TLSv1.3;

        root /usr/share/nginx/html/frontend;
        index index.html;

        location / {
            try_files `$uri `$uri/ /index.html;
        }
    }
}
"@

$NGINX_CONF | Out-File -FilePath "$PROJECT_DEPLOY_DIR\nginx\nginx.conf" -Encoding UTF8

# 生成部署脚本
$DEPLOY_SCRIPT = @"
# ${Name} 项目一键部署脚本
param(
    [string]`$Target = "all"
)

`$SERVER_IP = "${SERVER_IP}"
`$SERVER_USER = "root"
`$REMOTE_DIR = "/opt/${Name}"
`$BACKEND_DIR = "${BackendDir}"
`$FRONTEND_DIR = "${FrontendDir}"

function Deploy-Backend {
    Write-Host "部署后端..." -ForegroundColor Green
    Set-Location `$BACKEND_DIR
    scp -r app/ `${SERVER_USER}@`${SERVER_IP}:`${REMOTE_DIR}/backend/
    scp run.py `${SERVER_USER}@`${SERVER_IP}:`${REMOTE_DIR}/backend/
    scp requirements.txt `${SERVER_USER}@`${SERVER_IP}:`${REMOTE_DIR}/backend/
    ssh `${SERVER_USER}@`${SERVER_IP} "cd `${REMOTE_DIR} && docker compose up -d --build backend"
    Write-Host "后端部署完成!" -ForegroundColor Green
}

function Deploy-Frontend {
    Write-Host "部署前端..." -ForegroundColor Green
    Set-Location `$FRONTEND_DIR
    npm run build
    scp -r dist/ `${SERVER_USER}@`${SERVER_IP}:`${REMOTE_DIR}/frontend/
    ssh `${SERVER_USER}@`${SERVER_IP} "cd `${REMOTE_DIR} && docker compose restart nginx"
    Write-Host "前端部署完成!" -ForegroundColor Green
}

switch (`$Target) {
    "backend"  { Deploy-Backend }
    "frontend" { Deploy-Frontend }
    "all"      { Deploy-Backend; Deploy-Frontend }
}

Write-Host ""
Write-Host "前端: https://${Frontend}" -ForegroundColor Cyan
Write-Host "后端: https://${Backend}" -ForegroundColor Cyan
"@

$DEPLOY_SCRIPT | Out-File -FilePath "$PROJECT_DEPLOY_DIR\deploy.ps1" -Encoding UTF8

Write-Host ""
Write-Host "============================================" -ForegroundColor Green
Write-Host "项目部署配置创建完成！" -ForegroundColor Green
Write-Host "============================================" -ForegroundColor Green
Write-Host ""
Write-Host "配置文件位置: $PROJECT_DEPLOY_DIR"
Write-Host ""
Write-Host "下一步操作：" -ForegroundColor Yellow
Write-Host "1. 将后端代码放入: ${BackendDir}"
Write-Host "2. 将前端代码放入: ${FrontendDir}"
Write-Host "3. 配置域名解析: $Frontend 和 $Backend -> $SERVER_IP"
Write-Host "4. 在服务器执行初始化（见下方）"
Write-Host "5. 上传配置: scp -r $PROJECT_DEPLOY_DIR/* root@${SERVER_IP}:/opt/${Name}/"
Write-Host "6. 启动服务: cd /opt/${Name} && docker compose up -d --build"
Write-Host ""
Write-Host "数据库信息：" -ForegroundColor Yellow
Write-Host "  数据库: $Name"
Write-Host "  用户: $Name"
Write-Host "  密码: $DbPass"
Write-Host ""