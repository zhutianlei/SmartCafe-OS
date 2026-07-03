# 智咖网吧智能管理系统

基于 Home Assistant 的网吧智能管理系统，实现终端设备与HA的安全对接和集中管控。

## 项目结构

```
SmartCafe-OS/
├── repository.json            # HA Add-on仓库配置
├── smartcafe_server/          # 服务端（HA Add-on）
│   ├── server/                # Node.js服务端
│   ├── config.yaml            # Add-on配置
│   ├── Dockerfile             # Docker构建文件
│   └── run.sh                 # 启动脚本
│
└── smartcafe_control/         # HA集成
    ├── manifest.json          # 集成配置
    ├── config_flow.py         # 配置流程
    ├── coordinator.py         # 设备同步与Ping检测
    ├── switch.py              # WOL唤醒开关
    └── binary_sensor.py       # 在线状态传感器
```

## 功能特性

### 服务端 (smartcafe_server)

- **设备白名单** — 按IP授权终端设备
- **客户端开关** — 控制设备是否允许连接
- **分类管理** — 创建、重命名、删除分类
- **批量添加** — IP段模式 + 文本导入模式
- **Token管理** — 自动获取和刷新HA Token
- **Kiosk模式** — 终端全屏显示HA仪表板
- **Apple风格UI** — 管理面板美观易用

### HA集成 (smartcafe_control)

- **WOL唤醒** — 远程唤醒关机设备
- **在线检测** — 定时Ping检测设备状态
- **设备同步** — 自动从服务端获取设备列表
- **REST API** — 提供设备状态查询接口

## 安装

### 服务端安装

1. 在HA中添加自定义仓库：
   ```
   https://github.com/zhutianlei/SmartCafe-OS
   ```
2. 安装「智咖系统」Add-on
3. 配置HA地址和登录凭据
4. 启动服务，通过侧边栏访问管理面板

### 集成安装

1. 将 `smartcafe_control/` 目录复制到HA的 `custom_components/` 目录
2. 重启Home Assistant
3. 在集成中添加「智咖系统」
4. 填写服务端地址

## 使用流程

```
管理员添加设备(名称+IP+MAC)
        ↓
终端设备请求连接
        ↓
服务端验证白名单 + 客户端开关
        ↓
下发HA URL + Token
        ↓
终端加载仪表板
```

## 默认账号

- 用户名：`admin`
- 密码：`admin`

## License

MIT
