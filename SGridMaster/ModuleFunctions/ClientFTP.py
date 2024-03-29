from MasterMain import SGridV3Master


class ClientFTPFunction:

    def __init__(self, core: SGridV3Master):
        self.core = core

    def user_add(self, node: str, user: str, password: str, limit_mb: int):
        if not self.core.tool_function.is_node(node):
            return False
        node_address = self.core.tool_function.get_node_address(node)
        self.core.nodes[node_address]["ftp_users"][user] = {
            "password": password,
            "limit_mb": limit_mb
        }
        self.core.save_config(self.core.nodes, "nodes.json")
        grid = self.core.tool_function.get_sgrid_node(node)
        if grid is None:
            return False
        grid.ftp_user_set(self.core.nodes[node_address]["ftp_users"])
        return True

    def user_remove(self, node: str, user: str):
        pass

    def user_clear(self, node: str):
        pass
