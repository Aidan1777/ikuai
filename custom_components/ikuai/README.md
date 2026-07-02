# 爱快路由器 - Home Assistant 集成

基于 [dscao/ikuai](https://github.com/dscao/ikuai) 二次定制修改，支持 Docker 容器监控、双 WAN 接口和远程固件更新。

## ✨ 功能特性

- ✅ 系统状态监控（CPU、内存、流量、在线用户）
- ✅ Docker 容器自动发现（CPU、内存监控）
- ✅ 双 WAN 接口支持（WAN1 + WAN2 IP、在线时长）
- ✅ 远程固件更新检测与安装
- ✅ WAN 重连按钮
- ✅ MAC 地址过滤开关
- ✅ 设备追踪

## 🚀 安装

### HACS 安装

1. HACS → 集成 → 自定义仓库
2. 添加：`https://github.com/Aidan1777/ikuai`
3. 搜索「爱快路由器」→ 安装
4. 重启 Home Assistant

### 手动安装

```bash
cd /path/to/homeassistant/config/custom_components
git clone https://github.com/Aidan1777/ikuai.git
```

## ⚙️ 配置

1. 设置 → 设备与服务 → 添加集成
2. 搜索「ikuai」
3. 填写：路由器地址、用户名、密码

## 📊 实体列表

| 类型 | 实体 | 说明 |
|---|---|---|
| **传感器** | `sensor.ikuai_cpu` | CPU 使用率 |
| | `sensor.ikuai_memory` | 内存使用率 |
| | `sensor.ikuai_wan_ip` | WAN1 IP |
| | `sensor.ikuai_wan2_ip` | WAN2 IP |
| | `sensor.ikuai_lan_ip` | LAN IP |
| | `sensor.ikuai_docker_*_cpu` | Docker 容器 CPU |
| | `sensor.ikuai_docker_*_mem` | Docker 容器内存 |
| **按钮** | `button.ikuai_restart_reconnect_wan` | 重连 WAN |
| **更新** | `update.firmware_update` | 固件更新 |
| **开关** | `switch.*` | MAC 过滤开关 |
| **追踪** | `device_tracker.*` | 设备在线状态 |

## 📝 注意事项

- Docker 容器会自动发现，无需手动配置
- 固件更新会重启路由器，约需 3-5 分钟
- 建议开启自动更新检测提醒