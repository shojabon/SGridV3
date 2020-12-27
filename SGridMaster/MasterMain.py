import json
import os
from threading import Thread

import sys
sys.path.append('../')

import boto3
import uvicorn
from fastapi import FastAPI

from API.MongodbAPI import SMongoDB


class SGridV3Master:

    def __init__(self):
        self.fast_api = FastAPI(debug=True)

        self.nodes = self.load_config("nodes.json")
        self.config = self.load_config("config.json")

        self.mongo = SMongoDB(self.config["mongo"]["host"], self.config["mongo"]["port"], self.config["mongo"]["user"],
                              self.config["mongo"]["password"], self.config["mongo"]["database"])

        sess = boto3.Session(aws_access_key_id=self.config["object_storage_info"]["access_key"],
                             aws_secret_access_key=self.config["object_storage_info"]["secret_access_key"])
        self.boto = sess.client('s3', endpoint_url=self.config["object_storage_info"]["endpoint_url"])


        if "master_key" not in self.config:
            self.config["master_key"] = ""
        self.save_config(self.config, "config.json")

        from SGridMaster.ModuleFunctions.Nodes import NodeFunction
        self.node_function = NodeFunction(self)

        from SGridMaster.ModuleFunctions.Tool import ToolFunction
        self.tool_function = ToolFunction(self)

        from SGridMaster.ModuleFunctions.ClientFTP import ClientFTPFunction
        self.ftp_function = ClientFTPFunction(self)

        from SGridMaster.Endpoints.DockerEndpoint import DockerEndpoint
        self.docker_endpoint = DockerEndpoint(self)

        from SGridMaster.Endpoints.NodeEndpoint import NodeEndpoint
        self.node_endpoint = NodeEndpoint(self)

        from SGridMaster.Endpoints.FileEndpoint import FileEndpoint
        self.file_endpoint = FileEndpoint(self)

        from SGridMaster.Endpoints.FTPEndpoint import FTPEndpoint
        self.ftp_endpoint = FTPEndpoint(self)

        self.local_sync = self.tool_function.map_md5_local("data_dir/sync")

        self.node_function.register_new_nodes()

        self.node_name_address = self.node_function.create_nodeid_to_address()
        self.node_address_name = self.node_function.create_node_address_to_id()

        Thread(target=self.node_function.record_node_task).start()

        self.node_function.push_all_settings()

        uvicorn.run(self.fast_api, host="0.0.0.0", port=2500)

    def load_config(self, file: str):
        if not os.path.exists(file):
            d = open(file, "+a")
            d.write("{}")
            d.close()
        file = open(file, "r")
        data = json.loads(file.read())
        file.close()
        return data

    def save_config(self, data: dict, file: str):
        file = open(file, "w")
        file.write(json.dumps(data, sort_keys=True, indent=4))
        file.close()

if __name__ == '__main__':
    grid_master = SGridV3Master()