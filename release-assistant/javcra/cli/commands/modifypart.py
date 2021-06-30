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
Description: modify method's entrance for custom commands
Class:ModifyCommand
"""

from javcra.cli.base import BaseCommand
from javcra.application.serialize.validate import validate_giteeid
from javcra.application.modifypart.modifyentrance import ModifyEntrance

class ModifyCommand(BaseCommand):
    """
    Description: start the modiy part
    Attributes:
        sub_parse: Subcommand parameters
        params: Command line parameters
    """

    def __init__(self):
        """
        Description: Instance initialization
        """
        super(ModifyCommand, self).__init__()
        self.sub_parse = BaseCommand.subparsers.add_parser(
            'modify', help="release assistant of modify part")
        self.add_issueid_arg()
        self.add_giteeid_arg()
        group = self.sub_parse.add_mutually_exclusive_group()
        group.add_argument(
            '--add',
            help='adding a list of issues which would add to cve, bugfix or test list',
            default=True,
            action='store',
            choices=['cve', 'bug', 'test']
        )
        group.add_argument(
            '--delete',
            help='deleting a list of issues which would add to cve or bugfix list',
            default=True,
            action='store',
            choices=['cve', 'bug', 'test']
        )
        group.add_argument(
            '--release',
            help='(not) release a list of packages \
                which fixed cve or bugfix issues in this version',
            default=False,
            action='store',
            choices=['yes', 'no']
        )
        self.sub_parse.add_argument(
            '--id',
            help='the list of issueid which would add/del to cve or bugfix list',
            default=True,
            action='store',
            nargs='*',
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
        issue_id = params.releaseIssueID
        gitee_id = params.giteeid
        issue_list = params.id

        permission = validate_giteeid(issue_id, gitee_id)
        if not permission:
            return

        if params.release:
            print("modify release list", issue_id, gitee_id, issue_list)
            ModifyEntrance().modify_release_result()
            return

        if params.add == 'cve' or params.delete == 'cve':
            print("modify cve part", issue_id, gitee_id, issue_list)
            ModifyEntrance().modify_cve_list()
        elif params.add == 'bug' or params.delete == 'bug':
            print("modify bugfix part", issue_id, gitee_id, issue_list)
            ModifyEntrance().modify_bugfix_list()
        else:
            print("modify test part", issue_id, gitee_id, issue_list)
            ModifyEntrance().modify_test_list()
