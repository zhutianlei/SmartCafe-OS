# HaAssistant

局域网终端与 Home Assistant 安全对接系统。服务端集中管控，客户端零信任。

## 功能特性

- 终端设备白名单管理
- 自动获取 HA 访问令牌
- 定时刷新令牌（可选）
- 终端自动登录 HA 仪表板
- Apple 风格管理界面

## 配置说明

### HA Base URL
Home Assistant 的访问地址，例如：`http://homeassistant.local:8123`

### HA Username / Password
用于自动获取访问令牌的 HA 账号凭据。令牌会缓存在内存中，过期自动刷新。

### Token Auto Refresh
启用后，服务端会在指定时间自动刷新令牌，避免过期。

### Token Refresh Hour
定时刷新的小时数（0-23），建议设置为凌晨时段（如 3:00）。

## 使用方法

1. 安装应用后，在配置中填写 HA 地址和凭据
2. 保存配置，服务端会自动获取令牌
3. 在「设备管理」中添加终端设备的 IP 地址
4. 终端设备访问 `http://服务端IP:8080/api/terminal/pull` 获取 HA 仪表板地址

## 端口说明

- 8080：服务端 HTTP 端口（通过 Ingress 映射）

## 数据持久化

所有配置和白名单数据存储在 `/data/ha-assistant/` 目录中，应用更新不会丢失数据。
