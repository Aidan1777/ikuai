"""
get ikuai info by token and sess_key
兼容旧版(Result:30000)和新版(code:0)
"""

import logging
import json
import re
import time
import datetime
import asyncio
from async_timeout import timeout
from aiohttp.client_exceptions import ClientConnectorError
from homeassistant.helpers.aiohttp_client import async_get_clientsession

_LOGGER = logging.getLogger(__name__)

class DataFetcher:
    """Class to fetch data from iKuai router."""

    def __init__(self, hass, host, username, passwd, pas, tracker_config=None, custom_switches_config=None):
        """Initialize the data fetcher."""
        self._host = host
        self._username = username
        self._passwd = passwd
        self._pass = pas
        self._hass = hass
        self._session_client = async_get_clientsession(hass, verify_ssl=False)
        self._semaphore = asyncio.Semaphore(3)

    def is_json(self, jsonstr):
        try:
            json.loads(jsonstr)
        except (ValueError, TypeError):
            return False
        return True

    async def requestpost_json(self, url, headerstr, json_body):
        async with self._semaphore:
            try:
                async with timeout(10):
                    async with self._session_client.post(url, headers=headerstr, json=json_body) as response:
                        if response.status != 200:
                            return None
                        text = await response.text()
                        if self.is_json(text):
                            return json.loads(text)
                        return text
            except (ClientConnectorError, asyncio.TimeoutError) as e:
                _LOGGER.warning("Network error visiting iKuai: %s", e)
                return None
            except Exception as e:
                _LOGGER.error("Unexpected error in requestpost_json: %s", e)
                return None

    async def requestpost_cookies(self, url, headerstr, json_body):
        async with self._semaphore:
            try:
                async with timeout(10):
                    async with self._session_client.post(url, headers=headerstr, json=json_body) as response:
                        if response.status != 200:
                            return None
                        for cookie in response.cookies:
                            if cookie == "sess_key":
                                return response.cookies["sess_key"].value
                        return None
            except Exception as e:
                _LOGGER.error("Error in requestpost_cookies: %s", e)
                return None

    async def _login_ikuai(self):
        header = {"Content-Type": "application/json;charset=UTF-8"}
        json_body = {"username": self._username, "passwd": self._passwd, "pass": self._pass}
        url = self._host + "/Action/login"
        try:
            return await self.requestpost_cookies(url, header, json_body)
        except Exception:
            return None

    def seconds_to_dhms(self, seconds):
        try:
            seconds = int(seconds)
            days = seconds // (3600 * 24)
            hours = (seconds // 3600) % 24
            minutes = (seconds // 60) % 60
            seconds = seconds % 60
            if days > 0: return f"{days}天{hours}小时{minutes}分钟"
            if hours > 0: return f"{hours}小时{minutes}分钟"
            if minutes > 0: return f"{minutes}分钟{seconds}秒"
            return f"{seconds}秒"
        except: return "Unknown"

    def _get_data_block(self, resdata):
        if not isinstance(resdata, dict): return None
        if resdata.get("code") == 0 or resdata.get("Result") == 30000:
            return resdata.get("results") or resdata.get("Data")
        return None

    async def _get_ikuai_status(self, sess_key, data_dict):
        """系统情况: CPU占用、内存占用、连接数、启动时长、在线终端数、流量数据"""
        header = {'Cookie': f'username={self._username}; login=1; sess_key={sess_key}', 'Content-Type': 'application/json;charset=UTF-8'}
        json_body = {"func_name":"homepage","action":"show","param":{"TYPE":"sysstat,ac_status"}}
        resdata = await self.requestpost_json(self._host + "/Action/call", header, json_body)
        if isinstance(resdata, dict) and resdata.get("Result") == 10014: return 401
        
        data_block = self._get_data_block(resdata)
        if not data_block: return

        sysstat = data_block.get("sysstat", {})
        if sysstat:
            data_dict["ikuai_uptime"] = self.seconds_to_dhms(sysstat.get("uptime", 0))
            cpu_list = sysstat.get("cpu", [])
            data_dict["ikuai_cpu"] = str(cpu_list[0]).replace("%","") if (isinstance(cpu_list, list) and cpu_list) else "0"
            memory = sysstat.get("memory", {})
            data_dict["ikuai_memory"] = str(memory.get("used", "")).replace("%","")
            online_user = sysstat.get("online_user", {})
            data_dict["ikuai_online_user"] = online_user.get("count", 0)
            data_dict["ikuai_online_user_attrs"] = online_user
            stream = sysstat.get("stream", {})
            data_dict["ikuai_connect_num"] = int(stream.get("connect_num", 0))
            data_dict["ikuai_upload"] = round(stream.get("upload", 0)/1024/1024, 3)
            data_dict["ikuai_download"] = round(stream.get("download", 0)/1024/1024, 3)
            data_dict["ikuai_total_up"] = round(stream.get("total_up", 0)/1024/1024/1024, 2)
            data_dict["ikuai_total_down"] = round(stream.get("total_down", 0)/1024/1024/1024, 2)
            data_dict["sw_version"] = sysstat.get("verinfo", {}).get("verstring", "Unknown")
            data_dict["device_name"] = sysstat.get("hostname", "iKuai")
        return

    async def _get_ikuai_waninfo(self, sess_key, data_dict):
        """WAN1/WAN2/LAN: IP、在线时长、接口链接状态"""
        header = {'Cookie': f'username={self._username}; login=1; sess_key={sess_key}', 'Content-Type': 'application/json;charset=UTF-8'}
        json_body = {"func_name":"lan","action":"show","param":{"TYPE":"ether_info,snapshoot"}}
        resdata = await self.requestpost_json(self._host + "/Action/call", header, json_body)
        if not resdata: return
        
        data_block = self._get_data_block(resdata)
        if not data_block: return
        
        # WAN1/WAN2
        snapshoot_wan = data_block.get("snapshoot_wan")
        if isinstance(snapshoot_wan, list):
            for item in snapshoot_wan:
                wan_id = item.get("id", 0)
                ip = item.get("ip_addr", "")
                up_time = item.get("updatetime", 0)
                uptime_str = self.seconds_to_dhms(int(time.time() - up_time)) if up_time > 0 else ""
                if wan_id == 1:
                    data_dict["ikuai_wan_ip"] = ip
                    data_dict["ikuai_wan_ip_attrs"] = item
                    data_dict["ikuai_wan_uptime"] = uptime_str
                elif wan_id == 2:
                    data_dict["ikuai_wan2_ip"] = ip
                    data_dict["ikuai_wan2_ip_attrs"] = item
                    data_dict["ikuai_wan2_uptime"] = uptime_str

        # LAN口
        snapshoot_lan = data_block.get("snapshoot_lan")
        if isinstance(snapshoot_lan, list) and snapshoot_lan:
            lan = snapshoot_lan[0]
            data_dict["ikuai_lan_ip"] = lan.get("ip_addr", "")
            data_dict["ikuai_lan_ip_attrs"] = lan
        


    async def _get_ikuai_wan6info(self, sess_key, data_dict):
        """WAN1 IPv6"""
        header = {'Cookie': f'username={self._username}; login=1; sess_key={sess_key}', 'Content-Type': 'application/json;charset=UTF-8'}
        json_body = {"func_name":"ipv6","action":"show","param":{"TYPE":"data,total"}}
        resdata = await self.requestpost_json(self._host + "/Action/call", header, json_body)
        data_block = self._get_data_block(resdata)
        if data_block and isinstance(data_block.get("data"), list) and data_block["data"]:
            data_dict["ikuai_wan6_ip"] = data_block["data"][0].get("dhcp6_ip_addr", "")

    async def _get_ikuai_docker(self, sess_key, data_dict):
        """Docker容器信息 - 自动发现所有运行中的容器"""
        header = {'Cookie': f'username={self._username}; login=1; sess_key={sess_key}', 'Content-Type': 'application/json;charset=UTF-8'}
        json_body = {"func_name":"docker_server","action":"show","param":{"TYPE":"overview"}}
        resdata = await self.requestpost_json(self._host + "/Action/call", header, json_body)
        data_block = self._get_data_block(resdata)
        if not data_block:
            return
        
        overview = data_block.get("overview", {})
        containers = overview.get("running", [])
        discovered = []
        for container in containers:
            name = container.get("name", "")
            if not name:
                continue
            # 清理容器名，只保留字母数字和下划线作为 sensor key
            sanitized = re.sub(r'[^a-zA-Z0-9]', '_', name).strip('_').lower()
            cpu = container.get("cpu_used", "0%").replace("%", "")
            mem_bytes = container.get("memused", 0)
            if isinstance(mem_bytes, str):
                try: mem_bytes = float(mem_bytes)
                except: mem_bytes = 0
            mem_mb = round(mem_bytes / 1024 / 1024, 2)
            data_dict[f"ikuai_docker_{sanitized}_cpu"] = cpu
            data_dict[f"ikuai_docker_{sanitized}_mem"] = str(mem_mb)
            discovered.append({
                "name": name,
                "sanitized": sanitized,
                "cpu": cpu,
                "mem": str(mem_mb),
            })
            _LOGGER.debug("_get_ikuai_docker discovered: %s (key=%s) cpu=%s mem=%s", name, sanitized, cpu, mem_mb)
        data_dict["docker_containers"] = discovered

    async def _get_ikuai_upgrade_info(self, sess_key, data_dict):
        """固件升级信息: 当前版本、最新版本、更新日志、下载地址"""
        header = {'Cookie': f'username={self._username}; login=1; sess_key={sess_key}', 'Content-Type': 'application/json;charset=UTF-8'}
        json_body = {"func_name": "sysupgrade", "action": "show", "param": {"TYPE": "firmware"}}
        try:
            resdata = await self.requestpost_json(self._host + "/Action/call", header, json_body)
            data_block = self._get_data_block(resdata)
            if data_block:
                firmware = data_block.get("firmware", {})
                if firmware:
                    data_dict["firmware_latest_version"] = firmware.get("version", "")
                    data_dict["firmware_release_url"] = firmware.get("url", "")
                    data_dict["firmware_release_summary"] = firmware.get("update_log", "") or firmware.get("changelog", "")
                    data_dict["firmware_size"] = firmware.get("size", "")
                    _LOGGER.debug("Firmware update info: latest=%s, installed=%s",
                                  data_dict.get("firmware_latest_version"),
                                  data_dict.get("sw_version"))
        except Exception as e:
            _LOGGER.warning("Failed to fetch firmware update info: %s", e)

    async def do_firmware_upgrade(self, sess_key):
        """触发固件升级"""
        header = {'Cookie': f'username={self._username}; login=1; sess_key={sess_key}', 'Content-Type': 'application/json;charset=UTF-8'}
        json_body = {"func_name": "sysupgrade", "action": "upgrade", "param": {"TYPE": "firmware"}}
        try:
            resdata = await self.requestpost_json(self._host + "/Action/call", header, json_body)
            _LOGGER.info("Firmware upgrade triggered, response: %s", str(resdata)[:200])
            return resdata
        except Exception as e:
            _LOGGER.error("Firmware upgrade failed: %s", e)
            return None

    async def get_data(self, sess_key):
        """Fetch all iKuai data."""
        new_data = {
            "ikuai_wan_ip": "未获取",
            "ikuai_wan2_ip": "未获取",
            "ikuai_wan6_ip": "未获取",
            "ikuai_lan_ip": "未获取",
        }
        
        status_res = await self._get_ikuai_status(sess_key, new_data)
        if status_res == 401: return 401

        tasks = [
            self._get_ikuai_waninfo(sess_key, new_data),
            self._get_ikuai_wan6info(sess_key, new_data),
            self._get_ikuai_docker(sess_key, new_data),
            self._get_ikuai_upgrade_info(sess_key, new_data),
        ]
        await asyncio.gather(*tasks, return_exceptions=True)
        
        new_data["querytime"] = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        return new_data
