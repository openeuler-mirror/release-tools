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
Description:majun start method's entrance for custom commands
Class:StartMajunCommand
"""
from javcra.cli.base import BaseCommand
from javcra.application.majun.majun_start import MaJunStart


class StartMajunCommand(BaseCommand):
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
        super(StartMajunCommand, self).__init__()
        self.sub_parse = BaseCommand.subparsers.add_parser(
            "majunstart", help="majun start"
        )
        self.add_obs_ak_arg()
        self.add_obs_sk_arg()
        self.sub_parse.add_argument(
            "--useremail",
            type=str,
            help="the user's email address",
            action="store",
            required=True,
        )
        self.sub_parse.add_argument(
            "--task_title",
            type=str,
            help="task title eg.openEuler-20.03-LTS-SP1_update20221013",
            action="store",
            required=True,
        )
        self.sub_parse.add_argument(
            "--id",
            type=str,
            help="uuid",
            action="store",
            required=True,
        )

    def do_command(self, params):
        """
        Description: Executing command
        Args:
            params: Command line parameters
        Returns:

        Raises:

        """
        majunstart = MaJunStart()
        majunstart.send_cve_list_to_majun(params)
        
