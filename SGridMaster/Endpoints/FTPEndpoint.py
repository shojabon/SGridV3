import traceback

from API.SResponse import SResponse
from starlette.responses import JSONResponse

from MasterMain import SGridV3Master
from fastapi import Request

class FTPEndpoint:

    def __init__(self, core: SGridV3Master):
        self.core = core
        self.register_endpoints()

    def register_endpoints(self):
        @self.core.fast_api.route("/ftp/user/add", methods=["POST"])
        async def ftp_user_add(request: Request):
            json = await request.json()
            if not self.core.tool_function.does_post_params_exist(json, ["master_key", "node", "user", "password", "limit_mb"]):
                return SResponse("params.lacking").web()
            if self.core.config["master_key"] != json["master_key"]:
                return SResponse("key.invalid").web()
            if not self.core.tool_function.is_node(json["node"]):
                return SResponse("node.invalid").web()
            try:
                address = self.core.node_name_address[json["node"]]
                if "ftp_users" not in self.core.nodes[address]:
                    return SResponse("node.not.initialized").web()
                self.core.nodes[address]["ftp_users"][json["user"]] = {
                    "password": json["password"],
                    "limit_mb": json["limit_mb"],
                }
                self.core.save_config(self.core.nodes, "nodes.json")
                grid = self.core.tool_function.get_sgrid_node(json["node"])
                if grid is None:
                    return SResponse("node.invalid").web()
                return grid.ftp_user_set(self.core.nodes[address]["ftp_users"]).web()
            except Exception:
                return SResponse("internal.error").web()

        @self.core.fast_api.route("/ftp/user/remove", methods=["POST"])
        async def ftp_user_remove(request: Request):
            json = await request.json()
            if not self.core.tool_function.does_post_params_exist(json, ["master_key", "node", "user"]):
                return SResponse("params.lacking").web()
            if self.core.config["master_key"] != json["master_key"]:
                return SResponse("key.invalid").web()
            if not self.core.tool_function.is_node(json["node"]):
                return SResponse("node.invalid").web()
            try:
                address = self.core.node_name_address[json["node"]]
                if "ftp_users" not in self.core.nodes[address]:
                    return SResponse("node.not.initialized").web()
                del self.core.nodes[address]["ftp_users"][json["user"]]
                self.core.save_config(self.core.nodes, "nodes.json")
                grid = self.core.tool_function.get_sgrid_node(json["node"])
                if grid is None:
                    return SResponse("node.invalid").web()
                return grid.ftp_user_set(self.core.nodes[address]["ftp_users"]).web()
            except Exception:
                return SResponse("internal.error").web()

        @self.core.fast_api.route("/ftp/user/list", methods=["POST"])
        async def ftp_user_list(request: Request):
            json = await request.json()
            if not self.core.tool_function.does_post_params_exist(json, ["master_key"]):
                return SResponse("params.lacking").web()
            if self.core.config["master_key"] != json["master_key"]:
                return SResponse("key.invalid").web()
            try:
                result = {}
                for node_address in self.core.nodes.keys():
                    if "ftp_users" in self.core.nodes[node_address]:
                        result[self.core.node_address_name[node_address]] = self.core.nodes[node_address]["ftp_users"]
                return SResponse("success", result).web()
            except Exception:
                return SResponse("internal.error").web()
