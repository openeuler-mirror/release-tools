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
marshmallow class
"""
from marshmallow import Schema
from marshmallow import fields
from marshmallow import validate

from javcra.common.constant import CHECK_PART_LIST


class BaseSchema(Schema):
    """
    basic parameter validator
    """
    issueid = fields.String(required=True, validate=validate.Length(min=1))
    giteeid = fields.String(required=True, validate=validate.Length(min=1))
    token = fields.String(required=True, validate=validate.Length(min=1))


class StartSchema(BaseSchema):
    """
    start command parameter verification
    """
    repo = fields.String(required=True, validate=validate.Length(min=1))
    ak = fields.String(required=True, validate=validate.Length(min=1))
    sk = fields.String(required=True, validate=validate.Length(min=1))
    useremail = fields.String(required=True, validate=validate.Length(min=1))


class CheckSchema(BaseSchema):
    """
    check command parameter verification
    """
    type = fields.String(
        required=True, validate=validate.OneOf(CHECK_PART_LIST)
    )
    ak = fields.String(required=False, validate=validate.Length(min=1))
    sk = fields.String(required=False, validate=validate.Length(min=1))
    jenkinsuser = fields.String(required=False, validate=validate.Length(min=1))
    jenkinskey = fields.String(required=False, validate=validate.Length(min=1))


class ModifySchema(BaseSchema):
    """
    modify command parameter verification
    """
    id = fields.List(fields.String(), validate=validate.Length(min=1))
    choice = fields.String(
        required=True, validate=validate.OneOf(["cve", "bugfix", "remain"])
    )


class ReleaseSchema(BaseSchema):
    """
    Release command parameter verification
    """
    type = fields.String(required=True, validate=validate.OneOf(["checkok", "cvrfok"]))
    jenkinsuser = fields.String(required=True, validate=validate.Length(min=1))
    jenkinskey = fields.String(required=True, validate=validate.Length(min=1))
    publishuser = fields.String(required=True, validate=validate.Length(min=1))
    publishkey = fields.String(required=True, validate=validate.Length(min=1))
