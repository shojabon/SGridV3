import hashlib
import random

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
