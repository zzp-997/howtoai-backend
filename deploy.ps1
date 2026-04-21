# 极智协同 - 一键部署脚本 (PowerShell)
# 用法: 在项目根目录执行 .\deploy.ps1
# 支持参数: .\deploy.ps1 backend   (仅更新后端)
#           .\deploy.ps1 frontend  (仅更新前端)
#           .\deploy.ps1 all       (更新全部，默认)

param(
    [string]$Target = "all"
)

$SERVER_IP = "118.25.182.15"
$SERVER_USER = "root"
$REMOTE_DIR = "/opt/howtoai"
$BACKEND_DIR = "D:\coderzzp\howtoai-backend"
$FRONTEND_DIR = "D:\coderzzp\howtoai"

function Deploy-Backend {
    Write-Host "================================" -ForegroundColor Green
    Write-Host "部署后端..." -ForegroundColor Green
    Write-Host "================================" -ForegroundColor Green

    Set-Location $BACKEND_DIR

    # 上传后端代码
    scp -r app/ "${SERVER_USER}@${SERVER_IP}:${REMOTE_DIR}/backend/"
    scp run.py "${SERVER_USER}@${SERVER_IP}:${REMOTE_DIR}/backend/"
    scp requirements.txt "${SERVER_USER}@${SERVER_IP}:${REMOTE_DIR}/backend/"
    scp deploy/backend/Dockerfile "${SERVER_USER}@${SERVER_IP}:${REMOTE_DIR}/backend/"
    scp deploy/backend/.env.prod "${SERVER_USER}@${SERVER_IP}:${REMOTE_DIR}/backend/"

    # 重新构建并重启后端容器
    ssh "${SERVER_USER}@${SERVER_IP}" "cd ${REMOTE_DIR} && docker compose up -d --build backend"

    Write-Host "后端部署完成!" -ForegroundColor Green
}

function Deploy-Frontend {
    Write-Host "================================" -ForegroundColor Green
    Write-Host "部署前端..." -ForegroundColor Green
    Write-Host "================================" -ForegroundColor Green

    Set-Location $FRONTEND_DIR

    # 打包前端
    Write-Host "打包前端项目..." -ForegroundColor Yellow
    npm run build

    # 上传dist
    scp -r dist/ "${SERVER_USER}@${SERVER_IP}:${REMOTE_DIR}/frontend/"

    # 重启Nginx
    ssh "${SERVER_USER}@${SERVER_IP}" "cd ${REMOTE_DIR} && docker compose restart nginx"

    Write-Host "前端部署完成!" -ForegroundColor Green
}

function Deploy-Config {
    Write-Host "================================" -ForegroundColor Green
    Write-Host "部署配置文件..." -ForegroundColor Green
    Write-Host "================================" -ForegroundColor Green

    Set-Location $BACKEND_DIR

    scp deploy/docker-compose.yml "${SERVER_USER}@${SERVER_IP}:${REMOTE_DIR}/"
    scp deploy/.env "${SERVER_USER}@${SERVER_IP}:${REMOTE_DIR}/"
    scp deploy/nginx/nginx.conf "${SERVER_USER}@${SERVER_IP}:${REMOTE_DIR}/nginx/"

    Write-Host "配置文件更新完成!" -ForegroundColor Green
}

function Deploy-All {
    Deploy-Backend
    Deploy-Frontend
}

# 主逻辑
switch ($Target) {
    "backend"  { Deploy-Backend }
    "frontend" { Deploy-Frontend }
    "config"   { Deploy-Config }
    "all"      { Deploy-All }
    default    { Write-Host "未知参数: $Target (可选: backend, frontend, config, all)" -ForegroundColor Red }
}

Write-Host ""
Write-Host "部署完成! 访问地址:" -ForegroundColor Cyan
Write-Host "  前端: https://aixt.coderzzp.top" -ForegroundColor Cyan
Write-Host "  后端: https://admin.coderzzp.top" -ForegroundColor Cyan
