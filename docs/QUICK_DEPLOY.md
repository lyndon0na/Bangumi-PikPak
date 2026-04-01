# 一键部署脚本使用指南

Bangumi-PikPak 提供一键部署脚本，快速完成完整部署流程。

## 🚀 快速使用

### 自动模式（推荐）

**最简单的方式**：

```bash
curl -fsSL https://raw.githubusercontent.com/lyndon0na/Bangumi-PikPak/main/quick-deploy.sh | bash
```

或使用 wget：

```bash
wget https://raw.githubusercontent.com/lyndon0na/Bangumi-PikPak/main/quick-deploy.sh
bash quick-deploy.sh
```

**特点**：
- 使用默认目录： `~/Bangumi-PikPak`
- 自动完成所有步骤
- 非交互式，适合自动化部署
- 需要手动编辑配置文件

### 自定义目录

```bash
bash quick-deploy.sh /path/to/custom/directory
```

### 交互模式

适合需要逐步自定义的场景：

```bash
bash quick-deploy.sh --interactive
```

**特点**：
- 询问每个步骤的选择
- 可选择编辑器编辑配置
- 更灵活的控制

## 📋 部署流程

脚本自动完成以下步骤：

### [1/8] 检查系统依赖
- Python 3.10+ 版本验证
- git 命令检查
- systemd 检查

### [2/8] 克隆项目
- 从 GitHub 克隆项目
- 默认目录： `~/Bangumi-PikPak`
- 支持自定义目录
- 检测已有项目并提示更新

### [3/8] 创建虚拟环境
- 创建 Python 虚拟环境
- 检测已有环境避免重复

### [4/8] 安装依赖
- 安装所有 Python 包
- 包含主程序和 Web 界面依赖

### [5/8] 配置文件处理
**智能检测**：
- 检测已有配置文件
- 验证 JSON 格式
- 验证配置内容
- 检测缺少的字段（旧版本升级）

**自动处理**：
- 旧版本配置自动补充新字段
- 损坏的配置文件提示重建
- 缺少配置时生成模板

### [6/8] 验证配置
- JSON 格式验证
- 必需字段完整性检查
- 字段值合法性验证

### [7/8] 安装用户级服务
- 创建 systemd 用户服务
- 配置开机自启
- 检测并启用 linger

### [8/8] 启动服务
- 启动 systemd 服务
- 检查运行状态
- 显示访问信息

## ⚙️ 配置说明

### 自动模式配置

自动模式下，脚本会：
1. 生成配置模板（如果不存在）
2. 显示必需配置项说明
3. 提示用户手动编辑
4. 不自动启动服务（配置未完成）

**配置完成后启动服务**：
```bash
systemctl --user restart bangumi-pikpak
```

### 交互模式配置

交互模式下，脚本会：
1. 询问编辑方式（nano/vim/手动）
2. 打开编辑器或等待用户
3. 配置完成后再继续

### 配置验证

脚本使用 Python 的 `config.load_config()` 进行深度验证，包括：
- JSON 格式正确性
- 必需字段存在性
- 字段值合法性（邮箱格式、URL格式等）

## 🔧 常见场景

### 新机器首次部署

```bash
# 下载并运行
curl -fsSL https://raw.githubusercontent.com/lyndon0na/Bangumi-PikPak/main/quick-deploy.sh | bash

# 编辑配置（自动模式）
nano ~/Bangumi-PikPak/config.json

# 启动服务
systemctl --user start bangumi-pikpak
```

### 更新现有项目

```bash
# 运行脚本，会检测已有项目
bash quick-deploy.sh ~/Bangumi-PikPak

# 选择更新项目（交互模式会询问）
# 或删除并重新克隆
```

### 升级旧版本配置

脚本会自动检测旧版本配置缺少的字段，并：
- **自动模式**：自动补充默认值
- **交互模式**：询问是否补充

### 自定义目录部署

```bash
bash quick-deploy.sh /opt/my-bangumi
```

## 📊 输出信息

部署完成后，脚本显示：

```
========================================
🎉 部署成功！
========================================

🖥️  Web 界面
  本地访问: http://localhost:8080
  远程访问: http://192.168.x.x:8080

📋 服务管理命令
  启动服务:   systemctl --user start bangumi-pikpak
  停止服务:   systemctl --user stop bangumi-pikpak
  重启服务:   systemctl --user restart bangumi-pikpak
  查看状态:   systemctl --user status bangumi-pikpak
  查看日志:   journalctl --user -u bangumi-pikpak -f

📖 文档
  Web 使用指南: ~/Bangumi-PikPak/docs/WEB_GUIDE.md
  用户级部署:   ~/Bangumi-PikPak/docs/USER_DEPLOYMENT.md
  完整部署:     ~/Bangumi-PikPak/docs/DEPLOYMENT.md
```

## ⚠️ 注意事项

### 自动模式限制

- 配置文件需要手动编辑
- 服务不会自动启动（等待配置完成）
- linger 启用需要 sudo 权限（无法自动完成时需手动）

### 必需配置项

部署前需要准备：
1. PikPak 邮箱和密码
2. PikPak 目标文件夹ID
3. Mikan RSS 订阅链接

### 网络要求

需要能够访问：
- GitHub (克隆项目)
- PyPI (下载 Python 包)
- mikanani.me (后续运行)
- mypikpak.com (后续运行)

## 🐛 故障排查

### 克隆失败

检查网络连接：
```bash
ping github.com
```

或使用国内镜像：
```bash
# 手动克隆
git clone https://github.com/lyndon0na/Bangumi-PikPak.git
cd Bangumi-PikPak
bash quick-deploy.sh .
```

### 依赖安装失败

手动安装：
```bash
cd ~/Bangumi-PikPak
source venv/bin/activate
pip install -r requirements.txt
```

### 配置验证失败

检查错误信息：
```bash
cd ~/Bangumi-PikPak
source venv/bin/activate
python -c "from config import load_config; load_config('config.json')"
```

### 服务无法启动

查看日志：
```bash
journalctl --user -u bangumi-pikpak -n 50
```

检查 linger：
```bash
loginctl show-user $USER | grep Linger
# 如果未启用
sudo loginctl enable-linger $USER
```

## 🔄 重新部署

脚本支持重复运行：

```bash
# 重新运行（会检测已有安装）
bash quick-deploy.sh

# 强制重新创建虚拟环境（交互模式）
bash quick-deploy.sh --interactive
```

## 📚 相关文档

- [用户级部署指南](USER_DEPLOYMENT.md) - 详细部署说明
- [Web 界面指南](WEB_GUIDE.md) - Web 功能使用
- [完整部署文档](DEPLOYMENT.md) - 手动部署步骤
- [运维指南](OPERATIONS.md) - 服务管理