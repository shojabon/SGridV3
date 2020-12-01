# -*- coding:utf-8 -*-

import glob
import threading
from ftplib import FTP

from main import SGridV3Master


class SyncFunction:

    def __init__(self, core: SGridV3Master):
        self.core = core

    def local_sync(self, local_sync: dict, sync_paths: list):
        result = {}
        for path in sync_paths:
            key = "data_dir/sync/" + str(path)
            result[key] = local_sync[key]
        return result

    def get_delete_path(self, local: dict, remote: dict):
        file_result = []
        directory_result = []
        for remote_path in remote.keys():
            if type(remote[remote_path]) == dict:
                # if path
                if remote_path not in local.keys():
                    directory_result.append(remote_path)

                    def get_files(dic):
                        file, direct = [], []
                        for key in dic.keys():
                            if type(dic[key]) == dict:
                                direct.append(key)
                                temp_result = get_files(dic[key])
                                file += temp_result[0]
                                direct += temp_result[1]
                            else:
                                file.append(key)
                        return file, direct

                    temp_result = get_files(remote[remote_path])
                    file_result += temp_result[0]
                    directory_result += temp_result[1]
                    continue
                temp_file_res, temp_direct_res = self.get_delete_path(local[remote_path], remote[remote_path])
                file_result += temp_file_res
                directory_result += temp_direct_res
            else:
                # if file
                if remote_path not in local:
                    file_result.append(remote_path)
                    continue
                if remote[remote_path] != local[remote_path]:
                    file_result.append(remote_path)
        return file_result, directory_result

    def get_create_path(self, local: dict, remote: dict):
        file_result = []
        directory_result = []
        for local_path in local.keys():
            if type(local[local_path]) == dict:
                if local_path not in remote.keys():
                    directory_result.append(local_path)

                    def get_files(dic):
                        file, direct = [], []
                        for key in dic.keys():
                            if type(dic[key]) == dict:
                                direct.append(key)
                                temp_result = get_files(dic[key])
                                file += temp_result[0]
                                direct += temp_result[1]
                            else:
                                file.append(key)
                        return file, direct

                    temp_file, temp_direct = get_files(local[local_path])
                    file_result += temp_file
                    directory_result += temp_direct
                    continue
                temp_file_res, temp_direct_res = self.get_create_path(local[local_path], remote[local_path])
                file_result += temp_file_res
                directory_result += temp_direct_res
            else:
                if local_path not in remote:
                    file_result.append(local_path)
                    continue
                if remote[local_path] != local[local_path]:
                    file_result.append(local_path)
        return file_result, directory_result

    def sync_file_at_node(self, node: str):
        if not self.core.tool_function.is_node(node):
            return False
        try:
            print("[Sync] Starting calibration with ", node)
            ftp = FTP()
            ftp.connect(host=self.core.tool_function.get_raw_address_node(node), port=21)
            ftp.encoding = "utf-8"
            ftp.login("sgrid-master-user", self.core.config["master_key"])

            node_config = self.core.nodes[self.core.tool_function.get_node_address(node)]
            # Load Required Paths
            if len(node_config["sync_path"]) == 1 and node_config["sync_path"][0] == "all":
                sync_paths = [x.replace("\\", "/").split("/")[-1] for x in glob.glob("data_dir/sync/*", recursive=True)]
            else:
                sync_paths = node_config["sync_path"]
                existing_paths = [x.replace("\\", "/").split("/")[-1] for x in
                                  glob.glob("data_dir/sync/*", recursive=True)]
                for path in sync_paths:
                    if path not in existing_paths:
                        sync_paths.remove(path)

            local_sync = self.local_sync(self.core.local_sync, sync_paths)

            sgrid = self.core.tool_function.get_sgrid_node(node)
            if sgrid is None:
                ftp.close()
                return

            # Delete Files
            delete_files, delete_directory = self.get_delete_path(local_sync, sgrid.sync_map())
            delete_files = [x[9:] for x in delete_files]
            delete_directory = [x[9:] for x in delete_directory]

            for file in delete_files:
                ftp.delete(file)
            for file in sorted(delete_directory, key=len, reverse=True):
                ftp.rmd(file)

            # Create Files
            create_files, create_directory = self.get_create_path(local_sync, sgrid.sync_map())
            create_files = [x[9:] for x in create_files]
            create_directory = [x[9:] for x in create_directory]

            for file in create_directory:
                ftp.mkd(file)
            for file in sorted(create_files, key=len):
                file_object = open("data_dir/" + str(file), "rb")
                ftp.storbinary("STOR " + str(file), file_object)
                file_object.close()

            ftp.close()
            print("[Sync] Finished calibration with ", node)
        except Exception:
            print("[Sync] Exception in calibration with ", node)

    def sync_all_nodes(self):
        print("[Sync] Starting total calibration")
        for node in self.core.node_name_address.keys():
            threading.Thread(target=self.sync_file_at_node, args=(node, )).start()
