import traceback

from starlette.responses import JSONResponse

from SGridNode.main import SGridV3Node
from fastapi import Request
import json as json_class


class FTPClientEndpoint:
    def __init__(self, core: SGridV3Node):
        self.core = core
        self.register_endpoints()

    def register_endpoints(self):
        @self.core.fast_api.route("/ftp/users/set", methods=["POST"])
        async def ftp_user_set(request: Request):
            json = await request.json()
            if not self.core.tool_function.does_post_params_exist(json, ["master_key", "users"]):
                return JSONResponse({"body": "Not Enough Params", "code": "params.not_enough"}, 400)
            if self.core.config["master_key"] != json["master_key"]:
                return JSONResponse({"body": "Credentials Invalid", "code": "credentials.invalid"}, 401)
            if type(json["users"]) != dict:
                return JSONResponse({"body": "Not Enough Params", "code": "params.not_enough"}, 400)

            self.core.ftp_users = json["users"]
            self.core.ftp_function.load_users()

            return JSONResponse({"body": "", "code": "Success"}, 200)