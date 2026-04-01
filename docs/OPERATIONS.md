# Bangumi-PikPak 运维部署指南

本文档介绍如何将 Bangumi-PikPak 作为系统服务运行，以及运维监控最佳实践。

---

## 📦 systemd 服务部署

### 快速安装

**一键安装脚本**：

```bash
# 进入项目目录
cd Bangumi-PikPak

# 运行安装脚本
sudo ./deploy/install-service.sh
```

脚本会自动完成以下操作：
- ✅ 创建 systemd 服务文件
- ✅ 配置自动重启策略
- ✅ 启用开机自启
- ✅ 启动服务

### 手动安装

**1. 创建配置文件**

```bash
cp example.config.json config.json
# 编辑 config.json，填入你的信息
```

**2. 创建虚拟环境**

```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

**3. 安装服务**

**方式一：使用安装脚本（推荐）**

```bash
sudo ./deploy/install-service.sh
```

**方式二：手动配置**

```bash
# 1. 复制服务模板
sudo cp deploy/bangumi-pikpak.service /etc/systemd/system/bangumi-pikpak.service

# 2. 编辑服务文件，填入你的信息
sudo nano /etc/systemd/system/bangumi-pikpak.service

# 需要修改以下配置：
# - User=<your_username>
# - Group=<your_username>
# - WorkingDirectory=/path/to/Bangumi-PikPak
# - ExecStart=/path/to/Bangumi-PikPak/venv/bin/python /path/to/Bangumi-PikPak/main.py

# 3. 重载并启动
sudo systemctl daemon-reload
sudo systemctl enable bangumi-pikpak
sudo systemctl start bangumi-pikpak
```

### 服务管理

**常用命令**：

```bash
# 启动服务
sudo systemctl start bangumi-pikpak

# 停止服务
sudo systemctl stop bangumi-pikpak

# 重启服务
sudo systemctl restart bangumi-pikpak

# 查看状态
sudo systemctl status bangumi-pikpak

# 查看实时日志
sudo journalctl -u bangumi-pikpak -f

# 查看最近 100 行日志
sudo journalctl -u bangumi-pikpak -n 100
```

### 服务卸载

```bash
sudo ./deploy/uninstall-service.sh
```

---

## 🔧 配置优化

### systemd 服务配置

**服务特性**：

| 特性 | 说明 |
|------|------|
| **自动重启** | 失败后 10 秒自动重启 |
| **超时设置** | 启动 30 秒，停止 30 秒 |
| **日志输出** | 自动输出到 systemd journal |
| **资源限制** | 最大内存 512MB |
| **安全加固** | NoNewPrivileges, PrivateTmp |

**自定义配置**：

编辑 `/etc/systemd/system/bangumi-pikpak.service`：

```ini
# 修改用户和组（如果不是当前用户）
User=your_username
Group=your_username

# 修改工作目录（如果不是标准位置）
WorkingDirectory=/path/to/Bangumi-PikPak

# 修改内存限制
MemoryMax=1G

# 添加环境变量
Environment="MY_VAR=value"
```

修改后执行：

```bash
sudo systemctl daemon-reload
sudo systemctl restart bangumi-pikpak
```

---

## 📊 监控和健康检查

### 健康检查脚本

**运行健康检查**：

```bash
./deploy/health-check.sh
```

**检查内容**：
- ✅ 配置文件是否存在
- ✅ 配置格式是否正确
- ✅ 虚拟环境是否存在
- ✅ 依赖包是否安装
- ✅ 服务是否运行
- ✅ 日志文件是否正常
- ✅ 网络连接是否可用
- ✅ 磁盘空间是否充足

### 日志查看脚本

**查看日志**：

```bash
# 实时查看日志
./deploy/view-logs.sh -f

# 仅查看错误
./deploy/view-logs.sh -e

# 查看最近 50 行
./deploy/view-logs.sh -n 50

# 查看 systemd 日志
./deploy/view-logs.sh -s

# 显示统计信息
./deploy/view-logs.sh --stats

# 清空日志文件
./deploy/view-logs.sh -c
```

### 配置健康检查

**在 config.json 中启用**：

```json
{
  "enable_health_check": true,
  "health_check_interval": 3600,
  "enable_error_alert": true,
  "error_alert_threshold": 3
}
```

**健康检查报告**（每小时输出）：

```
============================================================
健康检查报告
运行时长: 2小时30分钟
错误计数: 0
RSS 条目: 15
============================================================
```

---

## 🚨 监控告警

### 错误告警配置

**启用错误告警**：

```json
{
  "enable_error_alert": true,
  "error_alert_threshold": 3,
  "enable_notifications": true,
  "ntfy_url": "https://ntfy.sh/your-topic"
}
```

**告警触发条件**：
- 连续错误次数达到阈值（默认 3 次）
- 自动发送 ntfy.sh 通知

**告警消息示例**：

```
⚠️ Bangumi-PikPak 告警
连续错误次数: 3
请检查服务状态！
```

### 日志敏感信息脱敏

**启用脱敏**：

```json
{
  "log_sensitive_filter": true
}
```

**自动脱敏字段**：
- password
- token
- secret
- key
- credential
- auth

**脱敏效果**：

```
原始: password=my_secret_password
脱敏: password=****************
```

### 结构化日志

**启用 JSON 格式**：

```json
{
  "log_json_format": true
}
```

**JSON 日志示例**：

```json
{
  "timestamp": "2024-01-01T10:00:00",
  "level": "INFO",
  "logger": "main",
  "message": "RSS 解析完成",
  "module": "main",
  "function": "run_once",
  "line": 50
}
```

**优势**：
- ✅ 便于日志分析工具处理
- ✅ 支持结构化查询
- ✅ 易于集成 ELK、Loki 等系统

---

## 🔍 故障排查

### 服务无法启动

**检查步骤**：

```bash
# 1. 检查配置文件
./deploy/health-check.sh

