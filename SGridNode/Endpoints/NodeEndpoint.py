import psutil
from starlette.responses import JSONResponse

from SGridNode.main import SGridV3Node
from fastapi import Request

class NodeEndpoint:

    def __init__(self, core: SGridV3Node):
        self.core = core
        self.register_endpoints()

    def register_endpoints(self):
        @self.core.fast_api.route("/node/info/", methods=["POST"])
        async def node_info(request: Request):
            json = await request.json()
            if not self.core.tool_function.does_post_params_exist(json, ["master_key"]):
                return JSONResponse({"body": "Not Enough Params", "code": "params.not_enough"}, 400)
            if self.core.config["master_key"] != json["master_key"]:
                return JSONResponse({"body": "Credentials Invalid", "code": "credentials.invalid"}, 401)
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
            return JSONResponse({"body": data, "code": "Success"}, 200)

        @self.core.fast_api.route("/node/status/", methods=["POST"])
        async def node_status(request: Request):
            json = await request.json()
            if not self.core.tool_function.does_post_params_exist(json, ["master_key"]):
                return JSONResponse({"body": "Not Enough Params", "code": "params.not_enough"}, 400)
            if self.core.config["master_key"] != json["master_key"]:
                return JSONResponse({"body": "Credentials Invalid", "code": "credentials.invalid"}, 401)
            net_usage, disk_usage, cpu_usage = self.core.tool_function.net_usage(), self.core.tool_function.disk_usage(), psutil.cpu_percent(interval=1, percpu=True)
            data = {
                "cpu_usage": cpu_usage,
                "ram_usage": psutil.virtual_memory().percent,
                "swap_usage": psutil.swap_memory().percent,
                "users": psutil.users(),
                "net_usage": net_usage,
                "disk_usage": disk_usage
            }
            return JSONResponse({"body": data, "code": "Success"}, 200)