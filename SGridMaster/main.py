import json
import os

import uvicorn
from fastapi import FastAPI


class SGridV3Master:

    def __init__(self):
        self.fast_api = FastAPI(debug=True)
        os.makedirs("data_dir/sync", exist_ok=True)

        self.nodes = self.load_config("nodes.json")
        self.config = self.load_config("config.json")
        if "master_key" not in self.config:
            self.config["master_key"] = ""
        self.save_config(self.config, "config.json")

        from SGridMaster.ModuleFunctions.Nodes import NodeFunction
        self.node_function = NodeFunction(self)

        from SGridMaster.ModuleFunctions.Sync import SyncFunction
        self.sync_function = SyncFunction(self)

        from SGridMaster.ModuleFunctions.Tool import ToolFunction
        self.tool_function = ToolFunction(self)

        self.local_sync = self.tool_function.map_md5_local("data_dir/sync")

        self.node_name_address = self.node_function.create_nodeid_to_address()

        self.node_function.register_new_nodes()

        self.sync_function.sync_all_nodes()


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