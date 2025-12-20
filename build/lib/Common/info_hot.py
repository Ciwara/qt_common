import json
import logging
import platform
import re
import socket
import uuid

import psutil


def getSystemInfo():
    try:
        hdd = psutil.disk_usage("/")
        info = {
            "platform": platform.system(),
            "platform_release": platform.release(),
            "platform_version": platform.version(),
            "architecture": platform.machine(),
            "hostname": socket.gethostname(),
            "ip_address": socket.gethostbyname(socket.gethostname()),
            "mac_address": ":".join(re.findall("..", "%012x" % uuid.getnode())),
            "processor": platform.processor(),
            "ram": str(round(psutil.virtual_memory().total / (1024.0**3))) + " GB",
            "rom_total": "{} GiB".format(hdd.total / (2**30)),
            "rom_used": "{} GiB".format(hdd.used / (2**30)),
            "rom_free": "{} GiB".format(hdd.free / (2**30)),
        }
        return json.dumps(info)
    except Exception as e:
        logging.exception(e)
