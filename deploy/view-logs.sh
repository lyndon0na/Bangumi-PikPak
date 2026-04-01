#!/bin/bash

# Bangumi-PikPak 日志查看脚本
# 使用方法: ./view-logs.sh [选项]

# 颜色输出
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

PROJECT_DIR=$(cd "$(dirname "$0")/.." && pwd)
LOG_FILE="${PROJECT_DIR}/rss-pikpak.log"

# 显示帮助
show_help() {
    echo -e "${GREEN}Bangumi-PikPak 日志查看工具${NC}"
    echo ""
    echo "使用方法: ./view-logs.sh [选项]"
    echo ""
    echo "选项:"
    echo "  -h, --help        显示帮助信息"
    echo "  -f, --follow      实时查看日志"
    echo "  -e, --errors      仅显示错误日志"
    echo "  -w, --warnings    仅显示警告和错误"
    echo "  -n NUM            显示最近 NUM 行日志"
    echo "  -s, --systemd     查看 systemd 日志"
    echo "  -c, --clear       清空日志文件"
    echo "  --stats           显示日志统计信息"
    echo ""
    echo "示例:"
    echo "  ./view-logs.sh -f         # 实时查看日志"
    echo "  ./view-logs.sh -e         # 仅显示错误"
    echo "  ./view-logs.sh -n 50      # 显示最近 50 行"
    echo "  ./view-logs.sh --stats    # 显示统计信息"
}

# 显示统计信息
show_stats() {
    if [ ! -f "${LOG_FILE}" ]; then
        echo -e "${RED}日志文件不存在${NC}"
        return
    fi
    
    echo -e "${GREEN}========================================${NC}"
    echo -e "${GREEN}日志统计信息${NC}"
    echo -e "${GREEN}========================================${NC}"
    
    TOTAL_LINES=$(wc -l < "${LOG_FILE}")
    ERROR_COUNT=$(grep -c "ERROR" "${LOG_FILE}" || echo "0")
    WARNING_COUNT=$(grep -c "WARNING" "${LOG_FILE}" || echo "0")
    INFO_COUNT=$(grep -c "INFO" "${LOG_FILE}" || echo "0")
    
    echo -e "${BLUE}总行数: ${TOTAL_LINES}${NC}"
    echo -e "${GREEN}INFO: ${INFO_COUNT}${NC}"
    echo -e "${YELLOW}WARNING: ${WARNING_COUNT}${NC}"
    echo -e "${RED}ERROR: ${ERROR_COUNT}${NC}"
    
    echo ""
    echo -e "${YELLOW}最近的错误:${NC}"
    grep "ERROR" "${LOG_FILE}" | tail -n 5
}

# 解析参数
MODE="normal"
LINES=20

while [[ $# -gt 0 ]]; do
    case $1 in
        -h|--help)
            show_help
            exit 0
            ;;
        -f|--follow)
            MODE="follow"
            shift
            ;;
        -e|--errors)
            MODE="errors"
            shift
            ;;
        -w|--warnings)
            MODE="warnings"
            shift
            ;;
        -n)
            LINES="$2"
            shift 2
            ;;
        -s|--systemd)
            MODE="systemd"
            shift
            ;;
        -c|--clear)
            MODE="clear"
            shift
            ;;
        --stats)
            show_stats
            exit 0
            ;;
        *)
            echo -e "${RED}未知选项: $1${NC}"
            show_help
            exit 1
            ;;
    esac
done

# 执行操作
case $MODE in
    normal)
        if [ -f "${LOG_FILE}" ]; then
            tail -n "${LINES}" "${LOG_FILE}"
        else
            echo -e "${RED}日志文件不存在${NC}"
        fi
        ;;
    follow)
        if [ -f "${LOG_FILE}" ]; then
            tail -f "${LOG_FILE}"
        else
            echo -e "${RED}日志文件不存在${NC}"
            echo -e "${YELLOW}提示: 服务可能还未运行${NC}"
        fi
        ;;
    errors)
        if [ -f "${LOG_FILE}" ]; then
            grep "ERROR" "${LOG_FILE}" | tail -n "${LINES}"
        else
            echo -e "${RED}日志文件不存在${NC}"
        fi
        ;;
    warnings)
        if [ -f "${LOG_FILE}" ]; then
            grep -E "WARNING|ERROR" "${LOG_FILE}" | tail -n "${LINES}"
        else
            echo -e "${RED}日志文件不存在${NC}"
        fi
        ;;
    systemd)
        echo -e "${YELLOW}查看 systemd 日志（最近 50 行）:${NC}"
        journalctl -u bangumi-pikpak -n 50 --no-pager
        ;;
    clear)
        if [ -f "${LOG_FILE}" ]; then
            echo -e "${YELLOW}清空日志文件...${NC}"
            > "${LOG_FILE}"
            echo -e "${GREEN}日志文件已清空${NC}"
        else
            echo -e "${YELLOW}日志文件不存在，无需清空${NC}"
        fi
        ;;
esac