import traceback

from API.SResponse import SResponse

from SGridNode.NodeMain import SGridV3Node
from fastapi import Request


class FTPClientEndpoint:
    def __init__(self, core: SGridV3Node):
        self.core = core
        self.register_endpoints()

    def register_endpoints(self):
        @self.core.fast_api.route("/ftp/users/set", methods=["POST"])
        async def ftp_user_set(request: Request):
            json = await request.json()
            if not self.core.tool_function.does_post_params_exist(json, ["master_key", "users"]):
                return SResponse("params.lacking").web()
            if self.core.config["master_key"] != json["master_key"]:
                return SResponse("key.invalid").web()
            if type(json["users"]) != dict:
                return SResponse("params.lacking").web()

            self.core.ftp_users = json["users"]
            self.core.ftp_function.load_users()

            return SResponse("success").web()
