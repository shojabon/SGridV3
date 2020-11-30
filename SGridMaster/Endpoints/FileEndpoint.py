import traceback

from starlette.responses import JSONResponse

from SGridMaster.main import SGridV3Master
from fastapi import Request

class FileEndpoint:

    def __init__(self, core: SGridV3Master):
        self.core = core
        self.register_endpoints()

        self.dir_cache = {}

    def getFilteredFilenames(self, file_names):
        if len(file_names) == 0:
            start = ''
        else:
            start = file_names[-1]

        response = self.core.boto.list_objects_v2(
            Bucket="testdevbucket",
            Prefix=start
        )
        if 'Contents' in response:
            file_names = [content['Key'] for content in response['Contents']]
            if 'IsTruncated' in response and response["IsTruncated"]:
                return self.getFilteredFilenames(file_names)
        return file_names

    def register_endpoints(self):
        @self.core.fast_api.route("/file/backup/list", methods=["POST"])
        async def backup_list(request: Request):
            json = await request.json()
            if not self.core.tool_function.does_post_params_exist(json, ["master_key", "user"]):
                return JSONResponse({"body": "Not Enough Params", "code": "params.not_enough"}, 400)
            if self.core.config["master_key"] != json["master_key"]:
                return JSONResponse({"body": "Credentials Invalid", "code": "credentials.invalid"}, 401)
            if json["user"] in self.dir_cache.keys():
                return JSONResponse({"body": self.dir_cache[json["user"]], "code": "Success"}, 200)
            try:
                result = [x[len("backup/" + str(json["user"])) + 1:] for x in self.getFilteredFilenames(["backup/" + str(json["user"])])]
                self.dir_cache[json["user"]] = result
                return JSONResponse({"body": result, "code": "Success"}, 200)
            except Exception:
                return JSONResponse({"body": "Internal Error", "code": "error.internal"}, 500)

        @self.core.fast_api.route("/file/backup/save", methods=["POST"])
        async def backup_save(request: Request):
            json = await request.json()
            if not self.core.tool_function.does_post_params_exist(json, ["master_key", "user", "node"]):
                return JSONResponse({"body": "Not Enough Params", "code": "params.not_enough"}, 400)
            if self.core.config["master_key"] != json["master_key"]:
                return JSONResponse({"body": "Credentials Invalid", "code": "credentials.invalid"}, 401)
            if not self.core.tool_function.is_node(json["node"]):
                return JSONResponse({"body": "Node Not Valid", "code": "error.internal"}, 500)
            if json["user"] in self.dir_cache.keys():
                return JSONResponse({"body": self.dir_cache[json["user"]], "code": "Success"}, 200)
            try:
                sgrid = self.core.tool_function.get_sgrid_node(json["node"])
                result = sgrid.backup_save(json["user"])
                if not result:
                    return JSONResponse({"body": "Internal Error", "code": "error.internal"}, 500)
                if json["user"] in self.dir_cache:
                    del self.dir_cache[json["user"]]
                return JSONResponse({"body": "", "code": "Success"}, 200)
            except Exception:
                return JSONResponse({"body": "Internal Error", "code": "error.internal"}, 500)

        @self.core.fast_api.route("/file/backup/load", methods=["POST"])
        async def backup_load(request: Request):
            json = await request.json()
            if not self.core.tool_function.does_post_params_exist(json, ["master_key", "user", "node", "key"]):
                return JSONResponse({"body": "Not Enough Params", "code": "params.not_enough"}, 400)
            if self.core.config["master_key"] != json["master_key"]:
                return JSONResponse({"body": "Credentials Invalid", "code": "credentials.invalid"}, 401)
            if not self.core.tool_function.is_node(json["node"]):
                return JSONResponse({"body": "Node Not Valid", "code": "error.internal"}, 500)
            if json["user"] in self.dir_cache.keys():
                return JSONResponse({"body": self.dir_cache[json["user"]], "code": "Success"}, 200)
            try:
                sgrid = self.core.tool_function.get_sgrid_node(json["node"])
                result = sgrid.backup_load(json["user"], json["key"])
                if not result:
                    return JSONResponse({"body": "Internal Error", "code": "error.internal"}, 500)
                return JSONResponse({"body": "", "code": "Success"}, 200)
            except Exception:
                return JSONResponse({"body": "Internal Error", "code": "error.internal"}, 500)

        @self.core.fast_api.route("/file/nuke/", methods=["POST"])
        async def backup_load(request: Request):
            json = await request.json()
            if not self.core.tool_function.does_post_params_exist(json, ["master_key", "user", "node"]):
                return JSONResponse({"body": "Not Enough Params", "code": "params.not_enough"}, 400)
            if self.core.config["master_key"] != json["master_key"]:
                return JSONResponse({"body": "Credentials Invalid", "code": "credentials.invalid"}, 401)
            if not self.core.tool_function.is_node(json["node"]):
                return JSONResponse({"body": "Node Not Valid", "code": "error.internal"}, 500)
            if json["user"] in self.dir_cache.keys():
                return JSONResponse({"body": self.dir_cache[json["user"]], "code": "Success"}, 200)
            try:
                sgrid = self.core.tool_function.get_sgrid_node(json["node"])
                result = sgrid.nuke_user(json["user"])
                if not result:
                    return JSONResponse({"body": "Internal Error", "code": "error.internal"}, 500)
                return JSONResponse({"body": "", "code": "Success"}, 200)
            except Exception:
                return JSONResponse({"body": "Internal Error", "code": "error.internal"}, 500)
