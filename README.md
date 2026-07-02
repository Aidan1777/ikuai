# 爱快路由器 Home Assistant 集成（个性化修改版）

基于 [dscao/ikuai](https://github.com/dscao/ikuai) 的二次定制修改。

## 上游源

- **原作者**：[@dscao](https://github.com/dscao)
- **上游仓库**：https://github.com/dscao/ikuai
- **上游最新版本**：2026.2.13

---

## 修改概述

在保留上游核心功能（传感器监控、按钮控制、MAC 开关、设备追踪、UI/Const 双模式配置）的基础上，进行了 **2 轮功能增强**：

---

## 修改一：Docker 容器监控 + 双 WAN 支持

### 新增传感器（`const.py` → `SENSOR_TYPES`）

相较上游的 14 个传感器，新增了 **7 个** 实体，总计 **21 个**：

| 实体键 | 用途 |
|--------|------|
| `ikuai_docker_gecoos_cpu` | Docker 容器 gecoos-ac CPU 占用 (%) |
| `ikuai_docker_gecoos_mem` | Docker 容器 gecoos-ac 内存占用 (MB) |
| `ikuai_docker_lucky_cpu` | Docker 容器 lucky CPU 占用 (%) |
| `ikuai_docker_lucky_mem` | Docker 容器 lucky 内存占用 (MB) |
| `ikuai_docker_fastnet_cpu` | Docker 容器 fastnet CPU 占用 (%) |
| `ikuai_docker_fastnet_mem` | Docker 容器 fastnet 内存占用 (MB) |
| `ikuai_lan_ip` | LAN 口 IP 地址 |

同时新增 WAN2 支持：

| 实体键 | 用途 |
|--------|------|
| `ikuai_wan2_ip` | 第二 WAN 口 IP 地址 |
| `ikuai_wan2_uptime` | 第二 WAN 口在线时长 |

### 数据获取（`data_fetcher.py`）

- **新增方法 `_get_ikuai_docker()`**：通过 `func_name=docker_server` API 获取容器运行状态
  - 硬编码匹配 3 个 Docker 容器：`gecoos_ac`、`lucky`、`fastnet`
  - CPU 使用率解析自 `cpu_used` 字段
  - 内存使用量从字节转换为 MB
- **新增方法 `_get_ikuai_upgrade_info()`**：固件更新信息获取（同修改二）
- **WAN 接口增强**：`_get_ikuai_waninfo()` 增加 WAN2 和 LAN 口 IP 解析
- **并发数据获取**：`get_data()` 增加了 docker 和 upgrade_info 的并发任务

### 传感器属性导出

每个传感器添加 `_attrs` 属性字段，导出原始 API 返回数据，方便自动化调用。新增实体键模式：`{sensor_key}_attrs`。

### 按钮精简

| 变更 | 说明 |
|------|------|
| 移除 `ikuai_restart` | 移除重启路由器按钮（防止误操作） |
| 保留 `ikuai_restart_reconnect_wan` | 仅保留重连 WAN 按钮 |

---

## 修改二：远程固件更新

### 新增平台（`__init__.py`）

```python
PLATFORMS = [Platform.SENSOR, Platform.BUTTON, Platform.UPDATE]
```

在原有 SENSOR 和 BUTTON 基础上，新增 **`Platform.UPDATE`** 平台。

### 新增文件（`update.py`）

固件更新实体 `IKUAIUpdate`，继承 `UpdateEntity`：

| 属性 | 说明 |
|------|------|
| `device_class` | `FIRMWARE` |
| `installed_version` | 当前路由器固件版本（从 `sysstat.verinfo` 解析） |
| `latest_version` | 最新可用固件版本 |
| `release_url` | 固件下载地址 |
| `release_summary` | 更新日志 |
| `supported_features` | `INSTALL`（支持一键安装） |

### 数据获取（`data_fetcher.py`）

| 方法 | 说明 |
|------|------|
| `_get_ikuai_upgrade_info()` | 调用 `sysupgrade → show` 获取固件升级信息 |
| `do_firmware_upgrade()` | 调用 `sysupgrade → upgrade` 触发远程固件升级 |

### 实体列表

| 实体 ID | 中文名 | 功能 |
|---------|--------|------|
| `update.firmware_update` | 系统固件更新 | 检测新版本 + 点击安装 |

> ⚠️ 固件升级会触发路由器重启，整个过程约需 3-5 分钟。

---

## 文件清单

```
custom_components/ikuai/
├── __init__.py          # 集成入口 + DataUpdateCoordinator（新增 UPDATE 平台）
├── const.py             # 常量定义（21 传感器 + 1 按钮 + 固件更新配置）
├── config_flow.py       # UI 配置流程（未修改）
├── data_fetcher.py      # API 数据获取（新增 Docker + 固件升级方法）
├── sensor.py            # 传感器实体（未修改）
├── switch.py            # 开关实体 / MAC 控制（未修改）
├── button.py            # 按钮实体（未修改）
├── device_tracker.py    # 设备追踪实体（未修改）
├── update.py            # 固件更新实体（新增）
├── manifest.json         # 集成元数据
└── translations/
    ├── en.json
    └── zh-Hans.json
```

---

## 安装使用

1. 将 `custom_components/ikuai/` 放入 HA 配置目录
2. 重启 Home Assistant
3. 配置 → 设备与服务 → 添加集成 → 搜索「ikuai」
4. 填入路由器地址、用户名、密码完成配置

实体将自动出现在：
- 传感器：`sensor.*`（21 个）
- 按钮：`button.*`（1 个：重连 WAN）
- 更新：`update.firmware_update`（1 个：固件更新）
- 设备追踪：`device_tracker.*`（按配置生成）
