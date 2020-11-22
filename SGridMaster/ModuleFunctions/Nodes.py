from SGridMaster.main import SGridV3Master
from SGridNode.SGridV3NodeAPI import SGridV3NodeAPI


class NodeFunction:

    def __init__(self, core: SGridV3Master):
        self.core = core

    def register_new_nodes(self):
        for node_ip in self.core.nodes.keys():
            if "node_id" not in self.core.nodes[node_ip]:
                grid_api = SGridV3NodeAPI(self.core.config["master_key"], node_ip)
                info = grid_api.node_info()
                if info is None:
                    continue
                self.core.nodes[node_ip] = info
                self.core.nodes[node_ip]["enabled"] = True
        self.core.save_config(self.core.nodes, "nodes.json")