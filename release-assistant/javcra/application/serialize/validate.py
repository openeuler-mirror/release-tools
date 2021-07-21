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
from javcra.common.constant import PERMISSION_INFO
from javcra.common.constant import COMMAND_DICT


def validate_giteeid(user, comment, personnel_authority: dict, permission_info=PERMISSION_INFO,
                     command_dict=COMMAND_DICT):
    """
    Description: get the ID with comment permission from the corresponding Gitee Issue
    Args:
        user: user id
        comment: Related permissions
        personnel_authority: personnel authority e.g:{'developer': 'xxx', 'version_manager':'xxx'}
        permission_info: permission info
        command_dict: command info
    Returns:
        True or False
    """
    try:
        user_id = ''
        user_list = command_dict[comment]
        for key, value in personnel_authority.items():
            if user in value and key in user_list:
                user_id = key
        if comment not in permission_info[user_id]:
            print("{} has no operation authority:{}, please contact the administrator".format(user, comment))
            return False
    except KeyError as error:
        print("Error:{}\n Gitee id:{}\n Comment:{}\n Related permissions: {} \n"
              "please check and try again".format(error, user, comment, permission_info))
        return False
    except AttributeError as error:
        print("Personnel Authority:{} \n User id:{} \n Comment:{} \n {}".format(personnel_authority, user, comment,
                                                                                error))
        return False
    return True
