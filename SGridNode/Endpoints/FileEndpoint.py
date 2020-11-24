import traceback

from starlette.responses import JSONResponse

from SGridNode.main import SGridV3Node
from fastapi import Request
import json as json_class


class FileEndpoint:
    def __init__(self, core: SGridV3Node):
        self.core = core
        self.register_endpoints()

    def register_endpoints(self):
        pass