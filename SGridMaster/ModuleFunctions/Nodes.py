import time
from datetime import datetime
from threading import Thread

from SGridMaster.main import SGridV3Master
from SGridNode.SGridV3NodeAPI import SGridV3NodeAPI


class NodeFunction:

    def __init__(self, core: SGridV3Master):
        self.core = core

        self.status_cache = {}
        self.container_stats = {}

    def register_new_nodes(self):
        for node_ip in self.core.nodes.keys():
            if "node_id" not in self.core.nodes[node_ip]:
                grid_api = SGridV3NodeAPI(self.core.config["master_key"], node_ip)
                info = grid_api.node_info()
                if info is None:
                    continue
                self.core.nodes[node_ip] = info
                self.core.nodes[node_ip]["enabled"] = True
                self.core.nodes[node_ip]["sync_path"] = ["all"]
        self.core.save_config(self.core.nodes, "nodes.json")

    def create_nodeid_to_address(self):
        result = {}
        for node_ip in self.core.nodes.keys():
            if "node_id" not in self.core.nodes[node_ip]:
                continue
            result[self.core.nodes[node_ip]["name"]] = node_ip
        return result

    def record_node_status(self):
        for node in self.core.node_name_address.keys():

            def fuc(name):
                print("[LOGGER] Logging node status of " + name)
                grid = self.core.tool_function.get_sgrid_node(name)
                if grid is None:
                    return
                result = grid.node_status()
                if result is None:
                    return
                result["date_time"] = datetime.now()
                self.status_cache[name] = result
                result["node"] = name
                self.core.mongo.insert_data("SGRID_node_stats", result)

                result = grid.container_stats()
                for container in result:
                    container["date_time"] = datetime.now()
                    container["node"] = name
                    self.container_stats[container["name"]] = container
                    self.core.mongo.insert_data("SGRID_container_stats", container)

            Thread(target=fuc, args=(node, )).start()

    def record_node_task(self):
        while True:
            self.record_node_status()
            time.sleep(60)
