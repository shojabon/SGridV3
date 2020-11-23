import glob
import hashlib
import os
import random
import time

import psutil

from SGridNode.main import SGridV3Node


class ToolFunction:

    def __init__(self, core: SGridV3Node):
        self.core = core

    def create_session_key(self, length: int):
        charset = "abcdefghijklmnopqrstuvwxyz0123456789"
        final = ""
        for x in range(length):
            final += random.choice(charset)
        return final

    def create_id_hash(self, *args):
        data_dump = ""
        args = random.choice(args)
        for data in args:
            data_dump += str(data) + "|"
        a = random.randint(0, 100000)
        b = random.randint(0, 100000)
        c = random.randint(1, 4)
        has = str(a) + "SInstance" + data_dump + str(b)
        for x in range(c):
            has = hashlib.md5(has.encode("utf-8")).hexdigest()
        return has

    def does_post_params_exist(self, json_data: dict, params: list):
        for par in params:
            if par not in json_data.keys():
                return False
        return True

    def net_usage(self):
        cache_1 = {}
        for interface in psutil.net_if_stats().keys():
            net_stat = psutil.net_io_counters(pernic=True, nowrap=True)[interface]
            cache_1[interface] = {"in": net_stat.bytes_recv, "out": net_stat.bytes_sent}
        time.sleep(1)
        cache_2 = {}
        for interface in psutil.net_if_stats().keys():
            net_stat = psutil.net_io_counters(pernic=True, nowrap=True)[interface]
            cache_2[interface] = {"in": net_stat.bytes_recv, "out": net_stat.bytes_sent}

        result = {}

        for interface in cache_1.keys():
            net_in = round((cache_2[interface]["in"] - cache_1[interface]["in"]) / 1024 / 1024, 3)
            net_out = round((cache_2[interface]["out"] - cache_1[interface]["out"]) / 1024 / 1024, 3)
            result[interface] = {"in": net_in, "out": net_out}

        return result

    def disk_usage(self):
        cache_1 = {}
        keys = psutil.disk_io_counters(perdisk=True, nowrap=True).keys()
        for interface in keys:
            disk_stat = psutil.disk_io_counters(perdisk=True, nowrap=True)[interface]
            cache_1[interface] = {"read": disk_stat.read_bytes, "write": disk_stat.write_bytes}
        time.sleep(1)
        cache_2 = {}
        for interface in keys:
            disk_stat = psutil.disk_io_counters(perdisk=True, nowrap=True)[interface]
            cache_2[interface] = {"read": disk_stat.read_bytes, "write": disk_stat.write_bytes}

        result = {}

        for interface in cache_1.keys():
            disk_read = round((cache_2[interface]["read"] - cache_1[interface]["read"]) / 1024 / 1024, 3)
            disk_write = round((cache_2[interface]["write"] - cache_1[interface]["write"]) / 1024 / 1024, 3)
            result[interface] = {"read": disk_read, "write": disk_write}

        return result

    def map_md5_local(self, path_location="data_dir/sync"):
        paths = [x.replace("\\", "/") for x in glob.glob(path_location + "/*", recursive=True)]
        result = {}
        for path in paths:
            if os.path.isfile(path):
                result[path] = hashlib.md5(open(path, "rb").read()).hexdigest()
            else:
                result[path] = self.map_md5_local(path)
        return result

    def get_dir_size(self, path='.'):
        total = 0
        with os.scandir(path) as it:
            for entry in it:
                if entry.is_file():
                    total += entry.stat().st_size
                elif entry.is_dir():
                    total += self.get_dir_size(entry.path)
        return total