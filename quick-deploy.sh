#!/bin/bash

# Bangumi-PikPak 一键部署脚本
# 使用方法:
#   curl -fsSL https://raw.githubusercontent.com/lyndon0na/Bangumi-PikPak/main/quick-deploy.sh | bash
#   或 wget https://raw.githubusercontent.com/lyndon0na/Bangumi-PikPak/main/quick-deploy.sh && bash quick-deploy.sh
#   或 bash quick-deploy.sh [目录路径] [--interactive]

set -e

# 颜色输出
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

# 仓库地址
REPO_URL="https://github.com/lyndon0na/Bangumi-PikPak.git"
DEFAULT_DIR="$HOME/Bangumi-PikPak"

# 模式标志
INTERACTIVE_MODE=false

# 当前步骤
CURRENT_STEP=0
TOTAL_STEPS=8

print_header() {
    echo -e "${GREEN}========================================${NC}"
    echo -e "${GREEN}Bangumi-PikPak 一键部署脚本${NC}"
    echo -e "${GREEN}========================================${NC}"
    echo ""
}

print_step() {
    CURRENT_STEP=$((CURRENT_STEP + 1))
    echo -e "${BLUE}[${CURRENT_STEP}/${TOTAL_STEPS}]${NC} $1"
}

print_success() {
    echo -e "${GREEN}  ✓ $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}  ⚠ $1${NC}"
}

print_error() {
    echo -e "${RED}  ✗ $1${NC}"
}

print_info() {
    echo -e "  $1"
}

check_system_dependencies() {
    print_step "检查系统依赖"
    
    # 检查 Python
    if ! command -v python3 &> /dev/null; then
        print_error "未找到 python3"
        echo -e "${YELLOW}请安装 Python 3.10 或更高版本${NC}"
        exit 1
    fi
    
    PYTHON_VERSION=$(python3 --version | awk '{print $2}')
    PYTHON_MAJOR=$(echo "$PYTHON_VERSION" | cut -d. -f1)
    PYTHON_MINOR=$(echo "$PYTHON_VERSION" | cut -d. -f2)
    
    if [ "$PYTHON_MAJOR" -lt 3 ] || ([ "$PYTHON_MAJOR" -eq 3 ] && [ "$PYTHON_MINOR" -lt 10 ]); then
        print_error "Python 版本过低: $PYTHON_VERSION"
        echo -e "${YELLOW}需要 Python 3.10 或更高版本${NC}"
        exit 1
    fi
    
    print_success "Python $PYTHON_VERSION"
    
    # 检查 git
    if ! command -v git &> /dev/null; then
        print_error "未找到 git"
        echo -e "${YELLOW}请安装 git:${NC}"
        echo "  Ubuntu/Debian: sudo apt install git"
        echo "  CentOS/RHEL:   sudo yum install git"
        exit 1
    fi
    
    print_success "git"
    
    # 检查 systemd
    if ! command -v systemctl &> /dev/null; then
        print_warning "未找到 systemctl (将无法使用服务管理功能)"
    else
        print_success "systemd"
    fi
    
    echo ""
}

clone_project() {
    print_step "克隆项目"
    
    # 解析参数
    PROJECT_DIR="$DEFAULT_DIR"
    
    for arg in "$@"; do
        if [ "$arg" = "--interactive" ]; then
            INTERACTIVE_MODE=true
        elif [ ! "$arg" = "--interactive" ]; then
            PROJECT_DIR="$arg"
        fi
    done
    
    # 交互模式：询问用户
    if [ "$INTERACTIVE_MODE" = true ]; then
        read -p "项目安装目录 [默认: $DEFAULT_DIR]: " CUSTOM_DIR
        PROJECT_DIR="${CUSTOM_DIR:-$DEFAULT_DIR}"
    fi
    
    print_info "安装目录: $PROJECT_DIR"
    
    # 检查目录是否已存在
    if [ -d "$PROJECT_DIR" ]; then
        if [ -d "$PROJECT_DIR/.git" ]; then
            print_warning "目录已存在且是git仓库"
            read -p "是否更新现有项目？ [y/N]: " UPDATE_CHOICE
            if [[ $UPDATE_CHOICE =~ ^[Yy]$ ]]; then
                cd "$PROJECT_DIR"
                git pull origin main || git pull origin master
                print_success "项目已更新"
            else
                print_info "使用现有项目目录"
            fi
        else
            print_warning "目录已存在但不是git仓库"
            read -p "是否删除并重新克隆？ [y/N]: " DELETE_CHOICE
            if [[ $DELETE_CHOICE =~ ^[Yy]$ ]]; then
                rm -rf "$PROJECT_DIR"
                git clone "$REPO_URL" "$PROJECT_DIR"
                print_success "项目已克隆到: $PROJECT_DIR"
            else
                print_error "无法继续，目录冲突"
                exit 1
            fi
        fi
    else
        git clone "$REPO_URL" "$PROJECT_DIR"
        print_success "项目已克隆到: $PROJECT_DIR"
    fi
    
    cd "$PROJECT_DIR"
    echo ""
}

