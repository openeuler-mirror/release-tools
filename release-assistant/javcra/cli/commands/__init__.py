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
from javcra.application.checkpart.checktest import CheckTest
from javcra.application.serialize.validate import validate, validate_giteeid
from javcra.common.constant import GITEE_REPO


def personnel_authority(param_dict, comment):
    """
    personnel name and responsibilities acquisition
    Args:
        param_dict: parameter dictionary
        comment: comment
    Returns:
        personnel_dict: personnel Information Dictionary
    """
    check = CheckTest(GITEE_REPO, param_dict.get("token"), param_dict.get("issueid"))
    personnel_dict = check.parsing_body()
    if not personnel_dict:
        print("[ERROR] Failed to get the list of personnel permissions")
        return {}
    if "start" not in comment:
        verify_res = check.verify_start_update()
        if not verify_res:
            print("[ERROR] not allowed operation, please start release issue first.")
            return {}
    return personnel_dict


def parameter_permission_validate(schema, param_dict, comment):
    """
    parameter verification and authorization verification
    Args:
        schema: validator class
        param_dict: parameter dictionary
        comment: comment
    Returns:
        return true if the verification is passed, otherwise return false
    """
    _, error = validate(schema, param_dict, load=True)
    if error:
        print("Parameter validation failed")
        return False
    personnel_dict = personnel_authority(param_dict, comment)
    if not personnel_dict:
        return False
    permission = validate_giteeid(param_dict.get("giteeid"), comment, personnel_dict)
    if not permission:
        print("[ERROR] The current user does not have relevant operation permissions")
        return False
    return True
