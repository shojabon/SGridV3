from SGridNode.main import SGridV3Node
import psutil

class NodeFunction:

    def __init__(self, core: SGridV3Node):
        self.core = core

    def node_info(self):
        data = {
            "node_id": self.core.config["node_id"],
            "name": self.core.config["name"],
            "region": self.core.config["region"],
            "tag": self.core.config["tag"],
            "cpu_logical": psutil.cpu_count(True),
            "cpu_physical": psutil.cpu_count(False),
            "ram": round(psutil.virtual_memory().total / 1024 / 1024),
            "swap": round(psutil.swap_memory().total / 1024 / 1024)
        }
        return data