#!/usr/bin/python3
# ******************************************************************************
# Copyright (c) Huawei Technologies Co., Ltd. 2020-2020. All rights reserved.
# licensed under the Mulan PSL v2.
# You can use this software according to the terms and conditions of the Mulan PSL v2.
# You may obtain a copy of Mulan PSL v2 at:
#     http://license.coscl.org.cn/MulanPSL2
# THIS SOFTWARE IS PROVIDED ON AN "AS IS" BASIS, WITHOUT WARRANTIES OF ANY KIND, EITHER EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO NON-INFRINGEMENT, MERCHANTABILITY OR FIT FOR A PARTICULAR
# PURPOSE.
# See the Mulan PSL v2 for more details.
# ******************************************************************************/
"""
file archiving
"""
import argparse
import os
import logging
import traceback
from functools import wraps
from obs import ObsClient
from obs import PutObjectHeader


def catch_error(func):
    """
    Exception capture decorator
    """

    @wraps(func)
    def inner(*args, **kwargs):
        """
        capture decorator
        """
        try:
            return func(*args, **kwargs)
        except:
            print(traceback.format_exc())

    return inner


class ObsCould:
    """
    file archiving
    Attributes:
        AK: AK in the access key.An empty string by default indicates an anonymous user.
        SK: SK in the access key.An empty string by default indicates an anonymous user.
        server: The service address to connect to OBS
        bucketName: bucket Name
        path: Archive file path
    """

    def __init__(self, AK, SK, server, bucketName):
        """
        Initialize attribute
        """
        self.obs_client = ObsClient(access_key_id=AK, secret_access_key=SK, server=server)
        self.bucketName = bucketName

    def bucket_exist(self):
        """
        Determine if the bucket exists
        Returns:
            If it exists, it returns true and if it does not, it returns false
        """
        resp = self.obs_client.headBucket(self.bucketName)
        if resp.status < 300:
            return True
        return False

    def bucket_list(self, prefix_name):
        """
        Gets all objects in the bucket
        Returns:
            files: All objects in the bucket
        """
        files = list()
        resp = self.obs_client.listObjects(self.bucketName, prefix=prefix_name)
        if resp.status < 300:
            for content in resp.body.contents:
                files.append(content.key)
            return files
        return files

    def delete_file(self, path_name):
        """
        Delete bucket object
        Returns:
              If it exists, it returns true and if it does not, it returns false
        """
        resp = self.obs_client.deleteObject(self.bucketName, path_name)
        if resp.status < 300:
            return True
        return False

    @staticmethod
    def os_list_dir(local_path, choice=""):
        """
        Go through local folders
        Returns:
            paths: A collection of folders that meet the requirements
        """
        paths = []
        if os.path.isdir(local_path):
            for root, dirs, files in os.walk(local_path, topdown=False):
                for name in files:
                    pa = os.path.join(root, name)
                    if choice == "build_result":
                        if "failed_log" in pa and choice in pa:
                            paths.append(pa)
                    else:
                        if "failed_log" in pa and choice in pa or "failed_install_pkglist" in pa:
                            paths.append(pa)
            return paths
        return paths

    def upload_dir(self, path_name, path):
        """
        Upload folder
        Args:
            path_name: A file object saved on the cloud
            path: Local file path

        Returns:
            True or False
        """

        headers = PutObjectHeader()
        headers.contentType = 'text/plain'
        resp = self.obs_client.putFile(self.bucketName, path_name, path, headers=headers)
        if resp.status < 300:
            return True
        return False

    def delete_dir(self, prefix_name):
        """
        Bulk delete file objects
        Args:
            prefix_name: prefix_name

        Returns:
            True: All deleted successfully
            False: An object exists that failed to delete
        """
        path_names = self.bucket_list(prefix_name)
        fails = []
        for path_name in path_names:
            res = self.delete_file(path_name)
            if not res:
                logging.error("Failed to delete {} file".format(path_name))
                fails.append(path_name)
        if fails:
            return False
        return True

    @catch_error
    def run(self, branch, choice, local_path, prefix_name="install_build_log"):
        """
        log dir archived function main entry
        Args:
            branch: branch name
            choice: Select install or compile log logging
            prefix_name: Save the document special name
            local_path: Locally generate the directory above the log folder

        Returns:

        """
        if choice not in ["build_result", "check_result"]:
            logging.error("The choice must be between build_result and check_result")
            return False
        if not self.bucket_exist():
            logging.info("The bucket does not exist")
            return False
        if choice == "build_result":
            paths = self.os_list_dir(local_path, choice=choice)
        else:
            paths = self.os_list_dir(local_path, choice=choice)
        if not paths:
            logging.error("The file to be uploaded was not retrieved locally")
            return False
        for path in paths:
            path_name = path.replace(str(local_path), "")
            res = self.upload_dir("{}/{}{}".format(prefix_name, branch, path_name), path)
            if not res:
                logging.error("%s File upload failed" % path_name)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="Cloud archive file upload")
    parser.add_argument("--choice", required=True, type=str,
                        help="Select the logs for uploading build_result and check_result")
    parser.add_argument("--ak", required=True, type=str, help="access key id")
    parser.add_argument("--sk", required=True, type=str, help="secret access key")
    parser.add_argument("--branch", required=True, type=str, help="Name of the branch")
    parser.add_argument("--path", required=True, type=str, help="The directory above which log logs are stored")
    args = parser.parse_args()
    server = 'obs.cn-north-4.myhuaweicloud.com'
    bucketName = "release-tools"
    client = ObsCould(args.ak, args.sk, server, bucketName)
    if not client.bucket_exist():
        print("bucket not exist.")
    client.run(args.branch, args.choice, args.path)
