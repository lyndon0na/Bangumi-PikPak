#!/bin/bash

# Bangumi-PikPak systemd 服务卸载脚本
# 使用方法: sudo ./uninstall-service.sh

set -e

# 颜色输出
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

echo -e "${GREEN}========================================${NC}"
echo -e "${GREEN}Bangumi-PikPak 服务卸载脚本${NC}"
echo -e "${GREEN}========================================${NC}"

# 检查是否以 root 运行
if [ "$EUID" -ne 0 ]; then
    echo -e "${RED}错误: 请使用 sudo 运行此脚本${NC}"
    exit 1
fi

SERVICE_NAME="bangumi-pikpak.service"
SERVICE_FILE="/etc/systemd/system/${SERVICE_NAME}"

# 检查服务是否存在
if [ ! -f "${SERVICE_FILE}" ]; then
    echo -e "${YELLOW}服务文件不存在，无需卸载${NC}"
    exit 0
fi

# 停止服务
echo -e "${YELLOW}停止服务...${NC}"
systemctl stop ${SERVICE_NAME} || true

# 禁用服务
echo -e "${YELLOW}禁用服务（移除开机自启）...${NC}"
systemctl disable ${SERVICE_NAME} || true

# 删除服务文件
echo -e "${YELLOW}删除服务文件...${NC}"
rm -f "${SERVICE_FILE}"

# 重载 systemd
echo -e "${YELLOW}重载 systemd 配置...${NC}"
systemctl daemon-reload

echo -e "${GREEN}========================================${NC}"
echo -e "${GREEN}卸载完成！${NC}"
echo -e "${GREEN}========================================${NC}"

echo ""
echo -e "${YELLOW}服务已完全移除${NC}"
echo -e "${YELLOW}如需重新安装，请运行:${NC}"
echo "  sudo ./deploy/install-service.sh"