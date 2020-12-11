import json
import traceback
from ftplib import FTP

import requests


class SGridV3MasterAPI:

    def __init__(self, master_key: str, api_endpoint: str):
        self.master_key = master_key
        if api_endpoint[-1] == "/":
            api_endpoint = api_endpoint[:-1]
        self.api_endpoint = api_endpoint

        self.node_list_cache = {}

    def __post_data(self, url: str, payload: dict):
        try:
            response = requests.post(url, json=payload)
            if response.status_code != 200:
                return None
            data = json.loads(response.text)
            return data
        except Exception:
            print(traceback.format_exc())
            return None

    # Docker Functions
    def container_run(self, node: str, image: str, params: dict):
        payload = {
            "master_key": self.master_key,
            "node": node,
            "image": image,
        }
        payload.update(params)
        response = self.__post_data(self.api_endpoint + "/docker/container/run/", payload)
        if response is None:
            return False
        return True

    def container_stop(self, node: str, container: str):
        payload = {
            "master_key": self.master_key,
            "node": node,
            "container": container
        }
        response = self.__post_data(self.api_endpoint + "/docker/container/stop/", payload)
        if response is None:
            return False
        return True

    def container_start(self, node: str, container: str):
        payload = {
            "master_key": self.master_key,
            "node": node,
            "container": container
        }
        response = self.__post_data(self.api_endpoint + "/docker/container/start/", payload)
        if response is None:
            return False
        return True

    def container_execute(self, node: str, container: str, command: str):
        payload = {
            "master_key": self.master_key,
            "node": node,
            "container": container,
            "command": command
        }
        response = self.__post_data(self.api_endpoint + "/docker/container/execute/", payload)
        if response is None:
            return False
        return True

    def container_list(self, node: str, name_only=True):
        payload = {
            "master_key": self.master_key,
            "node": node,
            "name_only": name_only
        }
        response = self.__post_data(self.api_endpoint + "/docker/container/list/", payload)
        if response is None:
            return None
        result = response["body"]
        if name_only:
            result = [str(x).replace("/", "") for x in result]
        return result

    # Node Functions
    def node_list(self):
        payload = {
            "master_key": self.master_key
        }
        response = self.__post_data(self.api_endpoint + "/node/list/", payload)
        if response is None:
            return None
        return response["body"]

    def is_node(self, node: str):
        if node in self.node_list_cache.keys():
            return True
        self.node_list_cache = self.node_list()
        if node in self.node_list_cache.keys():
            return True
        return False

    def get_node_ftp(self, node: str):
        if not self.is_node(node):
            return None
        node_data = self.node_list_cache[node]
        node_address = node_data["address"][7:]
        if node_address[-1] == "/":
            node_address = str(node_address[:-1]).split(":")[0]
        ftp = FTP(host=node_address, user="sgrid-master-user", passwd=self.master_key)
        ftp.set_pasv(False)
        return ftp

    # File Function  a
    def backup_list(self, user: str, cache: bool = True):
        payload = {
            "master_key": self.master_key,
            "user": user,
            "cache": cache
        }
        response = self.__post_data(self.api_endpoint + "/file/backup/list", payload)
        if response is None:
            return None
        lis = response["body"]
        if len(lis) == 1 and lis[0] == "":
            return None
        return lis

    def backup_save(self, node: str, user: str):
        payload = {
            "master_key": self.master_key,
            "user": user,
            "node": node
        }
        response = self.__post_data(self.api_endpoint + "/file/backup/save", payload)
        if response is None:
            return False
        return True

    def backup_load(self, node: str, user: str, key: str):
        payload = {
            "master_key": self.master_key,
            "user": user,
            "node": node,
            "key": key
        }
        response = self.__post_data(self.api_endpoint + "/file/backup/load", payload)
        if response is None:
            return False
        return True

    def backup_delete(self, user: str, key: str):
        payload = {
            "master_key": self.master_key,
            "user": user,
            "key": key
        }
        response = self.__post_data(self.api_endpoint + "/file/backup/delete", payload)
        if response is None:
            return False
        return True

    def nuke_user(self, node: str, user: str):
        payload = {
            "master_key": self.master_key,
            "user": user,
            "node": node
        }
        response = self.__post_data(self.api_endpoint + "/file/nuke", payload)
        if response is None:
            return False
        return True

    def file_unzip(self, node: str, target: str, destination: str):
        payload = {
            "master_key": self.master_key,
            "node": node,
            "target": target,
            "destination": destination
        }
        response = self.__post_data(self.api_endpoint + "/file/unzip", payload)
        if response is None:
            return False
        return True

    # FTP User

    def ftp_user_add(self, node: str, user: str, password: str, limit_mb: int):
        payload = {
            "master_key": self.master_key,
            "node": node,
            "user": user,
            "password": password,
            "limit_mb": limit_mb
        }
        response = self.__post_data(self.api_endpoint + "/ftp/user/add", payload)
        if response is None:
            return False
        return True

    def ftp_user_remove(self, node: str, user: str):
        payload = {
            "master_key": self.master_key,
            "node": node,
            "user": user,
        }
        response = self.__post_data(self.api_endpoint + "/ftp/user/remove", payload)
        if response is None:
            return False
        return True

    def ftp_user_list(self):
        payload = {
            "master_key": self.master_key,
        }
        response = self.__post_data(self.api_endpoint + "/ftp/user/list", payload)
        if response is None:
            return None
        return response["body"]

if __name__ == '__main__':
    grid = SGridV3MasterAPI("cOZUTx#k[x2-G6]1", "http://45.32.15.160:2500/")
    #print(grid.ftp_user_add("TEST", "asdasda", "asdaasd", 10))
    #print(grid.ftp_user_remove("TEST", "asdasda"))
    #print(grid.container_stop("development", "test"))
    #print(grid.container_run("development", "ubuntu:18.04", {"name": "test", "remove": True, "tty": True, "detach": True}))
    #print(grid.backup_list("sho"))
    #print(grid.backup_load("TEST", "sho", "1606417526"))
    #print(grid.nuke_user("TEST", "sho"))
