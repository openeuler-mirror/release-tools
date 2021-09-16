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
from marshmallow import ValidationError
from javcra.common.constant import PERMISSION_INFO


def _serialization(*args, **kwargs):
    """
    Validation after serialization
    Args:
        verifier: The class name of the validator
        data: data
    Returns:
        result: Verify the dictionary after success
        errors: The dictionary
    Raise:
        ValidationError: Validation error
    """
    result = {}
    errors = {}
    try:
        verifier, data = args
        result = verifier().load(data, partial=kwargs.get("partial", ()))
    except ValidationError as err:
        errors = err.messages
    return result, errors


def validate(verifier, data, load=False, partial=()):
    """
    Validation method
    Args:
        verifier:The name of the validator's class
        data: Passed parameter
        load: Defaults to False.
        partial: Specifies the field to validate

    Raises:
        TypeError: Type error

    Returns:
        result: Verify the dictionary after success
        errors: The dictionary
    """
    if not isinstance(data, dict):
        raise TypeError("The content to verify needs to be of a dictionary type")

    if load:
        result, errors = _serialization(verifier, data, partial=partial)
    else:
        errors = verifier().validate(data, partial=partial)
        result = data
    return result, errors


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
