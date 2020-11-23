import os
import threading

from pyftpdlib.authorizers import DummyAuthorizer
from pyftpdlib.handlers import FTPHandler
from pyftpdlib.servers import FTPServer

from SGridNode.main import SGridV3Node


class MasterFTPFunction:

    def __init__(self, core: SGridV3Node):
        self.core = core

        # FTP
        self.authorizer = DummyAuthorizer()

        self.handler = FTPHandler

        self.ftp_thread = None
        self.handler.passive_ports = range(10400, 10701)
        self.handler.masquerade_address = '127.0.0.1'

        self.handler.authorizer = self.authorizer
        self.ftp_server = FTPServer(("0.0.0.0", 2100), self.handler)
        self.handler.authorizer.add_user("sgrid-master-user", self.core.config["master_key"], "data_dir", "elradfmwMT")
        t = threading.Thread(target=self.ftp_server.serve_forever)
        t.start()
