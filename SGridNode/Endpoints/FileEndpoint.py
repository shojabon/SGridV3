import os
import shutil
import traceback
from datetime import datetime
from threading import Thread

import boto3
from API.SResponse import SResponse
from slugify import slugify

from SGridNode.NodeMain import SGridV3Node
from fastapi import Request


class FileEndpoint:
    def __init__(self, core: SGridV3Node):
        self.core = core
        self.register_endpoints()
        self.current_task = []

        self.object_cache = {}

    def delete_objects_in_cache(self):
        for path in self.object_cache.keys():
            time_data = self.object_cache[path]
            if datetime.now().timestamp() - time_data > 10 * 60:
                if os.path.exists("data_dir/ftp_data/object/" + str(path)):
                    os.remove("data_dir/ftp_data/object/" + str(path))
                    if path in self.object_cache:
                        del self.object_cache[path]

    def register_endpoints(self):
        @self.core.fast_api.route("/file/object/load", methods=["POST"])
        async def object_load(request: Request):
            json = await request.json()
            if not self.core.tool_function.does_post_params_exist(json, ["master_key", "user", "object_path"]):
                return SResponse("params.lacking").web()
            if self.core.config["master_key"] != json["master_key"]:
                return SResponse("key.invalid").web()
            user = json["user"]
            if user in self.current_task:
                return SResponse("task.exists").web()
            if self.core.config["object_storage_info"] == {} or self.core.boto is None:
                return SResponse("internal.error").web()
            if json["object_path"][len(json["object_path"])-4:] != ".zip":
                return SResponse("path.invalid").web()
            try:
                local_path = "data_dir/ftp_data/object/" + json["object_path"]
                file_name = str(json["object_path"]).split("/")[-1]
                os.makedirs(local_path[:-len(file_name)], exist_ok=True)

                def func():
                    try:
                        if json["object_path"] not in self.object_cache:
                            self.core.boto.download_file(self.core.config["object_storage_info"]["bucket"],
                                                         json["object_path"],
                                                         local_path)
                        self.object_cache[json["object_path"]] = datetime.now().timestamp()
                        if os.path.exists(local_path):
                            shutil.unpack_archive(local_path, "data_dir/ftp_data/users/" + str(user))
                        self.delete_objects_in_cache()
                    except Exception:
                        print(traceback.format_exc())
                        pass
                    finally:
                        if user in self.current_task:
                            self.current_task.remove(user)

                self.current_task.append(user)
                Thread(target=func).start()
                return SResponse("success").web()
            except Exception:
                print(traceback.format_exc())
                if user in self.current_task:
                    self.current_task.remove(user)
                return SResponse("internal.error").web()

        @self.core.fast_api.route("/file/setting/set", methods=["POST"])
        async def object_setting_set(request: Request):
            json = await request.json()
            if not self.core.tool_function.does_post_params_exist(json, ["master_key", "settings"]):
                return SResponse("params.lacking").web()
            if self.core.config["master_key"] != json["master_key"]:
                return SResponse("key.invalid").web()
            if type(json["settings"]) != dict:
                return SResponse("params.lacking").web()
            if self.core.config["object_storage_info"] != json["settings"]:
                self.core.config["object_storage_info"] = json["settings"]
                sess = boto3.Session(aws_access_key_id=json["settings"]["access_key"],
                                     aws_secret_access_key=json["settings"]["secret_access_key"])
                self.core.boto = sess.client('s3', endpoint_url=json["settings"]["endpoint_url"])
            return SResponse("success").web()

        @self.core.fast_api.route("/file/backup/final", methods=["POST"])
        async def backup_final(request: Request):
            json = await request.json()
            if not self.core.tool_function.does_post_params_exist(json, ["master_key", "user"]):
                return SResponse("params.lacking").web()
            if self.core.config["master_key"] != json["master_key"]:
                return SResponse("key.invalid").web()
            if self.core.config["object_storage_info"] == {} or self.core.boto is None:
                return SResponse("internal.error").web()
            try:
                def func():
                    try:
                        res = self.core.file_function.backup_user_data(json["user"])
                        if res is None:
                            return
                        self.core.boto.upload_file(res, self.core.config["object_storage_info"]["bucket"],
                                                   "final-upload/" + str(json["user"]) + ".zip")
                        if os.path.exists('data_dir/ftp_data/backup/' + res.split("/")[-1]):
                            os.remove('data_dir/ftp_data/backup/' + res.split("/")[-1])
                    except Exception:
                        pass

                Thread(target=func).start()
                return SResponse("success").web()
            except Exception:
                return SResponse("internal.error").web()

        @self.core.fast_api.route("/file/backup/status", methods=["POST"])
        async def backup_status(request: Request):
            json = await request.json()
            if not self.core.tool_function.does_post_params_exist(json, ["master_key", "user"]):
                return SResponse("params.lacking").web()
            if self.core.config["master_key"] != json["master_key"]:
                return SResponse("key.invalid").web()
            if self.core.config["object_storage_info"] == {} or self.core.boto is None:
                return SResponse("internal.error").web()
            user = json["user"]
            if user in self.current_task:
                return SResponse("success").web()
            return SResponse("task.invalid").web()

        @self.core.fast_api.route("/file/backup/save", methods=["POST"])
        async def backup_save(request: Request):
            json = await request.json()
            if not self.core.tool_function.does_post_params_exist(json, ["master_key", "user", "key"]):
                return SResponse("params.lacking").web()
            if self.core.config["master_key"] != json["master_key"]:
                return SResponse("key.invalid").web()
            user = json["user"]
            if user in self.current_task:
                return SResponse("task.exists").web()
            if self.core.config["object_storage_info"] == {} or self.core.boto is None:
                return SResponse("internal.error").web()
            key = slugify(str(json["key"]))
            if len(key) > 32:
                return SResponse("name.toolong").web()
            if key == "":
                key = None
            try:
                def func():
                    try:
                        res = self.core.file_function.backup_user_data(json["user"], key)
                        if res is None:
                            if user in self.current_task:
                                self.current_task.remove(user)
                            return
                        self.core.boto.upload_file(res, self.core.config["object_storage_info"]["bucket"],
                                                   "backup/" + str(user) + "/" + res.split("/")[-1][len(user) + 1:])
                        if os.path.exists('data_dir/ftp_data/backup/' + res.split("/")[-1]):
                            os.remove('data_dir/ftp_data/backup/' + res.split("/")[-1])
                        if user in self.current_task:
                            self.current_task.remove(user)
                    except Exception:
                        self.current_task.remove(user)

                self.current_task.append(user)
                Thread(target=func).start()
                return SResponse("success").web()
            except Exception:
                if user in self.current_task:
                    self.current_task.remove(user)
                return SResponse("internal.error").web()

        @self.core.fast_api.route("/file/backup/load", methods=["POST"])
        async def backup_load(request: Request):
            json = await request.json()
            if not self.core.tool_function.does_post_params_exist(json, ["master_key", "user", "backup_key"]):
                return SResponse("params.lacking").web()
            if self.core.config["master_key"] != json["master_key"]:
                return SResponse("key.invalid").web()
            user = json["user"]
            if user in self.current_task:
                return SResponse("task.exists").web()
            if self.core.config["object_storage_info"] == {} or self.core.boto is None:
                return SResponse("internal.error").web()
            if len(json["backup_key"]) > 32:
                return SResponse("name.toolong").web()
            backup_key = slugify(str(json["backup_key"]))
            try:
                def func():
                    file_name = str(backup_key) + ".zip"
                    try:
                        self.core.boto.download_file(self.core.config["object_storage_info"]["bucket"],
                                                     "backup/" + str(user) + "/" + str(file_name),
                                                     "data_dir/ftp_data/backup/" + str(file_name))
                        self.core.file_function.unpack_user_data(str(user), file_name)
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
                return SResponse("success").web()
            except Exception:
                if user in self.current_task:
                    self.current_task.remove(user)
                return SResponse("internal.error").web()

        @self.core.fast_api.route("/file/nuke/", methods=["POST"])
        async def nuke_user_data(request: Request):
            json = await request.json()
            if not self.core.tool_function.does_post_params_exist(json, ["master_key", "user"]):
                return SResponse("params.lacking").web()
            if self.core.config["master_key"] != json["master_key"]:
                return SResponse("key.invalid").web()
            user = json["user"]
            if user in self.current_task:
                return SResponse("task.exists").web()
            try:
                if not os.path.exists("data_dir/ftp_data/users/" + str(user)):
                    return SResponse("success").web()

                self.current_task.append(user)
                shutil.rmtree("data_dir/ftp_data/users/" + str(user))
                os.makedirs("data_dir/ftp_data/users/" + str(user), exist_ok=True)

                if user in self.current_task:
                    self.current_task.remove(user)
                return SResponse("success").web()
            except Exception:
                print(traceback.format_exc())
                if user in self.current_task:
                    self.current_task.remove(user)
                return SResponse("internal.error").web()

        @self.core.fast_api.route("/file/unzip/", methods=["POST"])
        async def file_unzip(request: Request):
            json = await request.json()
            if not self.core.tool_function.does_post_params_exist(json, ["master_key", "target", "destination"]):
                return SResponse("params.lacking").web()
            if self.core.config["master_key"] != json["master_key"]:
                return SResponse("key.invalid").web()
            try:
                if not os.path.exists(json["target"]):
                    return SResponse("path.invalid").web()
                shutil.unpack_archive(json["target"], json["destination"])
            except Exception:
                return SResponse("internal.error").web()
            return SResponse("success").web()

        @self.core.fast_api.route("/file/usage/", methods=["POST"])
        async def path_usage(request: Request):
            json = await request.json()
            if not self.core.tool_function.does_post_params_exist(json, ["master_key", "path"]):
                return SResponse("params.lacking").web()
            if self.core.config["master_key"] != json["master_key"]:
                return SResponse("key.invalid").web()
            try:
                if not os.path.exists(json["path"]):
                    return SResponse("path.invalid").web()
                return SResponse("success", self.core.tool_function.get_dir_size(json["path"])).web()
            except Exception:
                print(traceback.format_exc())
                return SResponse("internal.error").web()
