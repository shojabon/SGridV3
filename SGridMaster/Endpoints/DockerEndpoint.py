import traceback
from datetime import datetime

from API.SResponse import SResponse
from starlette.responses import JSONResponse

from MasterMain import SGridV3Master
from fastapi import Request

class DockerEndpoint:

    def __init__(self, core: SGridV3Master):
        self.core = core
        self.register_endpoints()

        self.container_list_cache = {}
        self.container_list_time_cache = {}

    def register_endpoints(self):
        @self.core.fast_api.route("/docker/container/run", methods=["POST"])
        async def container_run(request: Request):
            json = await request.json()
            if not self.core.tool_function.does_post_params_exist(json, ["master_key", "node", "image"]):
                return SResponse("params.lacking").web()
            if self.core.config["master_key"] != json["master_key"]:
                return SResponse("key.invalid").web()
            if not self.core.tool_function.is_node(json["node"]):
                return SResponse("node.invalid").web()
            try:
                sgrid = self.core.tool_function.get_sgrid_node(json["node"])
                del json["node"]
                return sgrid.container_run(**json).web()
            except Exception:
                return SResponse("internal.error").web()

        @self.core.fast_api.route("/docker/container/stop", methods=["POST"])
        async def container_stop(request: Request):
            json = await request.json()
            if not self.core.tool_function.does_post_params_exist(json, ["master_key", "node", "container"]):
                return SResponse("params.lacking").web()
            if self.core.config["master_key"] != json["master_key"]:
                return SResponse("key.invalid").web()
            if not self.core.tool_function.is_node(json["node"]):
                return SResponse("node.invalid").web()
            try:
                sgrid = self.core.tool_function.get_sgrid_node(json["node"])
                return sgrid.container_stop(json["container"]).web()
            except Exception:
                return SResponse("internal.error").web()

        @self.core.fast_api.route("/docker/container/start", methods=["POST"])
        async def container_start(request: Request):
            json = await request.json()
            if not self.core.tool_function.does_post_params_exist(json, ["master_key", "node", "container"]):
                return SResponse("params.lacking").web()
            if self.core.config["master_key"] != json["master_key"]:
                return SResponse("key.invalid").web()
            if not self.core.tool_function.is_node(json["node"]):
                return SResponse("node.invalid").web()
            try:
                sgrid = self.core.tool_function.get_sgrid_node(json["node"])
                return sgrid.container_start(json["container"]).web()
            except Exception:
                return SResponse("internal.error").web()

        @self.core.fast_api.route("/docker/container/list", methods=["POST"])
        async def container_list(request: Request):
            json = await request.json()
            if not self.core.tool_function.does_post_params_exist(json, ["master_key", "node", "name_only"]):
                return SResponse("params.lacking").web()
            if self.core.config["master_key"] != json["master_key"]:
                return SResponse("key.invalid").web()
            if not self.core.tool_function.is_node(json["node"]):
                return SResponse("node.invalid").web()
            node = json["node"]
            if node in self.container_list_time_cache.keys() and node in self.container_list_cache.keys() and datetime.now().timestamp() - self.container_list_time_cache[node] < 1:
                return SResponse("success", self.container_list_cache[node]).web()

            try:
                sgrid = self.core.tool_function.get_sgrid_node(json["node"])
                result = sgrid.container_list(name_only=json["name_only"])
                if result.fail():
                    return result.web()
                self.container_list_cache[node] = result
                self.container_list_time_cache[node] = datetime.now().timestamp()
                return result.web()
            except Exception:
                return SResponse("internal.error").web()

        @self.core.fast_api.route("/docker/container/execute", methods=["POST"])
        async def container_start(request: Request):
            json = await request.json()
            if not self.core.tool_function.does_post_params_exist(json, ["master_key", "node", "container", "command"]):
                return SResponse("params.lacking").web()
            if self.core.config["master_key"] != json["master_key"]:
                return SResponse("key.invalid").web()
            if not self.core.tool_function.is_node(json["node"]):
                return SResponse("node.invalid").web()
            try:
                sgrid = self.core.tool_function.get_sgrid_node(json["node"])
                return sgrid.container_exec(json["container"], json["command"]).web()
            except Exception:
                return SResponse("internal.error").web()