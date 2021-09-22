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
from javcra.cli.commands import parameter_permission_validate
from javcra.application.modifypart.modifyentrance import IssueOperation
from javcra.application.serialize.serialize import ModifySchema
from javcra.common.constant import GITEE_REPO


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
        self.add_subcommand_communal_args('modify',
                                          help_desc="release assistant of modify part")
        group = self.sub_parse.add_mutually_exclusive_group(required=True)
        group.add_argument(
            '--add',
            help='adding a list of issues which would add to cve, bugfix, test or remain list',
            default='',
            action='store',
            choices=['cve', 'bugfix', 'remain']
        )
        group.add_argument(
            '--delete',
            help='deleting a list of issues which would add to cve, bugfix, test or remain list',
            default='',
            action='store',
            choices=['cve', 'bugfix', 'remain']
        )
        self.sub_parse.add_argument(
            '--id',
            help='the list of issueid which would add/del to cve, bugfix, test or remain list',
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
        # parameter dictionary
        param_dict = {
            "issueid": params.releaseIssueID,
            "giteeid": params.giteeid,
            "id": params.id,
            "choice": params.add or params.delete,
            "token": params.token,
        }

        # get action and modify_type according to parameters
        action = "add" if params.add else "delete"
        modify_type = params.add if params.add else params.delete
        comment = "/" + action + "-" + modify_type
        if modify_type == "remain":
            comment = "/no-release"
        validate_result = parameter_permission_validate(
            ModifySchema, param_dict, comment
        )
        if not validate_result:
            return

        # add or delete issues according to your choice
        issue = IssueOperation(GITEE_REPO, params.token, params.releaseIssueID)
        modify_res = issue.operate_release_issue(operation=action, operate_block=modify_type, issues=params.id)
        if modify_res:
            print("[INFO] %s %s in %s successfully." % (action, ",".join(params.id), modify_type))
        else:
            print(
                "[ERROR] failed to %s %s in %s."
                % (action, ",".join(params.id), modify_type)
            )
        if modify_type == "remain":
            check_res = issue.update_remain_issue_state(params.id, action)
            if check_res:
                print("update remain issues successfully.")
            else:
                print("failed to update remain issues, "
                      "please check whether the issue exist in cve and bugfix part.")
