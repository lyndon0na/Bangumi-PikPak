# Bangumi-PikPak

<p align="center">
    <img title="mikan project" src="https://mikanani.me/images/mikan-pic.png" alt="" width="10%">
    <img title="pikpak" src="https://raw.githubusercontent.com/YinBuLiao/Bangumi-PikPak/main/img/pikpak.png">
</p>

***
## ✨ 新增功能

- 🌐 **代理支持**：支持 HTTP/HTTPS/SOCKS 代理
- 📱 **消息通知**：支持 ntfy.sh 实时推送通知
- ⚙️ **改进配置**：更好的配置文件管理
- 📊 **完善日志**：详细的日志记录系统
- 📚 **项目文档**：完整的安装和使用说明
- 🖥️ **Web 界面**：新增 Web 管理界面（密码保护）

---

## 🖥️ Web 界面

Bangumi-PikPak 现已支持 Web 管理界面，提供：

- **仪表盘监控**：查看运行状态、最近更新、番剧列表
- **日志查看**：实时查看和筛选运行日志
- **配置管理**：查看和修改配置（敏感信息脱敏）
- **服务控制**：启动/停止/重启服务（用户级部署）

**启用方式**：
```json
{
  "web_enabled": true,
  "web_port": 8080,
  "web_password": "your_secure_password"
}
```

**访问地址**：`http://your_vps_ip:8080`

**详细使用指南**：参见 [WEB_GUIDE.md](docs/WEB_GUIDE.md)

---

