import json
import traceback

import requests
from API.SResponse import SResponse


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
                return SResponse("web.error")
            return SResponse(error_code=None, body=json.loads(response.text))
        except Exception:
            return SResponse("internal.error")

    # Node functions
    def node_info(self):
        payload = {
            "master_key": self.master_key,
        }
        return self.__post_data(self.api_endpoint + "/node/info/", payload)

    def node_status(self):
        payload = {
            "master_key": self.master_key,
        }
        return self.__post_data(self.api_endpoint + "/node/status/", payload)

    # Docker function
    def container_list(self, all_containers=False, name_only=True):
        payload = {
            "master_key": self.master_key,
            "all": all_containers,
            "name_only": name_only
        }
        return self.__post_data(self.api_endpoint + "/docker/container/list/", payload)

    def container_stats(self):
        payload = {
            "master_key": self.master_key
        }
        return self.__post_data(self.api_endpoint + "/docker/container/stats/", payload)

    def container_run(self,  **kwargs):
        kwargs["master_key"] = self.master_key
        return self.__post_data(self.api_endpoint + "/docker/container/run/", kwargs)

    def container_stop(self, container_id: str):
        payload = {
            "master_key": self.master_key,
            "id": container_id
        }
        return self.__post_data(self.api_endpoint + "/docker/container/stop/", payload)

    def container_start(self, container_id: str):
        payload = {
            "master_key": self.master_key,
            "id": container_id
        }
        return self.__post_data(self.api_endpoint + "/docker/container/start/", payload)

    def container_exec(self, container_id: str, command: str):
        payload = {
            "master_key": self.master_key,
            "id": container_id,
            "command": command
        }
        return self.__post_data(self.api_endpoint + "/docker/container/execute/", payload)

    # Images

    def image_list(self, all_images=False):
        payload = {
            "master_key": self.master_key,
            "all": all_images
        }
        return self.__post_data(self.api_endpoint + "/docker/image/list/", payload)

    def image_build(self):
        payload = {
            "master_key": self.master_key,
        }
        return self.__post_data(self.api_endpoint + "/docker/image/build/", payload)

    def image_delete(self, image: str):
        payload = {
            "master_key": self.master_key,
            "image": image
        }
        return self.__post_data(self.api_endpoint + "/docker/image/delete/", payload)

    # Sync
    def sync_map(self):
        payload = {
            "master_key": self.master_key,
        }
        return self.__post_data(self.api_endpoint + "/sync/map/", payload)

    # FTP
    def ftp_user_set(self, users: dict):
        payload = {
            "master_key": self.master_key,
            "users": users
        }
        return self.__post_data(self.api_endpoint + "/ftp/users/set/", payload)

    # File
    def file_settings_set(self, settings: dict):
        payload = {
            "master_key": self.master_key,
            "settings": settings
        }
        return self.__post_data(self.api_endpoint + "/file/setting/set/", payload)

    def backup_save(self, user: str, key: str):
        payload = {
            "master_key": self.master_key,
            "user": user,
            "key": key
        }
        return self.__post_data(self.api_endpoint + "/file/backup/save/", payload)

    def backup_load(self, user: str, key: str):
        payload = {
            "master_key": self.master_key,
            "user": user,
            "backup_key": key
        }
        return self.__post_data(self.api_endpoint + "/file/backup/load/", payload)

    def backup_final(self, user: str):
        payload = {
            "master_key": self.master_key,
            "user": user,
        }
        return self.__post_data(self.api_endpoint + "/file/backup/final/", payload)

    def backup_status(self, user: str):
        payload = {
            "master_key": self.master_key,
            "user": user
        }
        return self.__post_data(self.api_endpoint + "/file/backup/status/", payload)

    def nuke_user(self, user: str):
        payload = {
            "master_key": self.master_key,
            "user": user
        }
        return self.__post_data(self.api_endpoint + "/file/nuke/", payload)

    def file_unzip(self, target: str, destination: str):
        payload = {
            "master_key": self.master_key,
            "target": target,
            "destination": destination
        }
        return self.__post_data(self.api_endpoint + "/file/unzip/", payload)
