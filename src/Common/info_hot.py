import json
import logging
import os
import platform
import re
import socket
import uuid
from getpass import getuser

import psutil


def getSystemInfo():
    try:
        hdd = psutil.disk_usage("/")
        try:
            ip_address = socket.gethostbyname(socket.gethostname())
        except OSError:
            ip_address = ""
        info = {
            "platform": platform.system(),
            "platform_release": platform.release(),
            "platform_version": platform.version(),
            "architecture": platform.machine(),
            "hostname": socket.gethostname(),
            "ip_address": ip_address,
            "mac_address": ":".join(re.findall("..", "%012x" % uuid.getnode())),
            "processor": platform.processor() or platform.machine(),
            "ram": str(round(psutil.virtual_memory().total / (1024.0**3))) + " GB",
            "rom_total": "{:.1f} GiB".format(hdd.total / (2**30)),
            "rom_used": "{:.1f} GiB".format(hdd.used / (2**30)),
            "rom_free": "{:.1f} GiB".format(hdd.free / (2**30)),
            "os_user": getuser(),
            "os_user_home": os.path.expanduser("~"),
            "python_version": platform.python_version(),
        }
        return json.dumps(info)
    except Exception as e:
        logging.exception(e)
        return json.dumps({})
