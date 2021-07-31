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


def validate_giteeid(giteeid, comment, personnel_authority):
    """
    Personnel permission verification
    Args:
        giteeid: personnel
        comment: comment
        personnel_authority: personnel authority

    Returns:
        True: Authentication is successful
        False: Validation fails
    """
    for role, person in personnel_authority.items():
        if giteeid in person and comment in PERMISSION_INFO.get(role):
            return True
    return False


