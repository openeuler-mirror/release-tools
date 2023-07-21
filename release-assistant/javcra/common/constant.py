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
        "/start-update"
        "/check-cve-bugfix"
    ],
    "developer": [
        "/add-bugfix",
        "/delete-bugfix",
        "/bugfix-ok",
        "/check-status",
        "/get-requires",
        "/check-cve-bugfix"
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
BRANCH_LIST = ["openEuler-20.03-LTS-SP1", "openEuler-20.03-LTS-SP2", "openEuler-20.03-LTS-SP3", "openEuler-20.03-LTS",
               "openEuler-22.03-LTS", "openEuler-22.03-LTS-SP1"]

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
    "openEuler-20.03-LTS-SP3": "openeuler-20.03-lts-sp3",
    "openEuler-20.03-LTS": "openeuler-20.03-lts",
    "openEuler-22.03-LTS": "openeuler-22.03-lts",
    "openEuler-22.03-LTS-SP1": "openeuler-22.03-lts-sp1",
}

# git warehouse address for release issue
GITEE_REPO = "release-management"

# ScanOSS API URL for jenkins trigger
JENKINS_API_URL = "https://shenzhen.scanoss.com/api/scan/direct"

# server repo for jenkins trigger
JENKINS_SERVER_REPO = "121.36.53.23"

# install jenkins job prefix
INSTALL_JOB_PREFIX = "function-item/release-manager/update_template_jobs/install_"

# jenkins base url
JENKINS_BASE_URL = 'https://openeulerjenkins.osinfra.cn'

REALSE_TOOLS_BUCKET_NAME = "release-tools"

REALSE_TOOLS_SERVER = "obs.cn-north-4.myhuaweicloud.com"

# max parallel jenkins num
MAX_PARAL_NUM = 5

# obs_project
OBS_PRJ = "openEuler:20.09"

# check comment dict
CHECK_COMMENT_DICT = {
    "status": "/check-status",
    "requires": "/get-requires",
    "test": "/test-ok",
    "cve_bugfix": "/check-cve-bugfix"
}

# release url
RELEASE_URL = "https://www.openeuler.org/api-cve/cve-security-notice-server/syncAll"

EPOL_DICT = {
    "openEuler-20.03-LTS": "EPOL",
    "openEuler-20.03-LTS-SP1": "EPOL",
    "openEuler-20.03-LTS-SP2": "EPOL-main",
    "openEuler-20.03-LTS-SP3": "EPOL-main",
    "openEuler-22.03-LTS": "EPOL-main",
    "openEuler-22.03-LTS-SP1": "EPOL-main"
}

# comment dict
COMMENT_DICT = {"cve": "/cve-ok", "bugfix": "/bugfix-ok", "test": "/test-ok"}

# label dict
LABEL_DICT = {"start": "check-pkg", "requires": "check-requires", "release": "release-check"}

MULTI_VERSION_BRANCHS = ["sp2", "sp3", "SP2", "SP3", "22.03-LTS", "22.03-LTS-SP1"]

CHECK_PART_LIST = ["status", "requires", "test", "cve_bugfix"]

# Number of retries
WAIT_NUMBER = 7
# Interval waiting times
WAIT_TIME = 90000
# majun callback url
MAJUN_CALLBACK_URL = \
    "https://majun-beta.osinfra.cn/api/http/majun-platform-release/publish/jenkins/saveJenkinsCallbackResult"
# CVE MANAGE URL
CVE_MANAGE_URL = "https://api.openeuler.org/cve-manager/v1/download/excel/triggerCveData"

BRANCH_MAP = {
    "openEuler-20.03-LTS-SP1": [
        "openEuler:20.03:LTS:SP1",
        "openEuler:20.03:LTS:SP1:Epol",
    ],
    "openEuler-20.03-LTS-SP3": [
        "openEuler:20.03:LTS:SP3",
        "openEuler:20.03:LTS:SP3:Epol",
    ],
    "openEuler-22.03-LTS": ["openEuler:22.03:LTS", "openEuler:22.03:LTS:Epol"],
    "openEuler-22.03-LTS-SP1": [
        "openEuler:22.03:LTS:SP1",
        "openEuler:22.03:LTS:SP1:Epol",
    ],
}

OBS_PROJECT_MULTI_VERSION_MAP = {
    "openEuler:22.03:LTS:Epol:Multi-Version:OpenStack:Train": "Multi-Version_OpenStack-Train_openEuler-22.03-LTS",
    "openEuler:22.03:LTS:Epol:Multi-Version:OpenStack:Wallaby": "Multi-Version_OpenStack-Wallaby_openEuler-22.03-LTS",
    "openEuler:22.03:LTS:Epol:Multi-Version:obs-server:2.10.11": "Multi-Version_obs-server-2.10.11_openEuler-22.03-LTS",
}

# jenkins cvrf name
CVRF_JOB_NAME = "obs/update_cve_xml_file_automatic"

# jenkins update info name
CVE_UPDATE_INFO_JOB_NAME = "function-item/update_repodata_by_updateinfo_automatic"

# job for upload package rpm to server
OBS_RELEASE_JOB = "obs/update_release_pkg_rpm"

# Test milestone routing
TEST_MILESTONE_URL = "http://radiatest.openeuler.org/api/v1/openeuler/update-release/validate"

MILESTONE_SUCCESS_CODE = "2000"
DAYLIBUILD_URL = "http://121.36.84.172/dailybuild/"

ISO_ARCH_MAP = {"ARM64": "openeuler_ARM64", "X86": "openeuler_X86"}

OBS_KEY_NAMES = ["obs_standard_prj", "obs_epol_prj", "obs_extras_prj"]

OBS_VALUES_NAMES = {
    "openEuler-20.03-LTS-SP1": [
        "openEuler:20.03:LTS:SP1",
        "openEuler:20.03:LTS:SP1:Epol",
        "openEuler:20.03:LTS:SP1:Extras",
    ],
    "openEuler-20.03-LTS-SP3": [
        "openEuler:20.03:LTS:SP3",
        "openEuler:20.03:LTS:SP3:Epol",
        "openEuler:20.03:LTS:SP3:Extras",
    ],
    "openEuler-22.03-LTS": [
        "openEuler:22.03:LTS",
        "openEuler:22.03:LTS:Epol",
        "openEuler:22.03:LTS:Extras",
    ],
    "openEuler-22.03-LTS-SP1": [
        "openEuler:22.03:LTS:SP1",
        "openEuler:22.03:LTS:SP1:Epol",
        "openEuler:22.03:LTS:SP1:Extras",
    ],
}

VM_IP_MAP = {
    "openEuler-20.03-LTS-SP1": "172.16.1.32",
    "openEuler-20.03-LTS-SP3": "172.16.1.32",
    "openEuler-22.03-LTS": "172.16.1.32",
    "openEuler-22.03-LTS-SP1": "172.16.1.95",
}

ISO_BUILD_JOB_MAP = {
    "openEuler-20.03-LTS-SP1": "openEuler-OS-build/Main-openEuler-20.03-LTS-SP1-build",
    "openEuler-20.03-LTS-SP3": "openEuler-OS-build/Main-openEuler-20.03-LTS-SP3-build",
    "openEuler-22.03-LTS": "openEuler-OS-build/Main-openEuler-22.03-LTS-build",
    "openEuler-22.03-LTS-SP1": "openEuler-OS-build/Main-openEuler-22.03-LTS-SP1-build",
}

MIN_JENKINS_BUILD_WAIT_TIME = 5
MAX_ISO_BUILD_WAIT_TIME = 1200
ISO_BUILD_WAIT_NUMBER = 6
