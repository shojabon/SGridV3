import os
import traceback
from threading import Thread

import boto3
from starlette.responses import JSONResponse

from SGridNode.main import SGridV3Node
from fastapi import Request
import json as json_class


class FileEndpoint:
    def __init__(self, core: SGridV3Node):
        self.core = core
        self.register_endpoints()

        self.current_task = []

    def register_endpoints(self):
        @self.core.fast_api.route("/file/setting/set", methods=["POST"])
        async def object_setting_set(request: Request):
            json = await request.json()
            if not self.core.tool_function.does_post_params_exist(json, ["master_key", "settings"]):
                return JSONResponse({"body": "Not Enough Params", "code": "params.not_enough"}, 400)
            if self.core.config["master_key"] != json["master_key"]:
                return JSONResponse({"body": "Credentials Invalid", "code": "credentials.invalid"}, 401)
            if type(json["settings"]) != dict:
                return JSONResponse({"body": "Not Enough Params", "code": "params.not_enough"}, 400)
            if self.core.object_storage_setting != json["settings"]:
                self.core.object_storage_setting = json["settings"]
                sess = boto3.Session(aws_access_key_id=json["settings"]["access_key"],
                                     aws_secret_access_key=json["settings"]["secret_access_key"])
                self.core.boto = sess.client('s3', endpoint_url=json["settings"]["endpoint_url"])
            return JSONResponse({"body": "", "code": "Success"}, 200)

        @self.core.fast_api.route("/file/backup/save", methods=["POST"])
        async def backup_save(request: Request):
            json = await request.json()
            if not self.core.tool_function.does_post_params_exist(json, ["master_key", "user"]):
                return JSONResponse({"body": "Not Enough Params", "code": "params.not_enough"}, 400)
            if self.core.config["master_key"] != json["master_key"]:
                return JSONResponse({"body": "Credentials Invalid", "code": "credentials.invalid"}, 401)
            user = json["user"]
            if user in self.current_task:
                return JSONResponse({"body": "Task Already Exists", "code": "error.internal"}, 500)
            if self.core.object_storage_setting == {} or self.core.boto is None:
                return JSONResponse({"body": "Image Delete Error", "code": "error.internal"}, 500)
            try:
                def func():
                    try:
                        res = self.core.file_function.backup_user_data(json["user"])
                        if res is None:
                            if user in self.current_task:
                                self.current_task.remove(user)
                            return
                        self.core.boto.upload_file(res, self.core.object_storage_setting["bucket"],
                                                   "backup/" + str(user) + "/" + res.split("/")[-1])
                        if os.path.exists('data_dir/ftp_data/backup/' + res.split("/")[-1]):
                            os.remove('data_dir/ftp_data/backup/' + res.split("/")[-1])
                        if user in self.current_task:
                            self.current_task.remove(user)
                    except Exception:
                        self.current_task.remove(user)

                self.current_task.append(user)
                Thread(target=func).start()

            except Exception:
                if user in self.current_task:
                    self.current_task.remove(user)
                return JSONResponse({"body": "Internal Error", "code": "error.internal"}, 500)
            return JSONResponse({"body": "", "code": "Success"}, 200)

        @self.core.fast_api.route("/file/backup/load", methods=["POST"])
        async def backup_load(request: Request):
            json = await request.json()
            if not self.core.tool_function.does_post_params_exist(json, ["master_key", "user", "backup_key"]):
                return JSONResponse({"body": "Not Enough Params", "code": "params.not_enough"}, 400)
            if self.core.config["master_key"] != json["master_key"]:
                return JSONResponse({"body": "Credentials Invalid", "code": "credentials.invalid"}, 401)
            user = json["user"]
            if user in self.current_task:
                return JSONResponse({"body": "Task Already Exists", "code": "error.internal"}, 500)
            if self.core.object_storage_setting == {} or self.core.boto is None:
                return JSONResponse({"body": "Image Delete Error", "code": "error.internal"}, 500)
            try:
                def func():
                    file_name = str(user) + "-" + str(json["backup_key"]) + ".zip"
                    try:
                        self.core.boto.download_file(self.core.object_storage_setting["bucket"], "backup/" + str(user) + "/" + file_name, "data_dir/ftp_data/backup/" + file_name)
                        self.core.file_function.unpack_user_data(str(user), str(json["backup_key"]))
                        if os.path.exists('data_dir/ftp_data/backup/' + file_name):
                            os.remove('data_dir/ftp_data/backup/' + file_name)
                        if user in self.current_task:
                            self.current_task.remove(user)
                    except Exception:
                        if os.path.exists('data_dir/ftp_data/backup/' + file_name):
                            os.remove('data_dir/ftp_data/backup/' + file_name)
                        if user in self.current_task:
                            self.current_task.remove(user)

                self.current_task.append(user)
                Thread(target=func).start()

            except Exception:
                self.current_task.remove(user)
                return JSONResponse({"body": "Internal Error", "code": "error.internal"}, 500)
            return JSONResponse({"body": "", "code": "Success"}, 200)