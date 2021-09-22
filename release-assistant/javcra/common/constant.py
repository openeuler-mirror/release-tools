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

# jenkins job path prefix
JENKINS_PATH_PREFIX = "function-item/release-manager/release_tools"

AARCH_FRAME = "aarch64"

X86_FRAME = "x86_64"

# branch list for standard epol list
BRANCH_LIST = ["openEuler-20.03-LTS-SP1", "openEuler-20.03-LTS-SP2", "openEuler-20.03-LTS"]

# lts branch
LTS_BRANCH = "openEuler-20.03-LTS"

# repo epol name list
REPO_EP_NAME = ["published-Epol-src", "published-Epol-update-src"]

# repo standard name list
REPO_STA_NAME = ["published-everything-src", "published-update-src"]

# epol src name
EPOL_SRC_NAME = ["published-Epol-src"]

# repo base url
REPO_BASE_URL = "http://121.36.84.172/repo.openeuler.org/"


# template job of aarch64
AARCH64_TM_JOB = "function-item/release-manager/update_template_jobs/aarch64/test_build"

# template job of x86
X86_TM_JOB = "function-item/release-manager/update_template_jobs/x86-64/test_build"

# template job of trigger
TRIGGER_TM_JOB = "function-item/release-manager/update_template_jobs/trigger"

ACTUATOR_DICT = {
    "openEuler-20.03-LTS-SP1": "openeuler-20.03-lts-sp1",
    "openEuler-20.03-LTS-SP2": "openeuler-20.03-lts-sp2",
    "openEuler-20.03-LTS": "openeuler-20.03-lts"
}

# git warehouse address for release issue
GITEE_REPO = "release-management"
