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
# Author: DisNight
# Create: 2021-06-24
# ******************************************************************************/

import os
import yaml
import logging

from yaml.error import YAMLError
from javcra.libs.config.global_config import (
    SUCCEED,
    FAILED,
    DEFAULT_OSCRC_APIURL,
    DEFAULT_OSCRC_POSITION,
    OSCRC_TEMPLETE,
    OSCRC_USER_FLAG,
    OSCRC_PASS_FLAG,
    OSCRC_APIURL_FLAG,
    OPENEULER_BRANCH_MAP,
    SUPPORTED_BRANCHES_LIST,
    YUM_REPO_TEMPLETE_FOLDER,
)


def init_oscrc(
    user: str,
    pswd: str,
    apiurl: str = DEFAULT_OSCRC_APIURL,
    oscrc: str = DEFAULT_OSCRC_POSITION,
    osc_templete: str = OSCRC_TEMPLETE,
) -> int:
    """
    init osc config file oscrc

    Attributes:
        user: username of obs account
        pass: password of obs account
        apiurl: remote of obs server
        oscrc: the position of oscrc file
        osc_templete: the position of oscrc templete

    return:
        finish_code:
            succeed : 0
            failed  : 1
    """
    if os.path.exists(oscrc):
        logging.info("%s exist, skip init step", oscrc)
        return SUCCEED
    if not os.path.exists(osc_templete):
        logging.error("init oscrc failed: %s templete not exist", osc_templete)
        return SUCCEED
    oscrc_data = ""

    # scanf format templete from file
    try:
        with open(osc_templete, "r") as f:
            oscrc_data = f.read()
    except UnicodeDecodeError as ude:
        logging.error("init oscrc failed: %s", str(ude))
        oscrc_data = ""
    if not oscrc_data:
        logging.error("cannot scan data from oscrc.template")
        return FAILED

    oscrc_data = oscrc_data.replace(OSCRC_USER_FLAG, user)
    oscrc_data = oscrc_data.replace(OSCRC_PASS_FLAG, pswd)
    oscrc_data = oscrc_data.replace(OSCRC_APIURL_FLAG, apiurl)

    try:
        with open(oscrc, "a") as f:
            f.write(oscrc_data)
    except UnicodeEncodeError as uee:
        logging.error("init oscrc failed: %s", str(uee))
        _ = os.path.exists(oscrc) and os.remove(oscrc)

    if not os.path.exists(oscrc):
        logging.warning("please init oscrc by yourself")
        return FAILED
    return SUCCEED


def load_support_branch(bmap_file: str = OPENEULER_BRANCH_MAP) -> dict:
    """
    load supported branch from configure file(yaml)

    Attributes:
        bmap_file: supported_branch.yaml

    return:
        dict bmap: {
            <obs project name> : <supported branch>,
            ......
        }
    """
    # load support branch map from config file
    temp_map = {}
    try:
        with open(bmap_file, "r") as f:
            temp_map = yaml.safe_load(f)
    except YAMLError as ye:
        logging.error("load branch map error: %s", str(ye))
        temp_map = {}
    if not temp_map:
        return temp_map

    # parse yaml format to  gitee_branch_name:obs_project_name
    bmap = {}
    for support_branch in SUPPORTED_BRANCHES_LIST:
        for bname in temp_map.get(support_branch, []):
            if not temp_map[support_branch][bname].get("obs_alias", ""):
                continue
            bmap[bname] = temp_map[support_branch][bname]["obs_alias"]
    return bmap


def get_yum_repo_file(branch: str, bmap_file: str = OPENEULER_BRANCH_MAP) -> str:
    """
    get specified branch's yum repo file

    Attributes:
        branch: branch in gitee or project name in obs
        bmap_file: supported_branch.yaml

    return:
        yum_repo_file:
            the specified branch's yum repo file
    """
    if not branch:
        logging.warning("branch is empty, skip this step")
        return ""
    bmap = load_support_branch(bmap_file)
    yum_repo_file = ""
    if not bmap:
        logging.warning("can not find specify branch, use local yum repo file")
        return ""
    key_list = list(bmap.keys())
    val_list = list(bmap.values())
    if branch in key_list:
        yum_repo_file = os.path.join(YUM_REPO_TEMPLETE_FOLDER, "{}.repo".format(branch))
        if not os.path.exists(yum_repo_file):
            logging.error(
                "template yum repo file [%s.repo] is missing",
                branch
            )
            return ""
        return yum_repo_file
    if branch in val_list:
        # find key from dict by value
        tmp_bname = key_list[val_list.index(branch)]
        yum_repo_file = os.path.join(
            YUM_REPO_TEMPLETE_FOLDER, "{}.repo".format(tmp_bname)
        )
        if not os.path.exists(yum_repo_file):
            logging.error(
                "template yum repo file [%s.repo] is missing",
                branch
            )
            return ""
        return yum_repo_file

    logging.warning("branch [%s] is not supporter", branch)
    return ""
