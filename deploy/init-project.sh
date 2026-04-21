#!/bin/bash
# ============================================
# 通用项目初始化脚本
# 用法: ./init-project.sh <项目名称> <前端域名> <后端域名> <数据库密码>
# 示例: ./init-project.sh myapp app.example.com api.example.com MyPass123
# ============================================

set -e

# 检查参数
if [ "$#" -lt 4 ]; then
    echo "用法: $0 <项目名称> <前端域名> <后端域名> <数据库密码>"
    echo "示例: $0 myapp app.example.com api.example.com MyPass123"
    exit 1
fi

PROJECT_NAME=$1
FRONTEND_DOMAIN=$2
BACKEND_DOMAIN=$3
DB_PASSWORD=$4

# 生成强密钥
SECRET_KEY=$(openssl rand -hex 32)

echo "============================================"
echo "初始化项目: $PROJECT_NAME"
echo "前端域名: $FRONTEND_DOMAIN"
echo "后端域名: $BACKEND_DOMAIN"
echo "============================================"

# 创建项目目录
PROJECT_DIR="/opt/$PROJECT_NAME"
mkdir -p $PROJECT_DIR/backend
mkdir -p $PROJECT_DIR/frontend/dist
mkdir -p $PROJECT_DIR/nginx/ssl/$FRONTEND_DOMAIN
mkdir -p $PROJECT_DIR/nginx/ssl/$BACKEND_DOMAIN
mkdir -p $PROJECT_DIR/init-sql

echo "✓ 目录结构创建完成"

# 生成环境变量文件
cat > $PROJECT_DIR/.env << EOF
# MySQL配置
MYSQL_ROOT_PASSWORD=${DB_PASSWORD}Root
MYSQL_PASSWORD=${DB_PASSWORD}

# JWT密钥
SECRET_KEY=${SECRET_KEY}
EOF

echo "✓ 环境变量文件创建完成"

# 申请SSL证书
echo "申请SSL证书..."
certbot certonly --standalone -d $FRONTEND_DOMAIN --register-unsafely-without-email --non-interactive || echo "前端证书申请失败，请检查域名解析"
certbot certonly --standalone -d $BACKEND_DOMAIN --register-unsafely-without-email --non-interactive || echo "后端证书申请失败，请检查域名解析"

# 复制证书
if [ -f "/etc/letsencrypt/live/$FRONTEND_DOMAIN/fullchain.pem" ]; then
    cp /etc/letsencrypt/live/$FRONTEND_DOMAIN/fullchain.pem $PROJECT_DIR/nginx/ssl/$FRONTEND_DOMAIN/
    cp /etc/letsencrypt/live/$FRONTEND_DOMAIN/privkey.pem $PROJECT_DIR/nginx/ssl/$FRONTEND_DOMAIN/
    echo "✓ 前端SSL证书配置完成"
fi

if [ -f "/etc/letsencrypt/live/$BACKEND_DOMAIN/fullchain.pem" ]; then
    cp /etc/letsencrypt/live/$BACKEND_DOMAIN/fullchain.pem $PROJECT_DIR/nginx/ssl/$BACKEND_DOMAIN/
    cp /etc/letsencrypt/live/$BACKEND_DOMAIN/privkey.pem $PROJECT_DIR/nginx/ssl/$BACKEND_DOMAIN/
    echo "✓ 后端SSL证书配置完成"
fi

echo ""
echo "============================================"
echo "项目初始化完成！"
echo "============================================"
echo ""
echo "项目目录: $PROJECT_DIR"
echo ""
echo "下一步："
echo "1. 上传后端代码到 $PROJECT_DIR/backend/"
echo "2. 上传前端打包文件到 $PROJECT_DIR/frontend/dist/"
echo "3. 上传 docker-compose.yml 和 nginx.conf"
echo "4. 执行: cd $PROJECT_DIR && docker compose up -d --build"
echo ""
echo "数据库连接信息:"
echo "  主机: localhost (容器内使用服务名: mysql)"
echo "  数据库: ${PROJECT_NAME}"
echo "  用户: ${PROJECT_NAME}"
echo "  密码: ${DB_PASSWORD}"