create_virtualenv() {
    print_step "创建虚拟环境"
    
    if [ -d "venv" ]; then
        print_warning "虚拟环境已存在"
        if [ "$INTERACTIVE_MODE" = true ]; then
            read -p "是否重新创建？ [y/N]: " RECREATE_CHOICE
            if [[ $RECREATE_CHOICE =~ ^[Yy]$ ]]; then
                rm -rf venv
                python3 -m venv venv
                print_success "虚拟环境已重新创建"
            else
                print_info "使用现有虚拟环境"
            fi
        else
            print_info "使用现有虚拟环境"
        fi
    else
        python3 -m venv venv
        print_success "虚拟环境已创建"
    fi
    
    source venv/bin/activate
    echo ""
}

install_dependencies() {
    print_step "安装依赖"
    
    print_info "正在安装 Python 包..."
    
    if pip install -q -r requirements.txt; then
        print_success "依赖安装完成"
    else
        print_error "依赖安装失败"
        echo -e "${YELLOW}尝试手动安装:${NC}"
        echo "  source venv/bin/activate"
        echo "  pip install -r requirements.txt"
        exit 1
    fi
    
    echo ""
}

check_existing_config() {
    if [ -f "config.json" ]; then
        print_warning "检测到已有配置文件"
        
        # 验证JSON格式
        if ! python3 -c "import json; json.load(open('config.json'))" 2>/dev/null; then
            print_error "配置文件JSON格式错误"
            read -p "是否删除损坏的配置文件？ [y/N]: " DELETE_CONFIG
            if [[ $DELETE_CONFIG =~ ^[Yy]$ ]]; then
                rm config.json
                return 1
            else
                print_error "无法继续，配置文件损坏"
                exit 1
            fi
        fi
        
        # 验证配置内容
        if ! python3 -c "
from config import load_config
try:
    load_config('config.json')
except Exception as e:
    print(f'ERROR: {e}')
    exit(1)
" 2>/dev/null; then
            print_warning "配置文件验证失败"
            ERROR_MSG=$(python3 -c "
from config import load_config
try:
    load_config('config.json')
except Exception as e:
    print(str(e))
" 2>&1)
            print_info "$ERROR_MSG"
            read -p "是否重新生成配置？ [y/N]: " REGEN_CONFIG
            if [[ $REGEN_CONFIG =~ ^[Yy]$ ]]; then
                rm config.json
                return 1
            else
                print_error "无法继续，配置验证失败"
                exit 1
            fi
        fi
        
        # 检查缺少的字段（旧版本升级）
        check_missing_config_fields
        
        print_success "配置验证通过"
        return 0
    fi
    
    return 1
}

check_missing_config_fields() {
    MISSING=0
    
    # Web配置
    if ! grep -q "web_enabled" config.json; then
        print_warning "缺少 Web 配置字段"
        MISSING=1
    fi
    
    # 健康检查配置
    if ! grep -q "enable_health_check" config.json; then
        print_warning "缺少健康检查配置字段"
        MISSING=1
    fi
    
    # 错误告警配置
    if ! grep -q "enable_error_alert" config.json; then
        print_warning "缺少错误告警配置字段"
        MISSING=1
    fi
    
    if [ $MISSING -eq 1 ]; then
        echo ""
        print_info "检测到旧版本配置，建议补充以下字段:"
        echo "  - web_enabled, web_port, web_password"
        echo "  - enable_health_check, health_check_interval"
        echo "  - enable_error_alert, error_alert_threshold"
        echo ""
        
        if [ "$INTERACTIVE_MODE" = true ]; then
            read -p "是否自动补充默认值？ [Y/n]: " AUTO_ADD
            if [[ ! $AUTO_ADD =~ ^[Nn]$ ]]; then
                python3 << 'PYEOF'
import json

with open('config.json', 'r') as f:
    config = json.load(f)

# Web配置
config.setdefault('web_enabled', False)
config.setdefault('web_host', '0.0.0.0')
config.setdefault('web_port', 8080)
config.setdefault('web_password', '')
config.setdefault('web_secret_key', '')

# 健康检查
config.setdefault('enable_health_check', False)
config.setdefault('health_check_interval', 3600)

# 错误告警
config.setdefault('enable_error_alert', False)
config.setdefault('error_alert_threshold', 3)

with open('config.json', 'w') as f:
    json.dump(config, f, indent=4, ensure_ascii=False)

print('✓ 配置已更新')
PYEOF
                print_success "配置字段已补充"
            fi
        else
            print_info "自动补充默认值..."
            python3 << 'PYEOF'
import json

with open('config.json', 'r') as f:
    config = json.load(f)

config.setdefault('web_enabled', False)
config.setdefault('web_host', '0.0.0.0')
config.setdefault('web_port', 8080)
config.setdefault('web_password', '')
config.setdefault('web_secret_key', '')

config.setdefault('enable_health_check', False)
config.setdefault('health_check_interval', 3600)

config.setdefault('enable_error_alert', False)
config.setdefault('error_alert_threshold', 3)

with open('config.json', 'w') as f:
    json.dump(config, f, indent=4, ensure_ascii=False)

print('✓ 配置已更新')
PYEOF
            print_success "配置字段已自动补充"
        fi
    fi
}

generate_config_template() {
    print_warning "未找到配置文件"
    
    cp example.config.json config.json
    print_success "已生成配置模板: config.json"
    echo ""
    
    echo -e "${YELLOW}========================================${NC}"
    echo -e "${YELLOW}请编辑 config.json 填写必需信息${NC}"
    echo -e "${YELLOW}========================================${NC}"
    echo ""
    echo "必需配置项:"
    echo "  1. username     - PikPak 邮箱"
    echo "  2. password     - PikPak 密码"
    echo "  3. path         - PikPak 目标文件夹ID"
    echo "  4. rss          - Mikan RSS 订阅链接"
    echo ""
    echo "可选配置项:"
    echo "  5. web_enabled      - 是否启用Web界面 (true/false)"
    echo "  6. web_port         - Web界面端口 (默认8080)"
    echo "  7. web_password     - Web访问密码"
    echo "  8. enable_proxy     - 是否启用代理 (true/false)"
    echo "  9. enable_notifications - 是否启用通知 (true/false)"
    echo ""
    echo -e "${BLUE}获取配置信息指南:${NC}"
    echo ""
    echo "PikPak 文件夹ID:"
    echo "  1. 登录 https://mypikpak.com/"
    echo "  2. 创建或选择目标文件夹"
    echo "  3. 从URL复制文件夹ID: https://mypikpak.com/drive/folder/[文件夹ID]"
    echo ""
    echo "Mikan RSS 链接:"
    echo "  1. 访问 https://mikanani.me"
    echo "  2. 订阅番剧"
    echo "  3. 在首页右下角复制 RSS 链接"
    echo ""
    
    if [ "$INTERACTIVE_MODE" = true ]; then
        # 询问编辑方式
        echo -e "${YELLOW}如何编辑配置文件？${NC}"
        echo "  1) 使用 nano 编辑器"
        echo "  2) 使用 vim 编辑器"
        echo "  3) 手动编辑（配置完成后继续）"
        echo ""
        read -p "选择编辑方式 [1-3]: " EDIT_CHOICE
        
        case $EDIT_CHOICE in
            1)
                nano config.json
                ;;
            2)
                vim config.json
                ;;
            3)
                echo ""
                echo -e "${YELLOW}请在其他终端编辑配置文件:${NC}"
                echo "  文件位置: $PROJECT_DIR/config.json"
                echo ""
                read -p "配置完成后按回车继续..." WAIT_INPUT
                ;;
        esac
    else
        echo -e "${YELLOW}非交互模式：请手动编辑配置文件${NC}"
        echo "  文件位置: $PROJECT_DIR/config.json"
        echo ""
        echo -e "${RED}⚠️ 配置文件未完成，服务将无法启动${NC}"
        echo -e "${YELLOW}配置完成后，请运行:${NC}"
        echo "  systemctl --user restart bangumi-pikpak"
        echo ""
    fi
    
    echo ""
}

