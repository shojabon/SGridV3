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
            print(traceback.format_exc())
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
    def container_list(self, all_containers=False):
        payload = {
            "master_key": self.master_key,
            "all": all_containers
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

    def container_run(self, image: str, **kwargs):
        kwargs["master_key"] = self.master_key
        kwargs["image"] = image
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

    def image_list(self, all_images=False):
        payload = {
            "master_key": self.master_key,
            "all": all_images
        }
        response = self.__post_data(self.api_endpoint + "/docker/image/list/", payload)
        if response is None:
            return None
        return response["body"]


if __name__ == '__main__':
    api = SGridV3NodeAPI("password", "http://127.0.0.1:2000/")
    # payload = {
    #     "tty": True,
    #     "detach": True,
    #     "name": "gridtest",
    #     "remove": True
    # }
    # print(api.container_run("ubuntu:18.04", **payload))
    print(api.node_status())