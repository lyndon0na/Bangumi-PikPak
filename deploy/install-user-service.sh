#!/bin/bash

# Bangumi-PikPak 用户级 systemd 服务安装脚本
# 使用方法: ./install-user-service.sh (不需要 sudo)

set -e

# 颜色输出
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

echo -e "${GREEN}========================================${NC}"
echo -e "${GREEN}Bangumi-PikPak 用户级服务安装脚本${NC}"
echo -e "${GREEN}========================================${NC}"

# 获取项目目录
PROJECT_DIR=$(cd "$(dirname "$0")/.." && pwd)
CURRENT_USER=$(whoami)

echo -e "${YELLOW}项目目录: ${PROJECT_DIR}${NC}"
echo -e "${YELLOW}当前用户: ${CURRENT_USER}${NC}"

# 检查配置文件
if [ ! -f "${PROJECT_DIR}/config.json" ]; then
    echo -e "${RED}错误: 配置文件不存在${NC}"
    echo -e "${YELLOW}请先创建配置文件:${NC}"
    echo "  cp ${PROJECT_DIR}/example.config.json ${PROJECT_DIR}/config.json"
    echo "  # 编辑 config.json 填入你的信息"
    exit 1
fi

# 创建用户级 systemd 目录
USER_SYSTEMD_DIR="${HOME}/.config/systemd/user"
mkdir -p "${USER_SYSTEMD_DIR}"

echo -e "${YELLOW}创建用户级服务目录: ${USER_SYSTEMD_DIR}${NC}"

# 创建服务文件
SERVICE_FILE="${USER_SYSTEMD_DIR}/bangumi-pikpak.service"
echo -e "${YELLOW}创建服务文件: ${SERVICE_FILE}${NC}"

cat > "${SERVICE_FILE}" <<EOF
[Unit]
Description=Bangumi-PikPak Auto Downloader Service (User)
Documentation=https://github.com/lyndon0na/Bangumi-PikPak
After=network.target network-online.target
Wants=network-online.target

[Service]
Type=simple
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

[Install]
WantedBy=default.target
EOF

# 检查虚拟环境
if [ ! -d "${PROJECT_DIR}/venv" ]; then
    echo -e "${YELLOW}警告: 虚拟环境不存在，正在创建...${NC}"
    cd "${PROJECT_DIR}"
    python3 -m venv venv
    source venv/bin/activate
    pip install -r requirements.txt
    deactivate
fi

# 启用 linger (让服务在用户未登录时也能运行)
echo -e "${YELLOW}检查并启用 linger...${NC}"
if ! loginctl show-user "${CURRENT_USER}" | grep -q "Linger=yes"; then
    echo -e "${YELLOW}需要启用 linger 以让服务在后台运行${NC}"
    echo -e "${YELLOW}请运行: sudo loginctl enable-linger ${CURRENT_USER}${NC}"
    echo ""
    echo -e "${YELLOW}是否现在启用？ (需要输入 sudo 密码) (y/n)${NC}"
    read -r answer
    
    if [ "$answer" = "y" ] || [ "$answer" = "Y" ]; then
        sudo loginctl enable-linger "${CURRENT_USER}"
        echo -e "${GREEN}Linger 已启用${NC}"
    else
        echo -e "${YELLOW}稍后请手动运行: sudo loginctl enable-linger ${CURRENT_USER}${NC}"
    fi
fi

# 重载 systemd 用户配置
echo -e "${YELLOW}重载 systemd 用户配置...${NC}"
systemctl --user daemon-reload

# 启用服务（开机自启）
echo -e "${YELLOW}启用服务（开机自启）...${NC}"
systemctl --user enable bangumi-pikpak.service

echo -e "${GREEN}========================================${NC}"
echo -e "${GREEN}安装完成！${NC}"
echo -e "${GREEN}========================================${NC}"

echo ""
echo -e "${YELLOW}使用方法:${NC}"
echo "  启动服务:   systemctl --user start bangumi-pikpak"
echo "  停止服务:   systemctl --user stop bangumi-pikpak"
echo "  重启服务:   systemctl --user restart bangumi-pikpak"
echo "  查看状态:   systemctl --user status bangumi-pikpak"
echo "  查看日志:   journalctl --user -u bangumi-pikpak -f"
echo ""
echo -e "${YELLOW}重要提示:${NC}"
echo "  - 服务运行在用户级别，不需要 sudo 权限"
echo "  - 已配置开机自启（需要 linger 已启用）"
echo "  - Web 界面可直接控制服务（无需 sudo）"
echo ""
echo -e "${YELLOW}是否立即启动服务？ (y/n)${NC}"
read -r answer

if [ "$answer" = "y" ] || [ "$answer" = "Y" ]; then
    echo -e "${YELLOW}启动服务...${NC}"
    systemctl --user start bangumi-pikpak.service
    
    sleep 2
    
    echo -e "${YELLOW}查看服务状态...${NC}"
    systemctl --user status bangumi-pikpak.service --no-pager
    
    echo ""
    echo -e "${GREEN}服务已启动！${NC}"
    echo -e "${YELLOW}使用以下命令查看实时日志:${NC}"
    echo "  journalctl --user -u bangumi-pikpak -f"
    
    if grep -q "web_enabled.*true" "${PROJECT_DIR}/config.json"; then
        WEB_PORT=$(grep "web_port" "${PROJECT_DIR}/config.json" | sed 's/.*: *//' | sed 's/,.*//')
        echo ""
        echo -e "${GREEN}Web 界面已启用！${NC}"
        echo -e "${YELLOW}访问地址: http://localhost:${WEB_PORT}${NC}"
    fi
fi

echo ""
echo -e "${GREEN}安装脚本完成！${NC}"