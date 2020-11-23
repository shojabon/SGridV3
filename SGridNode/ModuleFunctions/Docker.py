import glob
import hashlib
import io
import os
import random
import time
import traceback
from threading import Thread

import psutil

from SGridNode.main import SGridV3Node


class DockerFunction:

    def __init__(self, core: SGridV3Node):
        self.core = core

    def load_images_from_sync(self):
        if not os.path.exists("data_dir/sync/images"):
            return False
        images = []
        for tag in [x.tags for x in self.core.docker.images.list()]:
            if len(tag) == 0:
                continue
            images.append(tag[0])

        for image in [x.replace("\\", "/") for x in glob.glob("data_dir/sync/images/*.tar")]:
            if image not in images:

                def build(image_name):
                    try:
                        print("Building", image)
                        file = open(image, "rb")
                        stream = io.BytesIO(file.read())
                        self.core.docker.images.build(fileobj=stream, tag=image_name, custom_context=True)
                        stream.close()
                        file.close()
                        print("Build Complete", image)
                    except Exception:
                        print("Build Error", image_name)

                Thread(target=build, args=(image.split("/")[-1][:-4],)).start()

                print("Build Request Complete", image.split("/")[-1][:-4])