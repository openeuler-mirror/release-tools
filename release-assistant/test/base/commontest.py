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
Public methods for comparing data
"""


def compare_two_values(obj1, obj2):
    """
    compare two values
    Args:
        obj1:object1 It can be a data type in Python,
                and can be converted by using the str() method
        obj2:object2 same as obj1

    Returns: True or False

    """
    # With the help of the str() method provided by python,It's so powerful
    return obj1 == obj2 or (isinstance(obj1, type(obj2)) and
                            "".join(sorted(str(obj1))) == "".join(sorted(str(obj2))))