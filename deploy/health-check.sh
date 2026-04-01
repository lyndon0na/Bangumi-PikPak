#!/bin/bash

# Bangumi-PikPak 健康检查脚本
# 使用方法: ./health-check.sh

set -e

# 颜色输出
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

# 项目目录
PROJECT_DIR=$(cd "$(dirname "$0")/.." && pwd)
CONFIG_FILE="${PROJECT_DIR}/config.json"
LOG_FILE="${PROJECT_DIR}/rss-pikpak.log"
PID_FILE="${PROJECT_DIR}/bangumi-pikpak.pid"

echo -e "${GREEN}========================================${NC}"
echo -e "${GREEN}Bangumi-PikPak 健康检查${NC}"
echo -e "${GREEN}========================================${NC}"

# 检查结果
HEALTHY=true

# 1. 检查配置文件
echo -e "${YELLOW}[1] 检查配置文件...${NC}"
if [ -f "${CONFIG_FILE}" ]; then
    echo -e "${GREEN}  ✓ 配置文件存在: ${CONFIG_FILE}${NC}"
    
    # 检查配置是否有效
    if "${PROJECT_DIR}/venv/bin/python" -c "
from config import load_config
try:
    load_config('${CONFIG_FILE}')
    print('配置文件格式正确')
except Exception as e:
    print(f'配置文件错误: {e}')
    exit(1)
" 2>/dev/null; then
        echo -e "${GREEN}  ✓ 配置文件格式正确${NC}"
    else
        echo -e "${RED}  ✗ 配置文件格式错误${NC}"
        HEALTHY=false
    fi
else
    echo -e "${RED}  ✗ 配置文件不存在${NC}"
    HEALTHY=false
fi

# 2. 检查虚拟环境
echo -e "${YELLOW}[2] 检查虚拟环境...${NC}"
if [ -d "${PROJECT_DIR}/venv" ]; then
    echo -e "${GREEN}  ✓ 虚拟环境存在${NC}"
    
    # 检查依赖是否安装
    if "${PROJECT_DIR}/venv/bin/python" -c "
import feedparser, pikpakapi, httpx
print('依赖包已安装')
" 2>/dev/null; then
        echo -e "${GREEN}  ✓ 依赖包已安装${NC}"
    else
        echo -e "${RED}  ✗ 缺少依赖包${NC}"
        HEALTHY=false
    fi
else
    echo -e "${RED}  ✗ 虚拟环境不存在${NC}"
    HEALTHY=false
fi

# 3. 检查进程状态（systemd）
echo -e "${YELLOW}[3] 检查服务状态...${NC}"
if systemctl is-active --quiet bangumi-pikpak.service 2>/dev/null; then
    echo -e "${GREEN}  ✓ systemd 服务正在运行${NC}"
    
    # 显示服务详细信息
    systemctl status bangumi-pikpak.service --no-pager | head -n 10
else
    # 检查是否有手动运行的进程
    if pgrep -f "main.py" > /dev/null; then
        echo -e "${GREEN}  ✓ 进程正在运行（手动启动）${NC}"
        echo -e "${YELLOW}  提示: 建议使用 systemd 管理${NC}"
    else
        echo -e "${RED}  ✗ 服务未运行${NC}"
        HEALTHY=false
    fi
fi

# 4. 检查日志文件
echo -e "${YELLOW}[4] 检查日志文件...${NC}"
if [ -f "${LOG_FILE}" ]; then
    echo -e "${GREEN}  ✓ 日志文件存在: ${LOG_FILE}${NC}"
    
    # 检查最近的错误日志
    ERROR_COUNT=$(grep -c "ERROR" "${LOG_FILE}" 2>/dev/null || echo "0")
    echo -e "${YELLOW}  最近错误数: ${ERROR_COUNT}${NC}"
    
    if [ "${ERROR_COUNT}" -gt "10" ]; then
        echo -e "${RED}  ✗ 错误数量过多，建议检查${NC}"
        HEALTHY=false
    fi
    
    # 显示最后几行日志
    echo -e "${YELLOW}  最近日志:${NC}"
    tail -n 3 "${LOG_FILE}"
else
    echo -e "${YELLOW}  ⚠ 日志文件不存在（可能还未运行）${NC}"
fi

# 5. 检查网络连接（可选）
echo -e "${YELLOW}[5] 检查网络连接...${NC}"
if ping -c 1 mikanani.me > /dev/null 2>&1; then
    echo -e "${GREEN}  ✓ 可以连接到 mikanani.me${NC}"
else
    echo -e "${RED}  ✗ 无法连接到 mikanani.me${NC}"
    echo -e "${YELLOW}  提示: 请检查网络或代理配置${NC}"
    HEALTHY=false
fi

# 6. 检查磁盘空间
echo -e "${YELLOW}[6] 检查磁盘空间...${NC}"
AVAILABLE_SPACE=$(df "${PROJECT_DIR}" | awk 'NR==2 {print $4}')
if [ "${AVAILABLE_SPACE}" -gt "1048576" ]; then  # > 1GB
    echo -e "${GREEN}  ✓ 磁盘空间充足 (${AVAILABLE_SPACE} KB)${NC}"
else
    echo -e "${RED}  ✗ 磁盘空间不足 (${AVAILABLE_SPACE} KB)${NC}"
    HEALTHY=false
fi

# 总结
echo ""
echo -e "${GREEN}========================================${NC}"
if [ "$HEALTHY" = true ]; then
    echo -e "${GREEN}✓ 所有检查通过，系统健康${NC}"
    exit 0
else
    echo -e "${RED}✗ 发现问题，建议修复${NC}"
    echo -e "${YELLOW}建议操作:${NC}"
    echo "  1. 检查配置文件: cat ${CONFIG_FILE}"
    echo "  2. 安装依赖: source venv/bin/activate && pip install -r requirements.txt"
    echo "  3. 启动服务: sudo systemctl start bangumi-pikpak"
    echo "  4. 查看日志: sudo journalctl -u bangumi-pikpak -f"
    exit 1
fi