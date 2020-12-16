import glob
import os
from os import walk

import psutil
from API.SResponse import SResponse
from starlette.responses import JSONResponse

from SGridNode.NodeMain import SGridV3Node
from fastapi import Request

class SyncEndpoint:

    def __init__(self, core: SGridV3Node):
        self.core = core
        self.register_endpoints()

    def register_endpoints(self):
        @self.core.fast_api.route("/sync/map/", methods=["POST"])
        async def sync_map(request: Request):
            json = await request.json()
            if not self.core.tool_function.does_post_params_exist(json, ["master_key"]):
                return SResponse("params.lacking").web()
            if self.core.config["master_key"] != json["master_key"]:
                return SResponse("key.invalid").web()
            return SResponse("success", self.core.tool_function.map_md5_local("data_dir/sync"))