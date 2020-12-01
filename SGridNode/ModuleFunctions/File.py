import glob
import hashlib
import io
import os
import random
import shutil
import time
import traceback
from datetime import datetime
from threading import Thread

import boto3
import psutil

from SGridNode.NodeMain import SGridV3Node


class FileFunction:

    def __init__(self, core: SGridV3Node):
        self.core = core

    def backup_user_data(self, user: str):
        if not os.path.exists('data_dir/ftp_data/users/' + str(user)):
            return None
        try:
            return shutil.make_archive('data_dir/ftp_data/backup/' + str(user) + "-" + str(round(datetime.now().timestamp())),
                                'zip', root_dir='data_dir/ftp_data/users/' + str(user)).replace("\\", "/")
        except Exception:
            return None

    def unpack_user_data(self, user: str, key: str):
        if not os.path.exists('data_dir/ftp_data/backup/' + str(user) + "-" + str(key) + ".zip"):
            return False
        try:
            if os.path.exists("data_dir/ftp_data/users/" + str(user)):
                shutil.rmtree("data_dir/ftp_data/users/" + str(user))
            shutil.unpack_archive('data_dir/ftp_data/backup/' + str(user) + "-" + str(key) + ".zip",
                                  "data_dir/ftp_data/users/" + str(user))
            return True
        except Exception:
            return False

    def delete_user_backup(self, user: str, key: str):
        if not os.path.exists('data_dir/ftp_data/backup/' + str(user) + "-" + str(key) + ".zip"):
            return False
        os.remove('data_dir/ftp_data/backup/' + str(user) + "-" + str(key) + ".zip")
        return True

    def clear_backup(self):
        paths = [x.replace("\\", "/") for x in glob.glob("data_dir/ftp_data/backup/*.zip")]
        for path in paths:
            os.remove(path)