# 2. 查看详细错误
sudo journalctl -u bangumi-pikpak -n 50

# 3. 检查 Python 环境
source venv/bin/activate
python -c "from config import load_config; load_config('config.json')"

# 4. 手动运行测试
source venv/bin/activate
python main.py
```

### 网络连接问题

**检查网络**：

```bash
# 测试 Mikan 连接
curl -I https://mikanani.me

# 测试代理连接（如果启用）
curl -I --proxy http://127.0.0.1:7890 https://mikanani.me

# 检查 DNS
nslookup mikanani.me
```

### PikPak 登录问题

**常见错误**：

| 错误 | 解决方案 |
|------|----------|
| 用户名密码错误 | 检查 config.json 中的账号信息 |
| Token 失效 | 删除 pikpak.json 文件，重启服务 |
| 网络错误 | 检查代理配置或网络连接 |

**重置登录状态**：

```bash
# 删除保存的 token
rm pikpak.json

# 重启服务
sudo systemctl restart bangumi-pikpak
```

---

## 📈 性能优化

### 资源占用

**正常占用**：

| 资源 | 占用 |
|------|------|
| CPU | < 5% |
| 内存 | ~50MB |
| 磁盘 | ~10MB（日志） |

### 调整检查间隔

**降低资源占用**：

```json
{
  "rss_check_interval": 1200,  // 20 分钟检查一次
  "health_check_interval": 7200  // 2 小时健康检查
}
```

### 日志优化

**减少日志大小**：

```json
{
  "log_level": "WARNING",  // 只记录警告和错误
  "log_max_bytes": 5242880,  // 5MB
  "log_backup_count": 3
}
```

---

## 🔄 升级和维护

### 升级版本

```bash
# 1. 停止服务
sudo systemctl stop bangumi-pikpak

# 2. 备份配置
cp config.json config.json.backup
cp pikpak.json pikpak.json.backup

# 3. 更新代码
git pull

# 4. 更新依赖
source venv/bin/activate
pip install -r requirements.txt --upgrade

# 5. 运行健康检查
./deploy/health-check.sh

# 6. 启动服务
sudo systemctl start bangumi-pikpak
```

### 定期维护

**每周检查**：

```bash
# 检查服务状态
./deploy/health-check.sh

# 查看错误统计
./deploy/view-logs.sh --stats

# 清理旧日志（可选）
./deploy/view-logs.sh -c
```

---

## 🛡️ 安全建议

### 配置文件安全

**权限设置**：

```bash
# 仅允许当前用户访问配置文件
chmod 600 config.json

# 验证权限
ls -la config.json
# 应显示: -rw------- 1 user user ...
```

### 通知安全

**ntfy.sh 主题选择**：

- ✅ 使用独特且不易猜测的主题名称
- ✅ 避免使用常见词汇（如 "anime", "pikpak"）
- ✅ 建议格式：`yourname-randomstring-2024`

**示例**：

```json
{
  "ntfy_url": "https://ntfy.sh/myname-x7k9p2m-2024"
}
```

### 代理安全

**避免在日志中泄露代理信息**：

```json
{
  "log_sensitive_filter": true
}
```

---

## 📚 相关文档

- [主文档 README.md](../README.md)
- [配置说明](../README.md#配置说明)
- [常见问题](../README.md#常见问题)

---

## 💡 最佳实践总结

**生产环境推荐配置**：

```json
{
  // 基础配置
  "username": "your_email@example.com",
  "password": "your_password",
  "path": "your_folder_id",
  "rss": "your_rss_url",
  
  // 代理配置（如需要）
  "enable_proxy": true,
  "http_proxy": "http://127.0.0.1:7890",
  
  // 通知配置
  "enable_notifications": true,
  "ntfy_url": "https://ntfy.sh/your-unique-topic",
  
  // 运行参数
  "rss_check_interval": 600,
  "max_retries": 3,
  "request_timeout": 30,
  
  // 日志配置
  "log_level": "INFO",
  "log_sensitive_filter": true,
  "log_max_bytes": 10485760,
  
  // 监控配置
  "enable_health_check": true,
  "health_check_interval": 3600,
  "enable_error_alert": true,
  "error_alert_threshold": 3
}
```

**部署后检查清单**：

- ✅ 配置文件权限正确（600）
- ✅ 服务自动启动（systemctl enable）
- ✅ 健康检查通过（health-check.sh）
- ✅ 通知测试成功（手动触发一次）
- ✅ 日志正常输出（view-logs.sh -f）

---

**运维部署完成！祝使用愉快！** 🎉