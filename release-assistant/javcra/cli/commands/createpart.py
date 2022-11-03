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

from javcra.create_release import UpdateIssue
from javcra.cli.base import BaseCommand
from javcra.common.constant import GITEE_REPO, LABEL_DICT
from javcra.libs.log import logger


class CreateCommand(BaseCommand):
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
        super(CreateCommand, self).__init__()
        self.sub_parse = BaseCommand.subparsers.add_parser(
            "create", help="command to create release issue")

        self.sub_parse.add_argument(
            "--token",
            type=str,
            help="a valid GiteeToken value",
            action="store",
            required=True,
        )

    def do_command(self, params):
        """
        Description: Executing command
        Args:
            params: Command line parameters
        """
        issue = UpdateIssue(GITEE_REPO, params.token)
        create_res = issue.create_update_release()
        if create_res:
            logger.info("create release successfully.")
        else:
            logger.error("failed to create release.")
