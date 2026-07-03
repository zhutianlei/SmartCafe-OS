# 更新注意事项

## 版本号管理规则

### 重要：区分两种版本号

本项目有两种版本号，更新代码时需要注意：

| 版本号 | 文件位置 | 用途 | 是否需要重新构建Docker |
|--------|----------|------|------------------------|
| 文件版本号 | `smartcafe_server/config.yaml` 中的 `version` | 标识代码更新 | ❌ 不需要 |
| Docker镜像版本 | GitHub Actions自动管理 | 标识Docker镜像 | ✅ 需要 |

### 更新流程

#### 情况1：只更新代码文件（推荐）

当您只修改了以下文件时，**不需要重新构建Docker镜像**：

- `smartcafe_server/server/` 目录下的任何文件
- `smartcafe_control/` 目录下的任何文件
- `smartcafe_server/config.yaml`（除version字段外）
- README.md、CHANGELOG.md等文档文件

**操作步骤：**

1. 修改代码文件
2. 更新 `smartcafe_server/config.yaml` 中的 `version` 字段（如 `1.0.1` → `1.0.2`）
3. 提交并推送
4. 用户更新HA中的Add-on即可，无需等待Docker构建

**示例：**
```yaml
# smartcafe_server/config.yaml
version: "1.0.2"  # 只改这个版本号
```

#### 情况2：需要重新构建Docker镜像

当您修改了以下文件时，**需要重新构建Docker镜像**：

- `smartcafe_server/Dockerfile`
- `smartcafe_server/run.sh`
- `smartcafe_server/package.json`（如果添加了新依赖）

**操作步骤：**

1. 修改上述文件
2. 更新 `smartcafe_server/config.yaml` 中的 `version` 字段
3. 提交并推送
4. 等待GitHub Actions构建完成
5. 构建完成后用户才能更新

### 如何查看Docker镜像是否构建完成

1. 打开 https://github.com/zhutianlei/SmartCafe-OS/actions
2. 查看最新的构建状态：
   - ✅ 绿色：构建成功
   - ❌ 红色：构建失败
   - 🟡 黄色：正在构建

### 版本号格式建议

- 使用语义化版本号：`主版本.次版本.修订号`
- 例如：`1.0.0` → `1.0.1`（小更新）→ `1.1.0`（新功能）→ `2.0.0`（大改版）

### 快速检查清单

更新代码前，请确认：

- [ ] 是否修改了Dockerfile或run.sh？
  - 是 → 需要等待Docker构建
  - 否 → 只需更新config.yaml中的version

- [ ] 是否添加了新的npm依赖？
  - 是 → 需要等待Docker构建
  - 否 → 只需更新config.yaml中的version

- [ ] 是否只修改了server/*.js或前端文件？
  - 是 → 不需要等待Docker构建，直接更新version即可
