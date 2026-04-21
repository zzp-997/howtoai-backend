# 极智协同项目部署指南

## 项目信息

| 项目 | 值 |
|------|-----|
| 服务器 IP | `118.25.182.15` |
| 前端域名 | `aixt.coderzzp.com` |
| 后端域名 | `admin.coderzzp.com` |
| 操作系统 | Ubuntu 22.04 LTS（推荐） |
| 部署方式 | Docker Compose 容器化 |

## 部署架构

```
用户访问流程：
┌─────────────────────────────────────────────────────────────┐
│                                                             │
│  https://aixt.coderzzp.com (前端)                           │
│         │                                                   │
│         │ API请求                                           │
│         ▼                                                   │
│  https://admin.coderzzp.com (后端API)                       │
│         │                                                   │
│         ▼                                                   │
│  FastAPI (容器:8000) → MySQL (容器:3306)                    │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

---

## 第一步：域名解析配置

在域名服务商后台配置以下 A 记录：

| 域名 | 类型 | 记录值 |
|------|------|--------|
| aixt.coderzzp.com | A | 118.25.182.15 |
| admin.coderzzp.com | A | 118.25.182.15 |

**验证解析是否生效**：
```bash
# 在本地执行
ping aixt.coderzzp.com
ping admin.coderzzp.com
```

---

## 第二步：SSH 连接服务器

```bash
ssh root@118.25.182.15
# 输入密码登录
```

---

## 第三步：执行一键部署脚本

将 `server-setup.sh` 上传到服务器并执行：

```bash
# 本地上传脚本
scp deploy/server-setup.sh root@118.25.182.15:/root/

# 服务器执行
ssh root@118.25.182.15
chmod +x /root/server-setup.sh
./server-setup.sh
```

脚本会自动完成：
1. 系统更新和基础工具安装
2. Docker 和 Docker Compose 安装
3. 项目目录结构创建
4. Certbot 安装和 SSL 证书申请
5. 防火墙配置

---

## 第四步：上传项目文件到服务器

### 4.1 上传后端项目

```bash
# 在本地项目目录执行
cd D:\coderzzp\howtoai-backend

# 上传后端代码（排除不必要的文件）
scp -r app/ root@118.25.182.15:/opt/howtoai/backend/
scp run.py root@118.25.182.15:/opt/howtoai/backend/
scp requirements.txt root@118.25.182.15:/opt/howtoai/backend/

# 上传部署配置
scp deploy/backend/Dockerfile root@118.25.182.15:/opt/howtoai/backend/
scp deploy/backend/.env.prod root@118.25.182.15:/opt/howtoai/backend/
scp deploy/docker-compose.yml root@118.25.182.15:/opt/howtoai/
scp deploy/.env root@118.25.182.15:/opt/howtoai/
scp deploy/nginx/nginx.conf root@118.25.182.15:/opt/howtoai/nginx/

# 上传SQL初始化脚本
scp deploy/init-sql/init_tables.sql root@118.25.182.15:/opt/howtoai/init-sql/
```

### 4.2 上传前端打包文件

```bash
# 先在本地打包前端
cd D:\coderzzp\howtoai
npm run build

# 上传dist目录
scp -r dist/* root@118.25.182.15:/opt/howtoai/frontend/dist/
```

---

## 第五步：启动服务

```bash
# SSH登录服务器
ssh root@118.25.182.15

# 进入项目目录
cd /opt/howtoai

# 启动所有服务
docker compose up -d

# 查看服务状态
docker compose ps

# 查看日志
docker compose logs -f
```

---

## 第六步：初始化数据库

```bash
# 进入后端容器
docker exec -it howtoai-backend bash

# 执行初始化脚本
python -m app.init_data

# 退出容器
exit
```

---

## 第七步：验证部署

访问以下地址验证：

| 地址 | 说明 |
|------|------|
| https://aixt.coderzzp.com | 前端页面 |
| https://admin.coderzzp.com | 后端 API 根路径 |
| https://admin.coderzzp.com/health | 健康检查 |

---

## 常用运维命令

```bash
# 查看所有服务状态
docker compose ps

# 重启所有服务
docker compose restart

# 重启单个服务
docker compose restart backend
docker compose restart nginx

# 查看服务日志
docker compose logs -f backend
docker compose logs -f nginx
docker compose logs -f mysql

# 更新部署（重新构建）
docker compose down
docker compose up -d --build

# 备份数据库
docker exec howtoai-mysql mysqldump -u root -pHowtoaiRoot2024Secure howtoai > backup_$(date +%Y%m%d).sql

# 恢复数据库
docker exec -i howtoai-mysql mysql -u root -pHowtoaiRoot2024Secure howtoai < backup_20240420.sql
```

---

## 安全建议

1. **修改默认密码**：生产环境请修改 `.env` 中的数据库密码和 JWT 密钥
2. **关闭 MySQL 外部端口**：如不需要外部访问，可在 docker-compose.yml 中移除 MySQL 的 3306 端口映射
3. **定期备份**：设置定时任务每天备份数据库
4. **SSL 证书续期**：Certbot 会自动续期，可执行 `certbot renew --dry-run` 测试

---

## 文件清单

部署所需的所有文件都在 `deploy/` 目录下：

```
deploy/
├── backend/
│   ├── Dockerfile           # 后端容器构建文件
│   └── .env.prod            # 后端环境变量
├── nginx/
│   └── nginx.conf           # Nginx 配置文件
├── init-sql/
│   └── init_tables.sql      # 数据库初始化SQL
├── docker-compose.yml       # Docker Compose 配置
├── .env                     # Docker Compose 环境变量
├── server-setup.sh          # 服务器一键部署脚本
└── README.md                # 本文档
```