import traceback

from API.SResponse import SResponse
from starlette.responses import JSONResponse

from MasterMain import SGridV3Master
from fastapi import Request

class NodeEndpoint:

    def __init__(self, core: SGridV3Master):
        self.core = core
        self.register_endpoints()

    def register_endpoints(self):
        @self.core.fast_api.route("/node/list", methods=["POST"])
        async def node_list(request: Request):
            json = await request.json()
            if not self.core.tool_function.does_post_params_exist(json, ["master_key"]):
                return SResponse("params.lacking").web()
            if self.core.config["master_key"] != json["master_key"]:
                return SResponse("key.invalid").web()
            try:
                result = {}
                for node_address in self.core.nodes.keys():
                    node_name = self.core.node_address_name[node_address]
                    temp_dict = self.core.nodes[node_address].copy()
                    temp_dict["address"] = node_address
                    result[node_name] = temp_dict

                return SResponse("success", result).web()
            except Exception:
                return SResponse("internal.error").web()
