# Bangumi-PikPak 快速部署指南

本指南帮助你在新机器上快速部署 Bangumi-PikPak。

---

## 📋 部署前准备

### 系统要求

- **操作系统**：Linux（推荐 Ubuntu 20.04+、Debian 10+、CentOS 7+）
- **Python**：Python 3.10 或更高版本
- **网络**：能够访问 mikanani.me 和 mypikpak.com

### 必需账号

- **PikPak 账号**：有效的邮箱和密码
- **Mikan Project RSS**：订阅番剧后的 RSS 链接

---

## 🚀 快速部署步骤

### 1. 克隆项目

```bash
# 克隆到任意目录
git clone https://github.com/YinBuLiao/Bangumi-PikPak.git
cd Bangumi-PikPak
```

### 2. 创建虚拟环境

```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### 3. 配置文件

```bash
# 复制示例配置
cp example.config.json config.json

# 编辑配置文件
nano config.json  # 或使用你喜欢的编辑器
```

**必需配置项**：

```json
{
  "username": "your_email@example.com",  // PikPak 邮箱
  "password": "your_password",            // PikPak 密码
  "path": "folder_id",                    // PikPak 文件夹ID
  "rss": "https://mikanani.me/RSS/..."   // Mikan RSS 链接
}
```

### 4. 测试运行

```bash
# 手动运行测试
source venv/bin/activate
python main.py
```

如果看到 "Bangumi-PikPak 启动成功"，说明配置正确。

按 `Ctrl+C` 停止测试。

### 5. 安装为系统服务（推荐）

```bash
# 一键安装 systemd 服务
sudo ./deploy/install-service.sh
```

安装脚本会：
- ✅ 自动检测当前用户和项目路径
- ✅ 生成正确的 systemd 配置
- ✅ 启用开机自启
- ✅ 启动服务

---

## 🔧 配置说明

### 基础配置（必需）

| 配置项 | 说明 | 如何获取 |
|--------|------|----------|
| `username` | PikPak 邮箱 | 你的注册邮箱 |
| `password` | PikPak 密码 | 你的密码 |
| `path` | 文件夹ID | 从 PikPak URL 复制 |
| `rss` | RSS 链接 | 从 Mikan Project 复制 |

### 代理配置（可选）

如果需要代理访问：

```json
{
  "enable_proxy": true,
  "http_proxy": "http://127.0.0.1:7890",
  "https_proxy": "http://127.0.0.1:7890"
}
```

### 通知配置（可选）

启用番剧更新通知：

```json
{
  "enable_notifications": true,
  "ntfy_url": "https://ntfy.sh/your-unique-topic"
}
```

---

## 📊 服务管理

### 查看状态

```bash
# 查看服务状态
sudo systemctl status bangumi-pikpak

# 健康检查
./deploy/health-check.sh
```

### 查看日志

```bash
# systemd 日志
sudo journalctl -u bangumi-pikpak -f

# 应用日志
./deploy/view-logs.sh -f
```

### 重启服务

```bash
sudo systemctl restart bangumi-pikpak
```

### 停止服务

```bash
sudo systemctl stop bangumi-pikpak
```

---

## 🐛 常见问题

### Q: 提示 "配置加载失败"

**原因**：配置文件格式错误或缺少必填项

**解决**：
1. 检查 JSON 格式是否正确（注意逗号、引号）
2. 确保填写了 username、password、path、rss
3. 运行健康检查：`./deploy/health-check.sh`

### Q: 提示 "无法连接到 mikanani.me"

**原因**：网络问题或需要代理

**解决**：
1. 检查网络连接：`ping mikanani.me`
2. 如果需要代理，在配置中启用代理
3. 确保代理服务正常运行

### Q: systemd 服务启动失败

**原因**：Python 环境或路径问题

**解决**：
1. 检查虚拟环境：`ls -la venv/bin/python`
2. 查看详细错误：`sudo journalctl -u bangumi-pikpak -n 50`
3. 运行健康检查脚本
4. 手动测试：`source venv/bin/activate && python main.py`

### Q: 在其他机器上部署需要注意什么？

**注意**：
1. ✅ 项目路径可以是任意目录（脚本会自动检测）
2. ✅ systemd 服务会自动配置正确的路径
3. ✅ 使用 `install-service.sh` 脚本安装，无需手动修改路径
4. ❌ 不要手动编辑 `bangumi-pikpak.service` 模板文件

---

## 📁 项目结构

```
Bangumi-PikPak/
├── main.py              # 主程序
├── config.json          # 配置文件（你创建的）
├── venv/                # 虚拟环境
├── deploy/              # 部署脚本
│   ├── install-service.sh    # 一键安装
│   ├── health-check.sh       # 健康检查
│   └── view-logs.sh          # 日志查看
└── docs/                # 文档
    ├── DEPLOYMENT.md         # 本文档
    └── OPERATIONS.md         # 详细运维指南
```

---

## 🔗 更多文档

- **详细运维指南**：[docs/OPERATIONS.md](docs/OPERATIONS.md)
- **主文档**：[README.md](README.md)
- **配置示例**：[example.config.json](example.config.json)

---

## ✅ 部署检查清单

部署完成后，确认以下事项：

- ✅ 配置文件已创建（`config.json`）
- ✅ 虚拟环境已创建（`venv/`）
- ✅ 依赖已安装（`pip list`）
- ✅ 服务正在运行（`systemctl status`）
- ✅ 健康检查通过（`health-check.sh`）
- ✅ 日志正常输出（`view-logs.sh -f`）

---

## 💡 提示

- **首次部署**：建议先手动运行测试，确认配置正确后再安装服务
- **生产环境**：推荐启用健康检查和错误告警（见 OPERATIONS.md）
- **多机器部署**：每台机器独立配置，路径自动适配

---

**部署完成后，享受全自动追番体验！** 🎉