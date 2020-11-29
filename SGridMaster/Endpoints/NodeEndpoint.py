import traceback

from starlette.responses import JSONResponse

from SGridMaster.main import SGridV3Master
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
                return JSONResponse({"body": "Not Enough Params", "code": "params.not_enough"}, 400)
            if self.core.config["master_key"] != json["master_key"]:
                return JSONResponse({"body": "Credentials Invalid", "code": "credentials.invalid"}, 401)
            try:
                result = {}
                for node_address in self.core.nodes.keys():
                    node_name = self.core.node_address_name[node_address]
                    temp_dict = self.core.nodes[node_address].copy()
                    temp_dict["address"] = node_address
                    result[node_name] = temp_dict

                return JSONResponse({"body": result, "code": "Success"}, 200)
            except Exception:
                return JSONResponse({"body": "Internal Error", "code": "error.internal"}, 500)