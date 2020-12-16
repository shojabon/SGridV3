import traceback

from API.SResponse import SResponse
from starlette.responses import JSONResponse

from SGridNode.NodeMain import SGridV3Node
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
            if not self.core.tool_function.does_post_params_exist(json, ["master_key", "all", "name_only"]):
                return SResponse("params.lacking").web()
            if self.core.config["master_key"] != json["master_key"]:
                return SResponse("key.invalid").web()
            if type(json["all"]) != bool:
                return SResponse("params.lacking").web()
            if json["name_only"]:
                lis = [json_class.loads(json_class.dumps(x.__dict__, default=lambda o: '<not serializable>'))["attrs"]["Name"] for x in
                       self.core.docker.containers.list(json["all"])]
            else:
                lis = [json_class.loads(json_class.dumps(x.__dict__, default=lambda o: '<not serializable>')) for x in
                       self.core.docker.containers.list(json["all"])]
            return SResponse("success", lis).web()

        @self.core.fast_api.route("/docker/container/stats", methods=["POST"])
        async def container_stats(request: Request):
            json = await request.json()
            if not self.core.tool_function.does_post_params_exist(json, ["master_key"]):
                return SResponse("params.lacking").web()
            if self.core.config["master_key"] != json["master_key"]:
                return SResponse("key.invalid").web()
            try:
                result = []
                for container in self.core.docker.containers.list():
                    result.append(container.stats(stream=False))
                return SResponse("success", result).web()
            except Exception:
                return SResponse("internal.error").web()

        @self.core.fast_api.route("/docker/container/run", methods=["POST"])
        async def container_run(request: Request):
            json = await request.json()
            if not self.core.tool_function.does_post_params_exist(json, ["master_key", "image"]):
                return SResponse("params.lacking").web()
            if self.core.config["master_key"] != json["master_key"]:
                return SResponse("key.invalid").web()
            del json["master_key"]
            try:
                self.core.docker.containers.run(**json)
                return SResponse("success").web()
            except Exception:
                return SResponse("internal.error").web()

        @self.core.fast_api.route("/docker/container/stop", methods=["POST"])
        async def container_stop(request: Request):
            json = await request.json()
            if not self.core.tool_function.does_post_params_exist(json, ["master_key", "id"]):
                return SResponse("params.lacking").web()
            if self.core.config["master_key"] != json["master_key"]:
                return SResponse("key.invalid").web()
            try:
                self.core.docker.containers.get(json["id"]).stop()
                return SResponse("success").web()
            except Exception:
                return SResponse("internal.error").web()

        @self.core.fast_api.route("/docker/container/start", methods=["POST"])
        async def container_start(request: Request):
            json = await request.json()
            if not self.core.tool_function.does_post_params_exist(json, ["master_key", "id"]):
                return SResponse("params.lacking").web()
            if self.core.config["master_key"] != json["master_key"]:
                return SResponse("key.invalid").web()

            try:
                self.core.docker.containers.get(json["id"]).start()
                return JSONResponse({"body": "", "code": "Success"}, 200)
            except Exception:
                return SResponse("internal.error").web()

        @self.core.fast_api.route("/docker/image/list", methods=["POST"])
        async def image_list(request: Request):
            json = await request.json()
            if not self.core.tool_function.does_post_params_exist(json, ["master_key", "all"]):
                return SResponse("params.lacking").web()
            if self.core.config["master_key"] != json["master_key"]:
                return SResponse("key.invalid").web()
            if type(json["all"]) != bool:
                return SResponse("params.lacking").web()
            lis = [json_class.loads(json_class.dumps(x.__dict__, default=lambda o: '<not serializable>')) for x in self.core.docker.images.list(all=json["all"])]
            return SResponse("success", lis).web()

        @self.core.fast_api.route("/docker/image/build", methods=["POST"])
        async def image_build(request: Request):
            json = await request.json()
            if not self.core.tool_function.does_post_params_exist(json, ["master_key"]):
                return SResponse("params.lacking").web()
            if self.core.config["master_key"] != json["master_key"]:
                return SResponse("key.invalid").web()
            self.core.docker_function.load_images_from_sync()
            return SResponse("success").web()

        @self.core.fast_api.route("/docker/image/delete", methods=["POST"])
        async def image_delete(request: Request):
            json = await request.json()
            if not self.core.tool_function.does_post_params_exist(json, ["master_key", "image"]):
                return SResponse("params.lacking").web()
            if self.core.config["master_key"] != json["master_key"]:
                return SResponse("key.invalid").web()
            try:
                self.core.docker.images.remove(json["image"])
            except Exception:
                return SResponse("internal.error").web()
            return SResponse("success").web()

        @self.core.fast_api.route("/docker/container/execute", methods=["POST"])
        async def container_exec(request: Request):
            json = await request.json()
            if not self.core.tool_function.does_post_params_exist(json, ["master_key", "id", "command"]):
                return SResponse("params.lacking").web()
            if self.core.config["master_key"] != json["master_key"]:
                return SResponse("key.invalid").web()
            try:
                result = self.core.docker.containers.get(json["id"]).exec_run(cmd=json["command"], tty=True)
                return SResponse("success", result.output.decode("utf-8")).web()
            except Exception:
                return SResponse("internal.error").web()