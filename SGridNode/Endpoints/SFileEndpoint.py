import os
import shutil
import traceback
from datetime import datetime
from glob import glob
from threading import Thread

import boto3
from API.SResponse import SResponse
from slugify import slugify

from SGridNode.NodeMain import SGridV3Node
from fastapi import Request


class SFileEndpoint:
    def __init__(self, core: SGridV3Node):
        self.core = core
        self.register_endpoints()

    def register_endpoints(self):
        @self.core.fast_api.route("/sfile/list", methods=["POST"])
        async def sfile_list(request: Request):
            json = await request.json()
            if not self.core.tool_function.does_post_params_exist(json, ["master_key", "path"]):
                return SResponse("params.lacking").web()
            if self.core.config["master_key"] != json["master_key"]:
                return SResponse("key.invalid").web()
            path = "data_dir/ftp_data/" + json["path"]
            if path != "" and path[-1] != "/":
                path += "/"
            if not os.path.exists(path) and path != "":
                return SResponse("path.invalid").web()
            return SResponse("success", [str(x).replace("\\", "/")[len(path):] for x in glob(path + "*")]).web()

        @self.core.fast_api.route("/sfile/rm/directory", methods=["POST"])
        async def sfile_rm_directory(request: Request):
            json = await request.json()
            if not self.core.tool_function.does_post_params_exist(json, ["master_key", "path"]):
                return SResponse("params.lacking").web()
            if self.core.config["master_key"] != json["master_key"]:
                return SResponse("key.invalid").web()
            path = "data_dir/ftp_data/" + json["path"]
            if path != "" and path[-1] != "/":
                path += "/"
            if not os.path.exists(path) and os.path.isfile(path):
                return SResponse("path.invalid").web()
            try:
                os.removedirs(path)
            except Exception:
                print(traceback.format_exc())
                return SResponse("internal.error").web()
            return SResponse("success").web()

        @self.core.fast_api.route("/sfile/file/get", methods=["POST"])
        async def sfile_file_get(request: Request):
            json = await request.json()
            if not self.core.tool_function.does_post_params_exist(json, ["master_key", "path"]):
                return SResponse("params.lacking").web()
            if self.core.config["master_key"] != json["master_key"]:
                return SResponse("key.invalid").web()
            path = "data_dir/ftp_data/" + json["path"]
            if path != "" and path[-1] == "/":
                path = path[:-1]
            if not os.path.exists(path) and not os.path.isfile(path):
                return SResponse("path.invalid").web()
            try:
                file = open(path, "r")
                result = file.read().split("\n")
                file.close()
                return SResponse("success", result).web()
            except Exception:
                print(traceback.format_exc())
                return SResponse("internal.error").web()

        @self.core.fast_api.route("/sfile/file/set", methods=["POST"])
        async def sfile_file_set(request: Request):
            json = await request.json()
            if not self.core.tool_function.does_post_params_exist(json, ["master_key", "path", "data"]):
                return SResponse("params.lacking").web()
            if self.core.config["master_key"] != json["master_key"]:
                return SResponse("key.invalid").web()
            path = "data_dir/ftp_data/" + json["path"]
            if path != "" and path[-1] == "/":
                path = path[:-1]

            file_name = path.split("/")[-1]
            if file_name == "":
                return SResponse("name.invalid").web()
            if os.path.exists(path) and not os.path.isfile(path):
                return SResponse("path.invalid").web()
            try:
                file = open(path, "w+")
                file.writelines(json["data"])
                file.close()
                return SResponse("success").web()
            except Exception:
                print(traceback.format_exc())
                return SResponse("internal.error").web()

        @self.core.fast_api.route("/sfile/file/rename", methods=["POST"])
        async def sfile_file_rename(request: Request):
            json = await request.json()
            if not self.core.tool_function.does_post_params_exist(json, ["master_key", "path", "name"]):
                return SResponse("params.lacking").web()
            if self.core.config["master_key"] != json["master_key"]:
                return SResponse("key.invalid").web()
            path = "data_dir/ftp_data/" + json["path"]
            if path != "" and path[-1] == "/":
                path = path[:-1]

            file_name = path.split("/")[-1]
            if file_name == "":
                return SResponse("name.invalid").web()
            if os.path.exists(path) and not os.path.isfile(path):
                return SResponse("path.invalid").web()
            new_path = ""
            for x in path.split("/")[:-1]:
                new_path += str(x) + "/"
            new_path += str(json["name"]).split("/")[-1]
            try:
                os.rename(path, new_path)
                return SResponse("success").web()
            except Exception:
                print(traceback.format_exc())
                return SResponse("internal.error").web()

        @self.core.fast_api.route("/sfile/rm/file", methods=["POST"])
        async def sfile_rm_file(request: Request):
            json = await request.json()
            if not self.core.tool_function.does_post_params_exist(json, ["master_key", "path"]):
                return SResponse("params.lacking").web()
            if self.core.config["master_key"] != json["master_key"]:
                return SResponse("key.invalid").web()
            path = "data_dir/ftp_data/" + json["path"]
            if path != "" and path[-1] == "/":
                path = path[:-1]

            file_name = path.split("/")[-1]
            if file_name == "":
                return SResponse("name.invalid").web()
            if os.path.exists(path) and not os.path.isfile(path):
                return SResponse("path.invalid").web()
            try:
                os.remove(path)
                return SResponse("success").web()
            except Exception:
                print(traceback.format_exc())
                return SResponse("internal.error").web()
