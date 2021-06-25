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


def get_whatrequires(
    pkg_list: list,
    published_repos: list,
    dev_repos: list,
    branch: str = "openEuler:20.03:LTS:SP1",
) -> dict:
    """
    get effected src rpm list which requires rpm in pkg_list

    Attributes:
        pkg_list: source rpm list
        published_repos: published repo name list in /etc/yum.repo.d/xxx.repo (repo.openuler.org/xxx etc.)
        dev_repos: develop repo name list in /etc/yum.repo.d/xxx.repo (obs.repo/xxxx etc.)
        branch: branch in obs proj such as (openEuler:20.03:LTS:SP1, openEuler:20.03:LTS:SP1:EPOL, etc.)

    return:
        pkg_dict = {
            src_rpm: [bin_rpm],
            ...
        }
    """
    pass


def get_update_install(
    pkg_list: list,
    published_repos: list,
    dev_repos: list,
    branch: str = "openEuler:20.03:LTS:SP1",
) -> dict:
    """
    get effected src rpm list which requires rpm in pkg_list

    Attributes:
        pkg_list: source rpm list
        published_repos: published repo name list in /etc/yum.repo.d/xxx.repo (repo.openuler.org/xxx etc.)
        dev_repos: develop repo name list in /etc/yum.repo.d/xxx.repo (obs.repo/xxxx etc.)
        branch: branch in obs proj such as (openEuler:20.03:LTS:SP1, openEuler:20.03:LTS:SP1:EPOL, etc.)

    return:
        pkg_dict = {
            src_rpm: [bin_rpm],
            ...
        }
    """
    pass
