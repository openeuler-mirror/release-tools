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


class StartSchema(Schema):
    """
    start command parameter verification
    """
    issueid = fields.String(required=True, validate=validate.Length(min=1))
    giteeid = fields.String(required=True, validate=validate.Length(min=1))
    repo = fields.String(required=True, validate=validate.Length(min=1))
    ak = fields.String(required=True, validate=validate.Length(min=1))
    sk = fields.String(required=True, validate=validate.Length(min=1))
    useremail = fields.String(required=True, validate=validate.Length(min=1))
    token = fields.String(required=True, validate=validate.Length(min=1))


class CheckSchema(Schema):
    """
    check command parameter verification
    """
    issueid = fields.String(required=True, validate=validate.Length(min=1))
    giteeid = fields.String(required=True, validate=validate.Length(min=1))
    type = fields.String(
        required=True, validate=validate.OneOf(["status", "requires", "test"])
    )
    token = fields.String(required=True, validate=validate.Length(min=1))
    ak = fields.String(required=True, validate=validate.Length(min=1))
    sk = fields.String(required=True, validate=validate.Length(min=1))
    jenkinsuser = fields.String(required=True, validate=validate.Length(min=1))
    jenkinskey = fields.String(required=True, validate=validate.Length(min=1))


class ModifySchema(Schema):
    """
    modify command parameter verification
    """
    issueid = fields.String(required=True, validate=validate.Length(min=1))
    giteeid = fields.String(required=True, validate=validate.Length(min=1))
    id = fields.List(fields.String(), validate=validate.Length(min=1))
    choice = fields.String(
        required=True, validate=validate.OneOf(["cve", "bugfix", "remain"])
    )
    token = fields.String(required=True, validate=validate.Length(min=1))


class ReleaseSchema(Schema):
    """
    Release command parameter verification
    """
    issueid = fields.String(required=True, validate=validate.Length(min=1))
    giteeid = fields.String(required=True, validate=validate.Length(min=1))
    type = fields.String(required=True, validate=validate.OneOf(["checkok", "cvrfok"]))
    token = fields.String(required=True, validate=validate.Length(min=1))
    jenkinsuser = fields.String(required=True, validate=validate.Length(min=1))
    jenkinskey = fields.String(required=True, validate=validate.Length(min=1))
