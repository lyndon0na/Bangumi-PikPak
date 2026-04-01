# 用户级部署快速指南

本指南帮助你快速部署用户级 Bangumi-PikPak 服务，**无需 sudo 权限**。

## 为什么选择用户级部署？

✅ **优势：**
- 不需要 root/sudo 权限
- Web 界面可直接控制服务（启动/停止/重启）
- 更安全，权限隔离良好
- 服务在用户未登录时也能运行（通过 linger）

❌ **系统级部署的缺点：**
- Web 界面重启服务需要 sudo 权限
- 权限较高，安全风险更大

## 快速部署步骤

### 1. 克隆项目

```bash
git clone https://github.com/lyndon0na/Bangumi-PikPak.git
cd Bangumi-PikPak
```

### 2. 安装依赖

```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### 3. 配置文件

```bash
cp example.config.json config.json
nano config.json
```

**必需配置：**
```json
{
  "username": "your_email@example.com",
  "password": "your_pikpak_password",
  "path": "your_pikpak_folder_id",
  "rss": "https://mikanani.me/RSS/MyBangumi?token=xxx",
  
  "web_enabled": true,
  "web_port": 8080,
  "web_password": "your_web_password"
}
```

### 4. 安装用户级服务

```bash
./deploy/install-user-service.sh
```

脚本会提示是否启用 **linger**：
- Linger 让服务在用户未登录时也能运行
- 需要运行一次： `sudo loginctl enable-linger $USER`
- 之后所有服务管理都不需要 sudo

### 5. 管理服务

```bash
# 启动服务
systemctl --user start bangumi-pikpak

# 查看状态
systemctl --user status bangumi-pikpak

# 查看日志
journalctl --user -u bangumi-pikpak -f

# 重启服务
systemctl --user restart bangumi-pikpak

# 停止服务
systemctl --user stop bangumi-pikpak
```

### 6. 访问 Web 界面

浏览器打开： `http://localhost:8080`

输入配置中的 `web_password` 登录。

## 服务控制功能

Web 界面提供完整的服务控制（用户级部署）：

- ✅ 查看服务状态
- ✅ 启动服务
- ✅ 停止服务
- ✅ 重启服务

所有操作都不需要 sudo 权限！

## 故障排查

### 服务无法启动

检查 linger 是否启用：
```bash
loginctl show-user $USER | grep Linger
# 应显示: Linger=yes
```

如果未启用：
```bash
sudo loginctl enable-linger $USER
```

### Web 界面无法访问

1. 检查服务状态：
   ```bash
   systemctl --user status bangumi-pikpak
   ```

2. 检查配置：
   ```bash
   grep "web_enabled" config.json
   ```

3. 查看日志：
   ```bash
   journalctl --user -u bangumi-pikpak -n 50
   ```

### 服务管理命令不生效

确保使用 `--user` 参数：
```bash
systemctl --user status bangumi-pikpak  # 正确
systemctl status bangumi-pikpak         # 错误（会查找系统级服务）
```

## 开机自启

用户级服务默认已配置开机自启：
```bash
# 查看是否已启用
systemctl --user is-enabled bangumi-pikpak

# 手动启用
systemctl --user enable bangumi-pikpak
```

## 文件位置

用户级服务相关文件：

- **服务文件**： `~/.config/systemd/user/bangumi-pikpak.service`
- **日志**： 通过 `journalctl --user` 查看
- **配置**： 项目目录下的 `config.json`
- **状态**： 项目目录下的 `state.json`

## 与系统级部署对比

| 特性 | 用户级 | 系统级 |
|------|-------|--------|
| 需要 sudo | ❌ 不需要 | ✅ 需要 |
| Web 控制服务 | ✅ 完全支持 | ⚠️ 需要额外配置 |
| 安全性 | ✅ 更高 | ⚠️ 权限较高 |
| 多用户共享 | ❌ 不支持 | ✅ 支持 |
| 开机自启 | ✅ 支持 | ✅ 支持 |
| 后台运行 | ✅ 需要 linger | ✅ 默认支持 |

## 更多信息

- [完整部署指南](DEPLOYMENT.md)
- [Web 界面使用指南](WEB_GUIDE.md)
- [运维指南](OPERATIONS.md)