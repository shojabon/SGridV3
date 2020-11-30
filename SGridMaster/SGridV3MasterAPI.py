import json
import traceback

import requests


class SGridV3MasterAPI:

    def __init__(self, master_key: str, api_endpoint: str):
        self.master_key = master_key
        if api_endpoint[-1] == "/":
            api_endpoint = api_endpoint[:-1]
        self.api_endpoint = api_endpoint

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

    def container_list(self, node: str, name_only=True):
        payload = {
            "master_key": self.master_key,
            "node": node,
            "name_only": name_only
        }
        response = self.__post_data(self.api_endpoint + "/docker/container/list/", payload)
        if response is None:
            return None
        return response["body"]

    # Node Functions
    def node_list(self):
        payload = {
            "master_key": self.master_key
        }
        response = self.__post_data(self.api_endpoint + "/node/list/", payload)
        if response is None:
            return None
        return response["body"]

    # File Function
    def backup_list(self, user: str):
        payload = {
            "master_key": self.master_key,
            "user": user
        }
        response = self.__post_data(self.api_endpoint + "/file/backup/list", payload)
        if response is None:
            return None
        return response["body"]

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


if __name__ == '__main__':
    grid = SGridV3MasterAPI("password", "http://127.0.0.1:2500/")
    #print(grid.container_run("TEST", "ubuntu:18.04", {"name": "test", "remove": True, "tty": True, "detach": True}))
    #print(grid.backup_list("sho"))
    #print(grid.backup_load("TEST", "sho", "1606417526"))
    #print(grid.nuke_user("TEST", "sho"))
    print(grid.file_unzip("TEST", "data_dir/sync/images/sho-1606417526.zip", "data_dir/ftp_data/users/sho/"))