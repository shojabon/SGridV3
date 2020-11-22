import json
import os


class SGridV3Master:

    def __init__(self):
        os.makedirs("data_dir/sync", exist_ok=True)

        self.load_config("nodes.json")


    def load_config(self, file: str):
        if not os.path.exists(file):
            d = open(file, "+a")
            d.write("{}")
            d.close()
        file = open(file, "r")
        data = json.loads(file.read())
        file.close()
        return data

    def save_config(self, data: dict, file: str):
        file = open(file, "w")
        file.write(json.dumps(data, sort_keys=True, indent=4))
        file.close()
