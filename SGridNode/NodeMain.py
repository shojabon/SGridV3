import argparse
import json
import os

import sys
sys.path.append('../')

import boto3
import docker
import uvicorn
from fastapi import FastAPI


class SGridV3Node:

    def __init__(self, region: str, name: str, tag, master_key: str):

        os.makedirs("data_dir/sync", exist_ok=True)
        os.makedirs("data_dir/ftp_data", exist_ok=True)

        self.fast_api = FastAPI(debug=True)
        self.docker = docker.from_env()

        from SGridNode.ModuleFunctions.Tool import ToolFunction
        self.tool_function = ToolFunction(self)

        self.config = {}
        self.load_config("config.json")
        if "node_id" not in self.config.keys():
            self.config["node_id"] = self.tool_function.create_id_hash(self.tool_function.create_session_key(128))
        self.config["region"] = region
        self.config["name"] = name
        self.config["tag"] = tag
        self.config["master_key"] = master_key
        self.save_config(self.config, "config.json")
        self.ftp_users = {}



        self.object_storage_setting = {
            "access_key": "OFYJ3DMC54YH413KF35U",
            "bucket": "testdevbucket",
            "endpoint_url": "https://ewr1.vultrobjects.com",
            "secret_access_key": "7hoGXQfsCNnvHqC3x1sUxRF6kNkT181xCivg13nd"
        }

        self.boto = None

        sess = boto3.Session(aws_access_key_id=self.object_storage_setting["access_key"],
                             aws_secret_access_key=self.object_storage_setting["secret_access_key"])
        self.boto = sess.client('s3', endpoint_url=self.object_storage_setting["endpoint_url"])

        from SGridNode.ModuleFunctions.Docker import DockerFunction
        self.docker_function = DockerFunction(self)

        from SGridNode.Endpoints.NodeEndpoint import NodeEndpoint
        self.node_endpoint = NodeEndpoint(self)

        from SGridNode.Endpoints.DockerEndpoint import DockerEndpoint
        self.docker_endpoint = DockerEndpoint(self)

        from SGridNode.Endpoints.SyncEndpoint import SyncEndpoint
        self.sync_endpoint = SyncEndpoint(self)

        from SGridNode.ModuleFunctions.FTP import FTPFunction
        self.ftp_function = FTPFunction(self)

        from SGridNode.Endpoints.FTPEndpoint import FTPClientEndpoint
        self.ftp_endpoint = FTPClientEndpoint(self)

        from SGridNode.ModuleFunctions.File import FileFunction
        self.file_function = FileFunction(self)

        from SGridNode.Endpoints.FileEndpoint import FileEndpoint
        self.file_endpoint = FileEndpoint(self)

        self.file_function.clear_backup()

        uvicorn.run(self.fast_api, host="0.0.0.0", port=2000)

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
    parser = argparse.ArgumentParser(description='SGrid System')
    parser.add_argument("region", help="Set region of node", type=str)
    parser.add_argument("name", help="Set name of server", type=str)
    parser.add_argument("master_key", help="Set master key of node.", type=str)
    parser.add_argument("--tag", help="Set tag of node.", type=str)
    args = vars(parser.parse_args())
    grid = SGridV3Node(args["region"], args["name"], args["tag"], args["master_key"])