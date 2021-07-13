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
Description: modify commands entrance
Class: ModifyEntrance
"""

class ModifyEntrance():
    """
    Description: distributing different modify commands to correct methods
    Attributes:
    """
    def __init__(self, issue_id, issue_list):
        """
        Description: Instance initialization
        """
        pass

    def modify_cve_list(self, action):
        """
        Description: add or delete cve issue list
        Args:

        Returns:

        Raises:

        """
        print("add/delete cve checklist!")
        pass

    def modify_bugfix_list(self, action):
        """
        Description: add or delete bugfix issue list
        Args:

        Returns:

        Raises:

        """
        print("add/delete bugix checklist!")
        pass

    def modify_release_result(self, action):
        """
        Description: add or delete final release issue list
        Args:

        Returns:

        Raises:

        """
        print("modify final release list!")
        pass