validate_config() {
    print_step "验证配置文件"
    
    # 再次验证JSON格式
    if ! python3 -c "import json; json.load(open('config.json'))" 2>/dev/null; then
        print_error "配置文件JSON格式错误"
        exit 1
    fi
    
    print_success "JSON格式正确"
    
    # 验证配置内容
    VALIDATE_RESULT=$(python3 -c "
from config import load_config
try:
    load_config('config.json')
    print('OK')
except Exception as e:
    print(f'ERROR: {e}')
    exit(1)
" 2>&1)
    
    if [[ $VALIDATE_RESULT == "OK" ]]; then
        print_success "配置验证通过"
    else
        print_error "配置验证失败"
        echo "$VALIDATE_RESULT"
        exit 1
    fi
    
    echo ""
}

install_user_service() {
    print_step "安装用户级 systemd 服务"
    
    # 检查systemd
    if ! command -v systemctl &> /dev/null; then
        print_warning "未找到 systemctl，跳过服务安装"
        print_info "可以使用 'python main.py' 手动运行"
        return
    fi
    
    # 创建用户级服务目录
    USER_SYSTEMD_DIR="$HOME/.config/systemd/user"
    mkdir -p "$USER_SYSTEMD_DIR"
    
    print_success "服务目录已创建"
    
    # 生成服务文件
    SERVICE_FILE="$USER_SYSTEMD_DIR/bangumi-pikpak.service"
    
    cat > "$SERVICE_FILE" << EOF
[Unit]
Description=Bangumi-PikPak Auto Downloader Service (User)
Documentation=https://github.com/lyndon0na/Bangumi-PikPak
After=network.target network-online.target
Wants=network-online.target

[Service]
Type=simple
WorkingDirectory=$PROJECT_DIR

Environment="PYTHONUNBUFFERED=1"
Environment="LANG=en_US.UTF-8"
Environment="LC_ALL=en_US.UTF-8"

ExecStart=$PROJECT_DIR/venv/bin/python $PROJECT_DIR/main.py
ExecStop=/bin/kill -SIGTERM \$MAINPID

Restart=on-failure
RestartSec=10s

TimeoutStartSec=30s
TimeoutStopSec=30s

StandardOutput=journal
StandardError=journal
SyslogIdentifier=bangumi-pikpak

[Install]
WantedBy=default.target
EOF
    
    print_success "服务文件已生成: $SERVICE_FILE"
    
    # 重载 systemd
    systemctl --user daemon-reload
    print_success "systemd 配置已重载"
    
    # 启用服务
    systemctl --user enable bangumi-pikpak.service
    print_success "服务已启用开机自启"
    
    # 检查 linger
    if ! loginctl show-user "$USER" 2>/dev/null | grep -q "Linger=yes"; then
        print_warning "Linger 未启用"
        echo ""
        echo -e "${YELLOW}Linger 让服务在用户未登录时也能运行${NC}"
        
        if [ "$INTERACTIVE_MODE" = true ]; then
            echo -e "${YELLOW}需要运行一次:${NC}"
            echo "  sudo loginctl enable-linger $USER"
            echo ""
            read -p "是否现在启用？(需要sudo密码) [Y/n]: " ENABLE_LINGER
            
            if [[ ! $ENABLE_LINGER =~ ^[Nn]$ ]]; then
                sudo loginctl enable-linger "$USER"
                print_success "Linger 已启用"
            else
                print_warning "稍后请手动启用 linger"
            fi
        else
            echo -e "${YELLOW}自动模式：尝试启用 linger${NC}"
            if sudo -n loginctl enable-linger "$USER" 2>/dev/null; then
                print_success "Linger 已自动启用"
            else
                print_warning "无法自动启用（需要sudo密码）"
                echo -e "${YELLOW}请稍后手动运行:${NC}"
                echo "  sudo loginctl enable-linger $USER"
            fi
        fi
    else
        print_success "Linger 已启用"
    fi
    
    echo ""
}

start_service() {
    print_step "启动服务"
    
    if ! command -v systemctl &> /dev/null; then
        print_info "跳过自动启动"
        echo ""
        echo -e "${YELLOW}手动启动方式:${NC}"
        echo "  source venv/bin/activate"
        echo "  python main.py"
        return
    fi
    
    systemctl --user start bangumi-pikpak.service
    print_success "服务已启动"
    
    sleep 2
    
    # 检查服务状态
    SERVICE_STATUS=$(systemctl --user is-active bangumi-pikpak.service 2>&1)
    
    if [ "$SERVICE_STATUS" = "active" ]; then
        print_success "服务运行正常"
    else
        print_warning "服务状态: $SERVICE_STATUS"
        echo ""
        echo -e "${YELLOW}查看详细日志:${NC}"
        echo "  journalctl --user -u bangumi-pikpak -n 50"
    fi
    
    echo ""
}

print_completion() {
    echo ""
    echo -e "${GREEN}========================================${NC}"
    echo -e "${GREEN}🎉 部署成功！${NC}"
    echo -e "${GREEN}========================================${NC}"
    echo ""
    
    # 检查Web配置
    WEB_ENABLED=$(python3 -c "
import json
with open('config.json') as f:
    config = json.load(f)
print(config.get('web_enabled', False))
")
    
    if [ "$WEB_ENABLED" = "True" ]; then
        WEB_PORT=$(python3 -c "
import json
with open('config.json') as f:
    config = json.load(f)
print(config.get('web_port', 8080))
")
        
        echo -e "${BLUE}🖥️  Web 界面${NC}"
        echo "  本地访问: http://localhost:$WEB_PORT"
        echo "  远程访问: http://$(hostname -I | awk '{print $1}'):$WEB_PORT"
        echo ""
        echo -e "${YELLOW}请使用配置中的 web_password 登录${NC}"
        echo ""
    fi
    
    echo -e "${BLUE}📋 服务管理命令${NC}"
    echo "  启动服务:   systemctl --user start bangumi-pikpak"
    echo "  停止服务:   systemctl --user stop bangumi-pikpak"
    echo "  重启服务:   systemctl --user restart bangumi-pikpak"
    echo "  查看状态:   systemctl --user status bangumi-pikpak"
    echo "  查看日志:   journalctl --user -u bangumi-pikpak -f"
    echo ""
    
    echo -e "${BLUE}📖 文档${NC}"
    echo "  Web 使用指南: $PROJECT_DIR/docs/WEB_GUIDE.md"
    echo "  用户级部署:   $PROJECT_DIR/docs/USER_DEPLOYMENT.md"
    echo "  完整部署:     $PROJECT_DIR/docs/DEPLOYMENT.md"
    echo ""
    
    echo -e "${BLUE}🔧 其他操作${NC}"
    echo "  编辑配置:     nano $PROJECT_DIR/config.json"
    echo "  健康检查:     $PROJECT_DIR/deploy/health-check.sh"
    echo "  卸载服务:     $PROJECT_DIR/deploy/uninstall-service.sh"
    echo ""
    
    echo -e "${GREEN}========================================${NC}"
    echo -e "${GREEN}祝使用愉快！${NC}"
    echo -e "${GREEN}========================================${NC}"
}

main() {
    print_header
    
    # 步骤1: 检查系统依赖
    check_system_dependencies
    
    # 步骤2: 克隆项目
    clone_project "$1"
    
    # 步骤3: 创建虚拟环境
    create_virtualenv
    
    # 步骤4: 安装依赖
    install_dependencies
    
    # 步骤5: 配置文件处理
    print_step "配置文件处理"
    
    if ! check_existing_config; then
        generate_config_template
    fi
    
    # 步骤6: 验证配置
    validate_config
    
    # 步骤7: 安装服务
    install_user_service
    
    # 步骤8: 启动服务
    start_service
    
    # 显示完成信息
    print_completion
}

# 运行主函数
main "$@"