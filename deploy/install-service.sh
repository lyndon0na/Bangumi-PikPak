#!/bin/bash

# Bangumi-PikPak systemd 服务安装脚本
# 使用方法: sudo ./install-service.sh

set -e

# 颜色输出
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${GREEN}========================================${NC}"
echo -e "${GREEN}Bangumi-PikPak 服务安装脚本${NC}"
echo -e "${GREEN}========================================${NC}"

# 检查是否以 root 运行
if [ "$EUID" -ne 0 ]; then
    echo -e "${RED}错误: 请使用 sudo 运行此脚本${NC}"
    exit 1
fi

# 获取当前用户和项目目录
CURRENT_USER=$(whoami)
PROJECT_DIR=$(cd "$(dirname "$0")/.." && pwd)

echo -e "${YELLOW}项目目录: ${PROJECT_DIR}${NC}"
echo -e "${YELLOW}当前用户: ${CURRENT_USER}${NC}"

# 检查配置文件是否存在
if [ ! -f "${PROJECT_DIR}/config.json" ]; then
    echo -e "${RED}错误: 配置文件不存在${NC}"
    echo -e "${YELLOW}请先创建配置文件:${NC}"
    echo -e "  cp ${PROJECT_DIR}/example.config.json ${PROJECT_DIR}/config.json"
    echo -e "  # 编辑 config.json 填入你的信息"
    exit 1
fi

# 检查虚拟环境是否存在
if [ ! -d "${PROJECT_DIR}/venv" ]; then
    echo -e "${YELLOW}警告: 虚拟环境不存在，正在创建...${NC}"
    cd "${PROJECT_DIR}"
    python3 -m venv venv
    source venv/bin/activate
    pip install -r requirements.txt
    deactivate
fi

# 创建服务文件（替换用户和路径）
SERVICE_FILE="/etc/systemd/system/bangumi-pikpak.service"
echo -e "${YELLOW}创建服务文件: ${SERVICE_FILE}${NC}"

cat > "${SERVICE_FILE}" <<EOF
[Unit]
Description=Bangumi-PikPak Auto Downloader Service
Documentation=https://github.com/lyndon0na/Bangumi-PikPak
After=network.target network-online.target
Wants=network-online.target

[Service]
Type=simple
User=${CURRENT_USER}
Group=${CURRENT_USER}
WorkingDirectory=${PROJECT_DIR}

# 环境变量
Environment="PYTHONUNBUFFERED=1"
Environment="LANG=en_US.UTF-8"
Environment="LC_ALL=en_US.UTF-8"

# 启动命令
ExecStart=${PROJECT_DIR}/venv/bin/python ${PROJECT_DIR}/main.py

# 停止命令
ExecStop=/bin/kill -SIGTERM \$MAINPID

# 重启策略
Restart=on-failure
RestartSec=10s

# 超时设置
TimeoutStartSec=30s
TimeoutStopSec=30s

# 日志配置
StandardOutput=journal
StandardError=journal
SyslogIdentifier=bangumi-pikpak

# 资源限制
LimitNOFILE=65536
MemoryMax=512M

# 安全加固
NoNewPrivileges=yes
PrivateTmp=yes

[Install]
WantedBy=multi-user.target
EOF

# 重载 systemd
echo -e "${YELLOW}重载 systemd 配置...${NC}"
systemctl daemon-reload

# 启用服务（开机自启）
echo -e "${YELLOW}启用服务（开机自启）...${NC}"
systemctl enable bangumi-pikpak.service

echo -e "${GREEN}========================================${NC}"
echo -e "${GREEN}安装完成！${NC}"
echo -e "${GREEN}========================================${NC}"

echo ""
echo -e "${YELLOW}使用方法:${NC}"
echo "  启动服务:   sudo systemctl start bangumi-pikpak"
echo "  停止服务:   sudo systemctl stop bangumi-pikpak"
echo "  重启服务:   sudo systemctl restart bangumi-pikpak"
echo "  查看状态:   sudo systemctl status bangumi-pikpak"
echo "  查看日志:   sudo journalctl -u bangumi-pikpak -f"
echo ""
echo -e "${YELLOW}是否立即启动服务？ (y/n)${NC}"
read -r answer

if [ "$answer" = "y" ] || [ "$answer" = "Y" ]; then
    echo -e "${YELLOW}启动服务...${NC}"
    systemctl start bangumi-pikpak.service
    
    sleep 2
    
    echo -e "${YELLOW}查看服务状态...${NC}"
    systemctl status bangumi-pikpak.service --no-pager
    
    echo ""
    echo -e "${GREEN}服务已启动！${NC}"
    echo -e "${YELLOW}使用以下命令查看实时日志:${NC}"
    echo "  sudo journalctl -u bangumi-pikpak -f"
fi

echo ""
echo -e "${GREEN}安装脚本完成！${NC}"