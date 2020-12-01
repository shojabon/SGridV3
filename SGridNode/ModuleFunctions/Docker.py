import glob
import io
import os
import traceback

from SGridNode.NodeMain import SGridV3Node


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
            image_name = image.split("/")[-1][:-4]
            if image_name not in images:

                try:
                    print("Building", image_name)
                    file = open(image, "rb")
                    stream = io.BytesIO(file.read())
                    self.core.docker.images.build(fileobj=stream, tag=image_name, custom_context=True, rm=True)
                    stream.close()
                    file.close()
                    print("Build Complete", image_name)
                except Exception:
                    print(traceback.format_exc())
                    print("Build Error", image_name)

                print("Build Request Complete", image_name)