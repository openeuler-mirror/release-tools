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
Description: General constants
Class:
"""

PERMISSION_DICT = {
    'cve': 'security',
    'bug': 'developer',
    'status': 'all',
    'requires': 'developer',
    'test': 'test',
    'release': 'all',
    'checkok': 'all',
    'cvrfok': 'security',
    'start': 'manager'
}

CVE_MANAGE_SERVER = "obs.ap-southeast-1.myhuaweicloud.com"
CVE_MANAGE_BUCKET_NAME = "openeuler-cve-cvrf"
CVE_UPDATE_INFO = "cve-manager-updateinfo"
PERMISSION_INFO = {
    "version_manager": ["/start-update", "/no-release"],
    "security_committee": [
        "/add-cve",
        "/delete-cve",
        "/cve-ok",
        "/check-ok",
        "/cvrf-ok",
    ],
    "developer": [
        "/add-bugfix",
        "/delete-bugfix",
        "/bugfix-ok",
        "/check-status",
        "/get-requires",
    ],
    "tester": ["/test-ok"],
    "tc": ["/check-ok"],
    "release": ["/check-ok"],
    "qa": ["/check-ok"]
}
ROLE_DICT = {
    "version_manager": "版本经理",
    "security_committee": "安全委员会",
    "developer": "开发人员",
    "tester": "测试人员",
    "tc": "tc",
    "release": "release",
    "qa": "qa"
}
ROLES = ["tc", "release", "qa", "security_committee", "version_manager"]
