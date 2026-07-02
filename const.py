"""Constants for the ikuai health code integration."""

DOMAIN = "ikuai"

######### CONF KEY
CONF_USERNAME = "username"
CONF_PASSWD = "passwd"
CONF_PASS = "pas"
CONF_HOST = "host"
CONF_TOKEN_EXPIRE_TIME = "token_expire_time"
COORDINATOR = "coordinator"
CONF_UPDATE_INTERVAL = "update_interval_seconds"
CONF_CUSTOM_SWITCHES = "custom_switches"
CONF_ACT_BUFFER = "act_buffer"
CONF_TRACKER_CONFIG = "tracker_config"
CONF_SOURCE_MODE = "source_mode"
MODE_UI = "mode_ui"
MODE_CONST = "mode_const"

UNDO_UPDATE_LISTENER = "undo_update_listener"

##### IKUAI URL
LOGIN_URL = "/Action/login"
ACTION_URL = "/Action/call"


### Sensor Configuration

SENSOR_TYPES = {
    # 系统情况
    "ikuai_uptime": {
        "icon": "mdi:clock-time-eight",
        "label": "系统运行时长",
        "name": "System_uptime",
    },
    "ikuai_cpu": {
        "icon": "mdi:cpu-64-bit",
        "label": "CPU占用",
        "name": "Cpu_usage",
        "unit_of_measurement": "%",
    },
    "ikuai_memory": {
        "icon": "mdi:memory",
        "label": "内存占用",
        "name": "Memory_usage",
        "unit_of_measurement": "%",
    },
    "ikuai_connect_num": {
        "icon": "mdi:lan-connect",
        "label": "连接数",
        "name": "Connections",
        "unit_of_measurement": "个",
    },
    "ikuai_online_user": {
        "icon": "mdi:account-multiple",
        "label": "在线终端",
        "name": "Online_clients",
        "unit_of_measurement": "个",
    },
    # WAN1
    "ikuai_wan_ip": {
        "icon": "mdi:ip-network-outline",
        "label": "WAN1 IP",
        "name": "Wan1_ip",
    },
    "ikuai_wan_uptime": {
        "icon": "mdi:timer-sync-outline",
        "label": "WAN1 在线时长",
        "name": "Wan1_uptime",
    },
    # WAN2
    "ikuai_wan2_ip": {
        "icon": "mdi:ip-network-outline",
        "label": "WAN2 IP",
        "name": "Wan2_ip",
    },
    "ikuai_wan2_uptime": {
        "icon": "mdi:timer-sync-outline",
        "label": "WAN2 在线时长",
        "name": "Wan2_uptime",
    },
    # 流量（双WAN合计）
    "ikuai_upload": {
        "icon": "mdi:wifi-arrow-up",
        "label": "上传速度",
        "name": "Upload_speed",
        "unit_of_measurement": "MB/s",
    },
    "ikuai_download": {
        "icon": "mdi:wifi-arrow-down",
        "label": "下载速度",
        "name": "Download_speed",
        "unit_of_measurement": "MB/s",
    },
    "ikuai_total_up": {
        "icon": "mdi:upload-network",
        "label": "上传总量",
        "name": "Total_upload",
        "unit_of_measurement": "GB",
    },
    "ikuai_total_down": {
        "icon": "mdi:download-network",
        "label": "下载总量",
        "name": "Total_download",
        "unit_of_measurement": "GB",
    },
    # WAN1v6
    "ikuai_wan6_ip": {
        "icon": "mdi:ip-network",
        "label": "WAN1 IPv6",
        "name": "Wan1_ipv6",
    },
    # Docker - gecoos-ac
    "ikuai_docker_gecoos_cpu": {
        "icon": "mdi:docker",
        "label": "Docker gecoos CPU",
        "name": "Docker_gecoos_cpu",
        "unit_of_measurement": "%",
    },
    "ikuai_docker_gecoos_mem": {
        "icon": "mdi:memory",
        "label": "Docker gecoos 内存",
        "name": "Docker_gecoos_mem",
        "unit_of_measurement": "MB",
    },

    # Docker - lucky
    "ikuai_docker_lucky_cpu": {
        "icon": "mdi:docker",
        "label": "Docker lucky CPU",
        "name": "Docker_lucky_cpu",
        "unit_of_measurement": "%",
    },
    "ikuai_docker_lucky_mem": {
        "icon": "mdi:memory",
        "label": "Docker lucky 内存",
        "name": "Docker_lucky_mem",
        "unit_of_measurement": "MB",
    },

    # Docker - fastnet
    "ikuai_docker_fastnet_cpu": {
        "icon": "mdi:docker",
        "label": "Docker fastnet CPU",
        "name": "Docker_fastnet_cpu",
        "unit_of_measurement": "%",
    },
    "ikuai_docker_fastnet_mem": {
        "icon": "mdi:memory",
        "label": "Docker fastnet 内存",
        "name": "Docker_fastnet_mem",
        "unit_of_measurement": "MB",
    },

    # LAN口
    "ikuai_lan_ip": {
        "icon": "mdi:lan",
        "label": "LAN IP",
        "name": "Lan_ip",
    },
}


BUTTON_TYPES = {
    "ikuai_restart_reconnect_wan": {
        "label": "重连wan网络",
        "name": "Reconnect_wan",
        "device_class": "restart",
        "action_body": {"func_name":"wan","action":"link_pppoe_reconnect","param":{"id":1}}
    },
}


SWITCH_TYPES = {
}

### Update Configuration

UPDATE_ENTRY = "ikuai_firmware_update"

UPDATE_TYPES = {
    "ikuai_firmware_update": {
        "icon": "mdi:cloud-download",
        "label": "系统固件更新",
        "name": "Firmware_update",
        "device_class": "firmware",
    },
}
