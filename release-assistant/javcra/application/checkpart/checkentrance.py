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
Description: check commands entrance
Class: CheckEntrance
"""

class CheckEntrance():
    """
    Description: distributing different check commands to correct methods
    Attributes:
        issue_id: the openEuler update version issue ID
        type_status: the check status which would be yes, no or None type
    """
    def __init__(self, issue_id, type_status):
        """
        Description: Instance initialization
        """
        self.issue_id = issue_id
        self.type_status = type_status

    def check_pkglist_result(self):
        """
        Description: check cve or bugfix list yes or no
        Args:

        Returns:

        Raises:

        """
        print("get the check cve/bugfix list result!")
        pass

    def check_test_result(self):
        """
        Description: check test result yes or no
        Args:

        Returns:

        Raises:

        """
        print("get the check test result!")
        pass

    def check_issue_status(self):
        """
        Description: check issut status
        Args:

        Returns:

        Raises:

        """
        print("get the issue status list!")
        pass

    def check_requires(self):
        """
        Description: check release package requires list
        Args:

        Returns:

        Raises:

        """
        print("get the requires result!")
        pass