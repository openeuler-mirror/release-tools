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
Global environment variable value when the system is running
"""

import os

# STATUS_CODE
SUCCEED = 0
FAILED = 1

# global const for check_requires part
# the config file of check_requires part will be stroed in the following
CHECK_REQUIRES_CONFIG_FOLDER_PATH = os.path.join(os.path.dirname(__file__))

# oscrc config
# the template file of oscrc, which will be stored in CHECK_REQUIRES_CONFIG_FOLDER_PATH
OSCRC_TEMPLETE = os.path.join(
    CHECK_REQUIRES_CONFIG_FOLDER_PATH,
    "checkpart",
    "check_requires",
    "oscrc.templete"
)
DEFAULT_OSCRC_APIURL = "https://build.openeuler.org"
DEFAULT_OSCRC_POSITION = "/root/.config/osc/oscrc"
OSCRC_USER_FLAG = "@USERNAME@"
OSCRC_PASS_FLAG = "@PASSWORD@"
OSCRC_APIURL_FLAG = "@APIURL@"

# yum.repo config
YUM_REPO_TEMPLETE_FOLDER = os.path.join(
    CHECK_REQUIRES_CONFIG_FOLDER_PATH,
    "checkpart",
    "check_requires",
    "yum.repo"
)
OPENEULER_BRANCH_MAP = os.path.join(
    CHECK_REQUIRES_CONFIG_FOLDER_PATH,
    "checkpart",
    "check_requires",
    "support_branch.yaml"
)
SUPPORTED_BRANCHES_LIST = ["openEuler"]

LOG_DIR = "./"

# ip and port for sending update info to test
TEST_IP_PORT = "https://radiatest.openeuler.org"


# OBS 实时日志链接
OBS_PROJECT_LIVE_LOG= DEFAULT_OSCRC_APIURL + "/package/live_build_log/{obs_project}/{package}/{repo}/{arch}"
# oect top dir
LIBS_CONFIG_FOLDER = os.path.abspath(os.path.dirname(__file__))
# path of user-agent.json
USER_AGENT_JSON = f'{LIBS_CONFIG_FOLDER}/user-agent.json'
# gitee api config
GITEE_API_CONFIG = f'{LIBS_CONFIG_FOLDER}/gitee_api_config.yaml'
# gitee memebers id
GITEE_OPENEULER_MEMBERS_ID_YAML = f'{LIBS_CONFIG_FOLDER}/oe_memebers_id.yaml'