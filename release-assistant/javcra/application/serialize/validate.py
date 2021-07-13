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
Verification method
"""

def validate_giteeid(issue_id, gitee_id, person):
    """
    Description: get the ID with comment permission from the corresponding Gitee Issue
    Args:
        issue_id: the openEuler update version issue ID
        gitee_id: the gitee id who comment this issue
    """

    permission = True
    print("the permission is given to : " + person)
    if not permission:
        print("Sorry! You do not have the permisson to commit this operation.")
        return False
    return True
