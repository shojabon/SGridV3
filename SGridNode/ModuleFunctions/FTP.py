# -*- coding:utf-8 -*-
import os
import threading

from pyftpdlib.authorizers import DummyAuthorizer
from pyftpdlib.handlers import FTPHandler, ThrottledDTPHandler
from pyftpdlib.servers import FTPServer

from SGridNode.NodeMain import SGridV3Node


class CustomHandler(FTPHandler):
    core = None

    def process_command(self, cmd, *args, **kwargs):
        if cmd == "STOR":
            if str(args[0].replace("\\", "/")[len(os.getcwd().replace("\\", "/")) + 1:]).startswith("data_dir/ftp_data/users/"):
                dir_char_len = len(os.getcwd().replace("\\", "/")) + 1 + len("data_dir/ftp_data/users/")
                user = args[0].replace("\\", "/")[dir_char_len:].split("/")[0]
                data = self.core.ftp_users[user]
                dir_size = self.core.tool_function.get_dir_size("data_dir/ftp_data/users/" + str(user))
                if dir_size > data["limit_mb"] * 1024 * 1024:
                    self.respond("452 Disk full")
                else:
                    FTPHandler.process_command(self, cmd, *args, **kwargs)
            else:
                FTPHandler.process_command(self, cmd, *args, **kwargs)
        else:
            FTPHandler.process_command(self, cmd, *args, **kwargs)

    def on_file_received(self, file):
        if str(file.replace("\\", "/")[len(os.getcwd().replace("\\", "/")) + 1:]).startswith("data_dir/ftp_data/users/"):
            dir_char_len = len(os.getcwd().replace("\\", "/")) + 1 + len("data_dir/ftp_data/users/".replace("\\", "/"))
            user = str(file.replace("\\", "/")[dir_char_len:]).split("/")[0]
            data = self.core.ftp_users[user]
            dir_size = self.core.tool_function.get_dir_size("data_dir/ftp_data/users/" + str(user))
            if dir_size > data["limit_mb"] * 1024 * 1024:
                os.remove(file)


class FTPFunction:

    def __init__(self, core: SGridV3Node):
        self.core = core

        self.authorizer = DummyAuthorizer()
        self.authorizer.add_user("sgrid-master-user", self.core.config["master_key"], "data_dir/", "elradfmwMT")
        # self.authorizer.add_user("sho", "testpassword", "data_dir/ftp_data/users/sho", "elradfmwMT")

        self.handler = CustomHandler
        self.handler.passive_ports = range(10000, 10301)
        self.handler.masquerade_address = "127.0.0.1"
        self.handler.core = core

        self.throttler = ThrottledDTPHandler
        self.throttler.read_limit = 1.5 * 1024
        self.throttler.write_limit = 1.5 * 1024

        self.handler.dtp_handler = self.throttler

        # FTP
        self.handler.authorizer = self.authorizer
        self.ftp_server = FTPServer(("0.0.0.0", 21), self.handler)
        self.ftp_server.max_cons = 300
        self.ftp_server.max_cons_per_ip = 3

        os.makedirs("data_dir/ftp_data/backup", exist_ok=True)

        t = threading.Thread(target=self.ftp_server.serve_forever)
        t.start()

    def load_users(self):
        for user in self.core.ftp_users.keys():
            data = self.core.ftp_users[user]
            os.makedirs("data_dir/ftp_data/users/" + str(user), exist_ok=True)
            if not self.authorizer.has_user(user):
                self.authorizer.add_user(user, data["password"], "data_dir/ftp_data/users/" + str(user), "elradfmwMT")