本项目是基于 [Mikan Project](https://mikanani.me)、[PikPak](https://mypikpak.com/) 的全自动追番整理下载工具。只需要在 [Mikan Project](https://mikanani.me) 上订阅番剧，就可以全自动追番。

## ✨ 功能特性

- 🚀 **简易配置**：单次配置就能持续使用
- 🔄 **自动更新**：无需介入的 RSS 解析器，自动解析番组信息
- 📁 **智能整理**：根据番剧更新时间自动分类整理
- 🤖 **完全自动化**：无需维护，完全无感使用
- 🌐 **代理支持**：支持 HTTP/HTTPS/SOCKS 代理
- 📱 **消息通知**：支持 ntfy.sh 推送，第一时间获知番剧更新
- 📊 **日志记录**：完整的操作日志，便于问题排查

## 🚀 快速开始

> **💡 提示**：项目支持在任意目录部署，所有路径自动适配。详见 [部署指南](docs/DEPLOYMENT.md)。

### 环境要求

- Python 3.10 或更高版本
- 有效的 PikPak 账号
- Mikan Project 的 RSS 订阅链接

### 🚀 一键部署（推荐）

**使用一键部署脚本快速安装**：

```bash
# 方式一：直接运行（推荐，自动模式）
curl -fsSL https://raw.githubusercontent.com/lyndon0na/Bangumi-PikPak/main/quick-deploy.sh | bash

# 方式二：下载后运行
wget https://raw.githubusercontent.com/lyndon0na/Bangumi-PikPak/main/quick-deploy.sh
bash quick-deploy.sh

# 方式三：自定义目录
bash quick-deploy.sh /your/custom/path

# 方式四：交互模式（会询问每个步骤）
bash quick-deploy.sh --interactive
```

**一键部署脚本功能**：
- ✅ 自动克隆项目（默认目录：~/Bangumi-PikPak）
- ✅ 创建虚拟环境并安装所有依赖
- ✅ 智能配置处理（检测已有配置、验证格式、自动升级旧配置）
- ✅ 安装用户级 systemd 服务（无需sudo权限）
- ✅ 启动服务并显示完整管理信息

**两种运行模式**：
- **自动模式**（默认）：快速部署，使用标准配置，非交互式
- **交互模式**（`--interactive`）：逐步询问，适合自定义需求

**部署完成后**：
- Web界面访问： `http://localhost:8080`
- 服务管理： `systemctl --user start/stop/restart bangumi-pikpak`
- 查看日志： `journalctl --user -u bangumi-pikpak -f`

**详细文档**： [用户级部署指南](docs/USER_DEPLOYMENT.md) | [一键部署详解](docs/QUICK_DEPLOY.md)

---

### 手动安装步骤

如果你需要自定义安装或了解详细步骤：

1. **克隆项目**
```bash
git clone https://github.com/lyndon0na/Bangumi-PikPak.git
cd Bangumi-PikPak
```

2. **安装依赖**
```bash
# 创建虚拟环境（推荐）
python3 -m venv venv
source venv/bin/activate

# 安装依赖
pip install -r requirements.txt
```

3. **配置设置**
```bash
# 复制示例配置文件
cp example.config.json config.json

# 编辑配置文件
# 填入你的 PikPak 账号信息和 RSS 链接
```

4. **运行程序**
```bash
python main.py
```

## ⚙️ 配置说明

### 配置文件格式

编辑 `config.json` 文件：

```json
{
    "username": "your_email@example.com",
    "password": "your_password",
    "path": "your_pikpak_folder_id",
    "rss": "https://mikanani.me/RSS/MyBangumi?token=your_token_here",
    
    "http_proxy": "http://127.0.0.1:7890",
    "https_proxy": "http://127.0.0.1:7890",
    "socks_proxy": "socks5://127.0.0.1:7890",
    "enable_proxy": false,
    
    "ntfy_url": "https://ntfy.sh/mytopic",
    "enable_notifications": true,
    
    "rss_check_interval": 600,
    "token_refresh_interval": 21600,
    "max_retries": 3,
    "request_timeout": 30,
    
    "log_level": "INFO",
    "log_max_bytes": 10485760,
    "log_backup_count": 5
}
```

### 配置项说明

| 配置项 | 说明 | 示例 |
|--------|------|------|
| `username` | PikPak 账号邮箱 | `user@example.com` |
| `password` | PikPak 账号密码 | `your_password` |
| `path` | PikPak 目标文件夹ID | `VOXXWeEex835fv5C2hV5LBe1o2` |
| `rss` | Mikan RSS 订阅链接 | `https://mikanani.me/RSS/MyBangumi?token=xxx` |
| `http_proxy` | HTTP 代理地址 | `http://127.0.0.1:7890` |
| `https_proxy` | HTTPS 代理地址 | `http://127.0.0.1:7890` |
| `socks_proxy` | SOCKS 代理地址 | `socks5://127.0.0.1:7890` |
| `enable_proxy` | 是否启用代理 | `true` 或 `false` |
| `ntfy_url` | ntfy.sh 通知地址 | `https://ntfy.sh/mytopic` |
| `enable_notifications` | 是否启用通知 | `true` 或 `false` |
| `rss_check_interval` | RSS 检查间隔（秒） | `600`（默认） |
| `token_refresh_interval` | Token 刷新间隔（秒） | `21600`（默认） |
| `max_retries` | 网络请求最大重试次数 | `3`（默认） |
| `request_timeout` | 网络请求超时时间（秒） | `30`（默认） |
| `log_level` | 日志级别 | `INFO`、`DEBUG`、`WARNING`、`ERROR` |
| `log_max_bytes` | 日志文件最大大小（字节） | `10485760`（10MB） |
| `log_backup_count` | 日志备份文件数量 | `5`（默认） |

### 获取配置信息

#### 文件夹ID
1. 登录 [PikPak](https://mypikpak.com/)
2. 创建或选择目标文件夹
3. 从URL中复制文件夹ID：`https://mypikpak.com/drive/folder/文件夹ID`

#### RSS链接
1. 在 [Mikan Project](https://mikanani.me) 订阅番剧
2. 在首页右下角复制 RSS 订阅链接
3. 格式：`https://mikanani.me/RSS/MyBangumi?token=xxx%3d%3d`

#### 通知设置
1. 访问 [ntfy.sh](https://ntfy.sh) 
2. 选择一个独特的主题名称，例如：`your-unique-topic-name`
3. 通知地址格式：`https://ntfy.sh/your-unique-topic-name`
4. 在手机上安装 [ntfy app](https://ntfy.sh/docs/subscribe/phone/) 并订阅该主题
5. 或者使用 Web 版：在浏览器中访问 `https://ntfy.sh/your-unique-topic-name`

**安全提示**：请选择独特且不易猜测的主题名称，避免他人接收到您的通知

## 📦 打包部署

> **📖 完整部署指南**：[docs/DEPLOYMENT.md](docs/DEPLOYMENT.md) - 包含详细步骤和常见问题
>
> **📖 用户级部署**：[docs/USER_DEPLOYMENT.md](docs/USER_DEPLOYMENT.md) - 无需 sudo 权限的部署方式（推荐）
>
> **📖 运维指南**：[docs/OPERATIONS.md](docs/OPERATIONS.md) - systemd 服务、监控、告警

### systemd 服务部署（推荐）

有两种部署方式：

#### 方式一：用户级服务（推荐）

**优势**：不需要 sudo 权限，Web 界面可直接控制服务

```bash
# 进入项目目录
cd Bangumi-PikPak

# 运行安装脚本（不需要 sudo）
./deploy/install-user-service.sh

# 启用 linger（让服务在后台运行）
sudo loginctl enable-linger $USER
```

**服务管理**：
```bash
systemctl --user start bangumi-pikpak     # 启动
systemctl --user stop bangumi-pikpak      # 停止
systemctl --user restart bangumi-pikpak   # 重启
systemctl --user status bangumi-pikpak    # 查看状态
journalctl --user -u bangumi-pikpak -f    # 查看日志
```

#### 方式二：系统级服务

**适用场景**：多用户共享、系统级权限管理

```bash
# 进入项目目录
cd Bangumi-PikPak

# 运行安装脚本（需要 sudo）
sudo ./deploy/install-service.sh
```

**服务管理**：
```bash
sudo systemctl start bangumi-pikpak     # 启动
sudo systemctl stop bangumi-pikpak      # 停止
sudo systemctl restart bangumi-pikpak   # 重启
sudo systemctl status bangumi-pikpak    # 查看状态
sudo journalctl -u bangumi-pikpak -f    # 查看日志

# 健康检查
./deploy/health-check.sh
```

**详细运维指南**：参见 [OPERATIONS.md](docs/OPERATIONS.md)

### 生成可执行文件

```bash
# 安装 PyInstaller
pip install pyinstaller

# 打包程序
pyinstaller --onefile --noconsole main.py
```

### 开机自启动

#### Windows
- 将生成的可执行文件放入启动文件夹
- 或创建任务计划程序

#### macOS
- 系统偏好设置 → 用户与群组 → 登录项 → 添加可执行文件

#### Linux
- 将可执行文件路径添加到 `~/.bashrc`
- 或创建 systemd 服务

详细的 Linux 系统服务部署方法请参考：[Linux 部署指南](Bangumi-PikPak%20Linux部署.md)

## 🔧 工作原理

### 更新检测流程
1. **RSS 解析**：定期检查 Mikan RSS 源
2. **番剧识别**：访问番剧页面提取标题信息
3. **文件夹管理**：自动创建番剧分类文件夹
4. **种子处理**：下载种子并上传到 PikPak
5. **消息通知**：实时推送番剧更新通知到您的设备
6. **重复检测**：智能避免重复内容

### 文件组织结构
```
PikPak 根目录/
├── 进击的巨人 最终季/
│   ├── 第1集.torrent
│   └── 第2集.torrent
├── 阿松 第四季/
│   ├── 第1集.torrent
│   └── 第2集.torrent
└── ...
```

## 📝 日志说明

程序运行时会生成详细的日志文件 `rss-pikpak.log`，包含：
- 配置加载状态
- 代理设置信息
- RSS 更新检测
- 文件操作记录
- 错误和警告信息

## 🤝 贡献指南

欢迎提交 Issue 和 Pull Request！

### 开发环境设置
```bash
# 克隆项目
[git clone https://github.com/lyndon0na/Bangumi-PikPak.git](https://github.com/lyndon0na/Bangumi-PikPak.git)
cd Bangumi-PikPak

# 创建虚拟环境
python -m venv venv
source venv/bin/activate  # Linux/macOS
# 或
venv\Scripts\activate  # Windows

# 安装开发依赖
pip install -r requirements.txt
```

### 代码结构

项目采用模块化设计，便于维护和扩展：

```
Bangumi-PikPak/
├── main.py           # 主程序入口
├── config.py         # 配置加载和验证
├── utils.py          # 工具函数（重试机制、日志等）
├── requirements.txt  # Python 依赖
└── config.json       # 配置文件（用户创建）
```

**核心改进**：
- ✅ 启动时配置验证，避免运行时错误
- ✅ 网络请求自动重试，提高稳定性
- ✅ 统一的异常处理和日志记录
- ✅ 敏感信息脱敏，保护隐私
- ✅ 灵活的配置项（检查间隔、重试次数等）

### 代码规范
- 使用 Python 3.10+ 语法
- 遵循 PEP 8 代码风格
- 添加适当的注释和文档字符串

## 🐛 常见问题

### Q: 提示"文件夹不存在"错误
A: 检查配置文件中的 `path` 值是否正确，确保文件夹ID有效

### Q: 代理连接失败
A: 确认代理地址和端口正确，检查代理服务是否正常运行

### Q: RSS 更新延迟
A: Mikan RSS 有一定延迟，请耐心等待，或调整检查间隔时间

### Q: 种子重复添加
A: 程序会自动检测重复内容，如果仍有问题，检查日志文件

### Q: 没有收到通知
A: 确认 `enable_notifications` 设置为 `true`，检查 `ntfy_url` 配置是否正确，`topic`取名要尽量独特一点，确保网络连接正常

### Q: 通知内容乱码
A: 程序已自动处理非ASCII字符，如仍有问题，请检查ntfy客户端设置

## 📄 许可证

本项目采用 MIT 许可证，详见 [LICENSE](LICENSE) 文件。

## 🙏 致谢

- [Mikan Project](https://mikanani.me) - 提供番剧 RSS 源
- [PikPak](https://mypikpak.com/) - 提供云存储服务
- [pikpakapi](https://github.com/Quan666/PikPakAPI) - PikPak API 封装
- [ntfy](https://github.com/binwiederhier/ntfy) - 简单易用的推送通知服务

---

如果这个项目对你有帮助，请给个 ⭐ Star 支持一下！
