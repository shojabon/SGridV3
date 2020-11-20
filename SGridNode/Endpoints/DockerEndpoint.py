from starlette.responses import JSONResponse

from SGridNode.main import SGridV3Node
from fastapi import Request
import json as json_class


class DockerEndpoint:

    def __init__(self, core: SGridV3Node):
        self.core = core
        self.register_endpoints()

    def register_endpoints(self):
        @self.core.fast_api.route("/docker/container/list", methods=["POST"])
        async def container_list(request: Request):
            json = await request.json()
            if not self.core.tool_function.does_post_params_exist(json, ["master_key", "all"]):
                return JSONResponse({"body": "Not Enough Params", "code": "params.not_enough"}, 400)
            if self.core.config["master_key"] != json["master_key"]:
                return JSONResponse({"body": "Credentials Invalid", "code": "credentials.invalid"}, 401)
            if type(json["all"]) != bool:
                return JSONResponse({"body": "Not Enough Params", "code": "params.not_enough"}, 400)
            lis = [json_class.loads(json_class.dumps(x.__dict__, default=lambda o: '<not serializable>')) for x in self.core.docker.containers.list(json["all"])]
            return JSONResponse({"body": lis, "code": "Success"}, 200)

        @self.core.fast_api.route("/docker/container/stats", methods=["POST"])
        async def container_stats(request: Request):
            json = await request.json()
            if not self.core.tool_function.does_post_params_exist(json, ["master_key"]):
                return JSONResponse({"body": "Not Enough Params", "code": "params.not_enough"}, 400)
            if self.core.config["master_key"] != json["master_key"]:
                return JSONResponse({"body": "Credentials Invalid", "code": "credentials.invalid"}, 401)

            result = []
            for container in self.core.docker.containers.list():
                result.append(container.stats(stream=False))

            return JSONResponse({"body": result, "code": "Success"}, 200)
