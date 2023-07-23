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
Description: majun method's entrance for custom commands
Class:MajunOperateRepoCommand
"""
from javcra.cli.base import BaseCommand
from javcra.application.majun.majun_operate import MajunOperate


class MajunOperateRepoCommand(BaseCommand):
    """
    Description: start the release assistant
    Attributes:
        sub_parse: Subcommand parameters
        params: Command line parameters
    """

    def __init__(self):
        """
        Description: Instance initialization
        """
        super(MajunOperateRepoCommand, self).__init__()
        self.sub_parse = BaseCommand.subparsers.add_parser(
            "majunrepo", help="majun operate repo"
        )
        self.sub_parse.add_argument(
            "--task_title",
            type=str,
            help="task title eg.openEuler-20.03-LTS-SP1_update20221013",
            action="store",
            required=True,
        )
        self.sub_parse.add_argument(
            "--pkglist", required=False, nargs="+", help="package names"
        )
        self.sub_parse.add_argument(
            "--id",
            type=str,
            help="uuid",
            action="store",
            required=True,
        )
        self.sub_parse.add_argument(
            "--jenkinsuser",
            type=str,
            help="provide your jenkinsuser",
            action="store",
            required=True,
        )
        self.sub_parse.add_argument(
            "--jenkinskey",
            type=str,
            help="provide your jenkins key",
            action="store",
            required=True,
        )
        self.sub_parse.add_argument(
            "--action",
            type=str,
            help="the action of the repo operation",
            action="store",
            required=True,
            choices=["create", "del_pkg_rpm", "update", "del_update_dir"],
        )
        self.sub_parse.add_argument(
            "--package_family",
            type=str,
            help="owning group of the software package",
            action="store",
            required=False,
            choices=["standard", "EPOL", "EPOL-main", "EPOL-multi_version"],
        )

    def do_command(self, params):
        """
        Description: Executing command
        Args:
            params: Command line parameters
        Returns:

        Raises:

        """

        checkmajun = MajunOperate()
        checkmajun.operate_repo(params)
