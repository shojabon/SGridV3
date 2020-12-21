import traceback
from datetime import datetime

from API.SResponse import SResponse
from starlette.responses import JSONResponse

from MasterMain import SGridV3Master
from fastapi import Request

class FileEndpoint:

    def __init__(self, core: SGridV3Master):
        self.core = core
        self.register_endpoints()

        self.dir_cache = {}
        self.dir_time = {}

    def getFilteredFilenames(self, bucket_name, file_names):
        if len(file_names) == 0:
            start = ''
        else:
            if type(file_names[-1]) == dict:
                start = file_names[-1]["Key"]
            else:
                start = file_names[-1]

        response = self.core.boto.list_objects_v2(
            Bucket=bucket_name,
            Prefix=start
        )
        if 'Contents' in response:
            file_names = response["Contents"]
            if 'IsTruncated' in response and response["IsTruncated"]:
                response = self.getFilteredFilenames(bucket_name, response)
                [file_names.append(x) for x in response]
                return file_names
        return file_names

    def register_endpoints(self):
        @self.core.fast_api.route("/file/backup/list", methods=["POST"])
        async def backup_list(request: Request):
            json = await request.json()
            if not self.core.tool_function.does_post_params_exist(json, ["master_key", "user", "cache"]):
                return SResponse("params.lacking").web()
            if self.core.config["master_key"] != json["master_key"]:
                return SResponse("key.invalid").web()
            if json["cache"] and json["user"] in self.dir_cache.keys() and json["user"] in self.dir_time.keys() and round(datetime.now().timestamp() - self.dir_time[json["user"]]) < 10:
                return SResponse("success", self.dir_cache[json["user"]]).web()
            try:
                result = []
                for x in self.getFilteredFilenames(self.core.config["object_storage_info"]["bucket"],
                                                   ["backup/" + str(json["user"])]):
                    if x == "backup/" + str(json["user"]):
                        continue
                    result.append(x["Key"][len("backup/" + str(json["user"])) + 1:])
                self.dir_cache[json["user"]] = result
                self.dir_time[json["user"]] = round(datetime.now().timestamp())
                return SResponse("success", result).web()
            except Exception:
                print(traceback.format_exc())
                return SResponse("internal.error").web()

        @self.core.fast_api.route("/file/backup/final", methods=["POST"])
        async def backup_final(request: Request):
            json = await request.json()
            if not self.core.tool_function.does_post_params_exist(json, ["master_key", "user", "node"]):
                return SResponse("params.lacking").web()
            if self.core.config["master_key"] != json["master_key"]:
                return SResponse("key.invalid").web()
            if not self.core.tool_function.is_node(json["node"]):
                return SResponse("node.invalid").web()
            try:
                sgrid = self.core.tool_function.get_sgrid_node(json["node"])
                result = sgrid.backup_final(json["user"])
                if result.fail():
                    return result.web()
                return SResponse("success").web()
            except Exception:
                return SResponse("internal.error").web()

        @self.core.fast_api.route("/file/backup/save", methods=["POST"])
        async def backup_save(request: Request):
            json = await request.json()
            if not self.core.tool_function.does_post_params_exist(json, ["master_key", "user", "node", "key"]):
                return SResponse("params.lacking").web()
            if self.core.config["master_key"] != json["master_key"]:
                return SResponse("key.invalid").web()
            if not self.core.tool_function.is_node(json["node"]):
                return SResponse("node.invalid").web()
            try:
                sgrid = self.core.tool_function.get_sgrid_node(json["node"])
                result = sgrid.backup_save(json["user"], json["key"])
                if result.fail():
                    return result.web()
                if json["user"] in self.dir_cache:
                    del self.dir_cache[json["user"]]
                return SResponse("success").web()
            except Exception:
                return SResponse("internal.error").web()

        @self.core.fast_api.route("/file/backup/load", methods=["POST"])
        async def backup_load(request: Request):
            json = await request.json()
            if not self.core.tool_function.does_post_params_exist(json, ["master_key", "user", "node", "key"]):
                return SResponse("params.lacking").web()
            if self.core.config["master_key"] != json["master_key"]:
                return SResponse("key.invalid").web()
            if not self.core.tool_function.is_node(json["node"]):
                return SResponse("node.invalid").web()
            try:
                sgrid = self.core.tool_function.get_sgrid_node(json["node"])
                return sgrid.backup_load(json["user"], json["key"]).web()
            except Exception:
                return SResponse("internal.error").web()

        @self.core.fast_api.route("/file/nuke/", methods=["POST"])
        async def nuke_user(request: Request):
            json = await request.json()
            if not self.core.tool_function.does_post_params_exist(json, ["master_key", "user", "node"]):
                return SResponse("params.lacking").web()
            if self.core.config["master_key"] != json["master_key"]:
                return SResponse("key.invalid").web()
            if not self.core.tool_function.is_node(json["node"]):
                return SResponse("node.invalid").web()
            try:
                sgrid = self.core.tool_function.get_sgrid_node(json["node"])
                result = sgrid.nuke_user(json["user"])
                if result.fail():
                    return result.web()
                return SResponse("success").web()
            except Exception:
                return SResponse("internal.error").web()

        @self.core.fast_api.route("/file/backup/delete", methods=["POST"])
        async def backup_delete(request: Request):
            json = await request.json()
            if not self.core.tool_function.does_post_params_exist(json, ["master_key", "user", "key"]):
                return SResponse("params.lacking").web()
            if self.core.config["master_key"] != json["master_key"]:
                return SResponse("key.invalid").web()
            try:
                self.core.boto.delete_object(Bucket=self.core.config["object_storage_info"]["bucket"], Key="backup/" + str(json["user"]) + "/" + str(json["user"]) + "-" + str(json["key"]) + ".zip")
                if json["user"] in self.dir_cache:
                    del self.dir_cache[json["user"]]
                return SResponse("success").web()
            except Exception:
                if json["user"] in self.dir_cache:
                    del self.dir_cache[json["user"]]
                return SResponse("internal.error").web()

        @self.core.fast_api.route("/file/unzip", methods=["POST"])
        async def file_unzip(request: Request):
            json = await request.json()
            if not self.core.tool_function.does_post_params_exist(json, ["master_key", "node", "target", "destination"]):
                return SResponse("params.lacking").web()
            if self.core.config["master_key"] != json["master_key"]:
                return SResponse("key.invalid").web()
            if not self.core.tool_function.is_node(json["node"]):
                return SResponse("node.invalid").web()
            try:
                sgrid = self.core.tool_function.get_sgrid_node(json["node"])
                return sgrid.file_unzip(json["target"], json["destination"]).web()
            except Exception:
                return SResponse("internal.error").web()
