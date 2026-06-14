
import psutil
import shutil
import os
import time

def get_server_report():
    cpu = psutil.cpu_percent(interval=1)
    mem = psutil.virtual_memory()
    disk = shutil.disk_usage("/")

    uptime = time.time() - psutil.boot_time()
    uptime_str = time.strftime("%H:%M:%S", time.gmtime(uptime))

    text = f"""
📊 SERVER STATUS

CPU: {cpu}%
RAM: {mem.percent}% ({mem.used // (1024**2)}MB / {mem.total // (1024**2)}MB)

DISK: {disk.used // (1024**3)}GB / {disk.total // (1024**3)}GB

UPTIME: {uptime_str}
"""
    return text
