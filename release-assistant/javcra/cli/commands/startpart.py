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
Description: start method's entrance for custom commands
Class:StartCommand
"""

from javcra.cli.base import BaseCommand
from javcra.application.startpart.startentrance import StartEntrance

class StartCommand(BaseCommand):
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
        super(StartCommand, self).__init__()
        self.sub_parse = BaseCommand.subparsers.add_parser(
            'start', help="release assistant of start part")
        self.params = [
            self.sub_args(
                sub_command='releaseIssueID',
                help='start release issue ID',
                default=True,
                action='store',
                nargs=None,
                required=None,
                choices=None),
            self.sub_args(
                sub_command='--giteeid',
                help='the Gitee ID who trigger this command',
                default=True,
                action='store',
                nargs=None,
                required=True,
                choices=None)
        ]

    def register(self):
        """
        Description: Command line parameter registered
        Args:

        Returns:

        Raises:

        """
        super(StartCommand, self).register()
        self.sub_parse.set_defaults(func=self.do_command)

    @staticmethod
    def do_command(params):
        """
        Description: Executing command
        Args:
            params: Command line parameters
        Returns:

        Raises:

        """
        issue_id = params.releaseIssueID
        gitee_id = params.giteeid
        print("start part", issue_id, gitee_id)
        StartEntrance().get_pkg_list()
