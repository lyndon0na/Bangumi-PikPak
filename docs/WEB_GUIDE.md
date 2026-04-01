# Web界面使用指南

Bangumi-PikPak 现已支持Web管理界面!

## 功能特性

### 🎯 仪表盘监控
- 实时查看服务运行状态(运行时长、错误计数)
- 最近10条番剧更新记录
- 已追番剧列表
- RSS检查间隔、通知状态、代理状态等信息

### 📋 日志查看
- 查看最近100-1000行日志
- 按日志级别筛选(ERROR/WARNING/INFO/DEBUG)
- 自动刷新功能

### ⚙️ 配置管理
- 查看和修改配置(敏感信息已脱敏)
- 分页管理:基本配置、网络配置、Web配置、高级配置
- 保存配置并重启服务

### 🔄 服务控制
- 通过Web界面重启systemd服务
- 查看服务运行状态

## 配置启用

### 1. 选择部署方式

**推荐：用户级 systemd 服务**
- 不需要 sudo 权限
- Web 界面可直接控制服务（启动/停止/重启）
- 更安全，权限隔离

```bash
# 安装用户级服务
./deploy/install-user-service.sh

# 启用 linger（让服务在后台持续运行）
sudo loginctl enable-linger $USER
```

**可选：系统级 systemd 服务**
- 需要 sudo 权限
- Web 界面服务控制功能受限（需要 sudo 权限）

```bash
sudo ./deploy/install-service.sh
```

### 2. 更新配置文件

编辑 `config.json`,添加以下配置:

```json
{
  "web_enabled": true,
  "web_host": "0.0.0.0",
  "web_port": 8080,
  "web_password": "your_secure_password_here"
}
```

**配置说明:**
- `web_enabled`: 是否启用Web界面
- `web_host`: Web服务绑定地址,`0.0.0.0`允许所有网络访问
- `web_port`: Web服务端口,默认8080
- `web_password`: Web访问密码(必须设置)

### 2. 安装依赖

```bash
cd Bangumi-PikPak
source venv/bin/activate
pip install -r requirements.txt
```

新增依赖:
- FastAPI (Web框架)
- Uvicorn (ASGI服务器)
- python-jose (JWT认证)
- passlib/bcrypt (密码加密)

### 3. 重启服务

```bash
sudo systemctl restart bangumi-pikpak
```

或者手动启动:
```bash
source venv/bin/activate
python main.py
```

## 使用方法

### 访问Web界面

启动服务后,访问: `http://your_vps_ip:8080`

**首次访问:**
1. 输入配置文件中设置的 `web_password`
2. 登录成功后会自动跳转到仪表盘

### 页面导航

- **仪表盘** (`/dashboard`): 查看运行状态和最近更新
- **日志** (`/logs`): 查看运行日志
- **配置** (`/config`): 查看和修改配置
- **退出** (`/logout`): 登出系统

## API接口

Web界面提供RESTful API,可用于集成其他系统:

### 认证API
- `POST /login` - 登录
- `GET /logout` - 登出

### 状态API
- `GET /api/status` - 获取运行状态
- `GET /api/updates` - 获取更新记录
- `GET /api/bangumi` - 获取番剧列表

### 日志API
- `GET /api/logs?lines=100&level=ERROR` - 获取日志

### 配置API
- `GET /api/config` - 获取配置(脱敏)
- `POST /api/config` - 更新配置

### 服务控制API
- `GET /api/service/status` - 服务状态
- `POST /api/service/restart` - 重启服务

## 安全建议

### 密码安全
- 使用强密码,建议长度>16位
- 包含字母、数字、特殊字符
- 不要使用容易猜测的密码

### 网络安全
- 建议配置防火墙，只允许特定IP访问
- 推荐使用Nginx反向代理配置HTTPS
- 不要在公网暴露Web端口
- 用户级部署更安全，Web界面无法获取系统权限

### Nginx反向代理示例

```nginx
server {
    listen 443 ssl;
    server_name bangumi.yourdomain.com;
    
    ssl_certificate /path/to/cert.pem;
    ssl_certificate_key /path/to/key.pem;
    
    location / {
        proxy_pass http://127.0.0.1:8080;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

然后修改配置:
```json
{
  "web_host": "127.0.0.1",
  "web_port": 8080
}
```

## 状态持久化

Web界面会自动记录番剧更新历史到 `state.json`:

```json
{
  "updates": [
    {
      "bangumi_title": "进击的巨人",
      "episode": "第1集",
      "torrent_url": "...",
      "timestamp": "2024-01-01T12:00:00",
      "status": "success"
    }
  ],
  "stats": {
    "total_processed": 10,
    "success_count": 9,
    "failed_count": 1,
    "last_check": "2024-01-01T12:00:00"
  }
}
```

## 故障排查

### 无法访问Web界面
1. 检查 `web_enabled` 是否为 `true`
2. 检查防火墙是否开放端口
3. 检查服务是否正常运行: `systemctl status bangumi-pikpak`

### 登录失败
1. 确认密码配置正确
2. 检查日志是否有错误信息
3. 清除浏览器Cookie重新登录

### 配置保存失败
1. 检查配置文件权限
2. 确认JSON格式正确
3. 查看日志中的错误信息

## 技术架构

- **后端**: FastAPI (Python异步Web框架)
- **认证**: JWT Token (24小时有效期)
- **前端**: 响应式HTML/CSS/JavaScript
- **并发**: asyncio同时运行Web服务和主任务
- **持久化**: JSON文件存储

## 后续改进

可以继续扩展的功能:
- WebSocket实时日志推送
- 多用户支持
- 更详细的统计图表
- 通知历史查看
- 手动触发RSS检查
- 番剧订阅管理界面