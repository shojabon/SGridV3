import json
import os

import docker
import uvicorn
from fastapi import FastAPI


class SGridV3Node:

    def __init__(self, region: str, name: str, tag, master_key: str):

        self.fast_api = FastAPI(debug=True)
        self.docker = docker.from_env()

        from SGridNode.ModuleFunctions.Tool import ToolFunction
        self.tool_function = ToolFunction(self)

        from SGridNode.Endpoints.NodeEndpoint import NodeEndpoint
        self.node_endpoint = NodeEndpoint(self)

        from SGridNode.Endpoints.DockerEndpoint import DockerEndpoint
        self.docker_endpoint = DockerEndpoint(self)

        self.config = {}
        self.load_config("config.json")
        if "node_id" not in self.config.keys():
            self.config["node_id"] = self.tool_function.create_id_hash(self.tool_function.create_session_key(128))
        self.config["region"] = region
        self.config["name"] = name
        self.config["tag"] = tag
        self.config["master_key"] = master_key
        self.save_config(self.config, "config.json")

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
    grid = SGridV3Node("JAPAN", "TEST", None, "password")