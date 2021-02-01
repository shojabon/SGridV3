import json
import traceback
from datetime import datetime
from ftplib import FTP

import requests
from API.SResponse import SResponse


class SGridV3MasterAPI:

    def __init__(self, master_key: str, api_endpoint: str):
        self.master_key = master_key
        if api_endpoint[-1] == "/":
            api_endpoint = api_endpoint[:-1]
        self.api_endpoint = api_endpoint

        self.node_list_cache = {}

        self.path_usage_cache = {}
        self.path_usage_cache_time = {}

    def __post_data(self, url: str, payload: dict):
        try:
            response = requests.post(url, json=payload)
            if response.status_code != 200:
                return SResponse("web.error")
            return SResponse(error_code=None, body=json.loads(response.text))
        except Exception:
            return SResponse("internal.error")

    # Docker Functions
    def container_run(self, node: str, image: str, params: dict):
        payload = {
            "master_key": self.master_key,
            "node": node,
            "image": image,
        }
        payload.update(params)
        return self.__post_data(self.api_endpoint + "/docker/container/run/", payload)

    def container_stop(self, node: str, container: str):
        payload = {
            "master_key": self.master_key,
            "node": node,
            "container": container
        }
        return self.__post_data(self.api_endpoint + "/docker/container/stop/", payload)

    def container_start(self, node: str, container: str):
        payload = {
            "master_key": self.master_key,
            "node": node,
            "container": container
        }
        return self.__post_data(self.api_endpoint + "/docker/container/start/", payload)

    def container_execute(self, node: str, container: str, command: str):
        payload = {
            "master_key": self.master_key,
            "node": node,
            "container": container,
            "command": command
        }
        return self.__post_data(self.api_endpoint + "/docker/container/execute/", payload)

    def container_list(self, node: str, name_only=True):
        payload = {
            "master_key": self.master_key,
            "node": node,
            "name_only": name_only
        }
        response = self.__post_data(self.api_endpoint + "/docker/container/list/", payload)
        if response.fail():
            return response
        result = response.body()
        if name_only:
            result = [str(x).replace("/", "") for x in result]
        return SResponse("success", result)

    # Node Functions
    def node_list(self):
        payload = {
            "master_key": self.master_key
        }
        return self.__post_data(self.api_endpoint + "/node/list/", payload)

    def is_node(self, node: str):
        if node in self.node_list_cache.keys():
            return SResponse("success")
        node_list = self.node_list()
        if node_list.fail():
            return node_list
        self.node_list_cache = node_list.body()
        if node in self.node_list_cache.keys():
            return SResponse("success")
        return SResponse("node.invalid")

    def get_node_ip(self, node: str):
        is_node = self.is_node(node)
        if is_node.fail():
            return is_node
        node_data = self.node_list_cache[node]
        node_address = node_data["address"][7:]
        if node_address[-1] == "/":
            node_address = str(node_address[:-1]).split(":")[0]
        return SResponse("success", node_address)

    def get_node_region(self, node: str):
        is_node = self.is_node(node)
        if is_node.fail():
            return is_node
        return SResponse("success", self.node_list_cache[node]["region"])

    # File Function

    def object_load(self, node: str, user: str, object_path: str):
        payload = {
            "master_key": self.master_key,
            "user": user,
            "node": node,
            "object_path": object_path
        }
        return self.__post_data(self.api_endpoint + "/file/object/load", payload)

    def object_list(self, name_only: bool=True, sub_folder=None):
        payload = {
            "master_key": self.master_key,
            "name_only": name_only,
            "sub_folder": sub_folder,
        }
        return self.__post_data(self.api_endpoint + "/file/object/list", payload)

    def backup_final_list(self):
        payload = {
            "master_key": self.master_key,
        }
        return self.__post_data(self.api_endpoint + "/file/backup/final/list", payload)

    def backup_list(self, user: str, cache: bool = True, full: bool = False):
        payload = {
            "master_key": self.master_key,
            "user": user,
            "cache": cache,
            "full": full
        }
        return self.__post_data(self.api_endpoint + "/file/backup/list", payload)

    def backup_rename(self, node: str, user: str, key: str, new_key: str):
        payload = {
            "master_key": self.master_key,
            "user": user,
            "node": node,
            "key": key,
            "new_key": new_key
        }
        return self.__post_data(self.api_endpoint + "/file/backup/rename", payload)

    def backup_final(self, node: str, user: str):
        payload = {
            "master_key": self.master_key,
            "user": user,
            "node": node
        }
        return self.__post_data(self.api_endpoint + "/file/backup/final", payload)

    def backup_save(self, node: str, user: str, key: str = str(round(datetime.now().timestamp()))):
        payload = {
            "master_key": self.master_key,
            "user": user,
            "node": node,
            "key": key
        }
        return self.__post_data(self.api_endpoint + "/file/backup/save", payload)

    def backup_load(self, node: str, user: str, key: str):
        payload = {
            "master_key": self.master_key,
            "user": user,
            "node": node,
            "key": key
        }
        return self.__post_data(self.api_endpoint + "/file/backup/load", payload)

    def backup_delete(self, user: str, key: str):
        payload = {
            "master_key": self.master_key,
            "user": user,
            "key": key
        }
        return self.__post_data(self.api_endpoint + "/file/backup/delete", payload)

    def backup_status(self, node: str, user: str):
        payload = {
            "master_key": self.master_key,
            "user": user,
            "node": node
        }
        return self.__post_data(self.api_endpoint + "/file/backup/status", payload)

    def backup_get_download_link(self, user: str, key: str, expire: int = 3, file_name=None):
        payload = {
            "master_key": self.master_key,
            "user": user,
            "key": key,
            "expire": expire,
            "filename": file_name
        }
        return self.__post_data(self.api_endpoint + "/file/backup/download", payload)


    def nuke_user(self, node: str, user: str):
        payload = {
            "master_key": self.master_key,
            "user": user,
            "node": node
        }
        return self.__post_data(self.api_endpoint + "/file/nuke", payload)

    def file_unzip(self, node: str, target: str, destination: str):
        payload = {
            "master_key": self.master_key,
            "node": node,
            "target": target,
            "destination": destination
        }
        return self.__post_data(self.api_endpoint + "/file/unzip", payload)

    def path_usage(self, node: str, path: str):
        if "node-" + str(path) in self.path_usage_cache_time:
            if datetime.now().timestamp() - self.path_usage_cache_time["node-" + str(path)] < 10:
                return self.path_usage_cache["node-" + str(path)]
        payload = {
            "master_key": self.master_key,
            "node": node,
            "path": path,
        }
        result = self.__post_data(self.api_endpoint + "/file/usage", payload)
        self.path_usage_cache_time["node-" + str(path)] = datetime.now().timestamp()
        self.path_usage_cache["node-" + str(path)] = result
        return result

    # FTP User

    def ftp_user_add(self, node: str, user: str, password: str, directory: str, limit_mb: int):
        payload = {
            "master_key": self.master_key,
            "node": node,
            "user": user,
            "password": password,
            "limit_mb": limit_mb,
            "directory": directory
        }
        return self.__post_data(self.api_endpoint + "/ftp/user/add", payload)

    def ftp_user_remove(self, node: str, user: str):
        payload = {
            "master_key": self.master_key,
            "node": node,
            "user": user,
        }
        return self.__post_data(self.api_endpoint + "/ftp/user/remove", payload)

    def ftp_user_list(self):
        payload = {
            "master_key": self.master_key,
        }
        return self.__post_data(self.api_endpoint + "/ftp/user/list", payload)

    def get_sfile(self, node: str):
        class SFile:
            def __init__(self, master_key: str, endpoint: str):
                self.master_key = master_key
                self.api_endpoint = endpoint

            def __post_data(self, url: str, payload: dict):
                try:
                    response = requests.post(url, json=payload)
                    if response.status_code != 200:
                        return SResponse("web.error")
                    return SResponse(error_code=None, body=json.loads(response.text))
                except Exception:
                    return SResponse("internal.error")

            def list(self, path: str):
                payload = {
                    "master_key": self.master_key,
                    "path": path
                }
                return self.__post_data(self.api_endpoint + "/sfile/list/", payload)

            def rm_dir(self, path: str):
                payload = {
                    "master_key": self.master_key,
                    "path": path
                }
                return self.__post_data(self.api_endpoint + "/sfile/rm/directory", payload)

            def file_get(self, path: str):
                payload = {
                    "master_key": self.master_key,
                    "path": path
                }
                return self.__post_data(self.api_endpoint + "/sfile/file/get", payload)

            def file_set(self, path: str, data):
                payload = {
                    "master_key": self.master_key,
                    "path": path,
                    "data": data
                }
                return self.__post_data(self.api_endpoint + "/sfile/file/set", payload)

            def file_rename(self, path: str, name):
                payload = {
                    "master_key": self.master_key,
                    "path": path,
                    "name": name
                }
                return self.__post_data(self.api_endpoint + "/sfile/file/rename", payload)

            def rm_file(self, path: str):
                payload = {
                    "master_key": self.master_key,
                    "path": path
                }
                return self.__post_data(self.api_endpoint + "/sfile/rm/file", payload)

        is_node = self.is_node(node)
        if is_node.fail():
            return None
        return SFile(self.master_key, "http://" + self.get_node_ip(node).body() + ":2000")




if __name__ == '__main__':
    grid = SGridV3MasterAPI("cOZUTx#k[x2-G6]1", "http://167.179.89.11:2500/")