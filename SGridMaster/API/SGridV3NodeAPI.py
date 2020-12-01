import json
import traceback

import requests


class SGridV3NodeAPI:

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
            return None

    # Node functions
    def node_info(self):
        payload = {
            "master_key": self.master_key,
        }
        response = self.__post_data(self.api_endpoint + "/node/info/", payload)
        if response is None:
            return None
        return response["body"]

    def node_status(self):
        payload = {
            "master_key": self.master_key,
        }
        response = self.__post_data(self.api_endpoint + "/node/status/", payload)
        if response is None:
            return None
        return response["body"]

    # Docker function
    def container_list(self, all_containers=False, name_only=True):
        payload = {
            "master_key": self.master_key,
            "all": all_containers,
            "name_only": name_only
        }
        response = self.__post_data(self.api_endpoint + "/docker/container/list/", payload)
        if response is None:
            return None
        return response["body"]

    def container_stats(self):
        payload = {
            "master_key": self.master_key
        }
        response = self.__post_data(self.api_endpoint + "/docker/container/stats/", payload)
        if response is None:
            return None
        return response["body"]

    def container_run(self,  **kwargs):
        kwargs["master_key"] = self.master_key
        response = self.__post_data(self.api_endpoint + "/docker/container/run/", kwargs)
        if response is None:
            return False
        return True

    def container_stop(self, container_id: str):
        payload = {
            "master_key": self.master_key,
            "id": container_id
        }
        response = self.__post_data(self.api_endpoint + "/docker/container/stop/", payload)
        if response is None:
            return False
        return True

    def container_start(self, container_id: str):
        payload = {
            "master_key": self.master_key,
            "id": container_id
        }
        response = self.__post_data(self.api_endpoint + "/docker/container/start/", payload)
        if response is None:
            return False
        return True

    # Images

    def image_list(self, all_images=False):
        payload = {
            "master_key": self.master_key,
            "all": all_images
        }
        response = self.__post_data(self.api_endpoint + "/docker/image/list/", payload)
        if response is None:
            return None
        return response["body"]

    def image_build(self):
        payload = {
            "master_key": self.master_key,
        }
        response = self.__post_data(self.api_endpoint + "/docker/image/build/", payload)
        if response is None:
            return None
        return response["body"]

    def image_delete(self, image: str):
        payload = {
            "master_key": self.master_key,
            "image": image
        }
        response = self.__post_data(self.api_endpoint + "/docker/image/delete/", payload)
        if response is None:
            return None
        return response["body"]

    # Sync
    def sync_map(self):
        payload = {
            "master_key": self.master_key,
        }
        response = self.__post_data(self.api_endpoint + "/sync/map/", payload)
        if response is None:
            return None
        return response["body"]

    # FTP
    def ftp_user_set(self, users: dict):
        payload = {
            "master_key": self.master_key,
            "users": users
        }
        response = self.__post_data(self.api_endpoint + "/ftp/users/set/", payload)
        if response is None:
            return None
        return response["body"]

    # File
    def file_settings_set(self, settings: dict):
        payload = {
            "master_key": self.master_key,
            "settings": settings
        }
        response = self.__post_data(self.api_endpoint + "/file/setting/set/", payload)
        if response is None:
            return None
        return response["body"]

    def backup_save(self, user: str):
        payload = {
            "master_key": self.master_key,
            "user": user
        }
        response = self.__post_data(self.api_endpoint + "/file/backup/save/", payload)
        if response is None:
            return False
        return True

    def backup_load(self, user: str, key: str):
        payload = {
            "master_key": self.master_key,
            "user": user,
            "backup_key": key
        }
        response = self.__post_data(self.api_endpoint + "/file/backup/load/", payload)
        if response is None:
            return False
        return True

    def nuke_user(self, user: str):
        payload = {
            "master_key": self.master_key,
            "user": user
        }
        response = self.__post_data(self.api_endpoint + "/file/nuke/", payload)
        if response is None:
            return False
        return True

    def file_unzip(self, target: str, destination: str):
        payload = {
            "master_key": self.master_key,
            "target": target,
            "destination": destination
        }
        response = self.__post_data(self.api_endpoint + "/file/unzip/", payload)
        if response is None:
            return False
        return True


if __name__ == '__main__':
    api = SGridV3NodeAPI("password", "http://127.0.0.1:2000/")
    # payload = {
    #     "tty": True,
    #     "detach": True,
    #     "name": "gridtest",
    #     "remove": True
    # }
    #print(api.backup_load("sho", "1606417526"))
    print(api.file_unzip("data_dir/sho-1606417526.zip", "data_dir/ftp_data/users/sho/"))