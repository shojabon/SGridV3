import json
import os


class SGridV3Node:

    def __init__(self):



    def load_config(self, file: str):
        if not os.path.exists(file):
            d = open(file, "+a")
            d.write("{}")
            d.close()
        file = open(file, "r")
        data = eval(file.read())
        file.close()
        return data

    def save_config(self, data: dict, file: str):
        file = open(file, "w")
        file.write(json.dumps(data, sort_keys=True, indent=4))
        file.close()

if __name__ == '__main__':
    grid = SGridV3Node()