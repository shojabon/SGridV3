import traceback

from starlette.responses import JSONResponse

from SGridMaster.main import SGridV3Master
from fastapi import Request

class DockerEndpoint:

    def __init__(self, core: SGridV3Master):
        self.core = core
        self.register_endpoints()

    def register_endpoints(self):
        @self.core.fast_api.route("/docker/container/run", methods=["POST"])
        async def container_run(request: Request):
            json = await request.json()
            if not self.core.tool_function.does_post_params_exist(json, ["master_key", "node", "image"]):
                return JSONResponse({"body": "Not Enough Params", "code": "params.not_enough"}, 400)
            if self.core.config["master_key"] != json["master_key"]:
                return JSONResponse({"body": "Credentials Invalid", "code": "credentials.invalid"}, 401)
            if not self.core.tool_function.is_node(json["node"]):
                return JSONResponse({"body": "Node Not Valid", "code": "error.internal"}, 500)
            try:
                sgrid = self.core.tool_function.get_sgrid_node(json["node"])
                del json["node"]
                result = sgrid.container_run(**json)
                if not result:
                    return JSONResponse({"body": "Internal Error", "code": "error.internal"}, 500)
            except Exception:
                return JSONResponse({"body": "Internal Error", "code": "error.internal"}, 500)
            return JSONResponse({"body": "", "code": "Success"}, 200)

        @self.core.fast_api.route("/docker/container/stop", methods=["POST"])
        async def container_stop(request: Request):
            json = await request.json()
            if not self.core.tool_function.does_post_params_exist(json, ["master_key", "node", "container"]):
                return JSONResponse({"body": "Not Enough Params", "code": "params.not_enough"}, 400)
            if self.core.config["master_key"] != json["master_key"]:
                return JSONResponse({"body": "Credentials Invalid", "code": "credentials.invalid"}, 401)
            if not self.core.tool_function.is_node(json["node"]):
                return JSONResponse({"body": "Node Not Valid", "code": "error.internal"}, 500)
            try:
                sgrid = self.core.tool_function.get_sgrid_node(json["node"])
                result = sgrid.container_stop(json["container"])
                if not result:
                    return JSONResponse({"body": "Internal Error", "code": "error.internal"}, 500)
            except Exception:
                return JSONResponse({"body": "Internal Error", "code": "error.internal"}, 500)
            return JSONResponse({"body": "", "code": "Success"}, 200)

        @self.core.fast_api.route("/docker/container/start", methods=["POST"])
        async def container_start(request: Request):
            json = await request.json()
            if not self.core.tool_function.does_post_params_exist(json, ["master_key", "node", "container"]):
                return JSONResponse({"body": "Not Enough Params", "code": "params.not_enough"}, 400)
            if self.core.config["master_key"] != json["master_key"]:
                return JSONResponse({"body": "Credentials Invalid", "code": "credentials.invalid"}, 401)
            if not self.core.tool_function.is_node(json["node"]):
                return JSONResponse({"body": "Node Not Valid", "code": "error.internal"}, 500)
            try:
                sgrid = self.core.tool_function.get_sgrid_node(json["node"])
                result = sgrid.container_start(json["container"])
                if not result:
                    return JSONResponse({"body": "Internal Error", "code": "error.internal"}, 500)
            except Exception:
                return JSONResponse({"body": "Internal Error", "code": "error.internal"}, 500)
            return JSONResponse({"body": "", "code": "Success"}, 200)