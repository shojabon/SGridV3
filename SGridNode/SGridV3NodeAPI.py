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

if __name__ == '__main__':
    api = SGridV3NodeAPI("password", "http://127.0.0.1:2000/")
    print(api.container_stats())