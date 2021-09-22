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

from javcra.application.modifypart.modifyentrance import IssueOperation
from javcra.application.serialize.serialize import StartSchema
from javcra.cli.base import BaseCommand
from javcra.cli.commands import parameter_permission_validate
from javcra.common.constant import GITEE_REPO


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
        self.add_subcommand_communal_args('start',
                                          help_desc="release assistant of start part")
        self.add_obs_ak_arg()
        self.add_obs_sk_arg()
        self.sub_parse.add_argument(
            "--useremail",
            type=str,
            help="the user's email address",
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
        comment = "/start-update"
        param_dict = {
            "issueid": params.releaseIssueID,
            "giteeid": params.giteeid,
            "repo": GITEE_REPO,
            "useremail": params.useremail,
            "ak": params.ak,
            "sk": params.sk,
            "token": params.token,
        }
        validate_result = parameter_permission_validate(
            StartSchema, param_dict, comment
        )
        if not validate_result:
            return
        issue = IssueOperation(GITEE_REPO, params.token, params.releaseIssueID)
        args = (params.useremail, params.ak, params.sk)
        start_res = issue.operate_release_issue(operation="init", *args)
        if start_res:
            print("[INFO] start update successfully.")
        else:
            print("[ERROR] failed to start update.")
