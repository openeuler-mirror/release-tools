#! /usr/bin/env python
# coding=utf-8
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
# Create: 2021-07-3
# ******************************************************************************/

import subprocess
from javcra.libs.log import logger


class ExecuteCmd(object):
    """
    Encapsulates the external interface for executing shell statements 
    """
    @classmethod
    def cmd_status(cls, command, time_out=20):
        """
        Execute command and return to status

        Args:
            command: shell command to be executed
            time_out: time out

        Returns:
            subprocess.run(xxx).returncode

        """
        
        ret = subprocess.run(command, shell=False, stdout=subprocess.PIPE, 
            stderr=subprocess.PIPE, encoding="utf-8", timeout = time_out)
        if ret.returncode:
            logger.error(f"args:{ret.args} \n stderr:{ret.stderr}")
        
        return ret.returncode

    @classmethod
    def cmd_output(cls, command):
        """
        Execute the command and return the output

        Args:
            command: shell command to be executed

        Returns:
            subprocess.check_output(xxx)
        """
        
        try:
            subp = subprocess.check_output(command, shell=False, stderr=subprocess.STDOUT, encoding="utf-8")
            return subp
        except subprocess.CalledProcessError as err:
            logger.error(f"{command}:{err}")
            return None