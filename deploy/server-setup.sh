#!/bin/bash
# ============================================
# 极智协同项目 - 一键部署脚本
# 服务器: Ubuntu 22.04 LTS
# IP: 118.25.182.15
# ============================================

set -e

echo "============================================"
echo "极智协同项目部署脚本"
echo "============================================"

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

# 检查是否为root用户
if [ "$EUID" -ne 0 ]; then
    echo -e "${RED}请使用root用户运行此脚本${NC}"
    exit 1
fi

# ============================================
# 第一步：系统更新和基础工具安装
# ============================================
echo -e "${YELLOW}[1/6] 更新系统并安装基础工具...${NC}"
apt update && apt upgrade -y
apt install -y curl wget git vim net-tools htop

# 设置时区
timedatectl set-timezone Asia/Shanghai
echo -e "${GREEN}时区设置完成: Asia/Shanghai${NC}"

# ============================================
# 第二步：安装Docker
# ============================================
echo -e "${YELLOW}[2/6] 安装Docker和Docker Compose...${NC}"

if ! command -v docker &> /dev/null; then
    echo "安装Docker..."
    curl -fsSL https://get.docker.com | bash -s docker --mirror Aliyun

    # 配置Docker镜像加速（国内）
    mkdir -p /etc/docker
    cat > /etc/docker/daemon.json <<EOF
{
    "registry-mirrors": [
        "https://docker.mirrors.ustc.edu.cn",
        "https://hub-mirror.c.163.com",
        "https://mirror.baidubce.com"
    ]
}
EOF

    systemctl daemon-reload
    systemctl start docker
    systemctl enable docker
    echo -e "${GREEN}Docker安装完成${NC}"
else
    echo -e "${GREEN}Docker已安装${NC}"
fi

# 安装Docker Compose插件
if ! docker compose version &> /dev/null; then
    apt install -y docker-compose-plugin
fi

echo -e "${GREEN}Docker版本: $(docker --version)${NC}"
echo -e "${GREEN}Docker Compose版本: $(docker compose version)${NC}"

# ============================================
# 第三步：创建项目目录
# ============================================
echo -e "${YELLOW}[3/6] 创建项目目录结构...${NC}"

PROJECT_DIR="/opt/howtoai"
mkdir -p $PROJECT_DIR
mkdir -p $PROJECT_DIR/backend
mkdir -p $PROJECT_DIR/frontend/dist
mkdir -p $PROJECT_DIR/nginx/ssl/admin.coderzzp.top
mkdir -p $PROJECT_DIR/nginx/ssl/aixt.coderzzp.top
mkdir -p $PROJECT_DIR/init-sql

echo -e "${GREEN}目录结构创建完成: $PROJECT_DIR${NC}"

# ============================================
# 第四步：安装Certbot申请SSL证书
# ============================================
echo -e "${YELLOW}[4/6] 安装Certbot并申请SSL证书...${NC}"

apt install -y certbot

echo -e "${YELLOW}请确认域名已解析到本服务器(118.25.182.15):${NC}"
echo "  - aixt.coderzzp.top"
echo "  - admin.coderzzp.top"
echo ""
read -p "域名解析是否完成？(y/n): " domain_ready

if [ "$domain_ready" = "y" ]; then
    echo "申请 aixt.coderzzp.top 证书..."
    certbot certonly --standalone -d aixt.coderzzp.top --non-interactive --agree-tos --email your-email@example.com

    echo "申请 admin.coderzzp.top 证书..."
    certbot certonly --standalone -d admin.coderzzp.top --non-interactive --agree-tos --email your-email@example.com

    # 复制证书到项目目录
    cp /etc/letsencrypt/live/aixt.coderzzp.top/fullchain.pem $PROJECT_DIR/nginx/ssl/aixt.coderzzp.top/
    cp /etc/letsencrypt/live/aixt.coderzzp.top/privkey.pem $PROJECT_DIR/nginx/ssl/aixt.coderzzp.top/
    cp /etc/letsencrypt/live/admin.coderzzp.top/fullchain.pem $PROJECT_DIR/nginx/ssl/admin.coderzzp.top/
    cp /etc/letsencrypt/live/admin.coderzzp.top/privkey.pem $PROJECT_DIR/nginx/ssl/admin.coderzzp.top/

    echo -e "${GREEN}SSL证书配置完成${NC}"

    # 设置证书自动续期
    systemctl enable certbot.timer
    systemctl start certbot.timer
else
    echo -e "${RED}请先完成域名解析后再申请SSL证书${NC}"
fi

# ============================================
# 第五步：配置防火墙
# ============================================
echo -e "${YELLOW}[5/6] 配置防火墙...${NC}"

if command -v ufw &> /dev/null; then
    ufw allow 22/tcp    # SSH
    ufw allow 80/tcp    # HTTP
    ufw allow 443/tcp   # HTTPS
    ufw allow 3306/tcp  # MySQL（可选，建议仅内网访问）
    ufw --force enable
    echo -e "${GREEN}防火墙配置完成${NC}"
    ufw status
fi

# ============================================
# 第六步：提示后续操作
# ============================================
echo -e "${YELLOW}[6/6] 后续操作提示...${NC}"

echo ""
echo -e "${GREEN}============================================${NC}"
echo -e "${GREEN}服务器基础配置完成！${NC}"
echo -e "${GREEN}============================================${NC}"
echo ""
echo "后续步骤："
echo ""
echo "1. 上传后端项目文件到服务器:"
echo "   scp -r backend/* root@118.25.182.15:$PROJECT_DIR/backend/"
echo ""
echo "2. 上传前端打包文件到服务器:"
echo "   scp -r dist/* root@118.25.182.15:$PROJECT_DIR/frontend/dist/"
echo ""
echo "3. 上传部署配置文件:"
echo "   scp docker-compose.yml root@118.25.182.15:$PROJECT_DIR/"
echo "   scp .env root@118.25.182.15:$PROJECT_DIR/"
echo "   scp nginx/nginx.conf root@118.25.182.15:$PROJECT_DIR/nginx/"
echo ""
echo "4. 启动服务:"
echo "   cd $PROJECT_DIR"
echo "   docker compose up -d"
echo ""
echo "5. 初始化数据库数据:"
echo "   docker exec -it howtoai-backend python -m app.init_data"
echo ""
echo -e "${GREEN}部署完成！${NC}"
echo ""
echo "访问地址:"
echo "  前端: https://aixt.coderzzp.top"
echo "  后端: https://admin.coderzzp.top"
echo "  健康检查: https://admin.coderzzp.top/health"