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
from javcra.common.constant import PERMISSION_DICT

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
        group = self.sub_parse.add_mutually_exclusive_group(required=True)
        group.add_argument(
            '--add',
            help='adding a list of issues which would add to cve, bugfix, test or release list',
            default='',
            action='store',
            choices=['cve', 'bug', 'release']
        )
        group.add_argument(
            '--delete',
            help='deleting a list of issues which would add to cve, bugfix, test or release list',
            default='',
            action='store',
            choices=['cve', 'bug', 'release']
        )
        self.sub_parse.add_argument(
            '--id',
            help='the list of issueid which would add/del to cve, bugfix, test or release list',
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
        modify_type = ''

        if params.add:
            modify_type = params.add
            action = 'add'
        elif params.delete:
            modify_type = params.delete
            action = 'del'
        else:
            print("Cannot parse the parameter")
            return

        permission = validate_giteeid(issue_id, gitee_id, PERMISSION_DICT.get(modify_type))
        if not permission:
            return

        type_dict = {
            'cve': ModifyEntrance(issue_id, issue_list).modify_cve_list,
            'bug': ModifyEntrance(issue_id, issue_list).modify_bugfix_list,
            'release': ModifyEntrance(issue_id, issue_list).modify_release_result
        }

        print("modify part start!", issue_id, gitee_id, issue_list)
        type_dict.get(modify_type)(action)
