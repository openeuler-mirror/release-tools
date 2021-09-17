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
# Author: Jiachen Fan
# Create: 2021-7-13
# ******************************************************************************/

import logging
import os
import subprocess


class ShellCmdApi(object):
    @staticmethod
    def call_subprocess(cmd_list: list, rt_err=False):
        """
        use subprocess run shell cmd

        Attribute:
            cmd: shell command
            rt_err: True, return stdout and stderr; False only return stdout

        return:
            result: console output str
        """
        output = ""
        try:
            output = subprocess.check_output(
                cmd_list,
                # PIPE is default value of stderr
                stderr=subprocess.STDOUT if rt_err else subprocess.PIPE,
                shell=False,
            )
        except subprocess.CalledProcessError:
            logging.warning(f"cmd [{' '.join(cmd_list)}] exit with non-zero code")

        return output.decode("utf-8", "ignore") if output else ""


class RpmNameParser(object):
    def __init__(self, rpm_name, auto_parse=False):
        self.full_name = rpm_name.strip()
        self._name = ""
        self._epoch = ""
        self._version = ""
        self._release = ""
        self._arch = ""
        if auto_parse:
            self.parse_rpm_name()

    def parse_rpm_name(self):
        """
        split rpm name 2 <name>-<version>-<release>.<arch>.rpm

        attribute:
            rpm_name:

        return:
            bool: True, succeed to split name; False, failed to split name
        """
        if not self.full_name.endswith(".rpm"):
            logging.error("rpm name: [%s] is illegal", self.full_name)
            return False
        temp_list = self.full_name.rsplit(".", 2)
        if len(temp_list) < 3:  # split 2 [<name>-<version>-<release>, <arch>, "rpm"]
            logging.error("rpm name: [%s] is illegal", self.full_name)
            return False
        self._arch = temp_list[1]
        temp_list = temp_list[0].rsplit("-", 2)
        if len(temp_list) < 3:  # split 2 [<name>, <version>, <release>]
            logging.error("rpm name: [%s] is illegal", self.full_name)
            self._arch = ""
            return False
        self._name = temp_list[0]
        self._version = temp_list[1]
        self._release = temp_list[2]
        return True

    @staticmethod
    def parse_rpm_evr(rpm_evr):
        """
        parser version str 2 <epoch>:<version>-<release>

        Attribute:
            rpm_evr: rpm version info
        return:
            result: [<epoch>, <version>, <release>]
        """
        [epoch, version, release] = ["", "", ""]

        def _split2item(data, sep):
            temp_list = data.strip().rsplit(sep, 1)
            if len(temp_list) < 2:
                logging.error(f"split [{data}] by [{sep}] failed")
                return ["", ""]
            return temp_list

        [version, release] = _split2item(rpm_evr, "-")
        if ":" in version:
            [epoch, version] = _split2item(version, ":")
        return [epoch, version, release]

    @property
    def name(self):
        return self._name

    @property
    def version(self):
        return self._version

    @property
    def release(self):
        return self._release

    @property
    def arch(self):
        return self._arch
